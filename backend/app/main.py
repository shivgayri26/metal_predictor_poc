from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pandas as pd

from .predictor import load_history, train_model, predict, list_trained_models

app = FastAPI(title="Metal Predictor API - PoC")

class ForecastPoint(BaseModel):
    date: datetime
    forecast: float
    low: float
    high: float

class ForecastResponse(BaseModel):
    metal: str
    days: int
    model: str
    predictions: List[ForecastPoint]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/history/{metal}")
def history(metal: str, days: int = Query(90, ge=1, le=3650)):
    series = load_history(metal.lower())
    if series.empty:
        raise HTTPException(status_code=404, detail="No history for metal")
    recent = series.tail(days)
    # return date as ISO string and the close price
    data = [{"date": dt.strftime("%Y-%m-%d"), "close": float(v)} for dt, v in recent.items()]
    return {"metal": metal, "rows": len(recent), "data": data}

@app.post("/train/{metal}")
def train(metal: str):
    metal = metal.lower()
    try:
        path = train_model(metal)
        return {"metal": metal, "model_path": path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/predict/{metal}", response_model=ForecastResponse)
def predict_endpoint(metal: str, days: int = Query(10, ge=1, le=365)):
    metal = metal.lower()
    try:
        df = predict(metal, days=days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    preds = [
        ForecastPoint(date=row["date"].to_pydatetime(), forecast=float(row["forecast"]), low=float(row["low"]), high=float(row["high"]))
        for _, row in df.iterrows()
    ]
    model_name = f"{metal}_arima.pkl"
    return ForecastResponse(metal=metal, days=days, model=model_name, predictions=preds)
