import csv, random
from datetime import date, timedelta

random.seed(42)

items = [
    ("Tomatoes", "Wakulima", 80, "per kg", 0.04, 8),
    ("Sukuma Wiki", "Wakulima", 30, "per bundle", 0.02, 4),
    ("Onions", "Wakulima", 120, "per kg", 0.03, 10),
    ("Maize", "Wakulima", 150, "per tin", 0.025, 12),
    ("Potatoes", "Wakulima", 90, "per kg", 0.035, 9),
    ("Cabbage", "Wakulima", 60, "per piece", 0.02, 6),
]

start = date(2024, 1, 1)
days = 365  # 1 year daily

rows = [("date", "item", "market", "price_kes", "unit")]

for d in range(days):
    cur = start + timedelta(days=d)
    month = cur.month
    # rainy season effect: prices higher in Apr-May and Oct-Nov
    seasonal = 1.0
    if month in (4, 5):
        seasonal = 1.15
    elif month in (10, 11):
        seasonal = 1.10
    elif month in (1, 2):
        seasonal = 0.95
    weekday = cur.weekday()  # weekend prices slightly higher
    weekend = 1.05 if weekday >= 5 else 1.0
    for item, market, base, unit, trend, noise in items:
        trend_factor = 1 + (trend * d / 365)  # slow yearly rise
        price = base * seasonal * weekend * trend_factor + random.uniform(-noise, noise)
        price = max(5, round(price))
        rows.append((cur.isoformat(), item, market, price, unit))

with open("data/raw/prices.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerows(rows)

print(f"Wrote {len(rows)-1} rows to data/raw/prices.csv")
