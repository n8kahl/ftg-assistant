# feat: VWAP + /features_snapshot endpoint + prompt-first design hooks

**What**  
- Adds session VWAP and utility for anchored VWAP + opening ranges (5m/15m).
- New endpoint `GET /features_snapshot?symbol=SPY` that returns a compact JSON of indicators & levels:
  - price, ATR(14) on 5m
  - EMAs 9/21/50/200 on 5m/15m/1h
  - 5m momentum (RSI, MACD hist)
  - Session VWAP + anchor slots, OR(5/15) H/L
  - Previous day high/low
  - Options candidates (from Tradier) to support Δ≈0.45 and a vertical alt
- Mounts the new router under the existing auth guard so Chat-Data can call it.
- This supports a **prompt-first** policy: the bot decides final plan using the snapshot; the API stays fact-only.

**Why**
- Lets us iterate trading policy in Chat-Data system prompt (VWAP rules, event windows, etc.) without redeploying.
- Keeps API simple & fast, dedicated to reliable data calculations.

**Follow-ups (separate PRs)**
- Wire Unusual Whales flow endpoints to snapshot and confluence.
- Add econ/earnings event penalties (using CALENDAR_URL/EARNINGS_URL feeds).
- Real watcher loop (Redis) for live guidance.

**Env**
- No new env required. Ensure `POLYGON_API_KEY` and `TRADIER_ACCESS_TOKEN` (or `TRADIER_TOKEN`) are set.
