import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from src.config.settings import settings

class MT5Service:
    def initialize(self):
        """
        Initializes the connection to MetaTrader 5.
        Returns True if successful, False otherwise.
        """
        if not mt5.initialize(path=settings.MT5_PATH):
            print(f"❌ MT5 Initialization failed. Error: {mt5.last_error()}")
            return False
        
        # Ensure we are logged into the correct account
        authorized = mt5.login(
            login=settings.MT5_LOGIN, 
            password=settings.MT5_PASSWORD, 
            server=settings.MT5_SERVER
        )
        
        if not authorized:
            print(f"❌ Failed to login to account {settings.MT5_LOGIN}. Error: {mt5.last_error()}")
            return False
            
        return True

    def shutdown(self):
        """Closes the connection to MT5."""
        mt5.shutdown()

    def get_symbol_price(self, symbol: str):
        """Gets the current Ask/Bid price for a symbol."""
        if not mt5.symbol_select(symbol, True):
            print(f"⚠️ Symbol {symbol} not found or not visible.")
            return None
            
        tick = mt5.symbol_info_tick(symbol)
        return tick

    def get_historical_data(self, symbol: str, timeframe, num_candles: int = 100):
        """
        Fetches historical candles (rates) from MT5.
        
        Args:
            symbol (str): The asset symbol (e.g., "EURUSDm").
            timeframe: MT5 timeframe constant (e.g., mt5.TIMEFRAME_M5).
            num_candles (int): Number of past candles to retrieve.
        """
        # Ensure symbol is selected
        mt5.symbol_select(symbol, True)
        
        # Get candles from current time backwards
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
        
        if rates is None or len(rates) == 0:
            print(f"⚠️ No data retrieved for {symbol}")
            return None
            
        return rates
    

    def get_available_symbols(self):
        """
        Retrieves a list of all available symbol names from MT5.
        Returns: list[str]
        """
        if not self.connected:
            self.initialize()
        
        # Fetch all symbols
        symbols_info = mt5.symbols_get()
        
        if symbols_info:
            # Extract just the name using list comprehension
            return [s.name for s in symbols_info]
        return []