from flask import Flask, request, jsonify, render_template
import yfinance as yf
from pytrends.request import TrendReq
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to calculate RSI
def calculate_rsi(stock_code, period=14):
    stock = yf.Ticker(stock_code)
    df = stock.history(period="3mo")

    df["Price Change"] = df["Close"].diff()
    df["Gain"] = df["Price Change"].apply(lambda x: x if x > 0 else 0)
    df["Loss"] = df["Price Change"].apply(lambda x: -x if x < 0 else 0)

    df["Avg Gain"] = df["Gain"].rolling(window=period, min_periods=1).mean()
    df["Avg Loss"] = df["Loss"].rolling(window=period, min_periods=1).mean()

    df["RS"] = df["Avg Gain"] / df["Avg Loss"]
    df["RSI"] = 100 - (100 / (1 + df["RS"]))

    return df["RSI"].iloc[-1]

# Function to get pivot points
def calculate_pivot_points(stock_code):
    stock = yf.Ticker(stock_code)
    df = stock.history(period="7d")

    high = df["High"].iloc[-2]
    low = df["Low"].iloc[-2]
    close = df["Close"].iloc[-2]

    pivot = (high + low + close) / 3
    resistance_1 = (2 * pivot) - low
    support_1 = (2 * pivot) - high
    resistance_2 = pivot + (high - low)
    support_2 = pivot - (high - low)

    return {"Pivot": pivot, "Resistance 1": resistance_1, "Support 1": support_1, "Resistance 2": resistance_2, "Support 2": support_2}

# Function to get news sentiment
def get_news_sentiment(stock_name):
    search_url = f"https://www.google.com/search?q={stock_name}+stock+news"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = [h.text for h in soup.find_all("h3")][:5]
    sentiments = [TextBlob(h).sentiment.polarity for h in headlines]

    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment, headlines

# Function to get Google Trends data
def get_google_trends(stock_name):
    pytrends = TrendReq()
    pytrends.build_payload([stock_name], timeframe="now 7-d", geo="IN")

    data = pytrends.interest_over_time()
    return data[stock_name].mean() if not data.empty else 0

# Home Page Route
@app.route("/")
def home():
    return render_template("index.html")

# API Endpoint for chatbot
@app.route("/get_stock_analysis", methods=["POST"])
def get_stock_analysis():
    stock_name = request.form.get("stock")

    if not stock_name:
        return jsonify({"error": "Please provide a stock name."})

    stock_code = f"{stock_name.upper()}.NS"

    # Fetch stock analysis
    rsi = calculate_rsi(stock_code)
    pivot_levels = calculate_pivot_points(stock_code)
    sentiment_score, news_headlines = get_news_sentiment(stock_name)
    trend_score = get_google_trends(stock_name)

    return render_template("result.html", stock=stock_name.upper(), rsi=round(rsi, 2),
                           pivot=pivot_levels, sentiment=round(sentiment_score, 2),
                           trend_score=round(trend_score, 2), news=news_headlines)

if __name__ == "__main__":
    app.run(debug=True)
