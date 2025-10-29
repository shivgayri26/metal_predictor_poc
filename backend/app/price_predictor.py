import pandas as pd, os, joblib
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pmdarima import auto_arima
MODEL_DIR='./models'; os.makedirs(MODEL_DIR,exist_ok=True)
def _ensure_daily_index(df):
    df=df.copy(); df['timestamp']=pd.to_datetime(df['timestamp']); s=df.set_index('timestamp').sort_index()['price'].resample('D').last().ffill(); return s
def train_hw_model(series, metal, seasonal=7):
    m=ExponentialSmoothing(series, trend='add', seasonal='add' if seasonal else None, seasonal_periods=seasonal if seasonal else None).fit(optimized=True)
    joblib.dump(m, os.path.join(MODEL_DIR,f'hw_{metal}.joblib')); return m
def train_auto_arima(series, metal):
    model=auto_arima(series, seasonal=False, error_action='ignore', suppress_warnings=True, stepwise=True)
    joblib.dump(model, os.path.join(MODEL_DIR,f'arima_{metal}.joblib')); return model
def forecast_from_history(history_df, metal, horizon_days=1, method='auto_arima'):
    if isinstance(history_df, pd.Series): series=history_df
    else: series=_ensure_daily_index(history_df)
    if len(series.dropna())<10:
        last=float(series.dropna().iloc[-1]); return {'horizon':horizon_days,'predictions':[last]*horizon_days,'lower':[last]*horizon_days,'upper':[last]*horizon_days,'method':'naive_last'}
    if method=='hw': m=train_hw_model(series,metal); preds=m.forecast(horizon_days); return {'horizon':horizon_days,'predictions':[float(x) for x in preds],'lower':[float(x) for x in preds],'upper':[float(x) for x in preds],'method':'hw'}
    else: model=train_auto_arima(series,metal); pred,conf=model.predict(n_periods=horizon_days, return_conf_int=True); return {'horizon':horizon_days,'predictions':[float(x) for x in pred],'lower':[float(x) for x in conf[:,0]],'upper':[float(x) for x in conf[:,1]],'method':'auto_arima'}
