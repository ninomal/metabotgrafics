import asyncio
import logging
import sys
from src.main import TradingBot

# Configure Logging (To see what's happening in the console)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def run_application():
    """
    Entry point for the Async Application.
    """
    logger.info("🚀 Starting Trading Bot Application...")
    
    # Instantiate the Main Bot Orchestrator
    bot = TradingBot()
    
    try:
        # Start the main loop
        await bot.start()
    except KeyboardInterrupt:
        logger.warning("🛑 User stopped the application (Ctrl+C).")
    except Exception as e:
        logger.error(f"❌ Critical Error: {e}")
    finally:
        # Graceful Shutdown
        logger.info("💤 Shutting down services...")
        bot.stop()
        sys.exit(0)

if __name__ == "__main__":
    try:
        # Windows specific event loop policy (avoids common errors on Windows)
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
        asyncio.run(run_application())
    except KeyboardInterrupt:
        pass