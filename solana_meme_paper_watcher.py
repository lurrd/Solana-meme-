#!/usr/bin/env python3
"""
Solana meme-coin paper-trading watcher (no real trades, no wallet access).

What it does:
- Polls DexScreener's public search endpoint for configurable search terms.
- Filters Solana pairs by minimum liquidity and 24h volume.
- Keeps a small paper portfolio and logs simulated trades to CSV.
- Prints candidates and simulated positions to the terminal.

Important:
- This is an experimental starter, not a profitable strategy.
- Search terms do not discover every newly created token.
- Data can be delayed/incomplete; do not use this as a real-money execution bot.
- No private keys, wallet seed phrases, or exchange credentials are used.
"""

import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---- Configure these before running ----
SEARCH_TERMS = ["solana meme", "ai agent", "cat", "dog"]
POLL_SECONDS = 45
MIN_LIQUIDITY_USD = 15_000
MIN_VOLUME_24H_USD = 25_000
MAX_PAIR_AGE_HOURS = 72
PAPER_START_USD = 100.0
PAPER_POSITION_USD = 10.0
MAX_OPEN_POSITIONS = 3
TAKE_PROFIT_PCT = 0.25       # simulated exit at +25%
STOP_LOSS_PCT = 0.15         # simulated exit at -15%
MAX_HOLD_HOURS = 24
DATA_DIR = Path("meme_watcher_data")
# ---------------------------------------

DATA_DIR.mkdir(exist_ok=True)
TRADES_CSV = DATA_DIR / "paper_trades.csv"
STATE_JSON = DATA_DIR / "paper_state.json"


def utc_now():
    return datetime.now(timezone.utc)


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SolanaPaperWatcher/0.1"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def age_hours(pair):
    created = pair.get("pairCreatedAt")
    if not created:
        return None
    try:
        return max(0, (time.time() - float(created) / 1000) / 3600)
    except (TypeError, ValueError):
        return None


def pair_url(pair):
    return pair.get("url", "")


def fetch_candidates():
    found = {}
    for term in SEARCH_TERMS:
        url = "https://api.dexscreener.com/latest/dex/search/?" + urllib.parse.urlencode({"q": term})
        try:
            payload = get_json(url)
        except Exception as exc:
            print(f"[WARN] Search failed for {term!r}: {exc}")
            continue

        for pair in payload.get("pairs") or []:
            if pair.get("chainId") != "solana":
                continue
            address = pair.get("pairAddress")
            if not address:
                continue
            liquidity = number((pair.get("liquidity") or {}).get("usd"))
            volume24 = number((pair.get("volume") or {}).get("h24"))
            age = age_hours(pair)
            if liquidity < MIN_LIQUIDITY_USD or volume24 < MIN_VOLUME_24H_USD:
                continue
            if age is not None and age > MAX_PAIR_AGE_HOURS:
                continue
            found[address] = pair
    return list(found.values())


def load_state():
    if STATE_JSON.exists():
        try:
            return json.loads(STATE_JSON.read_text())
        except Exception:
            pass
    return {"cash": PAPER_START_USD, "positions": {}, "seen": []}


def save_state(state):
    STATE_JSON.write_text(json.dumps(state, indent=2))


def ensure_csv():
    if not TRADES_CSV.exists():
        with TRADES_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "timestamp_utc", "action", "symbol", "pair_address",
                "price_usd", "quantity", "usd_value", "pnl_usd", "reason", "url"
            ])


def log_trade(action, pair, price, quantity, usd_value, pnl, reason):
    ensure_csv()
    base = (pair.get("baseToken") or {})
    with TRADES_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            utc_now().isoformat(), action, base.get("symbol", "?"),
            pair.get("pairAddress", ""), price, quantity, usd_value, pnl,
            reason, pair_url(pair)
        ])


def print_candidate(pair):
    base = pair.get("baseToken") or {}
    liq = number((pair.get("liquidity") or {}).get("usd"))
    vol = number((pair.get("volume") or {}).get("h24"))
    fdv = number(pair.get("fdv"))
    price = number(pair.get("priceUsd"))
    change = number((pair.get("priceChange") or {}).get("h1"))
    age = age_hours(pair)
    print(
        f"  {base.get('symbol','?')} | price=${price:.8g} | "
        f"liq=${liq:,.0f} | vol24h=${vol:,.0f} | FDV=${fdv:,.0f} | "
        f"1h={change:+.1f}% | age={age if age is not None else 'unknown'}h\n"
        f"    {pair_url(pair)}"
    )


def update_positions(state, pairs_by_address):
    # Update marks and simulate exits only when the pair still appears in search results.
    for address, pos in list(state["positions"].items()):
        pair = pairs_by_address.get(address)
        if not pair:
            continue
        price = number(pair.get("priceUsd"))
        if price <= 0 or pos["entry_price"] <= 0:
            continue
        pnl_pct = price / pos["entry_price"] - 1
        held_hours = (time.time() - pos["entry_epoch"]) / 3600
        reason = None
        if pnl_pct >= TAKE_PROFIT_PCT:
            reason = "paper_take_profit"
        elif pnl_pct <= -STOP_LOSS_PCT:
            reason = "paper_stop_loss"
        elif held_hours >= MAX_HOLD_HOURS:
            reason = "paper_time_exit"
        if reason:
            quantity = pos["quantity"]
            proceeds = quantity * price
            pnl = proceeds - pos["cost_usd"]
            state["cash"] += proceeds
            log_trade("SELL", pair, price, quantity, proceeds, pnl, reason)
            print(f"[PAPER EXIT] {pos['symbol']} pnl={pnl:+.2f} USD ({pnl_pct:+.1%}) reason={reason}")
            del state["positions"][address]


def main():
    state = load_state()
    ensure_csv()
    print("Solana meme-coin PAPER watcher started.")
    print("No real trades are placed. Ctrl+C to stop.\n")
    while True:
        try:
            candidates = fetch_candidates()
            by_address = {p.get("pairAddress"): p for p in candidates}
            update_positions(state, by_address)

            print(f"\n[{utc_now().isoformat()}] candidates={len(candidates)} "
                  f"cash=${state['cash']:.2f} open_positions={len(state['positions'])}")
            for pair in sorted(
                candidates,
                key=lambda p: number((p.get("volume") or {}).get("h24")),
                reverse=True
            )[:10]:
                print_candidate(pair)

            # Conservative demonstration entry: only one paper entry per new pair,
            # and only if basic liquidity/volume filters pass.
            # This is NOT a validated trading edge.
            for pair in sorted(
                candidates,
                key=lambda p: number((p.get("volume") or {}).get("h24")),
                reverse=True
            ):
                address = pair.get("pairAddress")
                price = number(pair.get("priceUsd"))
                if not address or address in state["positions"] or price <= 0:
                    continue
                if len(state["positions"]) >= MAX_OPEN_POSITIONS:
                    break
                if state["cash"] < PAPER_POSITION_USD:
                    break
                # Avoid buying every token repeatedly: seen is persisted.
                if address in state["seen"]:
                    continue
                base = pair.get("baseToken") or {}
                cost = PAPER_POSITION_USD
                quantity = cost / price
                state["cash"] -= cost
                state["positions"][address] = {
                    "symbol": base.get("symbol", "?"),
                    "entry_price": price,
                    "entry_epoch": time.time(),
                    "quantity": quantity,
                    "cost_usd": cost
                }
                state["seen"].append(address)
                log_trade("BUY", pair, price, quantity, cost, 0, "paper_filter_entry")
                print(f"[PAPER ENTRY] {base.get('symbol','?')} ${cost:.2f} at ${price:.8g}")
            save_state(state)
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            save_state(state)
            print("\nStopped. Paper state saved.")
            break
        except Exception as exc:
            print(f"[ERROR] {exc}")
            save_state(state)
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
