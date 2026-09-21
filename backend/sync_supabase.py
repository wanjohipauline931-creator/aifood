"""Upload CSVs to Supabase. Set env first: $env:SUPABASE_URL="..."; $env:SUPABASE_SECRET="..." """
import os, csv
from supabase import create_client
URL = os.environ.get("SUPABASE_URL", "")
KEY = os.environ.get("SUPABASE_SECRET", "")
if not URL or not KEY:
    raise SystemExit("Set SUPABASE_URL and SUPABASE_SECRET env vars first. See AGENT.md")
sup = create_client(URL, KEY)

def sync_prices():
    with open(r"C:\aifood\data\raw\prices.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # clear then insert in batches of 500
    sup.table("prices").delete().neq("id", 0).execute()
    for i in range(0, len(rows), 500):
        batch = rows[i:i+500]
        sup.table("prices").insert(batch).execute()
    print(f"prices synced: {len(rows)}")

def sync_predictions():
    import glob
    sup.table("predictions").delete().neq("id", 0).execute()
    total = 0
    for path in glob.glob(r"C:\aifood\data\predictions\*_forecast.csv"):
        item = os.path.basename(path).replace("_forecast.csv", "").replace("_", " ").title()
        if "Sukuma" in item: item = "Sukuma Wiki"
        with open(path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sup.table("predictions").insert({"item": item, "ds": r["ds"][:10], "yhat": float(r["yhat"]), "yhat_lower": float(r["yhat_lower"]), "yhat_upper": float(r["yhat_upper"])}).execute()
                total += 1
    print(f"predictions synced: {total}")

if __name__ == "__main__":
    sync_prices()
    sync_predictions()
