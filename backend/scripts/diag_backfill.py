import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

METALS = {
    "gold": "GC=F",
    "silver": "SI=F",
    "copper": "HG=F",
    "aluminum": "ALI=F",
    "zinc": "ZNC=F",
}

DB_PATH = "data/metal_prices.db"

def ensure_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metal_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metal TEXT,
        date TEXT,
        close REAL
    )
    """)
    conn.commit()
    conn.close()

def fetch_and_write(years=3):
    ensure_db()
    end = datetime.now().date()
    start = end - timedelta(days=years*365)
    conn = sqlite3.connect(DB_PATH)
    total_inserted = 0
    for metal, ticker in METALS.items():
        print(f"--- Fetching {metal} (ticker {ticker}) from {start} to {end}")
        try:
            df = yf.download(ticker, start=start.isoformat(), end=(end+timedelta(days=1)).isoformat(), progress=False, auto_adjust=False)
            if df.empty:
                print(f"  -> NO DATA for {ticker} (empty dataframe).")
                continue

            # 🧠 Fix multi-index returned by yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            df.reset_index(inplace=True)
            df.rename(columns={"Date": "date", "Close": "close"}, inplace=True)

            inserted = 0
            for _, row in df.iterrows():
                date_val = row["date"]
                if not isinstance(date_val, str):
                    date_str = date_val.strftime("%Y-%m-%d")
                else:
                    date_str = date_val
                close_val = float(row["close"])
                conn.execute(
                    "INSERT INTO metal_prices (metal, date, close) VALUES (?, ?, ?)",
                    (metal, date_str, close_val),
                )
                inserted += 1
            conn.commit()
            print(f"  -> ✅ Inserted {inserted} rows for {metal}")
            total_inserted += inserted
        except Exception as e:
            print(f"  -> ❌ ERROR fetching {ticker}: {e}")
    conn.close()
    print(f"\n🎯 TOTAL rows inserted: {total_inserted}")

if __name__ == "__main__":
    fetch_and_write(years=3)
