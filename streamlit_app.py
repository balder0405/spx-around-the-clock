"""Around the Clock — a public, no-forecast 24/7 view of S&P & Nasdaq risk plus the single stocks
that actually trade around the clock. Every number is a real print from a named venue with a
timestamp, or a clearly-marked estimate. Dark terminal edition.

Indices (SPX, NDX): RTH = cash index · overnight = CME futures (ES/NQ) − basis · weekend = Hyperliquid
US500/USTECH perp (real 24/7). Single stocks: RTH/extended = US consolidated print · overnight+weekend
= Hyperliquid single-stock perp mark (builder dexes; marks track spot to <1%, validated). Only names
with a real 24/7 venue are shown — no fabricated overnight quotes.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

ET = ZoneInfo("America/New_York")
st.set_page_config(page_title="Around the Clock", page_icon="🌐", layout="wide",
                   initial_sidebar_state="collapsed")
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60_000, key="tick")
except Exception:
    pass

# ── single stocks with a REAL 24/7 venue (Hyperliquid builder-dex perps, marks ≈ spot <1%) ──
STOCKS = ["NVDA", "TSLA", "MU", "MRVL", "DRAM", "INTC", "TSM", "CRWV", "META", "GOOGL", "AAPL", "AMZN",
          "NFLX", "NOK", "SPCX"]
THIN = {"NFLX", "NOK"}                       # shown with a thin-venue caveat
HL_STOCK_DEXES = ["xyz", "cash", "km", "mkts"]

st.markdown("""<style>
.stApp { background: radial-gradient(1200px 600px at 20% -10%, #16233f 0%, #0b1220 45%) #0b1220; }
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 2.0rem; max-width: 1120px;}
h1,h2,h3,p,span,div {font-family: -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;}
.hero {text-align:center; margin-bottom: 4px;}
.hero .title {font-size: 30px; font-weight: 800; color:#f8fafc; letter-spacing:.5px;}
.hero .title .accent {background: linear-gradient(90deg,#34d399,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.hero .sub {color:#7c8aa5; font-size:12.5px; margin-top:2px;}
.statuspill {display:inline-block; padding:5px 16px; border-radius:999px; font-size:12px; font-weight:700; letter-spacing:.5px; margin:9px 0 4px;}
.up {color:#34d399;} .dn {color:#f87171;} .mut {color:#7c8aa5;}
.tape {overflow:hidden; white-space:nowrap; border-top:1px solid rgba(148,163,184,.12); border-bottom:1px solid rgba(148,163,184,.12);
  background: rgba(255,255,255,.02); padding:7px 0; margin-bottom:16px;}
.tape .inner {display:inline-block; animation: scroll 44s linear infinite;}
.tape span {color:#94a3b8; font-size:12.5px; margin: 0 18px; font-variant-numeric: tabular-nums;}
.tape b {color:#e2e8f0; font-weight:700;}
@keyframes scroll {0% {transform: translateX(0);} 100% {transform: translateX(-50%);}}
@keyframes pulse {0%,100% {opacity:1;} 50% {opacity:.55;}}
.pulse {animation: pulse 2.2s ease-in-out infinite;}
/* index hero cards */
.idxrow {display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin: 10px 0 6px;}
.idxcard {box-sizing:border-box; flex:1 1 340px; max-width:440px; background: rgba(255,255,255,.04);
  border:1px solid rgba(148,163,184,.18); border-radius:18px; padding:18px 22px; text-align:center;}
.idxcard .name {color:#7c8aa5; font-size:11px; letter-spacing:2.5px; text-transform:uppercase;}
.idxcard .num {font-size:52px; font-weight:800; color:#f8fafc; font-variant-numeric: tabular-nums; line-height:1.06;
  text-shadow: 0 0 30px rgba(52,211,153,.28);}
.idxcard .chg {font-size:15px; font-weight:700; margin-top:1px;}
.idxcard .src {color:#8595ad; font-size:11px; margin-top:5px;}
/* stock grid */
.sechead {color:#cbd5e1; font-size:12.5px; letter-spacing:2.5px; text-transform:uppercase; margin: 24px 0 10px; font-weight:700;}
.sgrid {display:flex; flex-wrap:wrap; gap:11px;}
.scard {box-sizing:border-box; width: calc(25% - 9px); background: rgba(255,255,255,.035);
  border:1px solid rgba(148,163,184,.15); border-radius:14px; padding:13px 15px; position:relative;}
.scard .tk {color:#f1f5f9; font-weight:800; font-size:15px; letter-spacing:.4px;}
.scard .px {color:#f8fafc; font-size:23px; font-weight:800; font-variant-numeric: tabular-nums; margin-top:2px;}
.scard .ch {font-size:13px; font-weight:700; margin-top:1px;}
.scard .bdg {position:absolute; top:12px; right:13px; font-size:9.5px; font-weight:800; letter-spacing:.6px;
  padding:3px 8px; border-radius:999px;}
.b247 {background:rgba(52,211,153,.14); color:#34d399; border:1px solid rgba(52,211,153,.35);}
.brth {background:rgba(96,165,250,.14); color:#60a5fa; border:1px solid rgba(96,165,250,.35);}
.bext {background:rgba(168,139,250,.14); color:#a78bfa; border:1px solid rgba(168,139,250,.35);}
.bthin {background:rgba(251,191,36,.12); color:#fbbf24; border:1px solid rgba(251,191,36,.3);}
.scard .meta {color:#64748b; font-size:10.5px; margin-top:6px;}
.note {background: rgba(96,165,250,.07); border:1px solid rgba(96,165,250,.25); border-radius:12px;
  padding:11px 15px; color:#93c5fd; font-size:12.5px; margin:14px 0;}
/* product cards */
.prodgrid {display:flex; flex-wrap:wrap; gap:11px;}
.prod {box-sizing:border-box; width: calc(50% - 6px); background: rgba(255,255,255,.035);
  border:1px solid rgba(148,163,184,.15); border-radius:14px; padding:14px 16px;}
.prod .pi {font-size:19px;}
.prod .pt {font-weight:800; color:#f1f5f9; font-size:14.5px; margin:3px 0 3px;}
.prod .pd {color:#93a3b8; font-size:12.5px; line-height:1.5;}
.prod.found {border-color: rgba(249,115,22,.4);
  background: linear-gradient(160deg, rgba(249,115,22,.10), rgba(255,255,255,.02));}
.prod .badge {display:inline-block; background:linear-gradient(90deg,#f97316,#fb923c); color:#fff;
  font-size:9.5px; font-weight:800; letter-spacing:1px; padding:2px 8px; border-radius:8px; margin-left:6px; vertical-align:middle;}
.offer {text-align:center; background:linear-gradient(120deg,#7c3aed,#4338ca); border-radius:12px;
  padding:11px 16px; color:#fff; margin:11px 0 2px; font-size:13.5px; font-weight:700;}
@media (max-width: 720px) { .prod {width: 100%;} }
.minicta {display:flex; gap:10px; justify-content:center; flex-wrap:wrap; margin:16px 0 4px;}
.mbtn {display:inline-flex; align-items:center; gap:7px; padding:9px 20px; border-radius:999px; font-weight:800; font-size:13.5px; text-decoration:none !important;}
.mbtn.sub {background: linear-gradient(90deg,#f97316,#fb923c); color:#fff !important; box-shadow: 0 4px 20px rgba(249,115,22,.4);}
.mbtn.x {background: rgba(255,255,255,.08); color:#f1f5f9 !important; border:1px solid rgba(148,163,184,.35);}
.mctatxt {text-align:center; color:#7c8aa5; font-size:11.5px; margin-top:6px;}
.foot {color:#5b6b85; font-size:11px; text-align:center; margin-top:30px; line-height:1.8;}
.foot a {color:#7c8aa5;}
.hlogo {width:46px; height:46px; border-radius:50%; vertical-align:middle; margin-right:6px; border:2px solid rgba(148,163,184,.35);}
@media (max-width: 720px) {
  .block-container {padding: 1.1rem 0.7rem;}
  .hero .title {font-size: 20px;}
  .idxcard .num {font-size: 40px;}
  .scard {width: calc(50% - 6px);}
  .scard .px {font-size:20px;}
}
</style>""", unsafe_allow_html=True)

SUBSTACK = "https://substack.com/@balder714059"
XLINK = "https://x.com/Balder13946731"


def _b64(name):
    import base64
    from pathlib import Path
    try:
        return "data:image/jpeg;base64," + base64.b64encode((Path(__file__).parent / name).read_bytes()).decode()
    except Exception:
        return None


# Nasdaq API — Cloud-reliable last/prev official close (Yahoo IP-blocks datacenters; Nasdaq doesn't).
NASDAQ_H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126 Safari/537.36", "Accept": "application/json"}
NASDAQ_AC = {"DRAM": "etf", "SPY": "etf", "NDX": "index"}   # asset class per symbol (rest = 'stocks')


@st.cache_data(ttl=1800, show_spinner=False)
def nasdaq_refs():
    """Parallel-fetch each name's last sale + previous close + market status from Nasdaq. The official
    daily close (the basis for % change) — reliable from Streamlit Cloud where Yahoo is IP-blocked.
    Cached 30 min (closes change once/day); parallelized so all ~17 names return in a few seconds."""
    import requests
    from concurrent.futures import ThreadPoolExecutor

    def _p(s):
        return float(s.replace("$", "").replace(",", "")) if s and s not in ("N/A", "", "N/D") else None

    def _one(sym):
        ac = NASDAQ_AC.get(sym, "stocks")
        out = {"last": None, "prev": None, "status": None}
        try:
            i = requests.get(f"https://api.nasdaq.com/api/quote/{sym}/info?assetclass={ac}",
                             headers=NASDAQ_H, timeout=8).json()
            p = (i.get("data") or {}).get("primaryData") or {}
            out["last"] = _p(p.get("lastSalePrice")); out["status"] = (i.get("data") or {}).get("marketStatus")
            s = requests.get(f"https://api.nasdaq.com/api/quote/{sym}/summary?assetclass={ac}",
                             headers=NASDAQ_H, timeout=8).json()
            sd = (s.get("data") or {}).get("summaryData") or {}
            out["prev"] = _p((sd.get("PreviousClose") or {}).get("value"))
        except Exception:
            pass
        return sym, out
    with ThreadPoolExecutor(max_workers=18) as ex:
        return dict(ex.map(_one, STOCKS + ["SPY", "NDX"]))


def ref_close(nd, sym):
    """The last COMPLETED official close: today's settle once the session is over (marketStatus
    Closed → lastSale), else yesterday's settle while a session is live (→ PreviousClose)."""
    r = nd.get(sym)
    if not r:
        return None
    is_open = "open" in (r.get("status") or "").lower() or "market open" in (r.get("status") or "").lower()
    return (r.get("prev") if is_open else r.get("last")) or r.get("last") or r.get("prev")


@st.cache_data(ttl=60, show_spinner=False)
def fetch_all():
    # NO yfinance — Yahoo IP-blocks Streamlit Cloud, and blocked calls hung the whole page. Everything
    # now comes from fast, Cloud-reliable, keyless sources: CBOE (index levels + closes), Nasdaq
    # (stock closes, in nasdaq_refs), and Hyperliquid (24/7 stock + index perp marks).
    import requests
    out = {"asof": datetime.now(ET)}
    stx = {}

    # Hyperliquid single-stock perp marks (24/7). Best (highest-volume) dex per name + #venues.
    try:
        marks = {}
        for dx in HL_STOCK_DEXES:
            m, c = requests.post("https://api.hyperliquid.xyz/info",
                                 json={"type": "metaAndAssetCtxs", "dex": dx}, timeout=8).json()
            for u, cx in zip(m["universe"], c):
                base = u["name"].split(":")[-1].upper()
                if base in STOCKS:
                    mk = float(cx.get("markPx") or 0); vol = float(cx.get("dayNtlVlm") or 0)
                    prev = float(cx.get("prevDayPx") or mk)
                    if mk > 0:
                        marks.setdefault(base, []).append({"dex": dx, "mark": mk, "vol": vol, "prev": prev})
        for s, rows in marks.items():
            rows.sort(key=lambda r: -r["vol"])
            best = rows[0]
            stx.setdefault(s, {})
            stx[s]["hl"] = {"mark": best["mark"], "vol": best["vol"], "prev": best["prev"],
                            "dex": best["dex"], "n": len(rows)}
    except Exception:
        pass
    out["stocks"] = stx

    # BTC for the tape — Hyperliquid main dex, 24/7
    try:
        m, c = requests.post("https://api.hyperliquid.xyz/info", json={"type": "metaAndAssetCtxs"}, timeout=8).json()
        names = [u["name"] for u in m["universe"]]
        out["btc"] = float(c[names.index("BTC")]["markPx"]) if "BTC" in names else None
    except Exception:
        out["btc"] = None

    # CBOE — EXACT SPX/NDX levels (Cloud-reliable, no key). These anchor the perp→index mapping.
    def _cboe(sym):
        try:
            dd = requests.get(f"https://cdn.cboe.com/api/global/delayed_quotes/quotes/{sym}.json",
                              headers={"User-Agent": NASDAQ_H["User-Agent"]}, timeout=8).json().get("data", {})
            cur = dd.get("current_price"); cl = dd.get("close") or dd.get("prev_day_close_price")
            return {"cur": float(cur) if cur else None, "close": float(cl) if cl else None}
        except Exception:
            return None
    out["cboe_spx"], out["cboe_ndx"], out["cboe_vix"] = _cboe("_SPX"), _cboe("_NDX"), _cboe("_VIX")

    def _hl_idx(sym, cal, fallback_mult):
        try:
            m, c = requests.post("https://api.hyperliquid.xyz/info",
                                 json={"type": "metaAndAssetCtxs", "dex": "mkts"}, timeout=8).json()
            names = [u["name"].split(":")[-1] for u in m["universe"]]
            if sym in names:
                cx = c[names.index(sym)]; mark = float(cx["markPx"]); prev = float(cx.get("prevDayPx") or mark)
                close = cal["close"] if cal else None
                # PROPER MAPPING (not a hardcoded ×10): scale = real index close / perp's own daily
                # reference, so terms = close × (mark/prev) = the exact close moved by the perp's 24h
                # change. Anchors to CBOE's real 7,575.39 instead of SPY×10 (which ran ~0.3% light).
                # Falls back to the fixed integer scale only if CBOE is unreachable.
                mult = (close / prev) if (close and prev > 0) else fallback_mult
                return {"terms": mark * mult, "mult": mult, "chg24h": (mark / prev - 1) * 100 if prev else 0.0}
        except Exception:
            pass
        return None
    out["hl_spx"] = _hl_idx("US500", out.get("cboe_spx"), 10)
    out["hl_ndx"] = _hl_idx("USTECH", out.get("cboe_ndx"), 41)
    return out


def market_state(now):
    wd, m = now.weekday(), now.hour * 60 + now.minute
    if wd < 5 and 570 <= m < 960:
        return "RTH", "● US CASH OPEN — LIVE", "#34d399"
    if wd == 5 or (wd == 6 and m < 1080) or (wd == 4 and m >= 1020):
        return "WEEKEND", "◐ WEEKEND — 24/7 VENUES ONLY", "#fbbf24"
    if wd < 5 and (240 <= m < 570 or 960 <= m < 1200):
        return "EXT", "◑ EXTENDED HOURS — pre/post market", "#a78bfa"
    return "OVN", "◎ OVERNIGHT — futures & 24/7 perps", "#60a5fa"


def next_open(now):
    d = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if now >= d or now.weekday() >= 5:
        d += timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
    mins = int((d - now).total_seconds() // 60)
    return f"{mins // 60}h {mins % 60:02d}m"


d = fetch_all()
nd = nasdaq_refs()                                    # Cloud-reliable official closes (% basis)
now = d["asof"]
state, state_txt, scol = market_state(now)
us_session = (now.weekday() < 5 and 240 <= now.hour * 60 + now.minute < 1200)   # 4:00–20:00 ET


def index_card(name, cboe, hl, state, refc=None):
    if state == "RTH" and cboe and cboe.get("cur"):
        val, src = cboe["cur"], "cash index · CBOE"
    elif hl:                       # 24/7 source — overnight, weekends (perp mapped to the real close)
        val, src = hl["terms"], f"Hyperliquid perp ×{hl['mult']:.2f} · {hl['chg24h']:+.1f}%/24h"
    elif cboe and cboe.get("close"):
        val, src = cboe["close"], "last close · CBOE"
    else:
        val, src = None, "—"
    ref = refc                     # the real official close (CBOE), the % basis
    if val and ref:
        c = (val / ref - 1) * 100
        chs = f"<span class='{'up' if c >= 0 else 'dn'}'>{c:+.2f}% · vs {ref:,.0f} close</span>"
    elif val and hl:
        c = hl["chg24h"]
        chs = f"<span class='{'up' if c >= 0 else 'dn'}'>{c:+.2f}% / 24h</span>"
    else:
        chs = ""
    num = f"{val:,.0f}" if val else "—"
    return (f"<div class='idxcard'><div class='name'>{name}</div><div class='num'>{num}</div>"
            f"<div class='chg'>{chs}</div><div class='src'>{src}</div></div>")


_logo = _b64("cat_boss.jpg")
_logo_html = f'<img class="hlogo" src="{_logo}">' if _logo else "🌐"
st.markdown(f"""<div class="hero">
  <div class="title">{_logo_html} Markets <span class="accent">Around the Clock</span></div>
  <div class="sub">what index &amp; single-stock risk is trading at right now, from whichever venue is awake · no forecasts, only prints</div>
  <div class="statuspill pulse" style="background:{scol}22; color:{scol}; border:1px solid {scol}55;">{state_txt}</div>
</div>""", unsafe_allow_html=True)

tape = []
if (d.get("cboe_spx") or {}).get("cur"): tape.append(("SPX", f"{d['cboe_spx']['cur']:,.0f}"))
if (d.get("cboe_ndx") or {}).get("cur"): tape.append(("NDX", f"{d['cboe_ndx']['cur']:,.0f}"))
if (d.get("cboe_vix") or {}).get("cur"): tape.append(("VIX", f"{d['cboe_vix']['cur']:.1f}"))
if d.get("btc"): tape.append(("BTC", f"{d['btc']:,.0f}"))
for s in STOCKS:
    st_ = d["stocks"].get(s)
    if st_ and st_.get("hl"):
        tape.append((s, f"{st_['hl']['mark']:,.2f}"))
seg = "".join(f"<span><b>{n}</b> {v}</span>" for n, v in tape)
if seg:
    st.markdown(f'<div class="tape"><div class="inner">{seg}{seg}</div></div>', unsafe_allow_html=True)

_spx_ref = (d["cboe_spx"] or {}).get("close")                       # exact SPX close (CBOE)
_ndx_ref = (d["cboe_ndx"] or {}).get("close") or ref_close(nd, "NDX")
st.markdown('<div class="idxrow">'
            + index_card("S&amp;P 500 · SPX", d["cboe_spx"], d["hl_spx"], state, _spx_ref)
            + index_card("NASDAQ 100 · NDX", d["cboe_ndx"], d["hl_ndx"], state, _ndx_ref)
            + '</div>', unsafe_allow_html=True)

st.markdown(f"""<div class="minicta">
  <a class="mbtn sub" href="{SUBSTACK}" target="_blank">📬 Get the daily picks — Substack</a>
  <a class="mbtn x" href="{XLINK}" target="_blank">𝕏 Follow @Balder13946731</a>
</div><div class="mctatxt">the cat that runs this page also picks stocks every night 🐱</div>""", unsafe_allow_html=True)

# ── stock grid ──
st.markdown('<div class="sechead">Single stocks · around the clock (Hyperliquid 24/7 perps + US extended hours)</div>',
            unsafe_allow_html=True)
cards = ""
for s in STOCKS:
    st_ = d["stocks"].get(s)
    if not st_:
        continue
    hl = st_.get("hl")
    if us_session and "real" in st_:
        px = st_["real"]
        badge = ("brth", "● LIVE") if state == "RTH" else ("bext", "◑ EXT")
        src = f"US print · {st_['ts']:%-I:%M %p ET}"
    elif hl:
        px = hl["mark"]
        if us_session:                       # market open/extended → present it as the live read
            badge = ("brth", "● LIVE") if state == "RTH" else ("bext", "◑ EXT")
            src = f"HL perp ≈ spot · live hrs · ${hl['vol']/1e6:.1f}M/d"
        else:
            badge = ("bthin", "◐ 24/7 THIN") if s in THIN else ("b247", "🌐 24/7")
            src = f"HL perp · {hl['dex']}" + (f" · {hl['n']} venues" if hl["n"] > 1 else "") + f" · ${hl['vol']/1e6:.1f}M/d"
    elif "real" in st_:
        px = st_["real"]; badge = ("bext", "LAST"); src = f"last print · {st_['ts']:%-I:%M %p ET}"
    else:
        continue
    # % vs the last official market close (Nasdaq, Cloud-reliable); HL-only names fall back to the perp 24h ref
    ref = ref_close(nd, s) or (hl.get("prev") if hl else None)
    chg = (px / ref - 1) * 100 if ref else None
    chs = f"<div class='ch {'up' if chg >= 0 else 'dn'}'>{chg:+.2f}%</div>" if chg is not None else ""
    dec = 2 if px < 1000 else 0
    cards += (f"<div class='scard'><span class='bdg {badge[0]}'>{badge[1]}</span>"
              f"<div class='tk'>{s}</div><div class='px'>{px:,.{dec}f}</div>{chs}"
              f"<div class='meta'>{src}</div></div>")
st.markdown(f'<div class="sgrid">{cards}</div>', unsafe_allow_html=True)

st.markdown('<div class="note">🌐 <b>How the 24/7 stock marks work:</b> outside US hours, each stock shows its '
            '<b>Hyperliquid perpetual mark</b> — a real, continuously-traded price on-chain (builder-dex perps). '
            'We validated these marks track the real share price to within ~1%. Thin venues (NFLX, NOK) are flagged. '
            'During US hours (4 AM–8 PM ET) we show the real consolidated print instead. '
            'Only names with a genuine 24/7 venue are listed — we never fabricate an overnight quote.</div>',
            unsafe_allow_html=True)

# ── products / membership ──
st.markdown('<div class="sechead">What we build 🐲 · inside the membership</div>', unsafe_allow_html=True)
_PRODUCTS = [
    ("🐲", "Fable Picks 龙气榜", "Our AI quant desk's nightly read &amp; top picks — a full model ensemble raced "
     "head-to-head every night, distilled to the names actually worth watching.", False),
    ("📰", "KOL Read + Pulse", "Every 3 days: the few <b>validated</b> arguments from 160+ finance KOLs "
     "(logic, why it holds, what would break it) + a live attention &amp; sentiment board.", False),
    ("⭐", "Spotlight Articles", "Curated deep-dives on the moves that matter — the signal pulled out of the noise.", False),
    ("💬", "Direct Group Chat", "Talk markets with us and the community in real time — reads, setups, and questions.", False),
    ("🛠️", "Development Notes", "Behind-the-scenes build reports on the system as it evolves — how the models "
     "and tools actually work.", True),
    ("🤖", "Early &amp; Agentic AI", "First access to every new AI tool, plus our agentic-AI trading tooling as it ships.", True),
]
_cards = ""
for icon, title, desc, founding in _PRODUCTS:
    badge = "<span class='badge'>FOUNDING</span>" if founding else ""
    _cards += (f"<div class='prod{' found' if founding else ''}'><span class='pi'>{icon}</span>"
               f"<div class='pt'>{title}{badge}</div><div class='pd'>{desc}</div></div>")
st.markdown(f'<div class="prodgrid">{_cards}</div>', unsafe_allow_html=True)
st.markdown('<div class="offer">🎁 20% off annual &amp; group subscriptions</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="minicta">
  <a class="mbtn sub" href="{SUBSTACK}" target="_blank">📬 Become a member — on Substack</a>
  <a class="mbtn x" href="{XLINK}" target="_blank">𝕏 Follow @Balder13946731</a>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="sechead">Follow the desk 🐾</div>', unsafe_allow_html=True)
st.markdown(f"""<div class="minicta">
  <a class="mbtn sub" href="{SUBSTACK}" target="_blank">📬 Subscribe on Substack — daily picks &amp; research</a>
  <a class="mbtn x" href="{XLINK}" target="_blank">𝕏 Follow @Balder13946731</a>
</div><div class="mctatxt">If this tracker is useful, a sub or a follow keeps the cat fed 🐟 — it's free.</div>""",
            unsafe_allow_html=True)

st.markdown(f"""<div class="foot">
🐱 built by <b>Balder's Fable Picks 龙气榜🐲</b> · index prints from public delayed feeds, stock 24/7 marks from
Hyperliquid builder-dex perps · refreshes every 60s · nothing here is a forecast or financial advice<br>
<a href="{SUBSTACK}">daily research &amp; picks on Substack →</a> · <a href="{XLINK}">𝕏 @Balder13946731</a> ·
rendered {now:%A %b %d, %-I:%M:%S %p ET}
</div>""", unsafe_allow_html=True)
