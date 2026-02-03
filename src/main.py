import asyncio
import logging
import MetaTrader5 as mt5

from src.config.settings import settings
from src.services.mt5_service import MT5Service
from src.services.trade_service import TradeService
from src.strategy.analysis import MarketAnalyzer
from src.utils import get_mt5_timeframe


logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        # Initialize Services
        self.mt5_service = MT5Service()
        self.trade_service = TradeService()
        self.analyzer = MarketAnalyzer()
        self.is_running = False

    async def start(self):
        """
        Main execution loop.
        """
        # 1. Connect to MT5
        if not self.mt5_service.initialize():
            logger.error("❌ Failed to connect to MT5. Exiting...")
            return

        self.is_running = True
        logger.info(f"✅ Bot connected to {settings.MT5_SERVER} | Account: {settings.MT5_LOGIN}")
        logger.info(f"📊 Monitoring: {settings.SYMBOL} | Timeframe: {settings.TIMEFRAME}")

        # 2. Infinite Loop
        while self.is_running:
            try:
                await self.tick()
                
                # Sleep for 1 second before next tick to save CPU
                # (You can adjust this based on your strategy needs)
                await asyncio.sleep(1) 
                
            except Exception as e:
                logger.error(f"⚠️ Error in main loop: {e}")
                await asyncio.sleep(5) # Wait a bit on error before retrying

    async def tick(self):
        """
        Single execution step (The logic happens here).
        """
        symbol = settings.SYMBOL
        
        # A. Check connection (Watchdog)
        if not mt5.terminal_info():
            logger.warning("⚠️ MT5 connection lost, reconnecting...")
            self.mt5_service.initialize()
            return

        # B. Get Data
        current_tf = get_mt5_timeframe(settings.TIMEFRAME)

        df = self.mt5_service.get_historical_data(
            symbol=symbol, 
            timeframe=current_tf, 
            num_candles=100
        )

        if df is None:
            return

        # C. Analyze Strategy (Delegating to Strategy Layer)
        df_analyzed = self.analyzer.prepare_data(df)
        
        buy_signal = self.analyzer.check_buy_signal(df_analyzed)
        sell_signal = self.analyzer.check_sell_signal(df_analyzed)

        # D. Execute Trade (Delegating to Trade Layer)
        if buy_signal:
            logger.info(f"🟢 BUY SIGNAL DETECTED for {symbol}")
            # Check if we already have positions to avoid opening 1000 orders
            positions = mt5.positions_get(symbol=symbol)
            if positions is None or len(positions) == 0:
                self.trade_service.open_buy(symbol, settings.VOLUME)
                # await self.telegram.send_message("Buy Order Executed!")
            
        elif sell_signal:
            logger.info(f"🔴 SELL SIGNAL DETECTED for {symbol}")
            positions = mt5.positions_get(symbol=symbol)
            if positions is None or len(positions) == 0:
                self.trade_service.open_sell(symbol, settings.VOLUME)
                # await self.telegram.send_message("Sell Order Executed!")

    def stop(self):
        """Stops the bot safely."""
        self.is_running = False
        self.mt5_service.shutdown()
        logger.info("Bot Stopped.")