import asyncio
from fastapi import APIRouter, HTTPException
from src.bot_instance import global_bot
from src.schemas import BotStatusResponse, ActionResponse
from src.config.settings import settings

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