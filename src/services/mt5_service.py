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
        Fetches candles and applies VSA (Volume Spread Analysis) logic.
        - Normal Volume: Standard Green/Red (Opaque)
        - High Volume (Flow): Neon Green/Red (Bright)
        """
        if not self.connected:
            self.initialize()

        if not mt5.symbol_select(symbol, True):
            print(f"⚠️ Symbol {symbol} not found.")
            return []
        
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            return []

        # 1. Calculate Average Volume
        total_volume = sum(r['tick_volume'] for r in rates)
        avg_volume = total_volume / len(rates)
        
        # --- REAL VSA LOGIC ---
        # Highlights only volumes 50% above the average (1.5x)
        flow_threshold = avg_volume * 1.5 
        
        data_list = []
        for rate in rates:
            close = float(rate['close'])
            open_price = float(rate['open'])
            volume = int(rate['tick_volume'])
            
            # 1. Default Colors (Standard Volume - Opaque)
            # Bullish: #22c55e | Bearish: #ef4444
            color = '#22c55e' if close >= open_price else '#ef4444'
            
            # 2. Flow Logic (Big Player Detected)
            if volume > flow_threshold:
                if close >= open_price:
                    # STRONG BUY FLOW (Neon Green)
                    color = '#00FF00' 
                else:
                    # STRONG SELL FLOW (Neon Red)
                    color = '#FF0040' 

            # Send all data to the Frontend
            data_list.append({
                "time": int(rate['time']),
                "open": open_price,
                "high": float(rate['high']),
                "low": float(rate['low']),
                "close": close,
                "tick_volume": volume,
                # Dynamic Colors
                "color": color,
                "wickColor": color,
                "borderColor": color
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