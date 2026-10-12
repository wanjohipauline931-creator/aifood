"""Train per-item forecasts on REAL Kaggle WFP data (monthly).
Strategy for defence:
- For each of 6 items, pick best series: Nairobi if >=60 rows else national monthly mean.
- Time-ordered split 80% train / 10% val / 10% test (no shuffle).
- Model: Holt-Winters ExponentialSmoothing trend add + seasonal add, periods=12 (monthly).
- Metrics on TEST: MAE, RMSE, MAPE. Target MAPE<15%.
- Refit on full series, forecast next 12 months, save data/predictions/<item>_forecast.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

BASE = Path(__file__).resolve().parent.parent
DATA = str(BASE / "data" / "raw" / "prices.csv")
OUT_DIR = str(BASE / "data" / "predictions")

def load_series(item):
    df = pd.read_csv(DATA)
    df = df[df["item"] == item].copy()
    df["date"] = pd.to_datetime(df["date"])
    # try Nairobi first
    nbo = df[df["market"] == "Nairobi"].sort_values("date")
    if len(nbo) >= 60:
        s = nbo.set_index("date")["price_kes"].resample("MS").mean().ffill()
        return s, "Nairobi", len(nbo)
    # fallback: national monthly mean
    s = df.set_index("date")["price_kes"].resample("MS").mean().ffill()
    return s, "NationalMean", len(df)

def mape(y_true, y_pred):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)

def main():
    import os
    os.makedirs(OUT_DIR, exist_ok=True)
    df_all = pd.read_csv(DATA)
    items = sorted(df_all["item"].unique())
    print(f"Items: {items}")
    results = []
    for item in items:
        s, src, nrows = load_series(item)
        s = s.dropna()
        n = len(s)
        n_train = int(n * 0.8)
        n_val = int(n * 0.1)
        train = s.iloc[:n_train]
        val = s.iloc[n_train:n_train + n_val]
        test = s.iloc[n_train + n_val:]
        # fit on train, validate
        try:
            fit = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True, use_brute=True)
        except Exception:
            fit = ExponentialSmoothing(train, trend="add", seasonal=None).fit(optimized=True, use_brute=True)
        pred_val = fit.forecast(len(val)) if len(val) else []
        # refit on train+val, test
        full_train = s.iloc[:n_train + n_val]
        try:
            fit2 = ExponentialSmoothing(full_train, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True, use_brute=True)
        except Exception:
            fit2 = ExponentialSmoothing(full_train, trend="add", seasonal=None).fit(optimized=True, use_brute=True)
        pred_test = fit2.forecast(len(test)) if len(test) else []
        mae = float(np.mean(np.abs(np.array(test) - np.array(pred_test)))) if len(test) else 0
        rmse = float(np.sqrt(np.mean((np.array(test) - np.array(pred_test)) ** 2))) if len(test) else 0
        mp = mape(test, pred_test) if len(test) else 0
        results.append((item, src, n, round(mae, 2), round(rmse, 2), round(mp, 2)))
        print(f"{item} [{src} months={n} train={len(train)} val={len(val)} test={len(test)}] TEST MAE={mae:.2f} RMSE={rmse:.2f} MAPE={mp:.2f}%")
        # final refit on ALL, forecast 12 months
        try:
            final = ExponentialSmoothing(s, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True, use_brute=True)
        except Exception:
            final = ExponentialSmoothing(s, trend="add", seasonal=None).fit(optimized=True, use_brute=True)
        fc = final.forecast(12)
        std = float(final.resid.std()) if hasattr(final, "resid") else float(s.std() * 0.1)
        last = s.index[-1]
        dates = [(last + pd.offsets.MonthBegin(i + 1)).normalize() for i in range(12)]
        out = pd.DataFrame({"ds": [d.strftime("%Y-%m-%d") for d in dates],
                            "yhat": np.round(fc.values, 2),
                            "yhat_lower": np.round(fc.values - 1.96 * std, 2),
                            "yhat_upper": np.round(fc.values + 1.96 * std, 2)})
        path = f"{OUT_DIR}/{item.replace(' ', '_').lower()}_forecast.csv"
        out.to_csv(path, index=False)
        print(f"  saved -> {path}")
    print("\n=== FINAL METRICS (for Ch3/Ch4) ===")
    for r in results:
        print(f"{r[0]}: source={r[1]} months={r[2]} MAE={r[3]} RMSE={r[4]} MAPE={r[5]}%")

if __name__ == "__main__":
    main()
