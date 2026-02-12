import pyautogui
import io
from telegram import Bot
from src.config.settings import settings

class TelegramService:
    def __init__(self):
        self.token = settings.TELEGRAM_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = None

        if self.token:
            self.bot = Bot(token=self.token)

    async def send_message(self, message: str):
        """
        Sends a simple text message to the configured chat asynchronously.
        """
        if not self.bot or not self.chat_id:
            print("⚠️ Telegram credentials not configured.")
            return

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"✅ Telegram message sent: {message}")
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")

    async def send_screenshot(self, caption: str = "Chart Screenshot"):
        """
        Captures the entire screen and sends it as a photo to Telegram asynchronously.
        Uses in-memory buffer (BytesIO) to avoid saving files to disk.
        """
        if not self.bot or not self.chat_id:
            print("⚠️ Telegram credentials not configured.")
            return

        try:
            # 1. Take Screenshot (Synchronous operation)
            screenshot = pyautogui.screenshot()
            
            # 2. Save to in-memory bytes buffer (fast)
            bio = io.BytesIO()
            bio.name = 'screenshot.png'
            screenshot.save(bio, 'PNG')
            bio.seek(0) # Reset pointer to start of file

            # 3. Send Photo Asynchronously
            await self.bot.send_photo(chat_id=self.chat_id, photo=bio, caption=caption)
            print("✅ Telegram screenshot sent successfully.")

        except Exception as e:
            print(f"❌ Failed to send screenshot: {e}")