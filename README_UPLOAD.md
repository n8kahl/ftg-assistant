# FTG Assistant — Chat-Data Actions Ready

This is a drop-in API you can push to Railway and wire to Chat-Data Actions.

## Endpoints
- GET /health
- GET /_routes
- GET /plan_action?symbol=SPY
- GET /fix_action?symbol=AMD&side=calls&qty=1&avg_price=1.35
- GET /watch_start?symbol=SPY&entry=...&stop=...&targets=557.2,558.1&ttl_min=30
- POST /analyze_screenshot (multipart `file` or JSON { "file_url": "..." })

All Action endpoints require header:
```
X-Api-Secret: <your secret>
```

## Deploy
1) Set env on Railway:
```
X_API_SECRET=846655a61ee5bec2980b8eff0a77dd177e4e8d0b0a26c7f25534147b87a79f7f
TZ=America/Chicago
```
2) Build & deploy (Railway auto)
3) Test:
```
BASE="https://ftg-assistant-production.up.railway.app"
SEC="$X_API_SECRET"
curl -s "$BASE/health"
curl -s -H "X-Api-Secret: $SEC" "$BASE/plan_action?symbol=SPY"
curl -s -H "X-Api-Secret: $SEC" "$BASE/fix_action?symbol=AMD&side=calls&qty=1&avg_price=1.35"
```

## Notes
- Indicator/flow logic is stubbed. Once Actions work, we’ll wire Polygon/Tradier/UW.
- If you already have a repo, just unzip this over it and commit.
