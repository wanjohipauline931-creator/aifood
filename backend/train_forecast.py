"""AI forecast with statsmodels Holt-Winters."""
import os
from pathlib import Path
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

BASE = Path(__file__).resolve().parent.parent
DATA = str(BASE / "data" / "raw" / "prices.csv")
OUT_DIR = str(BASE / "data" / "predictions")
os.makedirs(OUT_DIR, exist_ok=True)

def forecast_item(prices, periods=30):
    # Holt-Winters with weekly seasonality (7) + trend
    model = ExponentialSmoothing(prices, trend="add", seasonal="add", seasonal_periods=7)
    fit = model.fit(optimized=True, use_brute=True)
    pred = fit.forecast(periods)
    resid_std = fit.resid.std()
    return pred, resid_std

def main():
    df = pd.read_csv(DATA, parse_dates=["date"])
    for item in sorted(df["item"].unique()):
        sub = df[df["item"] == item].sort_values("date")
        prices = sub.set_index("date")["price_kes"].asfreq("D").ffill()
        pred, std = forecast_item(prices, 30)
        last_date = prices.index[-1]
        dates = [last_date + pd.Timedelta(days=i) for i in range(1, 31)]
        out = pd.DataFrame({"ds": dates, "yhat": pred.values.round(0).astype(int)})
        out["yhat_lower"] = (out["yhat"] - 1.96 * std).round(0).astype(int)
        out["yhat_upper"] = (out["yhat"] + 1.96 * std).round(0).astype(int)
        path = os.path.join(OUT_DIR, f"{item.replace(' ', '_').lower()}_forecast.csv")
        out.to_csv(path, index=False)
        p7 = out.head(7)["yhat"].tolist()
        trend = "increasing" if p7[-1] > p7[0] + 1 else "decreasing" if p7[-1] < p7[0] - 1 else "stable"
        print(f"\n{item}: current {prices.iloc[-1]} KES, 7-day trend: {trend}")
        for _, r in out.head(7).iterrows():
            print(f"  {r['ds'].date()}: {r['yhat']} KES (range {r['yhat_lower']}-{r['yhat_upper']})")
        print(f"  saved -> {path}")

if __name__ == "__main__":
    main()
