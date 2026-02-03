import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.router import router
from src.bot_instance import global_bot

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🔥 API Starting up...")
    yield
    # Shutdown (Garante que o robô pare se derrubarem o servidor)
    logger.info("🧯 API Shutting down...")
    if global_bot.is_running:
        global_bot.stop()

def create_app() -> FastAPI:
    app = FastAPI(title="Trading Bot API", version="1.0.0", lifespan=lifespan)

    # Configura CORS (Permite React)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclui as rotas
    app.include_router(router, prefix="/api")

    return app

# Instância para o Uvicorn achar
app = create_app()