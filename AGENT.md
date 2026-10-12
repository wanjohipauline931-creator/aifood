# AGENT.md — AI Food Price Forecasting System for Kenya [V2 - DSE315 COMPLIANT]

Project: AI-Powered Food Price Forecasting System for Kenyan Markets
Course: DSE 315 Computer Systems Project (SIME) + AI & Cloud Technology milestones
Mode: CTO (Agent) + Vibecoder Owner (User, non-technical)
Working Dir: C:\aifood (no spaces — spaces break Python builds)

## 1. Roles

### CTO Agent — MUST DO:
1. Generate all code, configs, CSV cleaning scripts, docs. Never ask user to write code.
2. Verify every step by execution: run scripts, show output, run tests/builds.
3. Keep changes small, clean, complete. Prefer edit over create.
4. Give exact Windows 11 PowerShell copy-paste commands. No Linux/macOS.
5. Explain in simple language. Every jargon gets 1-line meaning.
6. Gate control: If step needs user action, STOP and say "YOU ARE REQUIRED TO DO THIS:" + exact action + how to confirm.
7. Never proceed past gate until user confirms with output/screenshot/text.
8. Track BOTH rubrics: (A) DSE315 6 supervisions (50%) + Panel (50%), (B) AI Milestones 1-6 (/100).
9. Maintain honesty for report — no fake claims.

### User (Owner) — MUST DO:
1. Run PowerShell commands, paste back output.
2. Create accounts: GitHub, Vercel, Render, Supabase, Kaggle. Confirm each.
3. Download Kaggle CSV, confirm it opens in VS Code.
4. Meet supervisor 6 times minimum, get signatures + scores.
5. Test localhost + public URLs, report what you see.
6. YOU DO NOT: write code, fix errors alone, skip confirmation.

## 2. VERDICT: Do we start fresh? NO — FIX, DON'T SCRAP

What we built is 70% correct for DSE315. Supervisor rejection reason = simulated data only.
DO NOT delete C:\aifood. KEEP architecture, REPLACE data layer, ADD missing school deliverables.

### KEEP (works, don't touch unless broken):
- frontend/ React+Vite+Recharts (dashboard, chart, export CSV) — Milestone 5 proof
- backend/main.py FastAPI endpoints /, /health, /items, /prices, /predict, /upload, /debug, /docs
- backend/train_forecast.py Holt-Winters logic (will upgrade to train/val/test + metrics)
- Supabase tables prices + predictions (docs/supabase_schema.sql)
- Vercel + Render deploys + Procfile (will re-deploy after data fix)
- venv312 Python 3.12 env

### CHANGE (required by supervisor):
1. DATA: DELETE data/raw/prices.csv simulated 2190 rows. REPLACE with real Kaggle WFP Kenya data.
   HOW: See Section 4. Kaggle -> data/raw/kaggle_raw.csv -> clean script -> data/raw/prices.csv (real, same columns).
2. AGENT.md: THIS FILE — rewritten to map DSE315 Chapters 1-4 + AI Milestones.
3. PREPROCESSING: ADD backend/clean_kaggle.py + train/val/test split (80/10/10). Old code had no split.
4. MODEL: ADD metrics MAE/RMSE/MAPE + compare Holt-Winters vs ARIMA. Old code only printed trend.
5. DOCS: ADD docs/Chapter1.docx..Chapter4, Gantt chart, architecture diagram, UI sketches, flowchart, UML, ERD.
6. CLOUD: ADD Dockerfile + monitoring log + Supabase live-read mode (currently CSV-mode for safety).
7. HONEST LINES: UPDATE — no longer "simulated", now "WFP/Kaggle real data, cleaned".

## 3. DUAL MILESTONE MAP (do in order — this is your supervision form)

### DSE315 (50% supervision + 50% panel) + AI Score mapping:
- M1 DSE: Planning & Analysis (Ch1: Cover, Ch1, Gantt, requirements, goals) = AI M1 Planning & Architecture (/10)
  Deliverables: Problem statement (volatile prices, no unified API), Objectives measurable (MAPE<15%, latency<500ms, uptime 99%), Stack justification, Architecture diagram, Timeline Gantt.
  Gate: Supervisor signs M1.
- M2 DSE: Design & Modelling (Ch2: UI sketches, flowchart, UML use-case/sequence, ERD) = AI M2 Data+Infra part 1 (/20 part)
  Deliverables: 4 UI sketches (dashboard/predictions/admin/login), flowchart Dashboard->API->AI, ERD prices/predictions, infra provisioned (Supabase+Vercel+Render).
  Gate: Supervisor signs M2.
- M3 DSE: Development Testing Part I (Ch3 start, feature-by-feature) = AI M3 Preprocessing (/20)
  Deliverables: kaggle_raw.csv downloaded, clean_kaggle.py run, train/val/test split shown, missing values handled.
  Gate: Show cleaned prices.csv head + row counts.
- M4 DSE: Development Testing DB Integration = AI M4 Model Training (/20)
  Deliverables: train_forecast_v2.py with Holt-Winters+ARIMA, metrics table, saved artifacts data/predictions/*.csv versioned, Supabase synced.
  Gate: Show MAPE table, forecast sample.
- M5 DSE: Deployment + Preliminary docs = AI M5 Cloud Deploy (/20)
  Deliverables: Dockerfile, Render /health live, Vercel live, inference <500ms, monitoring log, prelim pages draft.
  Gate: Both public URLs work.
- M6 DSE: Documentation Consolidation (Ch4 Conclusions+Recommendations+Refs) = AI M6 Evaluation (/10)
  Deliverables: Ch1-4 complete, limitations (bias, overfit, drift), cost analysis, demo script, supervision form fully signed.
  Gate: Final sign-off -> Panel.

## 4. DATA FLOW — FRESH REAL DATA (replaces simulated)

### Primary source (use this one):
Kaggle: "Kenya Food Prices Dataset" by usmanlovescode (curated from World Food Programme Price Database)
- File: wfp_food_prices_ken.csv (1.43 MB)
- Covers: Maize, Maize white, Beans, Beans dry, Rice, Sugar, Potatoes Irish, Sorghum, Milk, Oil
- Markets: Nairobi, Mombasa, Kisumu, Kitui, Marsabit, Mandera, Lodwar/Turkana, Eldoret, etc.
- Dates: 2006-01-15 to 2024+ monthly (some weekly), columns: date, county, market, item, unit, price, lat/lon
- Why suitable: real, long history, multiple markets, same staples as your title, large enough for train/val/test, citable (WFP).
Backup: kaggle.com/datasets/edwincaleb/prices-for-food-crops-commodities-2012-to-2015 (has Cabbages, Tomatoes, Onions, Kales 2012-2015 monthly) + KilimoSTAT JSON + KAMIS kamis.kilimo.go.ke/site/market (daily, needs scraping).

### YOU ARE REQUIRED TO DO THIS (M3 Gate):
1. Create Kaggle account, open dataset page, Download ZIP.
2. Unzip, copy CSV to C:\aifood\data\raw\kaggle_raw.csv
3. Confirm in PowerShell:
```powershell
cd C:\aifood; dir data\raw\; Get-Content data\raw\kaggle_raw.csv -TotalCount 5
```
Paste output. Agent then writes backend/clean_kaggle.py to convert Kaggle columns -> date,item,market,price_kes,unit.

### Cleaning rules (clean_kaggle.py will do):
- Rename: mp_price -> price_kes, adm2 -> market fallback loc_market, commodity -> item standardize (Maize white->Maize, Beans dry->Beans)
- Filter: keep Kenya only, keep top 6 items with most rows, keep Nairobi + 2 markets min for DSE scope
- Handle missing: drop rows with null price, forward-fill monthly gaps, remove duplicates, normalize units to per kg (log conversion in report)
- Output: data/raw/prices.csv SAME columns as before so backend/frontend keep working
- Split: time-ordered 80% train / 10% val / 10% test (no shuffle — future must not leak to past)
- Log: print rows raw, rows cleaned, date range, items, markets — paste into Ch3

## 5. AI FLOW — WHAT IS HOLT-WINTERS + TRAINING (for defence)

Simple: Holt-Winters learns Level (current avg) + Trend (up/down slope) + Season (weekly/monthly repeat).
Training per item in backend/train_forecast_v2.py:
1. Load train split, set date index, freq monthly (WFP is monthly) or daily interpolate.
2. Fit ExponentialSmoothing(trend="add", seasonal="add", seasonal_periods=12 for monthly, 7 for daily).
3. Forecast val period, compute MAE (avg miss), RMSE (big-miss penalty), MAPE (percent miss). Pick params with lowest MAPE on val.
4. Refit on train+val, forecast test 30 steps, report final MAPE. Target MAPE<15% for food.
5. Save data/predictions/<item>_forecast.csv with ds,yhat,yhat_lower,yhat_upper where bounds = yhat +/-1.96*std (95% sure range).
Why statistical not deep learning: <5k rows, no GPU on Render free, needs explainability for panel. LSTM/Transformer = future work when daily KAMIS + weather joined. Prophet kept as theory (time-series, not deep learning, blocked on Windows CmdStan).

## 6. SYSTEM ARCHITECTURE (draw this for Ch2)

```
[Kaggle WFP CSV / KAMIS Excel]
        | clean_kaggle.py
        v
[data/raw/prices.csv] -> [train_forecast_v2.py] -> [data/predictions/*.csv]
        | sync_supabase.py                |
        v                                 v
[Supabase Postgres: prices, predictions] <- [FastAPI backend/main.py on Render]
        ^ /items /prices /predict /upload  | Procfile: uvicorn backend.main:app
        | VITE_API_URL                     |
[React Vite frontend/src/App.jsx on Vercel] -> user chart
```

- Pandas = Excel in code (read_csv, filter, resample). Needed because CSV manipulation manual = 50 lines.
- FastAPI = middleman so Python AI reachable via JSON. Auto /docs for testing. CORS allow_origins=["*"] lets Vercel call Render.
- Supabase = cloud Postgres, no server manage. Tables in docs/supabase_schema.sql. RLS public read.
- Vercel = frontend host (static, global fast). Render = backend host (runs Python 24/7).
- Docker (to add): Dockerfile packages venv312+requirements so Render/local identical. Monitoring: /health + Render logs latency/uptime.

## 7. TECH STACK LOCKED (justify in Ch1/Ch2)
- Frontend: React 19 + Vite 8 + Recharts 3 + Axios, Vercel
- Backend: Python 3.12 + FastAPI 0.115 + Uvicorn 0.34 + Pandas 2.2 + statsmodels 0.14 Holt-Winters (+ ARIMA compare), Render
- DB: Supabase PostgreSQL
- Data: Kaggle WFP wfp_food_prices_ken.csv -> cleaned date,item,market,price_kes,unit
- Title: AI-Powered Food Price Forecasting System for Kenyan Markets
- NOTE: Old simulated generator data/generate_data.py RETIRED after clean. Keep file but do not use for report.

## 8. HONEST REPORT LINES (updated — use these, not old simulated lines)
- "Data sourced from World Food Programme Price Database via Kaggle (Kenya Food Prices Dataset), cleaned and standardized to date,item,market,price_kes,unit; gaps forward-filled, monthly frequency."
- "Due to lack of unified real-time market API in Kenya (KAMIS/KilimoSTAT are web tables/Excel, not open REST), near-real-time is simulated via daily CSV upload + retrain; live scraper listed as future work."
- "Holt-Winters/ARIMA used as statistical time-series baselines, not deep learning, suitable for MVP with <5k rows and no GPU; LSTM is future work."
- "Evaluation uses time-ordered train/val/test split with MAE/RMSE/MAPE; MAPE<15% target."

## 9. CURRENT STATUS (reset for fresh data track)
- [x] Codebase kept: frontend/backend/Supabase/Vercel/Render live (old simulated demo: https://aifood-6cmh.onrender.com + https://aifood-iota.vercel.app/)
- [x] M3 DONE 2026-10-12: Kaggle WFP wfp_food_prices_ken.csv 10766 rows downloaded to data/raw/kaggle_raw.csv, cleaned via backend/clean_kaggle.py to 5605 rows data/raw/prices.csv (items Maize/Beans/Potatoes/Sorghum/Rice/Sugar, 2006-2023 monthly, per-kg normalized, Retail preferred). Old simulated backed up to prices_simulated_backup.csv.
- [x] M4 DONE 2026-10-12: backend/train_forecast_v2.py monthly Holt-Winters periods=12, 80/10/10 split, TEST Maize MAPE 15.59% Potatoes 14.28% Sugar 13.58% Rice 17.26% Beans 24.77% Sorghum 30.48%. 6 forecasts saved. backend/main.py default Nairobi + fallback, frontend market dropdown + monthly labels, npm build passes.
- [x] M4b DONE 2026-10-12: Supabase resynced REAL data — prices 5605 + predictions 72 (old simulated 2190+180 replaced, stale cabbage/onions/sukuma/tomatoes forecasts deleted).
- [ ] M4c: Redeploy Render/Vercel (git push) — NEXT
- [ ] M1/M2 docs: Ch1 + Gantt + UI sketches + ERD — WAITING

## 10. WORKFLOW RULE
1. Agent announces MILESTONE, GOAL, YOUR TASK (1-3 commands max).
2. User runs, replies output.
3. Agent verifies, next step. If wrong, repeat only that step with "YOU ARE REQUIRED TO DO THIS:".
Next action: M3 DATA — user downloads Kaggle CSV as in Section 4.
