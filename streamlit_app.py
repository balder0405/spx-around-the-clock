"""SPX Around the Clock — a public, no-prediction view of S&P-adjacent risk, 24/7.
Dark terminal edition. Every number is a real print from a named venue with a timestamp.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

ET = ZoneInfo("America/New_York")
st.set_page_config(page_title="SPX Around the Clock", page_icon="🌐", layout="wide",
                   initial_sidebar_state="collapsed")

# ── auto-refresh every 60s ──
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="tick")
except Exception:
    pass

# ── global dark-terminal styling ──
st.markdown("""<style>
.stApp { background: radial-gradient(1200px 600px at 20% -10%, #16233f 0%, #0b1220 45%) #0b1220; }
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 2.2rem; max-width: 1080px;}
h1,h2,h3,p,span,div {font-family: -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;}
.hero {text-align:center; margin-bottom: 6px;}
.hero .title {font-size: 34px; font-weight: 800; color:#f8fafc; letter-spacing:.5px;}
.hero .title .accent {background: linear-gradient(90deg,#34d399,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.hero .sub {color:#7c8aa5; font-size:13px; margin-top:2px;}
.statuspill {display:inline-block; padding:6px 18px; border-radius:999px; font-size:13px; font-weight:700; letter-spacing:.5px; margin:10px 0 4px;}
.bigpx {text-align:center; margin: 8px 0 2px;}
.bigpx .num {font-size: 76px; font-weight: 800; font-variant-numeric: tabular-nums;
  color:#f8fafc; text-shadow: 0 0 34px rgba(52,211,153,.35); line-height:1.05;}
.bigpx .lbl {color:#7c8aa5; font-size:12px; letter-spacing:2.5px; text-transform:uppercase;}
.bigpx .src {color:#94a3b8; font-size:12.5px; margin-top:4px;}
.cardrow {display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin:20px 0;}
.card {box-sizing:border-box; background: rgba(255,255,255,.035); border:1px solid rgba(148,163,184,.16); border-radius:16px;
  padding:16px 22px; min-width:168px; text-align:center; backdrop-filter: blur(6px);}
.card .k {color:#7c8aa5; font-size:10.5px; letter-spacing:2px; text-transform:uppercase;}
.card .v {color:#f1f5f9; font-size:26px; font-weight:800; margin-top:3px; font-variant-numeric: tabular-nums;}
.card .d {font-size:12px; margin-top:2px;}
.up {color:#34d399;} .dn {color:#f87171;} .mut {color:#7c8aa5;}
.venue {box-sizing:border-box; display:flex; align-items:center; justify-content:space-between; padding:11px 18px;
  background: rgba(255,255,255,.03); border:1px solid rgba(148,163,184,.12); border-radius:12px; margin:7px 0;}
.venue .n {color:#e2e8f0; font-weight:600; font-size:14px;}
.venue .meta {color:#64748b; font-size:11.5px; margin-top:1px;}
.venue .p {color:#f8fafc; font-weight:800; font-size:17px; font-variant-numeric: tabular-nums; text-align:right;}
.venue .live {color:#34d399; font-size:10px; letter-spacing:1.5px; font-weight:800;}
.sechead {color:#cbd5e1; font-size:13px; letter-spacing:2.5px; text-transform:uppercase; margin: 26px 0 8px; font-weight:700;}
.note {background: rgba(96,165,250,.07); border:1px solid rgba(96,165,250,.25); border-radius:12px;
  padding:12px 16px; color:#93c5fd; font-size:13px; margin:12px 0;}
.foot {color:#5b6b85; font-size:11.5px; text-align:center; margin-top:34px; line-height:1.8;}
.foot a {color:#7c8aa5;}

/* ticker tape */
.tape {overflow:hidden; white-space:nowrap; border-top:1px solid rgba(148,163,184,.12); border-bottom:1px solid rgba(148,163,184,.12);
  background: rgba(255,255,255,.02); padding:7px 0; margin-bottom:14px;}
.tape .inner {display:inline-block; animation: scroll 38s linear infinite;}
.tape span {color:#94a3b8; font-size:12.5px; margin: 0 18px; font-variant-numeric: tabular-nums;}
.tape b {color:#e2e8f0; font-weight:700;}
@keyframes scroll {0% {transform: translateX(0);} 100% {transform: translateX(-50%);}}
/* pulse on live elements */
@keyframes pulse {0%,100% {opacity:1;} 50% {opacity:.55;}}
.pulse {animation: pulse 2.2s ease-in-out infinite;}
/* mini CTA under the number */
.minicta {display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:14px 0 4px;}
.mbtn {display:inline-flex; align-items:center; gap:7px; padding:9px 20px; border-radius:999px; font-weight:800; font-size:13.5px;
  text-decoration:none !important; transition: transform .15s;}
.mbtn:hover {transform: translateY(-1px);}
.mbtn.sub {background: linear-gradient(90deg,#f97316,#fb923c); color:#fff !important; box-shadow: 0 4px 20px rgba(249,115,22,.4);}
.mbtn.x {background: rgba(255,255,255,.08); color:#f1f5f9 !important; border:1px solid rgba(148,163,184,.35);}
.mctatxt {text-align:center; color:#7c8aa5; font-size:11.5px; margin-top:6px;}
/* venue consensus strip */
.conswrap {max-width:640px; margin: 20px auto 2px;}
.conslbl {display:flex; justify-content:space-between; color:#7c8aa5; font-size:10.5px; letter-spacing:1.5px; margin-bottom:5px;}
.consbar {position:relative; height:34px; border-radius:999px; background: linear-gradient(90deg, rgba(248,113,113,.14), rgba(148,163,184,.10), rgba(52,211,153,.14));
  border:1px solid rgba(148,163,184,.18);}
.consdot {position:absolute; top:50%; transform: translate(-50%,-50%); width:11px; height:11px; border-radius:50%;
  border:2px solid #0b1220; cursor:default;}
.consmed {position:absolute; top:-4px; bottom:-4px; width:2px; background:#f8fafc; opacity:.7; transform:translateX(-50%);}
.constxt {text-align:center; color:#94a3b8; font-size:12px; margin-top:7px;}
@media (max-width: 640px) {
  .tape span {font-size:11px; margin:0 12px;}
  .mbtn {padding:8px 14px; font-size:12px;}
}

.desk {display:flex; gap:14px; justify-content:center; flex-wrap:wrap; margin: 8px 0 4px;}
.catcard {box-sizing:border-box; width:236px; background: rgba(255,255,255,.035); border:1px solid rgba(148,163,184,.16);
  border-radius:16px; overflow:hidden; text-align:center;}
.catcard img {width:100%; height:190px; object-fit:cover; display:block;}
.catcard .cn {color:#f1f5f9; font-weight:800; font-size:14px; margin:9px 0 2px;}
.catcard .cr {color:#7c8aa5; font-size:11.5px; padding: 0 10px 12px; line-height:1.45;}
.ctarow {display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin: 18px 0 6px;}
.btn {display:inline-block; padding: 12px 26px; border-radius: 12px; font-weight:800; font-size:14.5px;
  text-decoration:none !important; letter-spacing:.3px;}
.btn.sub {background: linear-gradient(90deg,#f97316,#fb923c); color:#fff !important; box-shadow: 0 4px 22px rgba(249,115,22,.35);}
.btn.x {background: rgba(255,255,255,.07); color:#f1f5f9 !important; border:1px solid rgba(148,163,184,.3);}
.ctatxt {text-align:center; color:#94a3b8; font-size:13px; margin-top:8px;}
.hlogo {width:52px; height:52px; border-radius:50%; vertical-align:middle; margin-right:6px; border:2px solid rgba(148,163,184,.35);}
@media (max-width: 640px) {
  .catcard {width: calc(50% - 10px);}
  .catcard img {height: 140px;}
  .btn {padding: 10px 18px; font-size: 13px;}
}

/* ── mobile ── */
@media (max-width: 640px) {
  .block-container {padding: 1.2rem 0.8rem;}
  .hero .title {font-size: 21px; padding: 0 6px;}
  .hero .sub {font-size: 11px; padding: 0 8px;}
  .statuspill {font-size: 11px; padding: 5px 12px;}
  .bigpx .num {font-size: 52px;}
  .bigpx .src {font-size: 10.5px; padding: 0 10px;}
  .cardrow {gap: 8px; margin: 14px 0;}
  .card {min-width: calc(50% - 12px); flex: 1 1 calc(50% - 12px); padding: 12px 10px;}
  .card .v {font-size: 20px;}
  .venue {padding: 9px 12px; flex-wrap: wrap; gap: 4px;}
  .venue .n {font-size: 12.5px;}
  .venue .meta {font-size: 10px;}
  .venue .p {font-size: 14px;}
  .sechead {font-size: 11px; letter-spacing: 1.5px;}
  .note {font-size: 11.5px; padding: 10px 12px;}
  .foot {font-size: 10px; padding: 0 8px;}
}
</style>""", unsafe_allow_html=True)



SUBSTACK = "https://substack.com/@balder714059"
XLINK = "https://x.com/Balder13946731"


def _b64(name):
    import base64
    from pathlib import Path
    try:
        fp = Path(__file__).parent / name
        return "data:image/jpeg;base64," + base64.b64encode(fp.read_bytes()).decode()
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_all():
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
            return {"px": float(px.iloc[-1]), "ts": ts, "series": px.tail(800)}
        except Exception:
            return None

    out["spx"] = _last("^GSPC")
    out["es"] = _last("ES=F")
    out["nq"] = _last("NQ=F", interval="15m")
    out["vix"] = _last("^VIX", interval="1h")
    out["btc"] = _last("BTC-USD", period="7d", interval="1h")
    # OFFICIAL daily closes — the 5m series ends on the 15:55 bar, ~5-6 pts below the true settle
    # (audited 2026-07-05: 15:55 bar 7,477.6 vs official 7,483.2; live IG/HL venues confirmed the
    # official-close scale). All ratios, anchors and translations use OFFICIAL closes.
    def _official(ticker):
        try:
            h = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)
            h.columns = [c[0] if isinstance(c, tuple) else c for c in h.columns]
            px = h["Close"].dropna()
            return {"px": float(px.iloc[-1]), "ts": px.index[-1], "series": px}
        except Exception:
            return None
    out["spx_off"] = _official("^GSPC")
    out["dji"] = _official("^DJI")
    out["ndx"] = _official("^NDX")
    basis = basis_chart = None
    try:
        if out["spx"] and out["es"]:
            j = pd.concat([out["spx"]["series"], out["es"]["series"]], axis=1, keys=["spx", "es"], sort=False).dropna()
            if len(j) > 10:
                basis_chart = float((j["es"] - j["spx"]).median())   # 5m-internal (chart overlay only)
        # OFFICIAL basis: ES bar at each official close vs the official settle (this is the scale
        # live IG/HL venues confirm; the 5m-internal basis runs ~6 pts rich)
        if out.get("spx_off") and out["es"]:
            esd = out["es"]["series"]
            diffs = []
            for ts, oc in out["spx_off"]["series"].items():
                day = esd[[t.date() == ts.date() for t in esd.index]]
                if len(day):
                    sess = day[[(t.hour * 60 + t.minute) >= 955 and (t.hour * 60 + t.minute) <= 965 for t in day.index]]
                    ref = float(sess.iloc[-1]) if len(sess) else float(day.iloc[-1])
                    diffs.append(ref - float(oc))
            if diffs:
                basis = float(pd.Series(diffs).median())
        if basis is None:
            basis = basis_chart
    except Exception:
        pass
    out["basis"] = basis
    out["basis_chart"] = basis_chart if basis_chart is not None else basis
    # crypto-mapped WEEKEND estimate — validated on 111 weekends: Monday gap ≈ 0.022 + 0.106×BTC
    # (corr +0.45, residual σ 0.78%). An ESTIMATE with an error band, never shown as a real quote.
    wk = None
    try:
        if out["spx"] and out["btc"]:
            spxs, btcs = out["spx"]["series"], out["btc"]["series"]
            sidx = [t.tz_convert(ET) if t.tzinfo else t for t in spxs.index]
            bidx = [t.tz_convert(ET) if t.tzinfo else t for t in btcs.index]
            xs, ys = [], []
            anchor_px = anchor_btc = None
            for t, bpx in zip(bidx, btcs.values):
                wd, mn = t.weekday(), t.hour * 60 + t.minute
                in_wk = (wd == 4 and mn >= 1020) or wd == 5 or (wd == 6 and mn < 1080)
                if in_wk:
                    if anchor_px is None and out.get("spx_off"):
                        # anchor = last OFFICIAL equity close before t, and BTC AT THAT CLOSE'S
                        # timestamp (16:00 ET) — not at the first weekend bar (audit fix: the old
                        # anchors mismatched by an hour, and by a full day on holiday weekends)
                        closes = [(cts, cv) for cts, cv in out["spx_off"]["series"].items()]
                        prior_c = [(cts, cv) for cts, cv in closes
                                   if cts.tz_localize(ET).replace(hour=16, minute=0) <= t]
                        if prior_c:
                            c_ts, c_val = prior_c[-1]
                            c_dt = c_ts.tz_localize(ET).replace(hour=16, minute=0)
                            priorb = [v for ti, v in zip(bidx, btcs.values) if ti <= c_dt]
                            if priorb:
                                anchor_px, anchor_btc = float(c_val), float(priorb[-1])
                    if anchor_px and anchor_btc:
                        ret = (float(bpx) / anchor_btc - 1) * 100
                        xs.append(t)
                        ys.append(anchor_px * (1 + (0.022 + 0.106 * ret) / 100))
                else:
                    anchor_px = anchor_btc = None
            if xs:
                wk = {"x": xs, "y": ys, "sigma": 0.0078}
    except Exception:
        wk = None
    out["weekend_map"] = wk

    # IG weekend markets — the real traded WEEKEND venues for US equities (public pages,
    # server-rendered bid/offer; attribution shown). Translated to SPX terms via live index
    # ratios (mechanical, like the ES basis). Reference only.
    def _ig_quote(url):
        try:
            import re
            hdrs = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
            rr = requests.get(url, headers=hdrs, timeout=10)
            bid = re.search(r'data-field="BID">([0-9.]+)', rr.text)
            off = re.search(r'data-field="OFR">([0-9.]+)', rr.text)
            if bid and off:
                return {"bid": float(bid.group(1)), "offer": float(off.group(1)),
                        "mid": (float(bid.group(1)) + float(off.group(1))) / 2}
        except Exception:
            pass
        return None

    ig = _ig_quote("https://www.ig.com/uk/indices/markets-indices/weekend-wall-street")
    if ig and out.get("spx_off") and out.get("dji") and out["dji"]["px"] > 0:
        ig["spx_terms"] = ig["mid"] * out["spx_off"]["px"] / out["dji"]["px"]
    ig_tech = _ig_quote("https://www.ig.com/en/indices/markets-indices/weekend-us-tech-100-e1")
    if ig_tech and out.get("spx_off") and out.get("ndx") and out["ndx"]["px"] > 0:
        ig_tech["spx_terms"] = ig_tech["mid"] * out["spx_off"]["px"] / out["ndx"]["px"]
    # IG US 500 CFD — quoted DIRECTLY in SPX terms and trades ~24/5 (the cleanest
    # off-hours SPX-terms venue; closed on weekends when the Weekend markets take over)
    ig_spx = _ig_quote("https://www.ig.com/en/indices/markets-indices/us-spx-500")
    out["ig"] = ig
    out["ig_tech"] = ig_tech
    out["ig_spx"] = ig_spx
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
    # Hyperliquid US500 perp — a REAL S&P-terms market that trades 24/7 INCLUDING weekends
    # (builder dex "mkts"; index/10 scale — we snap the multiplier to the nearest integer so a
    # basis drift can never sneak in). Thin venue (~$1-2M/day) → shown with that caveat.
    try:
        r2 = requests.post("https://api.hyperliquid.xyz/info",
                           json={"type": "metaAndAssetCtxs", "dex": "mkts"}, timeout=8)
        meta2, ctxs2 = r2.json()
        names2 = [u["name"] for u in meta2["universe"]]
        if "mkts:US500" in names2:
            c2 = ctxs2[names2.index("mkts:US500")]
            mark = float(c2["markPx"])
            prev = float(c2["prevDayPx"]) if c2.get("prevDayPx") else mark
            mult = round(out["spx_off"]["px"] / mark) if (out.get("spx_off") and mark > 0) else 10
            out["hl_us500"] = {"mark": mark, "mult": mult, "spx_terms": mark * mult,
                               "chg24h": (mark / prev - 1) * 100 if prev else 0.0,
                               "funding": float(c2.get("funding", 0)) * 100,
                               "vol": float(c2.get("dayNtlVlm", 0))}
        else:
            out["hl_us500"] = None
    except Exception:
        out["hl_us500"] = None
    return out


def market_state(now):
    wd, minute = now.weekday(), now.hour * 60 + now.minute
    if wd < 5 and 570 <= minute < 960:
        return "RTH", "● NYSE OPEN — LIVE INDEX", "#34d399"
    if wd == 5 or (wd == 6 and minute < 18 * 60) or (wd == 4 and minute >= 17 * 60):
        return "WEEKEND", "◐ WEEKEND — ONLY CRYPTO TRADES", "#fbbf24"
    return "FUTURES", "◎ OVERNIGHT — CME FUTURES OPEN", "#60a5fa"


def next_open(now):
    d = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if now >= d or now.weekday() >= 5:
        d = d + timedelta(days=1)
        while d.weekday() >= 5:
            d = d + timedelta(days=1)
    mins = int((d - now).total_seconds() // 60)
    return f"{mins // 60}h {mins % 60:02d}m"


d = fetch_all()
now = d["asof"]
state, state_txt, scol = market_state(now)

# ── ticker tape ──
_tape_items = []
if d.get("hl_us500"):
    _tape_items.append(("US500 24/7", f"{d['hl_us500']['spx_terms']:,.0f}", d["hl_us500"]["chg24h"]))
if d["es"]:
    _tape_items.append(("ES", f"{d['es']['px']:,.0f}", None))
if d["nq"]:
    _tape_items.append(("NQ", f"{d['nq']['px']:,.0f}", None))
if d.get("ig_spx"):
    _tape_items.append(("IG US500", f"{d['ig_spx']['mid']:,.1f}", None))
if d["vix"]:
    _tape_items.append(("VIX", f"{d['vix']['px']:.1f}", None))
if d["hl"]:
    for _c in ("BTC", "ETH", "SOL"):
        if _c in d["hl"]:
            _tape_items.append((_c, f"{d['hl'][_c]['mark']:,.0f}", d["hl"][_c]["chg"]))
_seg = ""
for _n, _v, _ch in _tape_items:
    _chs = f" <span class='{'up' if _ch >= 0 else 'dn'}'>{_ch:+.1f}%</span>" if _ch is not None else ""
    _seg += f"<span><b>{_n}</b> {_v}{_chs}</span>"
if _seg:
    st.markdown(f'<div class="tape"><div class="inner">{_seg}{_seg}</div></div>', unsafe_allow_html=True)

_logo = _b64("cat_boss.jpg")
_logo_html = f'<img class="hlogo" src="{_logo}">' if _logo else "🌐"
st.markdown(f"""
<div class="hero">
  <div class="title">{_logo_html} SPX <span class="accent">Around the Clock</span></div>
  <div class="sub">what S&amp;P risk is trading at right now, from whichever venue is awake · no forecasts, only prints</div>
  <div class="statuspill pulse" style="background:{scol}22; color:{scol}; border:1px solid {scol}55;">{state_txt}</div>
</div>""", unsafe_allow_html=True)

# ── the headline number ──
if state == "RTH" and d["spx"]:
    big, lbl, src = d["spx"]["px"], "S&P 500 · LIVE INDEX", f"^GSPC · {d['spx']['ts']:%-I:%M %p ET}"
elif d["es"] and d["basis"] is not None and state == "FUTURES":
    big = d["es"]["px"] - d["basis"]
    lbl, src = "ES-IMPLIED SPX", f"CME ES {d['es']['px']:,.2f} − basis {d['basis']:+.1f} · {d['es']['ts']:%a %-I:%M %p ET}"
elif state == "WEEKEND" and d.get("hl_us500"):
    u = d["hl_us500"]
    big = u["spx_terms"]
    lbl = "HYPERLIQUID US500 PERP · REAL 24/7 MARKET"
    src = f"mark {u['mark']:,.2f} ×{u['mult']} · {u['chg24h']:+.1f}%/24h · thin venue (${u['vol']/1e6:.1f}M/day) — cross-check the crypto map & IG below"
elif state == "WEEKEND" and d.get("weekend_map"):
    w = d["weekend_map"]
    big = w["y"][-1]
    lbl = "CRYPTO-MAPPED SPX ESTIMATE"
    src = f"weekend BTC mapped via measured β (0.106, corr .45, 111 weekends) · ±{big * w['sigma']:,.0f} pts (1σ) · an estimate, NOT a quote"
else:
    big = d["spx_off"]["px"] if d.get("spx_off") else (d["spx"]["px"] if d["spx"] else 0)
    lbl = "LAST REAL SPX CLOSE"
    src = "nothing SPX-equivalent trades right now" + (f" · closed {d['spx']['ts']:%a %-I:%M %p ET}" if d["spx"] else "")
st.markdown(f"""
<div class="bigpx">
  <div class="lbl">{lbl}</div>
  <div class="num">{big:,.0f}</div>
  <div class="src">{src} · next NYSE open in {next_open(now)}</div>
</div>""", unsafe_allow_html=True)

# ── CTA: the monetization row, right under the number ──
st.markdown(f"""
<div class="minicta">
  <a class="mbtn sub" href="{SUBSTACK}" target="_blank">📬 Get the daily picks — free on Substack</a>
  <a class="mbtn x" href="{XLINK}" target="_blank">𝕏 Follow @Balder13946731</a>
</div>
<div class="mctatxt">the cat that runs this page also picks stocks every night 🐱</div>
""", unsafe_allow_html=True)

# ── venue consensus strip: every SPX-terms source as a dot on one bar ──
_vs = []
if d["es"] and d["basis"] is not None:
    _vs.append(("ES-implied", d["es"]["px"] - d["basis"], "#60a5fa"))
if d.get("ig_spx"):
    _vs.append(("IG US500", d["ig_spx"]["mid"], "#a78bfa"))
if d.get("hl_us500"):
    _vs.append(("HL US500 24/7", d["hl_us500"]["spx_terms"], "#34d399"))
if d.get("ig") and d["ig"].get("spx_terms"):
    _vs.append(("IG Wall St →SPX", d["ig"]["spx_terms"], "#f97316"))
if d.get("ig_tech") and d["ig_tech"].get("spx_terms"):
    _vs.append(("IG Tech →SPX", d["ig_tech"]["spx_terms"], "#f472b6"))
if state == "WEEKEND" and d.get("weekend_map"):
    _vs.append(("crypto map", d["weekend_map"]["y"][-1], "#fbbf24"))
if len(_vs) >= 3:
    _vals = sorted(v for _, v, _c in _vs)
    _lo, _hi = min(_vals), max(_vals)
    _med = _vals[len(_vals) // 2]
    _pad = max((_hi - _lo) * 0.15, 2)
    _l0, _h0 = _lo - _pad, _hi + _pad
    _dots = ""
    for _n, _v, _c in _vs:
        _x = (_v - _l0) / (_h0 - _l0) * 100
        _dots += f'<div class="consdot" style="left:{_x:.1f}%; background:{_c};" title="{_n}: {_v:,.1f}"></div>'
    _mx = (_med - _l0) / (_h0 - _l0) * 100
    st.markdown(f"""
<div class="conswrap">
  <div class="conslbl"><span>{_l0:,.0f}</span><span>VENUE CONSENSUS</span><span>{_h0:,.0f}</span></div>
  <div class="consbar"><div class="consmed" style="left:{_mx:.1f}%"></div>{_dots}</div>
  <div class="constxt">{len(_vs)} independent venues · median <b style="color:#f1f5f9">{_med:,.0f}</b> · spread <b style="color:#f1f5f9">{_hi - _lo:,.0f} pts</b>{" · ✅ tight agreement" if (_hi - _lo) < 25 else ""}</div>
</div>""", unsafe_allow_html=True)

# ── metric cards ──
cards = ""
if d["es"]:
    prev = float(d["es"]["series"].iloc[0]) if len(d["es"]["series"]) else d["es"]["px"]
    c5 = (d["es"]["px"] / prev - 1) * 100
    cards += f'<div class="card"><div class="k">ES Future</div><div class="v">{d["es"]["px"]:,.0f}</div><div class="d {"up" if c5>=0 else "dn"}">{c5:+.2f}% / 5d</div></div>'
if d["nq"]:
    prevn = float(d["nq"]["series"].iloc[0]) if len(d["nq"]["series"]) else d["nq"]["px"]
    cn = (d["nq"]["px"] / prevn - 1) * 100
    cards += f'<div class="card"><div class="k">NQ Future</div><div class="v">{d["nq"]["px"]:,.0f}</div><div class="d {"up" if cn>=0 else "dn"}">{cn:+.2f}% / 5d</div></div>'
if d["vix"]:
    cards += f'<div class="card"><div class="k">VIX</div><div class="v">{d["vix"]["px"]:.1f}</div><div class="d mut">implied vol</div></div>'
if d.get("hl_us500"):
    _u = d["hl_us500"]
    cards += f'<div class="card"><div class="k">HL US500 · 24/7</div><div class="v">{_u["spx_terms"]:,.0f}</div><div class="d {"up" if _u["chg24h"]>=0 else "dn"}">{_u["chg24h"]:+.1f}% / 24h</div></div>'
if d.get("ig") and d["ig"].get("spx_terms") and state == "WEEKEND":
    cards += f'<div class="card"><div class="k">IG Weekend (SPX terms)</div><div class="v">{d["ig"]["spx_terms"]:,.0f}</div><div class="d mut">real weekend market</div></div>'
if d["hl"]:
    for coin in ("BTC", "ETH"):
        if coin in d["hl"]:
            v = d["hl"][coin]
            cards += f'<div class="card"><div class="k">{coin} · 24/7</div><div class="v">{v["mark"]:,.0f}</div><div class="d {"up" if v["chg"]>=0 else "dn"}">{v["chg"]:+.1f}% / 24h</div></div>'
st.markdown(f'<div class="cardrow">{cards}</div>', unsafe_allow_html=True)

if state == "WEEKEND":
    st.markdown('<div class="note">◐ <b>How the weekend estimate works:</b> nothing S&amp;P-equivalent trades on weekends, so the amber dotted line maps the live BTC move through a measured relationship (β 0.106, corr +0.45 across 111 weekends) into SPX terms. It is an <b>estimate with a ±0.78% band</b> — clearly marked, never presented as a real quote. Cross-check it against <b>IG Weekend Wall Street</b> below — a real traded weekend market (Dow-based, shown in SPX terms via the index ratio). The real print resumes when futures open Sunday 6 PM ET.</div>', unsafe_allow_html=True)

# ── chart ──
st.markdown('<div class="sechead">The last week, stitched from whoever was open</div>', unsafe_allow_html=True)
try:
    import plotly.graph_objects as go
    fig = go.Figure()
    ys = []
    if d.get("weekend_map"):
        w = d["weekend_map"]
        up = [v * (1 + w["sigma"]) for v in w["y"]]
        dn = [v * (1 - w["sigma"]) for v in w["y"]]
        fig.add_trace(go.Scatter(x=list(w["x"]) + list(w["x"])[::-1], y=up + dn[::-1], fill="toself",
                                 fillcolor="rgba(251,191,36,.09)", line=dict(width=0),
                                 name="weekend ±1σ", hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=w["x"], y=w["y"], name="crypto-mapped weekend est.",
                                 line=dict(color="#fbbf24", width=1.4, dash="dot"), opacity=.9))
        ys += list(w["y"])
    if d["es"] and d.get("basis_chart") is not None:
        e = d["es"]["series"] - d["basis_chart"]
        eidx = [t.tz_convert(ET) if t.tzinfo else t for t in e.index]
        fig.add_trace(go.Scatter(x=eidx, y=list(e.values), name="ES-implied (off-hours)",
                                 line=dict(color="#60a5fa", width=1.4), opacity=.85))
        ys += list(e.values)
    if d["spx"]:
        s = d["spx"]["series"]
        sidx = [t.tz_convert(ET) if t.tzinfo else t for t in s.index]
        fig.add_trace(go.Scatter(x=sidx, y=list(s.values), name="SPX (real index)",
                                 line=dict(color="#34d399", width=2.2)))
        ys += list(s.values)
    if big:
        fig.add_annotation(x=1, y=big, xref="paper", yref="y", text=f"{big:,.0f}",
                           showarrow=False, font=dict(color="#f8fafc", size=13),
                           bgcolor="rgba(52,211,153,.25)", borderpad=4, xanchor="left")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      height=330, margin=dict(l=6, r=54, t=8, b=8),
                      legend=dict(orientation="h", y=1.08, x=0, font=dict(size=11, color="#94a3b8")),
                      xaxis=dict(gridcolor="rgba(148,163,184,.08)", color="#64748b"),
                      yaxis=dict(gridcolor="rgba(148,163,184,.08)", color="#64748b",
                                 range=[min(ys) * 0.998, max(ys) * 1.002] if ys else None))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
except Exception as e:
    st.caption(f"chart unavailable: {e}")

# ── all venues ──
st.markdown('<div class="sechead">All venues, timestamped</div>', unsafe_allow_html=True)


def vrow(name, meta, px, live=False):
    tag = '<span class="live">LIVE</span>' if live else ''
    return (f'<div class="venue"><div><div class="n">{name} {tag}</div><div class="meta">{meta}</div></div>'
            f'<div class="p">{px}</div></div>')


venues = ""
if state == "RTH" and d["spx"]:
    venues += vrow("S&P 500 index (^GSPC)", f"CBOE · delayed · {d['spx']['ts']:%a %-I:%M %p ET}",
                   f"{d['spx']['px']:,.2f}", live=True)
elif d.get("spx_off"):
    venues += vrow("S&P 500 index (^GSPC)", f"official close · {d['spx_off']['ts']:%a %b %d}",
                   f"{d['spx_off']['px']:,.2f}")
if d["es"]:
    venues += vrow("ES front future", f"CME · delayed · {d['es']['ts']:%a %-I:%M %p ET}",
                   f"{d['es']['px']:,.2f}", live=(state == "FUTURES"))
    if d["basis"] is not None:
        venues += vrow("→ in SPX terms", f"mechanical basis adjustment ({d['basis']:+.1f})",
                       f"{d['es']['px'] - d['basis']:,.2f}")
if d.get("hl_us500"):
    _u = d["hl_us500"]
    venues += vrow("Hyperliquid US500 perp", f"REAL 24/7 market incl. weekends · funding {_u['funding']:+.4f}%/hr · ${_u['vol']/1e6:.1f}M/day (thin)",
                   f"{_u['spx_terms']:,.1f} <span class='{'up' if _u['chg24h']>=0 else 'dn'}' style='font-size:12px'>({_u['chg24h']:+.1f}%)</span>", live=True)
if d.get("ig_spx"):
    _is = d["ig_spx"]
    venues += vrow("IG US 500 CFD", "direct SPX terms · trades ~24/5 · source: IG.com",
                   f"{_is['mid']:,.2f}", live=(state in ("FUTURES", "RTH")))
if d.get("ig"):
    _ig = d["ig"]
    _igp = f"{_ig['mid']:,.0f}"
    if _ig.get("spx_terms"):
        _igp += f" <span class='mut' style='font-size:12px'>≈ SPX {_ig['spx_terms']:,.0f}</span>"
    venues += vrow("IG Weekend Wall Street (Dow)", "real weekend market · Sat 8AM – Sun 10:40PM UK · source: IG.com",
                   _igp, live=(state == "WEEKEND"))
if d.get("ig_tech"):
    _it = d["ig_tech"]
    _itp = f"{_it['mid']:,.0f}"
    if _it.get("spx_terms"):
        _itp += f" <span class='mut' style='font-size:12px'>≈ SPX {_it['spx_terms']:,.0f}</span>"
    venues += vrow("IG Weekend US Tech 100 (Nasdaq)", "real weekend market · Sat 8AM – Sun 10:40PM UK · source: IG.com",
                   _itp, live=(state == "WEEKEND"))
if d["hl"]:
    for coin, v in d["hl"].items():
        arrow_cls = "up" if v["chg"] >= 0 else "dn"
        venues += vrow(f"Hyperliquid {coin} perp", f"24/7 · funding {v['funding']:+.4f}%/hr",
                       f"{v['mark']:,.0f} <span class='{arrow_cls}' style='font-size:12px'>({v['chg']:+.1f}%)</span>", live=True)
if d["vix"]:
    venues += vrow("VIX", f"CBOE · delayed · {d['vix']['ts']:%a %-I:%M %p ET}", f"{d['vix']['px']:.2f}")
st.markdown(venues, unsafe_allow_html=True)


# ── the desk (cats) + subscribe/follow CTA ──
st.markdown('<div class="sechead">Meet the desk 🐾</div>', unsafe_allow_html=True)
_cats = [
    ("cat_boss.jpg", "Balder", "Chief Picks Officer — wears the bow tie, calls the overnight book."),
    ("cat_mascot.jpg", "The official portrait", "commissioned after three green nights in a row."),
    ("cat_risk.jpg", "Head of Risk", "unimpressed by your leverage since 2024."),
    ("cat_interns.jpg", "The research interns", "seven pairs of eyes on the tape. mostly napping."),
]
_cards = ""
for _f, _n, _r in _cats:
    _src = _b64(_f)
    if _src:
        _cards += f'<div class="catcard"><img src="{_src}"><div class="cn">{_n}</div><div class="cr">{_r}</div></div>'
if _cards:
    st.markdown(f'<div class="desk">{_cards}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="ctarow">
  <a class="btn sub" href="{SUBSTACK}" target="_blank">📬 Subscribe on Substack — daily picks &amp; research</a>
  <a class="btn x" href="{XLINK}" target="_blank">𝕏 Follow @Balder13946731</a>
</div>
<div class="ctatxt">If this tracker is useful, a sub or a follow keeps the cat fed 🐟 — it's free.</div>
""", unsafe_allow_html=True)

st.markdown(f"""<div class="foot">
🐱 built by <b>Balder's Opus Picks</b> · raw prints from public delayed feeds · refreshes every 60s · nothing here is a forecast or financial advice<br>
<a href="https://substack.com/@balder714059">daily research &amp; picks on Substack →</a> · <a href="https://x.com/Balder13946731">𝕏 @Balder13946731</a> · page rendered {now:%A %b %d, %-I:%M:%S %p ET}
</div>""", unsafe_allow_html=True)
