from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # --- Configurações do MetaTrader 5 ---
    # Field(...) torna o campo obrigatório. Se não estiver no .env, dá erro.
    MT5_LOGIN: int = Field(..., description="Número da conta MT5")
    MT5_PASSWORD: str = Field(..., description="Senha do MT5")
    MT5_SERVER: str = Field(..., description="Nome do servidor da corretora")
    MT5_PATH: str = Field(r"C:\Program Files\MetaTrader 5\terminal64.exe", description="Caminho do executável")

    # --- Configurações de Trade ---
    SYMBOL: str = Field("EURUSDm", description="Ativo para operar")
    TIMEFRAME: str = Field("M5", description="Tempo gráfico")
    VOLUME: float = Field(0.01, description="Lote inicial")

    # --- Configurações do Telegram ---
    # Optional: Se você não preencher agora, o programa não quebra, mas o bot não funciona
    TELEGRAM_TOKEN: str = Field("", description="Token do BotFather")
    TELEGRAM_CHAT_ID: str = Field("", description="ID do seu chat")

    # Configuração do Pydantic v2 para ler o arquivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variáveis extras no .env se houver
    )

# Instancia as configurações para serem usadas no resto do projeto
settings = Settings()