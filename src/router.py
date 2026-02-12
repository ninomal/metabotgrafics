import asyncio
from fastapi import APIRouter, Query # <--- Importamos Query
from typing import List, Optional
from src.bot_instance import global_bot
from src.schemas import BotStatusResponse, ActionResponse, CandleResponse
from src.config.settings import settings
import MetaTrader5 as mt5

router = APIRouter()

@router.get("/status", response_model=BotStatusResponse)
async def get_status():
    """Retorna o estado atual do bot."""
    return {
        "isRunning": global_bot.running,
        "symbol": settings.SYMBOL,
        "strategy": "RSI + OrderBlock",
        "activeOrders": 0
    }

@router.post("/start", response_model=ActionResponse)
async def start_bot():
    """Inicia o processamento do bot."""
    if global_bot.running:
        return {"success": False, "message": "Bot is already running."}
    
    asyncio.create_task(global_bot.run_cycle())
    return {"success": True, "message": "Bot started successfully."}

@router.post("/stop", response_model=ActionResponse)
async def stop_bot():
    """Para o processamento do bot."""
    if not global_bot.running:
        return {"success": False, "message": "Bot is not running."}
    
    global_bot.stop()
    return {"success": True, "message": "Bot stopped successfully."}

@router.get("/symbols", response_model=List[str])
async def get_all_symbols():
    """Endpoint para pegar a lista de moedas."""
    return global_bot.mt5_service.get_available_symbols()

@router.get("/chart-data", response_model=List[CandleResponse])
async def get_chart_data(symbol: Optional[str] = Query(None)): # <--- MUDANÇA CRÍTICA: = Query(None)
    """
    Endpoint para pegar dados do gráfico.
    Usa Query(None) para garantir que o FastAPI leia o ?symbol=USDJPY da URL.
    """
    # 1. Garante conexão
    if not global_bot.mt5_service.connected:
        global_bot.mt5_service.initialize()

    # 2. Define o símbolo (da URL ou padrão)
    target_symbol = symbol if symbol else settings.SYMBOL
    
    # 3. DEBUG: Imprime no terminal para sabermos o que está acontecendo
    print(f"🔍 DEBUG: Frontend pediu: '{symbol}' -> Backend vai buscar: '{target_symbol}'")

    # 4. Define Timeframe
    tf_map = {
        "M1": mt5.TIMEFRAME_M1, 
        "M5": mt5.TIMEFRAME_M5, 
        "H1": mt5.TIMEFRAME_H1,
        "D1": mt5.TIMEFRAME_D1
    }
    timeframe = tf_map.get(settings.TIMEFRAME, mt5.TIMEFRAME_M5)

    # 5. Busca os dados
    candles = global_bot.mt5_service.get_candles(
        symbol=target_symbol,
        timeframe=timeframe,
        num_candles=100
    )

    return candles

# ---  TELEGRAM ENDPOINT ---
@router.post("/telegram_test", response_model=ActionResponse)
async def send_telegram_alert():
    """
    Captures a full-screen screenshot and sends it to the configured Telegram chat.
    This is asynchronous to prevent blocking the main thread.
    """
    # 1. Check if the service is initialized and has a token
    if not global_bot.telegram_service.bot:
        return {
            "success": False, 
            "message": "Telegram credentials not configured in .env"
        }

    try:
        # 2. Send a text notification first
        status_text = "RUNNING" if global_bot.running else "STOPPED"
        await global_bot.telegram_service.send_message(
            f"📸 **Screenshot Requested!**\n"
            f"Asset: {settings.SYMBOL}\n"
            f"Bot Status: {status_text}"
        )

        # 3. Capture and send the screenshot (Async upload)
        # We assume you implemented send_screenshot in the service as discussed
        await global_bot.telegram_service.send_screenshot(
            caption=f"Current Chart: {settings.SYMBOL}"
        )

        return {
            "success": True, 
            "message": "Screenshot sent to Telegram successfully!"
        }

    except Exception as e:
        print(f"❌ Error sending to Telegram: {e}")
        return {
            "success": False, 
            "message": f"Failed to send: {str(e)}"
        }