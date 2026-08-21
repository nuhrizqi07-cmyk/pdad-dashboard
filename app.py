#!/usr/bin/env python3
"""Dashboard PDAD — DATA TERMINAL.
KPPBC Tipe Madya Pabean A Pasuruan · Analitik tiket CEISACare + scan solusi.
World: data terminal (monospace tabular, barcode bar-fields, sine dividers).
Data: data/tickets_clean.json + data/synth_results.json
"""
import html
import json
import os
import re

import pandas as pd
import streamlit as st

# ────────────────────────────────────────────────────────────────
# KONFIGURASI + KONTRAK ARAH (Data Terminal / seed 02dade84)
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDAD // TERMINAL",
    page_icon="▚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DIRECTION_CONTRACT = """<!--
THESIS: Dashboard PDAD is a data terminal, not a brochure. Every ticket is a signal frame, every SLA is an instrument reading, every search is a scan across the known solution space. It refuses the category default of rounded pastel cards on a white page.
OWN-WORLD: Near-black blue field (#0B0F14) with slate panels and hairline borders; one monospace face (JetBrains Mono) at data density with tabular numerals; barcode bar-fields and sine dividers as the only ornament; status ink in amber (watch), green (clear), red (critical), cyan (action).
STORY: The Duktek opens the terminal, scans the instrument row, types the kendala into the scan line, and receives solution frames with numbered handling steps — answers in seconds, not minutes.
FIRST VIEWPORT: Terminal header bar with system readout (dataset, window, frame count). Instrument row: four KPI readouts with uppercase labels and large tabular values. Below: the SCAN line (search) as the hero — a wide input with a blinking caret affordance and a live match counter, then solution frames as result cards and signal traces as a table.
FORM: Data terminal (ikeda-datamatics challenger, seed 02dade84).
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
-->
"""
st.markdown(DIRECTION_CONTRACT, unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ────────────────────────────────────────────────────────────────
# CSS — DATA TERMINAL WORLD
# ────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,700;0,800;1,400&display=swap');

:root {
  --dt-bg: #0B0F14;
  --dt-panel: #121A22;
  --dt-panel2: #0F151C;
  --dt-line: #1F2A36;
  --dt-ink: #E8EEF5;
  --dt-ink-dim: #8FA3B8;
  --dt-amber: #FFB454;
  --dt-green: #4ADE80;
  --dt-red: #F87171;
  --dt-cyan: #22D3EE;
  --dt-violet: #A78BFA;
}

html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--dt-bg) !important;
  color: var(--dt-ink) !important;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
}
[data-testid="stAppViewContainer"] { background: var(--dt-bg) !important; }

/* angka tabular di semua angka */
.stApp * { font-feature-settings: "tnum" 1, "zero" 1; }

/* sidebar = panel gelap */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background: var(--dt-panel2) !important;
  border-right: 1px solid var(--dt-line) !important;
}
[data-testid="stSidebar"] * { color: var(--dt-ink) !important; }

/* text input = scan line */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input {
  background: var(--dt-panel) !important;
  color: var(--dt-ink) !important;
  border: 1px solid var(--dt-line) !important;
  border-radius: 0 !important;
  font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--dt-cyan) !important;
  box-shadow: 0 0 0 1px var(--dt-cyan) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #4A5B6D !important; }

/* selectbox & multiselect */
[data-baseweb="select"] > div {
  background: var(--dt-panel) !important;
  border-color: var(--dt-line) !important;
  border-radius: 0 !important;
  color: var(--dt-ink) !important;
}

/* button = terminal action */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
  background: var(--dt-panel) !important;
  color: var(--dt-cyan) !important;
  border: 1px solid var(--dt-cyan) !important;
  border-radius: 0 !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
  background: var(--dt-cyan) !important;
  color: var(--dt-bg) !important;
  border-color: var(--dt-cyan) !important;
}

/* radio nav */
[data-testid="stSidebar"] [role="radiogroup"] label {
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 0.05em;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { color: var(--dt-cyan) !important; }

/* dataframe = signal trace table */
[data-testid="stDataFrame"] {
  border: 1px solid var(--dt-line) !important;
  border-radius: 0 !important;
}
[data-testid="stDataFrame"] * { font-family: 'JetBrains Mono', monospace !important; }

/* markdown headings */
h1, h2, h3, h4 { color: var(--dt-ink) !important; letter-spacing: -0.01em; }
h1 { font-weight: 800; }
h2, h3 { font-weight: 700; }

/* tabs */
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--dt-ink-dim) !important;
  border-radius: 0 !important;
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: 0.05em;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--dt-cyan) !important;
  border-bottom: 2px solid var(--dt-cyan) !important;
}

/* tooltip / caption */
[data-testid="stCaptionContainer"], .stCaption { color: var(--dt-ink-dim) !important; }

/* header terminal bar */
.dt-header {
  display: flex; align-items: center; justify-content: space-between;
  border: 1px solid var(--dt-line); border-radius: 0;
  background: var(--dt-panel); padding: 10px 16px; margin-bottom: 20px;
}
.dt-header .brand { font-weight: 800; font-size: 1.05rem; color: var(--dt-ink); letter-spacing: 0.1em; }
.dt-header .brand .cyan { color: var(--dt-cyan); }
.dt-header .readout { color: var(--dt-ink-dim); font-size: 0.72rem; letter-spacing: 0.06em; }
.dt-header .readout .ok { color: var(--dt-green); }
.dt-header .readout .warn { color: var(--dt-amber); }

/* barcode bar-field */
.dt-barcode {
  height: 26px; margin: 4px 0 18px 0;
  background: repeating-linear-gradient(90deg,
    var(--dt-ink) 0 2px, transparent 2px 5px,
    var(--dt-ink) 5px 6px, transparent 6px 11px,
    var(--dt-ink) 11px 14px, transparent 14px 18px,
    var(--dt-ink-dim) 18px 19px, transparent 19px 23px);
  opacity: 0.55;
}

/* sine divider */
.dt-sine {
  margin: 26px 0; opacity: 0.35;
}

/* KPI instrument readout */
.dt-kpi {
  background: var(--dt-panel); border: 1px solid var(--dt-line); border-radius: 0;
  padding: 14px 16px; margin-bottom: 10px; position: relative;
  overflow: hidden;
}
.dt-kpi .label { font-size: 0.68rem; color: var(--dt-ink-dim); letter-spacing: 0.14em; text-transform: uppercase; }
.dt-kpi .value { font-size: 1.9rem; font-weight: 800; color: var(--dt-ink); line-height: 1.15; font-variant-numeric: tabular-nums; }
.dt-kpi .value.amber { color: var(--dt-amber); }
.dt-kpi .value.green { color: var(--dt-green); }
.dt-kpi .value.red { color: var(--dt-red); }
.dt-kpi .value.cyan { color: var(--dt-cyan); }
.dt-kpi .sub { font-size: 0.66rem; color: var(--dt-ink-dim); margin-top: 2px; }
.dt-kpi .bar { position: absolute; right: 0; top: 0; bottom: 0; width: 6px; }
.dt-kpi .bar.amber { background: var(--dt-amber); }
.dt-kpi .bar.green { background: var(--dt-green); }
.dt-kpi .bar.red { background: var(--dt-red); }
.dt-kpi .bar.cyan { background: var(--dt-cyan); }

/* solution frame card — terminal corner brackets, no side tab */
.dt-frame {
  border: 1px solid var(--dt-line);
  background: var(--dt-panel); padding: 14px 18px; margin: 10px 0; border-radius: 0;
  position: relative;
}
.dt-frame::before, .dt-frame::after {
  content: ""; position: absolute; width: 10px; height: 10px;
  border-color: var(--dt-cyan); border-style: solid;
}
.dt-frame::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.dt-frame::after { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }
.dt-frame .f-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
.dt-frame .f-title { font-weight: 700; font-size: 0.95rem; color: var(--dt-ink); }
.dt-frame .f-count { font-size: 0.7rem; color: var(--dt-amber); letter-spacing: 0.08em; white-space: nowrap; }
.dt-frame .f-domain { font-size: 0.66rem; color: var(--dt-cyan); letter-spacing: 0.12em; text-transform: uppercase; margin: 2px 0 8px 0; }
.dt-frame .f-summary { color: var(--dt-ink-dim); font-size: 0.82rem; line-height: 1.5; margin-bottom: 10px; }
.dt-frame ol { margin: 0 0 0 18px; padding: 0; }
.dt-frame ol li { color: var(--dt-ink); font-size: 0.82rem; line-height: 1.55; margin-bottom: 4px; }
.dt-frame .f-note { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--dt-line); color: var(--dt-amber); font-size: 0.76rem; }

/* empty state */
.dt-empty {
  border: 1px dashed var(--dt-line); color: var(--dt-ink-dim);
  padding: 26px; text-align: center; font-size: 0.85rem; letter-spacing: 0.05em;
}

/* section label */
.dt-section {
  font-size: 0.72rem; color: var(--dt-cyan); letter-spacing: 0.16em;
  text-transform: uppercase; margin: 22px 0 10px 0; font-weight: 700;
}

/* metric-ish plain text cleanup */
[data-testid="stMetric"] { background: var(--dt-panel); border: 1px solid var(--dt-line); border-radius: 0; padding: 12px; }
[data-testid="stMetricLabel"] { color: var(--dt-ink-dim) !important; }
[data-testid="stMetricValue"] { color: var(--dt-ink) !important; }

/* info/warning boxes flattened */
[data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stError"], [data-testid="stSuccess"] {
  background: var(--dt-panel) !important; border: 1px solid var(--dt-line) !important;
  border-radius: 0 !important; color: var(--dt-ink) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────
# LOAD DATA (cached)
# ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_tickets():
    with open(os.path.join(DATA_DIR, "tickets_clean.json")) as f:
        rows = json.load(f)
    df = pd.DataFrame(rows)
    df["tanggal_dt"] = pd.to_datetime(df["tanggal_dt"], errors="coerce")
    df["submit_time"] = pd.to_datetime(df["submit_time"], errors="coerce")
    df["resolve_time"] = pd.to_datetime(df["resolve_time"], errors="coerce")
    df["bulan"] = df["tanggal_dt"].dt.to_period("M").astype(str)
    df["probis"] = df["probis"].fillna("-").replace("", "-")
    df["uraian"] = df["uraian"].fillna("-")
    return df


@st.cache_data(ttl=3600)
def load_synth():
    with open(os.path.join(DATA_DIR, "synth_results.json")) as f:
        return json.load(f)


df = load_tickets()
synth = load_synth()

# ────────────────────────────────────────────────────────────────
# HELPER RENDER
# ────────────────────────────────────────────────────────────────
def esc(s):
    return html.escape(str(s))


def header_bar():
    n = len(df)
    mn = df["tanggal_dt"].min().strftime("%y.%m.%d") if df["tanggal_dt"].notna().any() else "--"
    mx = df["tanggal_dt"].max().strftime("%y.%m.%d") if df["tanggal_dt"].notna().any() else "--"
    h = f"""
    <div class="dt-header">
      <div class="brand"><span class="cyan">PDAD</span>://TERMINAL <span style="color:#4A5B6D">v2.0</span></div>
      <div class="readout">
        FRAMES <span class="ok">{n:,}</span> · WINDOW <span class="warn">{mn}→{mx}</span> · MODE OPERATE · SIG <span class="ok">ONLINE</span>
      </div>
    </div>
    """
    st.markdown(h, unsafe_allow_html=True)


def barcode():
    st.markdown('<div class="dt-barcode"></div>', unsafe_allow_html=True)


def sine_divider():
    svg = """
    <svg class="dt-sine" viewBox="0 0 1200 24" width="100%" height="24" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 12 Q 30 0 60 12 T 120 12 T 180 12 T 240 12 T 300 12 T 360 12 T 420 12 T 480 12 T 540 12 T 600 12 T 660 12 T 720 12 T 780 12 T 840 12 T 900 12 T 960 12 T 1020 12 T 1080 12 T 1140 12 T 1200 12"
        fill="none" stroke="#22D3EE" stroke-width="1.2" opacity="0.5"/>
      <path d="M0 12 Q 30 24 60 12 T 120 12 T 180 12 T 240 12 T 300 12 T 360 12 T 420 12 T 480 12 T 540 12 T 600 12 T 660 12 T 720 12 T 780 12 T 840 12 T 900 12 T 960 12 T 1020 12 T 1080 12 T 1140 12 T 1200 12"
        fill="none" stroke="#4A5B6D" stroke-width="0.8" opacity="0.5"/>
    </svg>
    """
    st.markdown(svg, unsafe_allow_html=True)


def kpi_card(label, value, sub="", tone=""):
    st.markdown(
        f"""
        <div class="dt-kpi">
          <div class="label">{esc(label)}</div>
          <div class="value {tone}">{esc(value)}</div>
          <div class="sub">{esc(sub)}</div>
          <div class="bar {tone if tone else 'cyan'}"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(f'<div class="dt-section">▸ {esc(text)}</div>', unsafe_allow_html=True)


def empty_state(text):
    st.markdown(f'<div class="dt-empty">■ {esc(text)}</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────
# SIDEBAR — NAV + FILTER GLOBAL
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-weight:800;letter-spacing:0.12em;color:#22D3EE;">PDAD::NAV</div>', unsafe_allow_html=True)
    page = st.radio(
        "NAVIGASI",
        ["▚ SCAN SOLUSI", "▤ RINGKASAN", "⏱ SLA & KINERJA", "▦ EKSPLORASI"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown('<div style="font-size:0.72rem;letter-spacing:0.14em;color:#8FA3B8;">// FILTER GLOBAL</div>', unsafe_allow_html=True)

    min_date = df["tanggal_dt"].min()
    max_date = df["tanggal_dt"].max()
    date_range = st.date_input(
        "RENTANG", value=(min_date, max_date), min_value=min_date, max_value=max_date,
        label_visibility="collapsed",
    )
    katalog_list = sorted(df["katalog"].dropna().unique())
    sel_katalog = st.multiselect("KATEGORI", katalog_list, default=[], label_visibility="collapsed",
                                 placeholder="kategori…")
    duktek_list = sorted(df["duktek"].dropna().unique())
    sel_duktek = st.multiselect("DUKTEK", duktek_list, default=[], label_visibility="collapsed",
                                placeholder="duktek…")

    mask = pd.Series(True, index=df.index)
    if len(date_range) == 2:
        start, end = date_range
        mask &= (df["tanggal_dt"] >= pd.Timestamp(start)) & (df["tanggal_dt"] <= pd.Timestamp(end))
    if sel_katalog:
        mask &= df["katalog"].isin(sel_katalog)
    if sel_duktek:
        mask &= df["duktek"].isin(sel_duktek)
    fdf = df[mask]

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:0.68rem;color:#4A5B6D;">FRAMES {len(fdf):,} / {len(df):,} · TTL 3600s</div>',
        unsafe_allow_html=True,
    )

header_bar()

# ────────────────────────────────────────────────────────────────
# HALAMAN: SCAN SOLUSI (HERO — default)
# ────────────────────────────────────────────────────────────────
if page == "▚ SCAN SOLUSI":
    st.markdown('<div style="font-size:0.72rem;letter-spacing:0.2em;color:#22D3EE;">SCAN LINE // Cari kendala → solusi</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="margin-top:2px;font-size:1.7rem;">SCAN <span style="color:#FFB454;">SOLUSI</span></h1>', unsafe_allow_html=True)
    st.caption("Ketik kendala (mis. CK-5 stuck, login MFA, PIB reject) — terminal mencari panduan penanganan di 65 solution frames + riwayat tiket.")

    # instrument row (FIRST VIEWPORT: KPI readouts di atas scan line)
    _total = len(fdf)
    _kat = fdf["katalog"].nunique()
    _masalah = fdf["masalah"].nunique()
    _sla = fdf["sla_hours"].dropna()
    _med = _sla.median() if len(_sla) else 0
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1:
        kpi_card("FRAMES", f"{_total:,}", sub="tiket dalam filter", tone="cyan")
    with ck2:
        kpi_card("KATEGORI", str(_kat), sub="katalog", tone="")
    with ck3:
        kpi_card("MASALAH", str(_masalah), sub="jenis unik", tone="amber")
    with ck4:
        kpi_card("MEDIAN SLA", f"{_med:.1f} jam", sub="resolve", tone="green")
    barcode()

    # tombol contoh mengisi widget scan via session_state
    if st.session_state.pop("scan_fill", None):
        st.session_state["scan_input"] = st.session_state["scan_fill"]

    query = st.text_input(
        "SCAN", placeholder="SCAN █  cth: PIB stuck validasi / MFA looping / CK-5…",
        label_visibility="collapsed", key="scan_input",
    )

    if query.strip():
        q = query.lower()
        tokens = [t for t in re.split(r"\W+", q) if len(t) > 2]

        # --- scan di synth_results (65 panduan) ---
        results = []
        for key, d in synth.items():
            domain = d.get("domain", "")
            hay = (d.get("masalah", "") + " " + d.get("ringkasan", "") + " " +
                   " ".join(d.get("langkah", [])) + " " + d.get("catatan", "")).lower()
            score = 0
            if q in hay:
                score += 10
            for tok in tokens:
                if tok in hay:
                    score += 1
            if score > 0:
                results.append((score, key, d))

        results.sort(key=lambda x: -x[0])
        barcode()
        st.markdown(
            f'<div class="dt-section">▸ {len(results)} SOLUTION FRAME(S) COCOK · SCORE>0</div>',
            unsafe_allow_html=True,
        )

        if results:
            for score, key, d in results[:8]:
                domain = d.get("domain", "")
                cnt = d.get("jumlah", "?")
                title = d.get("masalah", key)
                head = f"""
                <div class="dt-frame">
                  <div class="f-head">
                    <span class="f-title">{esc(title)}</span>
                    <span class="f-count">▮ {esc(cnt)} tiket</span>
                  </div>
                  <div class="f-domain">{esc(domain)}</div>
                """
                body = ""
                if d.get("ringkasan"):
                    body += f'<div class="f-summary">{esc(d["ringkasan"])}</div>'
                if d.get("langkah"):
                    body += "<ol>"
                    for i, s in enumerate(d["langkah"], 1):
                        body += f"<li>{esc(s)}</li>"
                    body += "</ol>"
                if d.get("catatan"):
                    body += f'<div class="f-note">◆ {esc(d["catatan"])}</div>'
                st.markdown(head + body + "</div>", unsafe_allow_html=True)
        else:
            empty_state("TIDAK ADA FRAME COCOK — coba kata kunci lain, atau cek tiket terkait di bawah.")

        # --- scan tiket mentah ---
        section_label("SIGNAL TRACES // tiket terkait")
        if tokens:
            def ticket_score(row):
                hay = f"{row['masalah'] or ''} {row['katalog'] or ''} {row['uraian'] or ''}".lower()
                s = 0
                if q in hay:
                    s += 5
                for tok in tokens:
                    if tok in hay:
                        s += 1
                return s

            fdf2 = fdf.copy()
            fdf2["_score"] = fdf2.apply(ticket_score, axis=1)
            top = fdf2[fdf2["_score"] > 0].sort_values("_score", ascending=False).head(15)
            if len(top):
                st.dataframe(
                    top[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "duktek", "sla_hours"]]
                    .rename(columns={"sla_hours": "sla_jam"}),
                    width="stretch", hide_index=True,
                )
            else:
                empty_state("TIDAK ADA TIKET TERKAIT")
    else:
        barcode()
        st.markdown(
            """
            <div class="dt-frame" style="border-left-color:#4A5B6D;">
              <div class="f-title" style="color:#8FA3B8;">TUNGGU INPUT…</div>
              <div class="f-summary">Contoh scan yang sering dilakukan Duktek:</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ex = ["PIB reject validasi", "MFA looping login", "CK-5 stuck", "tidak bisa akses aplikasi", "perubahan data"]
        cols = st.columns(len(ex))
        for c, e in zip(cols, ex):
            with c:
                if st.button(f"› {e}", key=f"ex_{e}"):
                    st.session_state["scan_fill"] = e
                    st.rerun()

    sine_divider()
    st.markdown('<div style="font-size:0.66rem;color:#4A5B6D;">SCAN ENGINE: fuzzy-token · 65 frames · 3.807 signals</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# HALAMAN: RINGKASAN
# ────────────────────────────────────────────────────────────────
elif page == "▤ RINGKASAN":
    st.markdown('<h1 style="font-size:1.7rem;">▤ RINGKASAN <span style="color:#4A5B6D;">// signal summary</span></h1>', unsafe_allow_html=True)
    barcode()

    total = len(fdf)
    total_kat = fdf["katalog"].nunique()
    total_masalah = fdf["masalah"].nunique()
    with_sla = fdf["sla_hours"].dropna()
    med_sla = with_sla.median() if len(with_sla) else 0
    pct24 = (with_sla <= 24).mean() * 100 if len(with_sla) else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("TOTAL FRAMES", f"{total:,}", sub="tiket dalam filter", tone="cyan")
    with c2:
        kpi_card("KATEGORI", str(total_kat), sub="katalog", tone="")
    with c3:
        kpi_card("JENIS MASALAH", str(total_masalah), sub="masalah unik", tone="amber")
    with c4:
        kpi_card("MEDIAN SLA", f"{med_sla:.1f} jam", sub=f"≤24 jam: {pct24:.0f}%", tone="green")

    sine_divider()
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_label("TREN TIKET PER BULAN")
        tren = fdf.groupby("bulan").size().reset_index(name="jumlah")
        st.line_chart(tren, x="bulan", y="jumlah", height=300)

        section_label("DISTRIBUSI PER KATEGORI")
        kat = fdf["katalog"].value_counts().reset_index()
        kat.columns = ["kategori", "jumlah"]
        st.bar_chart(kat.set_index("kategori"), height=260)

    with col_right:
        section_label("TOP MASALAH")
        top_masalah = fdf["masalah"].value_counts().head(12)
        st.dataframe(top_masalah.rename("jumlah"), width="stretch", height=320, hide_index=False)

        section_label("TOP PELAPOR")
        top_perusahaan = fdf["pelapor"].value_counts().head(10)
        st.dataframe(top_perusahaan.rename("tiket"), width="stretch", height=280, hide_index=False)

# ────────────────────────────────────────────────────────────────
# HALAMAN: SLA & KINERJA
# ────────────────────────────────────────────────────────────────
elif page == "⏱ SLA & KINERJA":
    st.markdown('<h1 style="font-size:1.7rem;">⏱ SLA & KINERJA <span style="color:#4A5B6D;">// resolve instrument</span></h1>', unsafe_allow_html=True)
    barcode()

    sla = fdf[fdf["sla_hours"].notna()].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("MEDIAN SLA", f"{sla['sla_hours'].median():.1f} jam", tone="amber")
    with c2:
        kpi_card("RATA-RATA", f"{sla['sla_hours'].mean():.1f} jam", tone="")
    with c3:
        pct_24 = (sla["sla_hours"] <= 24).mean() * 100
        kpi_card("SELESAI ≤24J", f"{pct_24:.0f}%", tone="green")
    with c4:
        pct_1 = (sla["sla_hours"] <= 1).mean() * 100
        kpi_card("SELESAI ≤1J", f"{pct_1:.0f}%", tone="cyan")

    sine_divider()
    col_left, col_right = st.columns(2)

    with col_left:
        section_label("DISTRIBUSI WAKTU PENYELESAIAN")
        bins = [0, 1, 4, 24, 72, 168, float("inf")]
        labels = ["≤1 jam", "1-4 jam", "4-24 jam", "1-3 hari", "3-7 hari", ">7 hari"]
        sla["bucket"] = pd.cut(sla["sla_hours"], bins=bins, labels=labels, right=True)
        bucket_cnt = sla["bucket"].value_counts().reindex(labels)
        st.bar_chart(bucket_cnt.rename("jumlah"), height=300)

    with col_right:
        section_label("SLA PER KATEGORI (median jam)")
        sla_kat = sla.groupby("katalog")["sla_hours"].median().round(1).sort_values()
        st.dataframe(sla_kat.rename("median_jam"), width="stretch", height=300, hide_index=False)

    sine_divider()
    section_label("KINERJA PER DUKTEK")
    kinerja = (
        sla.groupby("duktek")
        .agg(jumlah=("nomor_tiket", "count"), median_jam=("sla_hours", "median"), max_jam=("sla_hours", "max"))
        .round(1)
        .sort_values("jumlah", ascending=False)
    )
    st.dataframe(kinerja, width="stretch", hide_index=False)

# ────────────────────────────────────────────────────────────────
# HALAMAN: EKSPLORASI
# ────────────────────────────────────────────────────────────────
else:
    st.markdown('<h1 style="font-size:1.7rem;">▦ EKSPLORASI <span style="color:#4A5B6D;">// signal dump</span></h1>', unsafe_allow_html=True)
    barcode()

    col1, col2, col3 = st.columns(3)
    with col1:
        q_pelapor = st.text_input("FILTER PELAPOR", placeholder="mengandung…", label_visibility="collapsed")
    with col2:
        q_masalah = st.text_input("FILTER MASALAH", placeholder="mengandung…", label_visibility="collapsed")
    with col3:
        q_nomor = st.text_input("NOMOR TIKET", placeholder="cth: JFBC…", label_visibility="collapsed")

    view = fdf.copy()
    if q_pelapor:
        view = view[view["pelapor"].str.contains(q_pelapor, case=False, na=False)]
    if q_masalah:
        view = view[view["masalah"].str.contains(q_masalah, case=False, na=False)]
    if q_nomor:
        view = view[view["nomor_tiket"].str.contains(q_nomor, case=False, na=False)]

    st.markdown(f'<div class="dt-section">▸ {len(view):,} FRAME DITAMPILKAN</div>', unsafe_allow_html=True)
    st.dataframe(
        view[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "probis", "duktek", "sla_hours", "uraian"]]
        .rename(columns={"sla_hours": "sla_jam"}),
        width="stretch", height=560, hide_index=True,
    )

    st.download_button(
        "⬇ DOWNLOAD CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="tiket_pdad.csv",
        mime="text/csv",
    )
