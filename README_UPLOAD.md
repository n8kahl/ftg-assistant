# FTG Assistant — Full VWAP/EMA build (API v0.4.0)

This repo is a complete drop-in: real EMA/ATR/MACD/RSI, Session VWAP, Opening Range, features snapshot endpoint, and thin Actions for Chat-Data.

## Endpoints
- GET /health
- GET /_routes
- GET /features_snapshot?symbol=SPY  (protected)
- GET /plan_action?symbol=SPY        (protected)
- GET /fix_action?symbol=AMD&side=calls  (protected)
- POST /analyze_screenshot?file_url=...  (protected)
- GET /watch_start?...                   (protected)

All protected endpoints require header: `X-Api-Secret: <secret>`.

## Railway env
- X_API_SECRET=…
- POLYGON_API_KEY=…
- TRADIER_ACCESS_TOKEN=… (or TRADIER_TOKEN)
- TZ=America/Chicago

## Upload via GitHub (no terminal)
1) Unzip this archive locally.
2) Open your repo -> press `.` to open the web editor.
3) Delete existing files, then drag the **unzipped contents** into the editor.
4) Commit to main. Railway redeploys automatically.
