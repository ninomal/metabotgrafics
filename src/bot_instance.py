import asyncio
from src.services.mt5_service import MT5Service
from src.services.telegram_service import TelegramService 

class TradingBot:
    """
    Main class that orchestrates the trading logic, connecting MT5, 
    Telegram, and the strategy.
    """
    def __init__(self):
        self.running = False
        
        # Initialize Services
        self.mt5_service = MT5Service()
        self.telegram_service = TelegramService()  
    
    async def run_cycle(self):
        """
        Main analysis cycle (Infinite Loop).
        This method will be called when you click 'START' on the dashboard.
        """
        print("🚀 Bot started! Waiting for market data...")
        
        while self.running:
            try:
                # Placeholder for future strategy logic:
                # 1. Get Candle Data -> self.mt5_service.get_candles(...)
                # 2. Analyze Strategy (RSI, OrderBlock)
                # 3. Execute Trade -> self.mt5_service.open_trade(...)
                # 4. Send Alert -> await self.telegram_service.send_message(...)
                
                print("💤 Bot heartbeat... (Analysis pending)")
                
                # Wait 5 seconds before next check to avoid overloading CPU
                await asyncio.sleep(5) 
                
            except Exception as e:
                print(f"❌ Error in main cycle: {e}")
                await asyncio.sleep(5) # Wait before retrying

    def stop(self):
        """Stops the analysis cycle."""
        self.running = False
        print("🛑 Bot stopped.")

# Global instance used by the API Router
global_bot = TradingBot()