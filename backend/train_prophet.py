"""Train Prophet per item, save models + 30-day forecast CSVs. Run with py -3.12"""
import os
import pandas as pd
from prophet import Prophet

DATA = "data/raw/prices.csv"
OUT_DIR = "data/predictions"
os.makedirs(OUT_DIR, exist_ok=True)

def forecast_item(df_item, periods=30):
    df = df_item.rename(columns={"date": "ds", "price_kes": "y"})[["ds", "y"]]
    df["ds"] = pd.to_datetime(df["ds"])
    m = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods)
    fc = m.predict(future)
    return m, fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

def main():
    df = pd.read_csv(DATA)
    items = df["item"].unique()
    print(f"Items: {list(items)}")
    for item in items:
        sub = df[df["item"] == item].sort_values("date")
        _, fc = forecast_item(sub, 30)
        path = os.path.join(OUT_DIR, f"{item.replace(' ', '_').lower()}_forecast.csv")
        fc.to_csv(path, index=False)
        last = sub.iloc[-1]
        pred7 = fc.head(7)["yhat"].tolist()
        trend = "increasing" if pred7[-1] > pred7[0] + 1 else "decreasing" if pred7[-1] < pred7[0] - 1 else "stable"
        print(f"\n{item}: current {last['price_kes']} KES on {last['date']}, 7-day trend: {trend}")
        for _, r in fc.head(7).iterrows():
            print(f"  {r['ds'].date()}: {r['yhat']:.0f} KES (range {r['yhat_lower']:.0f}-{r['yhat_upper']:.0f})")
        print(f"  saved -> {path}")

if __name__ == "__main__":
    main()
