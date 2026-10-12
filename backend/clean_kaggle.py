"""Clean Kaggle WFP Kenya CSV -> data/raw/prices.csv (real data, DSE315 M3).
Input: data/raw/kaggle_raw.csv (WFP, with extra header row starting with #)
Output: data/raw/prices.csv with columns date,item,market,price_kes,unit
Rules:
- Standardize 6 staples with enough Nairobi history: Maize, Beans, Potatoes, Sorghum, Rice, Sugar
- Normalize all bag prices to per KG (90 KG /90, 50 KG /50)
- Prefer Retail, fallback Wholesale (consumer relevance)
- Monthly frequency (WFP is monthly on 15th). Keep date as YYYY-MM-DD.
- Log counts for Chapter 3.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw" / "kaggle_raw.csv"
OUT = BASE / "data" / "raw" / "prices.csv"
BACKUP = BASE / "data" / "raw" / "prices_simulated_backup.csv"

ITEM_MAP = {
    "Maize": "Maize",
    "Maize (white)": "Maize",
    "Maize (white, dry)": "Maize",
    "Beans": "Beans",
    "Beans (dry)": "Beans",
    "Potatoes (Irish)": "Potatoes",
    "Potatoes (Irish, white)": "Potatoes",
    "Potatoes (Irish, red)": "Potatoes",
    "Sorghum": "Sorghum",
    "Sorghum (red)": "Sorghum",
    "Sorghum (white)": "Sorghum",
    "Rice": "Rice",
    "Rice (aromatic)": "Rice",
    "Sugar": "Sugar",
}

def to_per_kg(row):
    unit = str(row["unit"]).strip()
    price = float(row["price"])
    # units like "90 KG", "50 KG" -> divide
    if "KG" in unit:
        parts = unit.split()
        if len(parts) == 2 and parts[0].replace(".", "", 1).isdigit():
            return round(price / float(parts[0]), 2)
        return round(price, 2)  # plain KG
    return None  # skip L, ML, G, Unit, Bunch, Head (oil/milk/salt etc.)

def main():
    # WFP file has 2 header rows: real header + #adm1+name row. Skip row index 1.
    df = pd.read_csv(RAW, skiprows=[1])
    print(f"RAW rows: {len(df)}, cols: {list(df.columns)}")
    print(f"RAW date range: {df['date'].min()} to {df['date'].max()}")

    # keep only mapped commodities
    df = df[df["commodity"].isin(ITEM_MAP.keys())].copy()
    print(f"After item filter: {len(df)}")
    df["item"] = df["commodity"].map(ITEM_MAP)

    # normalize price to per KG, drop non-KG units
    df["price_kes"] = df.apply(to_per_kg, axis=1)
    before = len(df)
    df = df.dropna(subset=["price_kes"])
    print(f"Dropped {before - len(df)} non-KG rows (oil/milk etc.)")

    # prefer Retail per date/item/market, fallback Wholesale
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values(["date", "item", "market", "pricetype"])
    # Retail sorts after Wholesale alphabetically? Force: Retail first
    df["pref"] = df["pricetype"].map({"Retail": 0, "Wholesale": 1}).fillna(2)
    df = df.sort_values(["date", "item", "market", "pref"]).drop_duplicates(["date", "item", "market"], keep="first")

    # focus markets with most history: keep all, frontend will list them
    # but ensure Nairobi present for all 6 items (it is)
    out = df[["date", "item", "market", "price_kes"]].copy()
    out["unit"] = "per kg"
    out = out.rename(columns={"market": "market"})
    out = out.sort_values(["item", "market", "date"])

    # backup old simulated
    if OUT.exists() and not BACKUP.exists():
        OUT.rename(BACKUP)
        print(f"Backed up old simulated to {BACKUP.name}")

    out.to_csv(OUT, index=False)
    print(f"WROTE {len(out)} rows to {OUT}")
    print("Items:", sorted(out["item"].unique().tolist()))
    print("Markets top:", out["market"].value_counts().head(10).to_string())
    print("Per item counts:")
    print(out["item"].value_counts().to_string())
    print("Date range:", out["date"].min(), "to", out["date"].max())
    print("Sample:")
    print(out.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
