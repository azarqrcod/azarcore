#!/usr/bin/env python3
"""AZAR SIGNAL hourly Binance USD-M public-market scanner.

No credentials, no order placement, no artificial performance.
Conservative default: missing event/news verification = fail closed.
"""
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "signals" / "state.json"
LEDGER_FILE = ROOT / "signals" / "ledger.ndjson"
NEWS_FILE = ROOT / "signals" / "event_risk.json"
API = "https://fapi.binance.com"
SYMBOLS = ("BTCUSDT", "ETHUSDT")
CAPITAL = 32.0
RISK = 0.32
FEE_RATE = 0.0004
SLIPPAGE_RATE = 0.0002
MAX_RECORDS = 240
UTC = dt.timezone.utc

def iso(t=None):
    return (t or dt.datetime.now(UTC)).isoformat(timespec="seconds").replace("+00:00", "Z")

def to_dt(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def api(path, **params):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": "AZAR-SIGNAL-Scanner/1.0"})
    with urllib.request.urlopen(req, timeout=18) as res:
        return json.load(res)

def ema(a, n):
    alpha = 2.0 / (n + 1)
    x = a[0]
    for v in a[1:]:
        x = alpha * v + (1 - alpha) * x
    return x

def rsi(a, n=14):
    gain = sum(max(0, a[i] - a[i - 1]) for i in range(1, n + 1)) / n
    loss = sum(max(0, a[i - 1] - a[i]) for i in range(1, n + 1)) / n
    for i in range(n + 1, len(a)):
        gain = (gain * (n - 1) + max(0, a[i] - a[i - 1])) / n
        loss = (loss * (n - 1) + max(0, a[i - 1] - a[i])) / n
    return 100.0 if not loss else 100 - 100 / (1 + gain / loss)

def atr(bars, n=14):
    trs = [max(bars[i]["h"] - bars[i]["l"],
               abs(bars[i]["h"] - bars[i-1]["c"]),
               abs(bars[i]["l"] - bars[i-1]["c"])) for i in range(1, len(bars))]
    x = sum(trs[:n]) / n
    for t in trs[n:]:
        x = (x * (n - 1) + t) / n
    return x

def candles(symbol, period, now):
    raw = api("/fapi/v1/klines", symbol=symbol, interval=period, limit=160)
    arr = [{"t": int(x[0]), "end": int(x[6]),
            "o": float(x[1]), "h": float(x[2]),
            "l": float(x[3]), "c": float(x[4]), "v": float(x[5])}
           for x in raw if int(x[6]) < now]
    if len(arr) < 75:
        raise ValueError("insufficient closed candles")
    max_age = 2 * 3600_000 if period == "1h" else 5 * 3600_000
    if now - arr[-1]["end"] > max_age:
        raise ValueError("stale closed candles")
    return arr

def trends(bars):
    close = [b["c"] for b in bars]
    e20, e50 = ema(close, 20), ema(close, 50)
    t = "صعودی" if e20 > e50 and close[-1] > e20 else (
        "نزولی" if e20 < e50 and close[-1] < e20 else "نامشخص")
    return t, e20, e50

def filt_qty(value, step):
    return math.floor((value + 1e-12) / step) * step

def symbol_filters(filters, symbol):
    info = next(x for x in filters["symbols"] if x["symbol"] == symbol)
    data = {x["filterType"]: x for x in info["filters"]}
    lot = data["LOT_SIZE"]
    minq = float(lot["minQty"])
    step = float(lot["stepSize"])
    mn = data.get("MIN_NOTIONAL", data.get("NOTIONAL", {}))
    minnotional = float(mn.get("notional", mn.get("minNotional", 0)))
    return minq, step, minnotional

def event_gate(now):
    # News/risk approval MUST come from a separately checked, recent human or service review.
    # Fail closed otherwise: never treat absence of a feed as a clear macro calendar.
    try:
        data = json.loads(NEWS_FILE.read_text())
        reviewed = to_dt(data["reviewed_at"])
        expires = to_dt(data["valid_until"])
        if (data.get("status") == "VERIFIED_CLEAR" and
                reviewed <= dt.datetime.fromtimestamp(now / 1000, UTC) < expires and
                (dt.datetime.fromtimestamp(now / 1000, UTC) - reviewed).total_seconds() <= 2 * 3600):
            return True, "Verified clear economic-event gate"
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return False, "News/event risk not independently verified"

def check(symbol, exch, now):
    h = candles(symbol, "1h", now)
    f = candles(symbol, "4h", now)
    ticker = api("/fapi/v1/ticker/bookTicker", symbol=symbol)
    premium = api("/fapi/v1/premiumIndex", symbol=symbol)
    oih = api("/futures/data/openInterestHist", symbol=symbol, period="1h", limit=8)
    taker = api("/futures/data/takerlongshortRatio", symbol=symbol, period="1h", limit=8)
    depth = api("/fapi/v1/depth", symbol=symbol, limit=20)
    th, e20h, e50h = trends(h)
    tf, e20f, e50f = trends(f)
    close = [b["c"] for b in h]
    bid, ask = float(ticker["bidPrice"]), float(ticker["askPrice"])
    price = (bid + ask) / 2
    spread = ask - bid
    ratio = h[-1]["v"] / (sum(b["v"] for b in h[-21:-1]) / 20)
    oi_ratio = float(oih[-1]["sumOpenInterest"]) / float(oih[0]["sumOpenInterest"]) - 1
    buy = sum(float(x["buyVol"]) for x in taker[-6:])
    sell = sum(float(x["sellVol"]) for x in taker[-6:])
    taker_ratio = buy / sell if sell else 1.0
    top_bid = sum(float(p) * float(q) for p,q in depth["bids"][:10])
    top_ask = sum(float(p) * float(q) for p,q in depth["asks"][:10])
    r = rsi(close)
    a = atr(h)
    support = min(b["l"] for b in h[-23:-3])
    resistance = max(b["h"] for b in h[-23:-3])
    news_clear, news_reason = event_gate(now)
    freshness = (now - int(ticker.get("time", now)) < 180_000 and
                 now - int(premium.get("time", now)) < 180_000)
    m = {"symbol": symbol, "quality": "verified" if freshness else "stale",
         "price": round(price, 3), "bid": bid, "ask": ask, "spread": round(spread, 4),
         "trend_1h": th, "trend_4h": tf, "ema20_1h": round(e20h, 3),
         "ema50_1h": round(e50h, 3), "ema20_4h": round(e20f, 3),
         "ema50_4h": round(e50f, 3), "rsi_1h": round(r, 2), "atr_1h": round(a, 3),
         "volume_ratio": round(ratio, 3), "oi_change": round(oi_ratio, 4),
         "funding": float(premium["lastFundingRate"]),
         "taker_ratio": round(taker_ratio, 4),
         "top10_bid_notional": round(top_bid), "top10_ask_notional": round(top_ask),
         "support": round(support, 3), "resistance": round(resistance, 3),
         "last_closed_1h": iso(dt.datetime.fromtimestamp(h[-1]["end"]/1000,UTC)),
         "last_closed_4h": iso(dt.datetime.fromtimestamp(f[-1]["end"]/1000,UTC)),
         "closes": [round(v, 3) for v in close[-40:]]}
    # Confirm breakout on candle T-2, retest on T-1, confirmation on T.
    b, rt, cf = h[-3], h[-2], h[-1]
    lev_hi = max(x["h"] for x in h[-28:-3])
    lev_lo = min(x["l"] for x in h[-28:-3])
    is_long = (b["c"] > lev_hi * 1.0008 and rt["l"] <= lev_hi * 1.002
               and rt["c"] >= lev_hi and cf["c"] > rt["h"])
    is_short = (b["c"] < lev_lo * 0.9992 and rt["h"] >= lev_lo * 0.998
                and rt["c"] <= lev_lo and cf["c"] < rt["l"])
    side = "LONG" if is_long else "SHORT" if is_short else None
    align = side is not None and th == tf == ("صعودی" if side == "LONG" else "نزولی")
    volume_ok = ratio >= 1.15
    momentum_ok = (42 <= r <= 66 if side == "LONG" else 34 <= r <= 58 if side else False)
    oi_ok = oi_ratio > 0.002
    taker_ok = (taker_ratio > 1.08 if side == "LONG" else taker_ratio < 0.92 if side else False)
    funding_ok = abs(m["funding"]) <= 0.0004
    liquidity_ok = (spread/max(price,1) < .00015 and min(top_bid,top_ask) >= 20000)
    gates = {"confirmed_break_and_retest": bool(side),
             "trend_1h_4h_aligned": bool(align), "relative_volume": bool(volume_ok),
             "RSI_gate": bool(momentum_ok), "OI_gate": bool(oi_ok),
             "taker_flow": bool(taker_ok), "funding_gate": bool(funding_ok),
             "spread_and_depth": bool(liquidity_ok), "fresh_data": bool(freshness),
             "news_gate": bool(news_clear)}
    score = sum(w for k,w in [
        ("trend_1h_4h_aligned",20),("confirmed_break_and_retest",20),
        ("relative_volume",12),("RSI_gate",7),("OI_gate",9),
        ("taker_flow",8),("funding_gate",6),("spread_and_depth",8),
        ("fresh_data",5),("news_gate",5)] if gates[k])
    reason = " / ".join(k for k,v in gates.items() if not v) or "All gates passed"
    decision = {"id": symbol+"-"+str(h[-1]["t"]),
                "at": iso(), "symbol": symbol, "decision": "NO TRADE",
                "score": score, "reason": reason,
                "ruleset": "1.0", "gates": gates, "news_status": news_reason,
                "last_closed_1h": m["last_closed_1h"]}
    proposal = None
    if score >= 70 and all(gates.values()) and side:
        entry = cf["c"]
        stop = (min(rt["l"],lev_hi) - 0.15 * a if side == "LONG" else
                max(rt["h"],lev_lo) + 0.15 * a)
        distance = abs(entry - stop)
        if distance > 0:
            # Use observed historical price extremes for targets, not arbitrary fixed levels.
            highs = sorted(set(x["h"] for x in h[-110:-3] if x["h"] > entry))
            lows = sorted(set(x["l"] for x in h[-110:-3] if x["l"] < entry), reverse=True)
            levels = highs if side == "LONG" else lows
            t1 = next((x for x in levels if abs(x-entry) >= 1.1*distance), None)
            t2 = next((x for x in levels if abs(x-entry) >= 2.8*distance), None)
            if t1 and t2:
                per_coin_risk = distance + entry*(2*FEE_RATE+SLIPPAGE_RATE)
                minqty, step, minnotional = symbol_filters(exch, symbol)
                qty = filt_qty(RISK / per_coin_risk,step)
                for leverage in (2,3):
                    margin = qty*entry/leverage
                    if qty >= minqty and qty*entry >= minnotional and margin <= CAPITAL*.85:
                        net_loss = qty*per_coin_risk
                        net_gain = qty*(abs(t2-entry)-entry*(2*FEE_RATE+SLIPPAGE_RATE))
                        rr = net_gain/net_loss if net_loss > 0 else 0
                        if rr >= 2.5 and net_loss <= RISK:
                            issued = iso()
                            proposal = {"id":symbol+"-"+str(h[-1]["t"]),
                                "issued_at":issued,"symbol":symbol,"side":side,
                                "entry":round(entry,3),"entry_low":round(entry-0.04*a,3),
                                "entry_high":round(entry+0.04*a,3),
                                "trigger":"After close + valid retest; entry zone only, next 3 hours",
                                "stop":round(stop,3),"tp1":round(t1,3),"tp2":round(t2,3),
                                "rr_net":round(rr,2),"risk_usd":round(net_loss,3),
                                "qty":round(qty,8),"leverage":leverage,"margin_type":"ISOLATED",
                                "expires_at":iso(dt.datetime.fromtimestamp(now/1000, UTC)+dt.timedelta(hours=3)),
                                "status":"NOT TRIGGERED", "score":score,"ruleset":"1.0",
                                "evidence":decision["gates"],
                                "disclaimer":"Only a proposal; no real Binance order"}
                            decision["decision"]="SIGNAL"
                            decision["reason"]="All gates and position sizing passed"
                            break
                if proposal is None:
                    decision["reason"]="Failed risk sizing, order minimums, or net R:R"
                    decision["decision"]="REJECTED"
            else:
                decision["reason"]="No actual historical TP1/TP2 levels with net R:R"
                decision["decision"]="REJECTED"
    return m, decision, proposal, h

def hash_record(row, prev):
    raw = json.dumps(row, ensure_ascii=False, separators=(",",":"),sort_keys=True)
    return hashlib.sha256((prev + raw).encode("utf-8")).hexdigest()

def append_ledger(items):
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = LEDGER_FILE.read_text().splitlines() if LEDGER_FILE.exists() else []
    seen = set()
    prev = "GENESIS"
    for line in existing:
        try:
            x = json.loads(line)
            seen.add(x["record"]["id"])
            prev = x["hash"]
        except (KeyError, json.JSONDecodeError):
            raise ValueError("Malformed ledger, refusing to append")
    with LEDGER_FILE.open("a", encoding="utf-8") as output:
        for row in items:
            if row["id"] in seen:
                continue
            d={"prev_hash":prev,"record":row}
            d["hash"] = hash_record(row,prev)
            output.write(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
            prev=d["hash"]
            seen.add(row["id"])

def outcome_update(state, by_symbol, now):
    for sig in state["signals"]:
        if sig.get("status") in ("TP2","SL","EXPIRED","AMBIGUOUS"): continue
        h=by_symbol.get(sig["symbol"])
        if not h: continue
        issued=to_dt(sig["issued_at"]).timestamp()*1000
        future=[b for b in h if b["t"] > issued]
        if sig.get("status")=="NOT TRIGGERED":
            touch=next((b for b in future if b["l"] <= sig["entry_high"] and b["h"] >= sig["entry_low"]),None)
            if touch:
                sig["status"]="TRIGGERED"
                sig["triggered_at"]=iso(dt.datetime.fromtimestamp(touch["t"]/1000,UTC))
                state["outcomes"].append({"id":sig["id"]+"-TRIGGERED","signal_id":sig["id"],
                    "observed_at":sig["triggered_at"],"event":"TRIGGERED","price":sig["entry"],
                    "reason":"Price touched entry zone; not evidence of an executed order"})
            elif dt.datetime.fromtimestamp(now/1000,UTC) > to_dt(sig["expires_at"]):
                sig["status"]="EXPIRED"
                state["outcomes"].append({"id":sig["id"]+"-EXPIRED","signal_id":sig["id"],
                    "observed_at":iso(),"event":"EXPIRED","price":None,"reason":"Entry not seen before expiry"})
        if sig.get("status") not in ("TRIGGERED","TP1"):continue
        start=to_dt(sig["triggered_at"]).timestamp()*1000 if sig.get("triggered_at") else issued
        subsequent=[b for b in future if b["t"] >= start]
        for b in subsequent:
            high,low=b["h"],b["l"]
            side=sig["side"]
            stop_hit = low<=sig["stop"] if side=="LONG" else high>=sig["stop"]
            tp2_hit=high>=sig["tp2"] if side=="LONG" else low<=sig["tp2"]
            tp1_hit=high>=sig["tp1"] if side=="LONG" else low<=sig["tp1"]
            event = "AMBIGUOUS" if (stop_hit and (tp1_hit or tp2_hit)) else (
                "SL" if stop_hit else "TP2" if tp2_hit else "TP1" if tp1_hit and sig["status"]!="TP1" else None)
            if not event: continue
            if event=="TP1":
                sig["status"]="TP1"
            else: sig["status"]=event
            if not any(x["id"]==sig["id"]+"-"+event for x in state["outcomes"]):
                state["outcomes"].append({"id":sig["id"]+"-"+event,"signal_id":sig["id"],
                    "observed_at":iso(dt.datetime.fromtimestamp(b["end"]/1000,UTC)),
                    "event":event,"price":b["c"] if event=="AMBIGUOUS" else sig.get(event.lower()) if event in ("TP1","TP2") else sig["stop"],
                    "reason":"Based on closed candle high/low; sequence ambiguous if both touched"})
            if event != "TP1": break
    state["outcomes"]=state["outcomes"][-MAX_RECORDS:]

def main():
    state=json.loads(STATE_FILE.read_text(encoding="utf-8"))
    state.setdefault("signals",[])
    state.setdefault("outcomes",[])
    state.setdefault("decisions",[])
    now=int(time.time()*1000)
    states={}
    decisions=[]
    proposals=[]
    bars={}
    errors=[]
    try:
        exch=api("/fapi/v1/exchangeInfo")
    except Exception as exc:
        exch=None
        errors.append("exchange information unavailable: "+type(exc).__name__)
    for symbol in SYMBOLS:
        if exch is None:break
        try:
            m,d,p,h=check(symbol,exch,now)
            states[symbol]=m
            decisions.append(d)
            bars[symbol]=h
            if p:proposals.append(p)
        except Exception as exc:
            errors.append(symbol+": "+type(exc).__name__+" "+str(exc)[:130])
    state["scanned_at"]=iso()
    state["data_status"]="ok" if not errors and len(states)==2 else "unavailable"
    if states:state["markets"]=states
    if errors:
        state["latest_decision"]="NO VERIFIED DATA"
        state["reason"]="داده‌های تازه یا کامل بازار دریافت نشد؛ هیچ سیگنال معتبری صادر نمی‌شود."
        state["errors"]=errors
    else:
        state["errors"]=[]
        state["latest_decision"]="NO TRADE" if not proposals else "VERIFIED SIGNAL"
        state["reason"]="تنها سیگنال‌های دارای تأیید تمام گیت‌ها و حداقل ریسک مجاز منتشر می‌شوند."
        known={x["id"] for x in state["signals"]}
        for s in proposals:
            if s["id"] not in known:state["signals"].append(s)
        outcome_update(state,bars,now)
        # Public latest decisions; full chained ledger in ledger.ndjson
        state["decisions"]=(state["decisions"]+decisions)[-MAX_RECORDS:]
        append_ledger(decisions)
        append_ledger([{"id":"SIG-"+x["id"],"type":"SIGNAL","at":x["issued_at"],
                        "symbol":x["symbol"],"entry":x["entry"],"stop":x["stop"],
                        "tp1":x["tp1"],"tp2":x["tp2"]} for x in proposals])
        append_ledger([{"id":"OUT-"+x["id"],"type":"OUTCOME","at":x["observed_at"],
                        "signal_id":x["signal_id"],"event":x["event"]}
                       for x in state["outcomes"]])
    state["signals"]=state["signals"][-MAX_RECORDS:]
    STATE_FILE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(state["data_status"],state["latest_decision"],len(state["signals"]),
          len(state["outcomes"]),errors)

if __name__=="__main__":
    main()
