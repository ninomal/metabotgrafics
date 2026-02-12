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