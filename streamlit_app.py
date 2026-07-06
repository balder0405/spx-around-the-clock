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
    basis = None
    try:
        if out["spx"] and out["es"]:
            j = pd.concat([out["spx"]["series"], out["es"]["series"]], axis=1, keys=["spx", "es"]).dropna()
            if len(j) > 10:
                basis = float((j["es"] - j["spx"]).median())
    except Exception:
        pass
    out["basis"] = basis
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

_logo = _b64("cat_boss.jpg")
_logo_html = f'<img class="hlogo" src="{_logo}">' if _logo else "🌐"
st.markdown(f"""
<div class="hero">
  <div class="title">{_logo_html} SPX <span class="accent">Around the Clock</span></div>
  <div class="sub">what S&amp;P risk is trading at right now, from whichever venue is awake · no forecasts, only prints</div>
  <div class="statuspill" style="background:{scol}22; color:{scol}; border:1px solid {scol}55;">{state_txt}</div>
</div>""", unsafe_allow_html=True)

# ── the headline number ──
if state == "RTH" and d["spx"]:
    big, lbl, src = d["spx"]["px"], "S&P 500 · LIVE INDEX", f"^GSPC · {d['spx']['ts']:%-I:%M %p ET}"
elif d["es"] and d["basis"] is not None and state == "FUTURES":
    big = d["es"]["px"] - d["basis"]
    lbl, src = "ES-IMPLIED SPX", f"CME ES {d['es']['px']:,.2f} − basis {d['basis']:+.1f} · {d['es']['ts']:%a %-I:%M %p ET}"
else:
    big = d["spx"]["px"] if d["spx"] else 0
    lbl = "LAST REAL SPX CLOSE"
    src = "nothing SPX-equivalent trades right now" + (f" · closed {d['spx']['ts']:%a %-I:%M %p ET}" if d["spx"] else "")
st.markdown(f"""
<div class="bigpx">
  <div class="lbl">{lbl}</div>
  <div class="num">{big:,.0f}</div>
  <div class="src">{src} · next NYSE open in {next_open(now)}</div>
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
if d["hl"]:
    for coin in ("BTC", "ETH"):
        if coin in d["hl"]:
            v = d["hl"][coin]
            cards += f'<div class="card"><div class="k">{coin} · 24/7</div><div class="v">{v["mark"]:,.0f}</div><div class="d {"up" if v["chg"]>=0 else "dn"}">{v["chg"]:+.1f}% / 24h</div></div>'
st.markdown(f'<div class="cardrow">{cards}</div>', unsafe_allow_html=True)

if state == "WEEKEND":
    st.markdown('<div class="note">◐ <b>Weekend honesty note:</b> crypto is the only live tape right now. It correlates with Monday\'s equity open, but it is <b>not</b> an S&amp;P price — we show it as context and refuse to fake an "SPX quote" from it.</div>', unsafe_allow_html=True)

# ── chart ──
st.markdown('<div class="sechead">The last week, stitched from whoever was open</div>', unsafe_allow_html=True)
try:
    import plotly.graph_objects as go
    fig = go.Figure()
    ys = []
    if d["es"] and d["basis"] is not None:
        e = d["es"]["series"] - d["basis"]
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
if d["spx"]:
    venues += vrow("S&P 500 index (^GSPC)", f"CBOE · delayed · {d['spx']['ts']:%a %-I:%M %p ET}",
                   f"{d['spx']['px']:,.2f}", live=(state == "RTH"))
if d["es"]:
    venues += vrow("ES front future", f"CME · delayed · {d['es']['ts']:%a %-I:%M %p ET}",
                   f"{d['es']['px']:,.2f}", live=(state == "FUTURES"))
    if d["basis"] is not None:
        venues += vrow("→ in SPX terms", f"mechanical basis adjustment ({d['basis']:+.1f})",
                       f"{d['es']['px'] - d['basis']:,.2f}")
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
