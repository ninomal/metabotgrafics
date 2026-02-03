import MetaTrader5 as mt5
from src.config.settings import settings

class TradeService:
    def __init__(self):
        self.magic_number = 123456 # Unique ID for this bot's orders

    def open_buy(self, symbol: str, volume: float, sl: float = 0.0, tp: float = 0.0):
        """
        Opens a Market BUY Order.
        """
        # 1. Prepare the request structure
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print("❌ Error: Could not get price for Buy order.")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": sl,
            "tp": tp,
            "deviation": 20, # Max slippage allowed (points)
            "magic": self.magic_number,
            "comment": "Python Bot Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 2. Send the order
        result = mt5.order_send(request)
        return self._process_result(result, "BUY")

    def open_sell(self, symbol: str, volume: float, sl: float = 0.0, tp: float = 0.0):
        """
        Opens a Market SELL Order.
        """
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print("❌ Error: Could not get price for Sell order.")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic_number,
            "comment": "Python Bot Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return self._process_result(result, "SELL")

    def _process_result(self, result, order_type):
        """Internal helper to print result status."""
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ {order_type} Order Failed. Error Code: {result.retcode}")
            print(f"   Description: {result.comment}")
            return None
        
        print(f"✅ {order_type} Executed Successfully! Ticket: {result.order}")
        return result