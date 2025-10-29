from pathlib import Path
import sqlite3
import pandas as pd
import joblib
import numpy as np
from pmdarima import auto_arima
from datetime import datetime

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

DB_PATH = "data/metal_prices.db"

def load_history(metal: str) -> pd.Series:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT date, close FROM metal_prices WHERE metal = ? ORDER BY date ASC",
        conn, params=(metal,)
    )
    conn.close()
    if df.empty:
        return pd.Series(dtype=float)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    s = df["close"].asfreq("D").fillna(method="ffill")
    return s

def train_model(metal: str, seasonal: bool = True):
    s = load_history(metal)
    if s.empty or len(s) < 30:
        raise RuntimeError(f"not enough data to train for {metal} (rows={len(s)})")
    m = auto_arima(s, seasonal=seasonal, m=7, stepwise=True, suppress_warnings=True, max_p=5, max_q=5)
    path = MODELS_DIR / f"{metal}_arima.pkl"
    joblib.dump(m, path)
    return str(path)

def predict(metal: str, days: int = 10):
    model_path = MODELS_DIR / f"{metal}_arima.pkl"
    if not model_path.exists():
        train_model(metal)
    model = joblib.load(model_path)
    fc, conf_int = model.predict(n_periods=days, return_conf_int=True)
    index = pd.date_range(start=pd.Timestamp.now().normalize() + pd.Timedelta(days=1), periods=days, freq="D")
    df = pd.DataFrame({
        "date": index,
        "forecast": np.round(fc, 4),
        "low": np.round(conf_int[:, 0], 4),
        "high": np.round(conf_int[:, 1], 4),
    })
    return df

def list_trained_models():
    return [p.name for p in MODELS_DIR.glob("*_arima.pkl")]
