"""SPX Around the Clock — a public, no-prediction view of S&P-adjacent risk, 24/7.

Aggregates, labels, and timestamps every venue that prices S&P risk at any hour:
  • regular hours  → real SPX (^GSPC)
  • futures hours  → ES front contract, mechanically basis-adjusted to SPX terms
  • true weekend   → Hyperliquid BTC/ETH as the only live risk tape (clearly labeled
                     "context only — nothing SPX-equivalent trades right now")
No forecasts anywhere — every number is a real trade from a named venue with a timestamp.

Run locally:   streamlit run spx247.py
Deploy public: push to a GitHub repo → share.streamlit.io → point at spx247.py
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

ET = ZoneInfo("America/New_York")

st.set_page_config(page_title="SPX Around the Clock", page_icon="🌐", layout="centered")


@st.cache_data(ttl=60)
def fetch_all():
    """One cached fetch per minute regardless of visitor count."""
    import requests
    import yfinance as yf
    out = {"asof": datetime.now(ET)}

    def _last(ticker, period="5d", interval="5m"):
        try:
            h = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            h.columns = [c[0] if isinstance(c, tuple) else c for c in h.columns]
            px = h["Close"].dropna()
            if px.empty:
                return None
            ts = px.index[-1]
            ts = ts.tz_convert(ET) if ts.tzinfo else ts.tz_localize("UTC").tz_convert(ET)
            return {"px": float(px.iloc[-1]), "ts": ts, "series": px.tail(500)}
        except Exception:
            return None

    out["spx"] = _last("^GSPC")
    out["es"] = _last("ES=F")
    out["vix"] = _last("^VIX", interval="1h")
    # basis: ES − SPX at the moments both printed (median of the overlap)
    basis = None
    try:
        if out["spx"] and out["es"]:
            j = pd.concat([out["spx"]["series"], out["es"]["series"]], axis=1, keys=["spx", "es"]).dropna()
            if len(j) > 10:
                basis = float((j["es"] - j["spx"]).median())
    except Exception:
        pass
    out["basis"] = basis
    # Hyperliquid — 24/7 crypto risk tape (public API, no key)
    try:
        r = requests.post("https://api.hyperliquid.xyz/info", json={"type": "metaAndAssetCtxs"}, timeout=8)
        meta, ctxs = r.json()
        names = [u["name"] for u in meta["universe"]]
        hl = {}
        for coin in ("BTC", "ETH", "SOL"):
            if coin in names:
                c = ctxs[names.index(coin)]
                mark, prev = float(c["markPx"]), float(c["prevDayPx"])
                hl[coin] = {"mark": mark, "chg": (mark / prev - 1) * 100 if prev else 0.0,
                            "funding": float(c["funding"]) * 100}
        out["hl"] = hl
    except Exception:
        out["hl"] = None
    return out


def market_state(now):
    wd, minute = now.weekday(), now.hour * 60 + now.minute
    if wd < 5 and 570 <= minute < 960:
        return "RTH", "🟢 NYSE regular session — this is the real index"
    if wd == 5 or (wd == 6 and minute < 18 * 60) or (wd == 4 and minute >= 17 * 60):
        return "WEEKEND", "🌙 Everything equity is closed — only crypto trades (context, not SPX)"
    return "FUTURES", "🌃 Stocks closed, CME futures open — ES is the live S&P price"


d = fetch_all()
now = d["asof"]
state, state_txt = market_state(now)

st.markdown("<h1 style='margin-bottom:0'>🌐 SPX Around the Clock</h1>", unsafe_allow_html=True)
st.caption(f"What is S&P risk trading at *right now*, from whichever venue is awake · {now:%A %b %d, %-I:%M %p ET} · no predictions, only prints")
st.info(state_txt)

# ── the headline number, source-labeled ──
col1, col2, col3 = st.columns(3)
if state == "RTH" and d["spx"]:
    col1.metric("S&P 500 (live index)", f"{d['spx']['px']:,.0f}")
elif state == "FUTURES" and d["es"]:
    implied = d["es"]["px"] - (d["basis"] or 0)
    col1.metric("ES-implied SPX", f"{implied:,.0f}",
                help=f"ES {d['es']['px']:,.2f} minus basis {d['basis']:+.1f} — a mechanical translation of the live futures print")
else:
    col1.metric("Last real SPX close", f"{d['spx']['px']:,.0f}" if d["spx"] else "—",
                help="Nothing SPX-equivalent is trading right now")
if d["es"]:
    col2.metric("ES front future", f"{d['es']['px']:,.2f}", help=f"as of {d['es']['ts']:%a %-I:%M %p ET}")
if d["vix"]:
    col3.metric("VIX (last)", f"{d['vix']['px']:.1f}")

# ── every source, timestamped ──
st.markdown("#### All venues")
rows = []
if d["spx"]:
    rows.append(("S&P 500 index (^GSPC)", f"{d['spx']['px']:,.2f}", f"{d['spx']['ts']:%a %-I:%M %p}", "CBOE / delayed"))
if d["es"]:
    rows.append(("ES futures (CME)", f"{d['es']['px']:,.2f}", f"{d['es']['ts']:%a %-I:%M %p}", "delayed feed"))
    if d["basis"] is not None:
        rows.append(("→ basis-adjusted SPX terms", f"{d['es']['px'] - d['basis']:,.2f}", "derived", f"basis {d['basis']:+.1f}"))
if d["hl"]:
    for coin, v in d["hl"].items():
        rows.append((f"Hyperliquid {coin} perp (24/7)", f"{v['mark']:,.0f}  ({v['chg']:+.1f}%/24h)",
                     "live", f"funding {v['funding']:+.4f}%/hr"))
if d["vix"]:
    rows.append(("VIX", f"{d['vix']['px']:.2f}", f"{d['vix']['ts']:%a %-I:%M %p}", "delayed"))
st.table(pd.DataFrame(rows, columns=["venue", "last print", "as of (ET)", "notes"]))

if state == "WEEKEND" and d["hl"]:
    st.caption("⚠️ Weekend honesty note: crypto is the only live tape. It correlates with Monday's equity open "
               "but it is NOT an S&P price — we show it as context and refuse to fake an 'SPX quote' from it.")

# ── stitched 7-day picture ──
st.markdown("#### The last week, stitched from whoever was open")
try:
    frames = []
    if d["spx"]:
        s = d["spx"]["series"].rename("SPX (index)")
        frames.append(s)
    if d["es"] and d["basis"] is not None:
        e = (d["es"]["series"] - d["basis"]).rename("ES-implied (off-hours)")
        frames.append(e)
    if frames:
        chart = pd.concat(frames, axis=1)
        chart.index = [t.tz_convert(ET) if t.tzinfo else t for t in chart.index]
        st.line_chart(chart, height=320)
        st.caption("Solid coverage during NYSE hours = the real index; the futures-implied line carries the story overnight. Gaps = truly closed.")
except Exception:
    pass

st.markdown("---")
st.caption("🐱 Built by Balder's Opus Picks · raw prints from public delayed feeds, refreshed ≤60s · "
           "nothing here is a forecast or financial advice · [more research →](https://open.substack.com/pub/baldertrader)")
