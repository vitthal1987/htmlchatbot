def calculate_rsi(stock_code, period=14):
    stock = yf.Ticker(stock_code)
    df = stock.history(period="3mo")  # Get last 3 months of data

    if df.empty:
        return "Stock data not found!"  # Return an error message

    # Calculate daily price changes
    df["Price Change"] = df["Close"].diff()

    # Calculate gains and losses
    df["Gain"] = df["Price Change"].apply(lambda x: x if x > 0 else 0)
    df["Loss"] = df["Price Change"].apply(lambda x: -x if x < 0 else 0)

    # Avoid index error by checking if data is available
    if len(df) < period:
        return "Not enough data for RSI calculation!"

    # Calculate average gain and loss
    df["Avg Gain"] = df["Gain"].rolling(window=period, min_periods=1).mean()
    df["Avg Loss"] = df["Loss"].rolling(window=period, min_periods=1).mean()

    # Compute RSI
    df["RS"] = df["Avg Gain"] / df["Avg Loss"]
    df["RSI"] = 100 - (100 / (1 + df["RS"]))

    return round(df["RSI"].iloc[-1], 2)  # Return latest RSI value safely
