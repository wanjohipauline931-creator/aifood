"""FastAPI backend - CSV mode, Supabase optional."""
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA_CSV = str(BASE / "data" / "raw" / "prices.csv")
PRED_DIR = str(BASE / "data" / "predictions")

app = FastAPI(title="AI Food Price Forecasting - Kenya")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_prices():
    return pd.read_csv(DATA_CSV, parse_dates=["date"])

@app.get("/")
def root():
    return {"message": "AI Food Price Forecasting - Kenya", "docs": "/docs", "health": "/health", "items": "/items"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/items")
def items():
    df = load_prices()
    return {"items": sorted(df["item"].unique().tolist()), "markets": sorted(df["market"].unique().tolist())}

@app.get("/prices")
def prices(item: str = "Tomatoes", market: str = "Wakulima", limit: int = 90):
    df = load_prices()
    sub = df[(df["item"] == item) & (df["market"] == market)].sort_values("date").tail(limit)
    return {"item": item, "market": market, "current": float(sub.iloc[-1]["price_kes"]),
            "history": [{"date": r["date"].strftime("%Y-%m-%d") if hasattr(r["date"], "strftime") else str(r["date"]), "price": float(r["price_kes"])} for _, r in sub.iterrows()]}

@app.get("/predict")
def predict(item: str = "Tomatoes", days: int = 7):
    fname = os.path.join(PRED_DIR, f"{item.replace(' ', '_').lower()}_forecast.csv")
    if not os.path.exists(fname):
        return {"error": f"No forecast for {item}. Run train_forecast.py"}
    fc = pd.read_csv(fname).head(days)
    vals = fc["yhat"].tolist()
    trend = "increasing" if vals[-1] > vals[0] + 1 else "decreasing" if vals[-1] < vals[0] - 1 else "stable"
    rec = f"{item} price is expected to {trend} in the next {days} days. "
    rec += "Best time to buy may be within the next 3 days." if trend == "increasing" else "You may wait before buying." if trend == "decreasing" else "Price is stable."
    return {"item": item, "days": days, "trend": trend, "recommendation": rec,
            "forecast": [{"date": str(r["ds"]), "predicted": float(r["yhat"]), "lower": float(r["yhat_lower"]), "upper": float(r["yhat_upper"])} for _, r in fc.iterrows()]}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    # validate columns before overwriting
    import io
    try:
        df_new = pd.read_csv(io.BytesIO(content))
    except Exception:
        return {"error": "Not a valid CSV"}
    required = {"date", "item", "market", "price_kes", "unit"}
    if not required.issubset(set(df_new.columns)):
        return {"error": f"CSV must have columns: {sorted(required)}. Got: {list(df_new.columns)}. Do NOT upload exported forecast files."}
    open(DATA_CSV, "wb").write(content)
    # retrain quickly
    from backend.train_forecast import main as retrain
    import backend.train_forecast as tf
    tf.DATA = DATA_CSV
    retrain()
    return {"saved": DATA_CSV, "rows": len(pd.read_csv(DATA_CSV))}
