import asyncio
from fastapi import APIRouter, HTTPException
from src.bot_instance import global_bot
from src.schemas import BotStatusResponse, ActionResponse, CandleResponse
from src.config.settings import settings
import MetaTrader5 as mt5
from typing import List

router = APIRouter()

@router.get("/status", response_model=BotStatusResponse)
async def get_status():
    return {
        "is_running": global_bot.is_running,
        "symbol": settings.SYMBOL,
    }


@router.post("/start", response_model=ActionResponse)
async def start_bot():
    if global_bot.is_running:
        return {"status": "warning", "message": "Bot is already running!"}
    
    # Cria a task em background sem travar a API
    asyncio.create_task(global_bot.start())
    
    return {"status": "success", "message": "Bot started successfully."}

@router.post("/stop", response_model=ActionResponse)
async def stop_bot():
    if not global_bot.is_running:
        return {"status": "warning", "message": "Bot is not running."}
    
    global_bot.stop()
    return {"status": "success", "message": "Stop signal sent."}

@router.get("/chart-data", response_model=List[CandleResponse])
async def get_chart_data():
    """
    Retorna os últimos 100 candles do ativo configurado.
    """
    # 1. Tenta reconectar se o MT5 tiver caído (segurança)
    if not mt5.terminal_info():
        global_bot.mt5_service.initialize()

    # 2. Define o timeframe (Pegando do settings ou padrão M5)
    # Mapeamento rápido de string para constante do MT5
    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "H1": mt5.TIMEFRAME_H1,
        "D1": mt5.TIMEFRAME_D1
    }
    timeframe = tf_map.get(settings.TIMEFRAME, mt5.TIMEFRAME_M5)

    # 3. Busca os dados usando o serviço que já criamos
    rates = global_bot.mt5_service.get_historical_data(
        symbol=settings.SYMBOL,
        timeframe=timeframe,
        num_candles=100
    )

    if rates is None or len(rates) == 0:
        return []

    # 4. Converte Numpy Array para Lista de Dicionários (JSON Friendly)
    data_list = []
    for rate in rates:
        data_list.append({
            "time": int(rate['time']), # React usa timestamp em segundos ou milissegundos
            "open": float(rate['open']),
            "high": float(rate['high']),
            "low": float(rate['low']),
            "close": float(rate['close']),
            "tick_volume": int(rate['tick_volume'])
        })

    return data_list