import MetaTrader5 as mt5
from src.config.settings import settings

class MT5Service:
    def __init__(self):
        # Initialize connection state to prevent AttributeErrors
        self.connected = False

    def initialize(self):
        """
        Initializes the connection to MetaTrader 5 using settings.
        Returns True if successful, False otherwise.
        """
        # Attempt to initialize with the specific path
        if not mt5.initialize(path=settings.MT5_PATH):
            print(f"❌ MT5 Initialization failed. Error: {mt5.last_error()}")
            self.connected = False
            return False
        
        # Ensure we are logged into the correct account
        authorized = mt5.login(
            login=settings.MT5_LOGIN, 
            password=settings.MT5_PASSWORD, 
            server=settings.MT5_SERVER
        )
        
        if not authorized:
            print(f"❌ Failed to login to account {settings.MT5_LOGIN}. Error: {mt5.last_error()}")
            self.connected = False
            return False
            
        print("✅ MT5 Connected Successfully")
        self.connected = True
        return True

    def shutdown(self):
        """Closes the connection to MT5."""
        mt5.shutdown()
        self.connected = False

    def get_available_symbols(self):
        """
        Retrieves a list of all available symbol names from MT5.
        Returns: list[str]
        """
        if not self.connected:
            if not self.initialize():
                return []
        
        # Fetch all symbols from the broker
        symbols_info = mt5.symbols_get()
        
        if symbols_info:
            # Extract just the name using list comprehension
            return [s.name for s in symbols_info]
        
        return []

    def get_candles(self, symbol: str, timeframe, num_candles: int = 100):
        """
        Fetches candles, applies VSA, and detects V-Shape Patterns.
        Filters:
        1. VSA Threshold: 1.5x Average Volume.
        2. V-Shape Cooldown: Must wait 3 candles between patterns.
        3. V-Shape Size: Candle must be larger than the average body size (no noise).
        """
        if not self.connected:
            self.initialize()

        if not mt5.symbol_select(symbol, True):
            print(f"⚠️ Symbol {symbol} not found.")
            return []
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            return []

        # 1. Calculate Average Volume (for VSA)
        total_volume = sum(r['tick_volume'] for r in rates)
        avg_volume = total_volume / len(rates)
        flow_threshold = avg_volume * 1.5 

        # 2. Calculate Average Body Size (for Volatility Filter)
        # We need this to avoid marking tiny candles as patterns
        total_body_size = sum(abs(r['open'] - r['close']) for r in rates)
        avg_body_size = total_body_size / len(rates)
        
        data_list = []
        
        # Track the index of the last detected pattern to enforce the "3 candle rule"
        last_pattern_index = -10 
        
        for i in range(len(rates)):
            rate = rates[i]
            
            close = float(rate['close'])
            open_price = float(rate['open'])
            high = float(rate['high'])
            low = float(rate['low'])
            volume = int(rate['tick_volume'])
            
            # --- Default Colors ---
            color = '#22c55e' if close >= open_price else '#ef4444'
            
            # --- VSA Logic ---
            if volume > flow_threshold:
                if close >= open_price:
                    color = '#00FF00' 
                else:
                    color = '#FF0040' 

            # --- V-SHAPE PATTERN LOGIC (Filtered) ---
            pattern_name = None 
            
            # Rule 1: Must have a previous candle
            # Rule 2: COOLDOWN - Ensure 3 candles passed since last pattern
            if i > 0 and (i - last_pattern_index) >= 3:
                
                prev_rate = rates[i-1]
                prev_open = float(prev_rate['open'])
                prev_close = float(prev_rate['close'])
                
                # Check Direction: Red then Green
                is_prev_bearish = prev_close < prev_open
                is_curr_bullish = close > open_price
                
                if is_prev_bearish and is_curr_bullish:
                    prev_body = prev_open - prev_close
                    curr_body = close - open_price
                    
                    # Rule 3: VOLATILITY FILTER
                    # The previous drop must be at least the size of an average candle.
                    # This ignores tiny noise.
                    if prev_body > avg_body_size:
                        
                        # Rule 4: Strong Recovery (>80%)
                        if curr_body >= (prev_body * 0.8):
                            pattern_name = "V_SHAPE"
                            color = '#FF00FF' # Hot Pink
                            
                            # Update the tracker so we don't mark the next few candles
                            last_pattern_index = i 

            data_list.append({
                "time": int(rate['time']),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "tick_volume": volume,
                "color": color,
                "wickColor": color,
                "borderColor": color,
                "pattern": pattern_name 
            })

        return data_list
        
    def get_symbol_price(self, symbol: str):
        """Gets the current Ask/Bid price for a symbol."""
        if not self.connected:
            self.initialize()

        if not mt5.symbol_select(symbol, True):
            print(f"⚠️ Symbol {symbol} not found or not visible.")
            return None
            
        tick = mt5.symbol_info_tick(symbol)
        return tick