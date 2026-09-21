"""Baseline predictor - no dependencies. Reads CSV, predicts next 7 days."""
import csv
from collections import defaultdict

DATA = "data/raw/prices.csv"

def load(item="Tomatoes", market="Wakulima"):
    pts = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["item"] == item and r["market"] == market:
                pts.append((r["date"], float(r["price_kes"])))
    pts.sort()
    return pts

def predict(item="Tomatoes", market="Wakulima", days=7):
    pts = load(item, market)
    prices = [p for _, p in pts]
    # trend = avg daily change over last 14 days
    recent = prices[-14:]
    trend = (recent[-1] - recent[0]) / len(recent)
    last = prices[-1]
    out = []
    for i in range(1, days + 1):
        pred = round(last + trend * i, 2)
        lo = round(pred * 0.92, 2)
        hi = round(pred * 1.08, 2)
        out.append((f"day+{i}", pred, lo, hi))
    direction = "increasing" if trend > 0.3 else "decreasing" if trend < -0.3 else "stable"
    return {"current": last, "trend_per_day": round(trend, 2), "direction": direction, "forecast": out}

if __name__ == "__main__":
    for item in ["Tomatoes", "Sukuma Wiki", "Onions", "Maize", "Potatoes", "Cabbage"]:
        r = predict(item)
        print(f"\n{item}: current {r['current']} KES, trend {r['direction']} ({r['trend_per_day']}/day)")
        for d, p, lo, hi in r["forecast"]:
            print(f"  {d}: {p} KES (range {lo}-{hi})")
    print("\nRecommendation example:")
    r = predict("Tomatoes")
    if r["direction"] == "increasing":
        print("Tomato price is expected to rise in the next 7 days. Best time to buy may be within the next 3 days.")
