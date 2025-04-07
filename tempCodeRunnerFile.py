from flask import Flask, request, render_template
import requests
import google.generativeai as genai

app = Flask(__name__)

# Updated Gemini API key
GEMINI_API_KEY = "AIzaSyBOLaBdjFHCRW-M9UJYBc-ATggLR1NoAyE"
genai.configure(api_key=GEMINI_API_KEY)

# Alpha Vantage API (Replace with your own key)
ALPHA_VANTAGE_API_KEY = "L51WSWBOXOS8M6HF"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

def get_stock_data(symbol):
    """Fetch real-time stock data using Alpha Vantage API"""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(ALPHA_VANTAGE_URL, params=params)
    data = response.json()

    if "Time Series (5min)" in data:
        latest_timestamp = sorted(data["Time Series (5min)"].keys())[-1]
        stock_info = data["Time Series (5min)"][latest_timestamp]
        return {
            "symbol": symbol.upper(),
            "timestamp": latest_timestamp,
            "open": stock_info["1. open"],
            "high": stock_info["2. high"],
            "low": stock_info["3. low"],
            "close": stock_info["4. close"],
            "volume": stock_info["5. volume"]
        }
    return None

def process_input(user_input):
    """Process user queries related to stock market insights"""
    user_input = user_input.lower().strip()

    if "stock price of" in user_input:
        symbol = user_input.split("stock price of")[-1].strip().upper()
        stock_data = get_stock_data(symbol)
        if stock_data:
            return (f"Latest Stock Data for {stock_data['symbol']}:\n"
                    f"📅 Time: {stock_data['timestamp']}\n"
                    f"📈 Open: {stock_data['open']}\n"
                    f"📊 High: {stock_data['high']}\n"
                    f"📉 Low: {stock_data['low']}\n"
                    f"🔚 Close: {stock_data['close']}\n"
                    f"📊 Volume: {stock_data['volume']}")
        else:
            return f"Could not retrieve stock data for {symbol}. Please check the symbol and try again."

    if "hi" in user_input or "hello" in user_input:
        return "Hello! I can provide real-time stock market insights. Ask me for the stock price of any company!"

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Provide stock market analysis: {user_input}")
        return response.text
    except Exception as e:
        return f"Sorry, I couldn’t process that. Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def stock_insights():
    response = None
    if request.method == "POST":
        user_input = request.form["query"]
        response = process_input(user_input)
    return render_template("index.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)
