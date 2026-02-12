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
        Fetches historical candles (rates) from MT5 and converts them to a list of dictionaries.
        
        Args:
            symbol (str): The asset symbol (e.g., "EURUSD").
            timeframe: MT5 timeframe constant (e.g., mt5.TIMEFRAME_M5).
            num_candles (int): Number of past candles to retrieve.
        """
        if not self.connected:
            self.initialize()

        # IMPORTANT: Ensure symbol is selected in Market Watch
        # The second argument 'True' forces the symbol to be enabled
        if not mt5.symbol_select(symbol, True):
            print(f"⚠️ Symbol {symbol} not found or could not be selected.")
            return []
        
        # Get candles from current time backwards
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            print(f"⚠️ No data retrieved for {symbol}")
            return []
            
        # Convert Numpy Array to List of Dictionaries (JSON friendly)
        data_list = []
        for rate in rates:
            data_list.append({
                "time": int(rate['time']),
                "open": float(rate['open']),
                "high": float(rate['high']),
                "low": float(rate['low']),
                "close": float(rate['close']),
                "tick_volume": int(rate['tick_volume'])
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