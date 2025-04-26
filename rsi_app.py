import yfinance as yf
import pandas as pd
import numpy as np


def calculate_rsi_corrected(symbol, period='1y', interval='1d', window=14):
    # Fetch data
    data = yf.download(symbol, period=period, interval=interval, progress=False)

    if data.empty:
        return None

    # Calculate price changes
    delta = data['Close'].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate EMA of gains and losses
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    print(rsi)
    return rsi.iloc[-1]


# Example usage
symbol = "NIF100IETF.NS"
current_rsi = calculate_rsi_corrected(symbol)

print(current_rsi)