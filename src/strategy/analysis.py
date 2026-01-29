import pandas as pd
import pandas_ta as ta

class MarketAnalyzer:
    def __init__(self):
        pass

    def prepare_data(self, rates_frame):
        """
        Receives raw data from MT5 and converts it into a Pandas DataFrame
        with calculated technical indicators.
        """
        # Create DataFrame from MT5 raw data
        df = pd.DataFrame(rates_frame)
        
        # Convert time (seconds) to a readable datetime format
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # --- PANDAS_TA CALCULATIONS ---
        
        # 1. RSI (Relative Strength Index) - 14 periods
        df['RSI'] = df.ta.rsi(length=14)

        # 2. EMAs (Exponential Moving Averages)
        df['EMA_20'] = df.ta.ema(length=20)
        df['EMA_50'] = df.ta.ema(length=50)

        # 3. Bollinger Bands
        # pandas_ta returns 3 columns: BBL (Lower), BBM (Mid), BBU (Upper)
        bbands = df.ta.bbands(length=20, std=2)
        
        # Concatenate the bands columns to our main DataFrame
        if bbands is not None:
            df = pd.concat([df, bbands], axis=1)

        # Drop NaN values (initial candles without enough data for calculations)
        df.dropna(inplace=True)

        return df

    def check_buy_signal(self, df):
        """
        Simple Logic: If RSI < 30 (Oversold) -> Buy Signal
        """
        if df is None or df.empty:
            return False

        # Get the last closed candle (most recent completed data)
        last_candle = df.iloc[-1]
        current_rsi = last_candle['RSI']
        
        # Debug print (optional)
        # print(f"📊 Technical Analysis -> Current RSI: {current_rsi:.2f}")

        if current_rsi < 30:
            return True
        return False

    def check_sell_signal(self, df):
        """
        Simple Logic: If RSI > 70 (Overbought) -> Sell Signal
        """
        if df is None or df.empty:
            return False

        last_candle = df.iloc[-1]
        current_rsi = last_candle['RSI']

        if current_rsi > 70:
            return True
        return False