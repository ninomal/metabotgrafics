Markdown

# 🐍 TradeBot PRO - Python Backend

This is the core engine of the TradeBot PRO platform. It handles the communication with MetaTrader 5, processes market data, calculates VSA (Volume Spread Analysis) indicators, and manages the Telegram automation.

## 🚀 Features
* **FastAPI Infrastructure:** High-performance asynchronous API.
* **MT5 Connection:** Real-time data bridge with MetaTrader 5.
* **VSA Logic:** Automated volume analysis to detect institutional flow.
* **Telegram Service:** Automated alerts and chart screenshot delivery.

## 🛠️ Installation

1. **Setup Virtual Environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
2. **Install Dependencies:**

Bash

pip install fastapi uvicorn MetaTrader5 pydantic python-dotenv
Environment Configuration:
Create a .env file based on .env.example:

Ini, TOML

MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server
MT5_PATH="C:\Program Files\MetaTrader 5\terminal64.exe"
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_id

3.**🔌 API Endpoints**
GET /api/chart-data: Returns candlestick data with VSA coloring.

GET /api/symbols: Lists available trading assets.

POST /api/telegram_test: Sends a test alert to Telegram.

4. ** 🏃 Running the Server**
Bash

python app.py