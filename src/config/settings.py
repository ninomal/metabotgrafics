import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # --- MetaTrader 5 Configuration ---
    MT5_LOGIN: int = Field(..., description="MT5 Account Number")
    MT5_PASSWORD: str = Field(..., description="MT5 Account Password")
    MT5_SERVER: str = Field(..., description="Broker Server Name")
    # Using raw string (r"...") to avoid issues with backslashes in Windows paths
    MT5_PATH: str = Field(r"C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe", description="Path to terminal64.exe")

    # --- Trading Configuration ---
    SYMBOL: str = Field("EURUSDm", description="Symbol to trade")
    TIMEFRAME: str = Field("M5", description="Timeframe string (e.g., M5, H1)")
    VOLUME: float = Field(0.01, description="Trade volume")

    # --- Telegram Configuration ---
    # Optional fields (default to empty string if not provided)
    TELEGRAM_TOKEN: str = Field("", description="BotFather Token")
    TELEGRAM_CHAT_ID: str = Field("", description="Your Chat ID")

    # --- Pydantic v2 Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignores extra variables in .env to prevent errors
    )

# Instantiate settings to be imported by other modules
settings = Settings()