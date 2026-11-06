# AZAR SIGNAL | independent website

Website source: `/signals/index.html` (Persian, responsive, no Telegram integration).

## Architecture
- Public market source: Binance USD-M Futures, BTCUSDT and ETHUSDT only.
- Hourly runner: `.github/workflows/azar-signal-hourly.yml`, planned at minute 17 UTC.
- Scanner: `scripts/azar_scan.py`; zero trade execution, no credentials.
- State for website: `signals/state.json`.
- Tamper-evident **not tamper-proof** record chain: `signals/ledger.ndjson` with SHA-256 and versioned logic.
- Event risk approval: `signals/event_risk.json`. Currently UNVERIFIED. The scanner **will not issue any signals** until independently verified news/event context exists. Approval must be renewed at most every 2 hours, or integrated with an authenticated economic calendar.

## Website publishing
GitHub Pages: repository Settings → Pages → Deploy from branch → main → / (root). Page path under the existing website: `/azarcore/signals/`. If GitHub Pages is not configured, the source code can be moved intact to any static host or your own domain.

Do not claim the public page is online until its actual URL has been tested.

## Honest readiness
The page, scan source, scheduled-workflow definition and history schema exist. **No hourly workflow execution, live web delivery, complete news feed, live signal or real trade was independently verified at creation.** Adding files does NOT mean all services have been activated. If Binance blocks the runner network, the scanner records the error and does not issue signals.

News verification, alert deduplication, and source-chain review remain operational responsibilities. GitHub commits can be rewritten by a repository admin, so the hash chain is only tamper-evident relative to a trusted external checkpoint, not immutable storage.

## Ruleset
- BTCUSDT and ETHUSDT, 1h/4h closed candles, EMA20/50, structure, break/retest, volume, RSI, ATR, OI, funding, taker ratio, depth.
- AZAR Score >= 70/100 is not enough: *all* hard gates must pass.
- Estimated net R:R >= 2.5 at historical structure-derived TP2 and max $0.32 reference risk on $32.
- Isolated margin, only 2x or 3x. Size must satisfy Binance symbol filters.
- Never auto-trade. Signal only. Verify futures eligibility in Germany before any real trade.

## No Telegram
This code contains no Telegram API, token or channel reference.

## Security note
All content in this repository and its page is PUBLIC. Never commit API keys, brokerage credentials or personal account identifiers.
