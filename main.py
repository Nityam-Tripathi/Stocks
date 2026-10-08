from dotenv import load_dotenv
import os
from fastapi import FastAPI
import requests
import psycopg2

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# -------------------------
# Home endpoint
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Stock API is running"
    }


# -------------------------
# Stock endpoint
# -------------------------

@app.get("/stock/{symbol}")
def get_stock(symbol: str):

    # 1. Get stock price from Finnhub

    url = "https://finnhub.io/api/v1/quote"

    params = {
        "symbol": symbol.upper(),
        "token": FINNHUB_API_KEY
    }

    response = requests.get(url, params=params)

    data = response.json()

    # Current price
    price = data["c"]

    # 2. Connect to Supabase PostgreSQL

    conn = psycopg2.connect(DATABASE_URL)

    cursor = conn.cursor()

    # 3. Store stock price

    query = """
        INSERT INTO stock_prices (symbol, price)
        VALUES (%s, %s)
    """

    cursor.execute(
        query,
        (symbol.upper(), price)
    )

    conn.commit()

    # 4. Close database connection

    cursor.close()
    conn.close()

    # 5. Return response

    return {
        "symbol": symbol.upper(),
        "price": price
    }
    
    
@app.get("/stock/{symbol}/history")
def get_stock_history(symbol: str):

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    query = """
        SELECT symbol, price, timestamp
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY timestamp DESC
    """

    cursor.execute(query, (symbol.upper(),))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "symbol": row[0],
            "price": float(row[1]),
            "timestamp": row[2]
        })

    return history