#!/usr/bin/env python3
"""Dashboard PDAD — BUKU SOP.
KPPBC Tipe Madya Pabean A Pasuruan · Analitik tiket CEISACare + scan solusi.
World: official SOP manual (chapter numbering, margin steps, stamp marks).
Data: data/tickets_clean.json + data/synth_results.json
"""
import html
import json
import os
import re

import pandas as pd
import streamlit as st

# ────────────────────────────────────────────────────────────────
# KONFIGURASI + KONTRAK ARAH (Buku SOP — user-pinned)
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BUKU SOP // PDAD",
    page_icon="📗",
    layout="wide",
    initial_sidebar_state="expanded",
)

DIRECTION_CONTRACT = """<!--
THESIS: Dashboard PDAD is the unit's own SOP manual made live — a book of answers the Duktek opens every day, where each kendala has a numbered handling procedure. It refuses the category default of a dark analytics dashboard and of generic cream-and-serif AI pages alike; this is an official document, not a screen.
OWN-WORLD: Cream paper field (#F5EFE0) with aged panels and hairline rules; chapter numbering (BAB I–IV) as navigation; Source Serif 4 for chapter titles, Source Sans 3 for body with tabular numerals, JetBrains Mono for form values; red ink-stamp marks (cap) as the only saturated accent; dotted leaders and ruled dividers instead of charts-chrome.
STORY: The Duktek opens the book, reads the instrument entries, writes the kendala into the search form, and turns to the numbered steps — answers in seconds, in the register of the office's own procedures.
FIRST VIEWPORT: Document header with book title, unit line, edition and a red TERVERIFIKASI stamp. Entry row: four form-field KPI entries with underlined values. Below: the search form as the hero (LANGKAH 0 — ISI LEMBAR PENCARIAN), then solution entries as numbered margin-step cards and signal traces as an appendix table.
FORM: Buku SOP manual (user-pinned direction; replaces Data Terminal seed 02dade84).
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
-->
"""
st.markdown(DIRECTION_CONTRACT, unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ────────────────────────────────────────────────────────────────
# CSS — BUKU SOP WORLD
# ────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700;8..60,900&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --sop-bg: #F5EFE0;
  --sop-panel: #FBF7EC;
  --sop-panel2: #EDE4CE;
  --sop-line: #D8CDB2;
  --sop-line-strong: #B9AB8A;
  --sop-ink: #23314F;
  --sop-ink-dim: #66708A;
  --sop-red: #B23A2F;
  --sop-gold: #A87F2D;
  --sop-green: #2F7D4F;
  --sop-teal: #1F6F8F;
}

html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--sop-bg) !important;
  color: var(--sop-ink) !important;
  font-family: 'Source Sans 3', 'Segoe UI', system-ui, sans-serif !important;
}
[data-testid="stAppViewContainer"] { background: var(--sop-bg) !important; }

/* tabular numerals for all numbers */
.stApp * { font-feature-settings: "tnum" 1, "zero" 1; }

/* sidebar = aged paper table of contents */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background: var(--sop-panel2) !important;
  border-right: 1px solid var(--sop-line) !important;
}
[data-testid="stSidebar"] * { color: var(--sop-ink) !important; }

/* inputs = form fields with bottom rule */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input {
  background: transparent !important;
  color: var(--sop-ink) !important;
  border: none !important;
  border-bottom: 2px solid var(--sop-ink) !important;
  border-radius: 0 !important;
  font-family: 'JetBrains Mono', 'Source Sans 3', monospace !important;
  font-weight: 700;
}
[data-testid="stTextInput"] input:focus {
  border-bottom-color: var(--sop-red) !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #A99E85 !important; font-weight: 400; }

/* selectbox & multiselect */
[data-baseweb="select"] > div {
  background: var(--sop-panel) !important;
  border: 1px solid var(--sop-line-strong) !important;
  border-radius: 0 !important;
  color: var(--sop-ink) !important;
}
[data-baseweb="popover"] { background: var(--sop-panel) !important; }

/* buttons = document actions */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
  background: transparent !important;
  color: var(--sop-ink) !important;
  border: 1.5px solid var(--sop-ink) !important;
  border-radius: 0 !important;
  font-family: 'Source Sans 3', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
  background: var(--sop-ink) !important;
  color: var(--sop-bg) !important;
}

/* radio nav = daftar isi */
[data-testid="stSidebar"] [role="radiogroup"] label {
  font-family: 'Source Serif 4', serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { color: var(--sop-red) !important; }

/* dataframe = appendix table */
[data-testid="stDataFrame"] {
  border: 1px solid var(--sop-line-strong) !important;
  border-radius: 0 !important;
  background: var(--sop-panel) !important;
}
[data-testid="stDataFrame"] * { font-family: 'Source Sans 3', sans-serif !important; }

/* headings = serif chapter titles */
h1, h2, h3, h4 { font-family: 'Source Serif 4', Georgia, serif !important; color: var(--sop-ink) !important; }
h1 { font-weight: 900; letter-spacing: -0.01em; }
h2, h3 { font-weight: 700; }

/* tabs */
[data-testid="stTabs"] button {
  background: transparent !important;
  color: var(--sop-ink-dim) !important;
  border-radius: 0 !important;
  font-family: 'Source Serif 4', serif !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--sop-red) !important;
  border-bottom: 2px solid var(--sop-red) !important;
}

[data-testid="stCaptionContainer"], .stCaption { color: var(--sop-ink-dim) !important; }

/* document header */
.sop-header {
  border: 1.5px solid var(--sop-ink); border-radius: 0;
  background: var(--sop-panel); padding: 18px 22px; margin-bottom: 22px;
  position: relative;
}
.sop-header .kicker { font-size: 0.68rem; letter-spacing: 0.22em; color: var(--sop-red); font-weight: 700; text-transform: uppercase; }
.sop-header .title { font-family: 'Source Serif 4', Georgia, serif; font-weight: 900; font-size: 1.5rem; color: var(--sop-ink); margin: 4px 0 2px 0; line-height: 1.15; }
.sop-header .subtitle { font-size: 0.85rem; color: var(--sop-ink-dim); font-style: italic; }
.sop-header .meta { display: flex; gap: 26px; margin-top: 10px; font-size: 0.72rem; color: var(--sop-ink-dim); letter-spacing: 0.06em; }
.sop-header .meta b { color: var(--sop-ink); }
/* red ink stamp */
.sop-stamp {
  position: absolute; right: 22px; top: 16px;
  width: 118px; height: 118px; border-radius: 50%;
  border: 3px solid var(--sop-red);
  display: flex; align-items: center; justify-content: center;
  transform: rotate(-8deg); opacity: 0.82;
  color: var(--sop-red); font-weight: 700; text-align: center;
  font-size: 0.72rem; line-height: 1.25; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 10px;
  pointer-events: none; user-select: none;
}
.sop-stamp .inner { border: 1.5px solid var(--sop-red); border-radius: 50%; width: 92px; height: 92px; display: flex; align-items: center; justify-content: center; }

/* KPI = form-field entry */
.sop-kpi {
  background: var(--sop-panel); border: 1px solid var(--sop-line-strong); border-radius: 0;
  padding: 14px 16px 12px 16px; margin-bottom: 10px; position: relative;
}
.sop-kpi .label { font-size: 0.66rem; color: var(--sop-ink-dim); letter-spacing: 0.16em; text-transform: uppercase; font-weight: 600; }
.sop-kpi .value { font-size: 1.9rem; font-weight: 900; color: var(--sop-ink); line-height: 1.15; font-family: 'Source Serif 4', Georgia, serif; }
.sop-kpi .value.red { color: var(--sop-red); }
.sop-kpi .value.green { color: var(--sop-green); }
.sop-kpi .value.gold { color: var(--sop-gold); }
.sop-kpi .sub { font-size: 0.66rem; color: var(--sop-ink-dim); margin-top: 2px; letter-spacing: 0.04em; }
.sop-kpi .rule { position: absolute; left: 16px; right: 16px; bottom: 0; height: 2px; }
.sop-kpi .rule.red { background: var(--sop-red); }
.sop-kpi .rule.green { background: var(--sop-green); }
.sop-kpi .rule.gold { background: var(--sop-gold); }
.sop-kpi .rule.navy { background: var(--sop-ink); }

/* solution entry card */
.sop-entry {
  border: 1px solid var(--sop-line-strong); border-top: 3px solid var(--sop-ink);
  background: var(--sop-panel); padding: 14px 18px 14px 62px; margin: 12px 0; border-radius: 0;
  position: relative;
}
.sop-entry .step-no {
  position: absolute; left: 12px; top: 14px;
  font-family: 'Source Serif 4', Georgia, serif; font-weight: 900; font-size: 1.35rem;
  color: var(--sop-red); line-height: 1;
}
.sop-entry .e-title { font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; font-size: 1.02rem; color: var(--sop-ink); }
.sop-entry .e-meta { display: flex; gap: 16px; margin: 4px 0 8px 0; font-size: 0.68rem; color: var(--sop-ink-dim); letter-spacing: 0.05em; }
.sop-entry .e-meta .katalog { color: var(--sop-teal); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.sop-entry .e-meta .count { color: var(--sop-red); font-weight: 700; }
.sop-entry .e-summary { color: var(--sop-ink-dim); font-size: 0.84rem; line-height: 1.55; margin-bottom: 10px; font-style: italic; }
.sop-entry ol { margin: 8px 0 0 22px; padding: 0; counter-reset: step; list-style: none; }
.sop-entry ol li {
  counter-increment: step; position: relative; padding-left: 30px;
  color: var(--sop-ink); font-size: 0.84rem; line-height: 1.6; margin-bottom: 5px;
}
.sop-entry ol li::before {
  content: counter(step, decimal-leading-zero);
  position: absolute; left: 0; top: 0;
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700;
  color: var(--sop-ink-dim); letter-spacing: 0.04em;
}
.sop-entry .e-note {
  margin-top: 10px; padding-top: 8px; border-top: 1px dotted var(--sop-line-strong);
  color: var(--sop-gold); font-size: 0.78rem;
}
.sop-entry .e-note::before { content: "ANOTASI — "; font-weight: 700; letter-spacing: 0.08em; }

/* empty state = blank form */
.sop-empty {
  border: 1.5px dashed var(--sop-line-strong); color: var(--sop-ink-dim);
  padding: 26px; text-align: center; font-size: 0.85rem; letter-spacing: 0.06em;
  background: transparent; font-style: italic;
}

/* section label = chapter heading */
.sop-section {
  font-size: 0.78rem; color: var(--sop-red); letter-spacing: 0.14em;
  text-transform: uppercase; margin: 24px 0 10px 0; font-weight: 700;
  font-family: 'Source Sans 3', sans-serif;
}

/* ruled divider */
.sop-rule { display: flex; align-items: center; gap: 10px; margin: 22px 0; color: var(--sop-line-strong); }
.sop-rule .l { flex: 1; border-top: 1px solid var(--sop-line-strong); }
.sop-rule .r { flex: 1; border-top: 3px double var(--sop-line-strong); }
.sop-rule .diamond { color: var(--sop-red); font-size: 0.7rem; }

/* metric cleanup */
[data-testid="stMetric"] { background: var(--sop-panel); border: 1px solid var(--sop-line-strong); border-radius: 0; padding: 12px; }
[data-testid="stMetricLabel"] { color: var(--sop-ink-dim) !important; }
[data-testid="stMetricValue"] { color: var(--sop-ink) !important; font-family: 'Source Serif 4', serif !important; }

/* info/warning flattened to document note */
[data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stError"], [data-testid="stSuccess"] {
  background: var(--sop-panel) !important; border: 1px solid var(--sop-line-strong) !important;
  border-radius: 0 !important; color: var(--sop-ink) !important;
}

/* chart backgrounds */
[data-testid="stArrowVegaLiteChart"], [data-testid="stVegaLiteChart"] { background: var(--sop-panel) !important; border: 1px solid var(--sop-line-strong) !important; }
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
    mn = df["tanggal_dt"].min().strftime("%d.%m.%Y") if df["tanggal_dt"].notna().any() else "--"
    mx = df["tanggal_dt"].max().strftime("%d.%m.%Y") if df["tanggal_dt"].notna().any() else "--"
    h = f"""
    <div class="sop-header">
      <div class="kicker">KPPBC Tipe Madya Pabean A Pasuruan</div>
      <div class="title">Buku Standar Operasional Prosedur — Penanganan Tiket CEISACare</div>
      <div class="subtitle">Buku jawaban harian Duktek: setiap kendala punya prosedur bernomor.</div>
      <div class="meta">
        <span>NOMOR DOK: <b>PDAD/SOP/2026/02</b></span>
        <span>EDISI: <b>2.0</b></span>
        <span>DATA: <b>{n:,} tiket</b> ({mn} — {mx})</span>
        <span>STATUS: <b>BERLAKU</b></span>
      </div>
      <div class="sop-stamp"><div class="inner">TERVERI<br>FIKASI<br>Duktek<br>PDAD</div></div>
    </div>
    """
    st.markdown(h, unsafe_allow_html=True)


def ruled_divider():
    st.markdown(
        '<div class="sop-rule"><span class="l"></span><span class="diamond">◆</span><span class="r"></span></div>',
        unsafe_allow_html=True,
    )


def kpi_card(label, value, sub="", tone=""):
    tone = tone if tone in ("red", "green", "gold") else "navy"
    st.markdown(
        f"""
        <div class="sop-kpi">
          <div class="label">{esc(label)}</div>
          <div class="value {tone}">{esc(value)}</div>
          <div class="sub">{esc(sub)}</div>
          <div class="rule {tone}"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(f'<div class="sop-section">{esc(text)}</div>', unsafe_allow_html=True)


def empty_state(text):
    st.markdown(f'<div class="sop-empty">— {esc(text)} —</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────
# SIDEBAR — DAFTAR ISI + FILTER
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'Source Serif 4\',serif;font-weight:900;font-size:1.05rem;letter-spacing:0.04em;">BUKU SOP<br><span style="color:#B23A2F;font-size:0.72rem;letter-spacing:0.18em;">DAFTAR ISI</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.66rem;color:#66708A;margin-top:-4px;">PDAD://SOP · Pasuruan</div>', unsafe_allow_html=True)
    page = st.radio(
        "DAFTAR ISI",
        ["BAB I — SCAN SOLUSI", "BAB II — RINGKASAN", "BAB III — SLA & KINERJA", "BAB IV — EKSPLORASI"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown('<div style="font-size:0.68rem;letter-spacing:0.16em;color:#B23A2F;font-weight:700;">// LAMPIRAN FILTER</div>', unsafe_allow_html=True)

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
        f'<div style="font-size:0.66rem;color:#A99E85;">ENTRI {len(fdf):,} / {len(df):,} · TTL 3600s</div>',
        unsafe_allow_html=True,
    )

header_bar()

# ────────────────────────────────────────────────────────────────
# BAB I — SCAN SOLUSI (HERO)
# ────────────────────────────────────────────────────────────────
if page == "BAB I — SCAN SOLUSI":
    st.markdown('<div style="font-size:0.7rem;letter-spacing:0.2em;color:#B23A2F;font-weight:700;">BAB I · PROSEDUR PENCARIAN SOLUSI</div>', unsafe_allow_html=True)
    st.markdown('<h1 style="margin-top:2px;font-size:1.7rem;">SCAN <span style="color:#B23A2F;">SOLUSI</span></h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:#66708A;font-style:italic;font-size:0.85rem;">Tuliskan kendala pada lembar pencarian — buku membuka prosedur penanganan bernomor dari 65 pasal solusi + riwayat tiket.</div>', unsafe_allow_html=True)

    # entry row (FIRST VIEWPORT: form-field KPI di atas lembar pencarian)
    _total = len(fdf)
    _kat = fdf["katalog"].nunique()
    _masalah = fdf["masalah"].nunique()
    _sla = fdf["sla_hours"].dropna()
    _med = _sla.median() if len(_sla) else 0
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1:
        kpi_card("ENTRI TIKET", f"{_total:,}", sub="dalam lampiran filter", tone="red")
    with ck2:
        kpi_card("KATEGORI", str(_kat), sub="katalog", tone="navy")
    with ck3:
        kpi_card("JENIS MASALAH", str(_masalah), sub="masalah unik", tone="gold")
    with ck4:
        kpi_card("MEDIAN SLA", f"{_med:.1f} jam", sub="waktu penyelesaian", tone="green")

    ruled_divider()

    # tombol contoh mengisi lembar pencarian via session_state
    if st.session_state.pop("scan_fill", None):
        st.session_state["scan_input"] = st.session_state["scan_fill"]

    query = st.text_input(
        "LANGKAH 0 — ISI LEMBAR PENCARIAN",
        placeholder="tulis kendala di sini ▍  cth: PIB reject validasi / MFA looping / CK-5…",
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

        st.markdown(
            f'<div class="sop-section">BAB I · {len(results)} PASAL SOLUSI COCOK</div>',
            unsafe_allow_html=True,
        )

        if results:
            for idx, (score, key, d) in enumerate(results[:8], 1):
                domain = d.get("domain", "")
                cnt = d.get("jumlah", "?")
                title = d.get("masalah", key)
                body = f"""
                <div class="sop-entry">
                  <div class="step-no">{idx:02d}</div>
                  <div class="e-title">{esc(title)}</div>
                  <div class="e-meta">
                    <span class="katalog">{esc(domain)}</span>
                    <span class="count">▮ {esc(cnt)} tiket</span>
                  </div>
                """
                if d.get("ringkasan"):
                    body += f'<div class="e-summary">{esc(d["ringkasan"])}</div>'
                if d.get("langkah"):
                    body += '<div style="font-size:0.7rem;letter-spacing:0.14em;color:#23314F;font-weight:700;margin-top:6px;">PROSEDUR PENANGANAN</div><ol>'
                    for s in d["langkah"]:
                        body += f"<li>{esc(s)}</li>"
                    body += "</ol>"
                if d.get("catatan"):
                    body += f'<div class="e-note">{esc(d["catatan"])}</div>'
                st.markdown(body + "</div>", unsafe_allow_html=True)
        else:
            empty_state("Tidak ada pasal yang cocok — coba kata kunci lain, atau periksa lampiran tiket di bawah.")

        # --- scan tiket mentah ---
        section_label("LAMPIRAN — TIKET TERKAIT")
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
                empty_state("Tidak ada tiket terkait.")
    else:
        ruled_divider()
        st.markdown(
            """
            <div class="sop-empty">Lembar pencarian kosong. Contoh kendala yang sering dihadapi:</div>
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

    ruled_divider()
    st.markdown('<div style="font-size:0.66rem;color:#A99E85;">PASAL 65 · LAMPIRAN 3.807 · MESIN PENCARIAN: FUZZY-TOKEN</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# BAB II — RINGKASAN
# ────────────────────────────────────────────────────────────────
elif page == "BAB II — RINGKASAN":
    st.markdown('<h1 style="font-size:1.7rem;">BAB II · RINGKASAN <span style="color:#A99E85;font-size:0.9rem;">// ikhtisar dokumen</span></h1>', unsafe_allow_html=True)
    ruled_divider()

    total = len(fdf)
    total_kat = fdf["katalog"].nunique()
    total_masalah = fdf["masalah"].nunique()
    with_sla = fdf["sla_hours"].dropna()
    med_sla = with_sla.median() if len(with_sla) else 0
    pct24 = (with_sla <= 24).mean() * 100 if len(with_sla) else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("ENTRI TIKET", f"{total:,}", sub="dalam filter", tone="red")
    with c2:
        kpi_card("KATEGORI", str(total_kat), sub="katalog", tone="navy")
    with c3:
        kpi_card("JENIS MASALAH", str(total_masalah), sub="masalah unik", tone="gold")
    with c4:
        kpi_card("MEDIAN SLA", f"{med_sla:.1f} jam", sub=f"≤24 jam: {pct24:.0f}%", tone="green")

    ruled_divider()
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_label("PASAL 1 · TREN TIKET PER BULAN")
        tren = fdf.groupby("bulan").size().reset_index(name="jumlah")
        st.line_chart(tren, x="bulan", y="jumlah", height=300)

        section_label("PASAL 2 · DISTRIBUSI PER KATEGORI")
        kat = fdf["katalog"].value_counts().reset_index()
        kat.columns = ["kategori", "jumlah"]
        st.bar_chart(kat.set_index("kategori"), height=260)

    with col_right:
        section_label("PASAL 3 · TOP MASALAH")
        top_masalah = fdf["masalah"].value_counts().head(12)
        st.dataframe(top_masalah.rename("jumlah"), width="stretch", height=320, hide_index=False)

        section_label("PASAL 4 · TOP PELAPOR")
        top_perusahaan = fdf["pelapor"].value_counts().head(10)
        st.dataframe(top_perusahaan.rename("tiket"), width="stretch", height=280, hide_index=False)

# ────────────────────────────────────────────────────────────────
# BAB III — SLA & KINERJA
# ────────────────────────────────────────────────────────────────
elif page == "BAB III — SLA & KINERJA":
    st.markdown('<h1 style="font-size:1.7rem;">BAB III · SLA & KINERJA <span style="color:#A99E85;font-size:0.9rem;">// standar pelayanan</span></h1>', unsafe_allow_html=True)
    ruled_divider()

    sla = fdf[fdf["sla_hours"].notna()].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("MEDIAN SLA", f"{sla['sla_hours'].median():.1f} jam", tone="gold")
    with c2:
        kpi_card("RATA-RATA", f"{sla['sla_hours'].mean():.1f} jam", tone="navy")
    with c3:
        pct_24 = (sla["sla_hours"] <= 24).mean() * 100
        kpi_card("SELESAI ≤24J", f"{pct_24:.0f}%", tone="green")
    with c4:
        pct_1 = (sla["sla_hours"] <= 1).mean() * 100
        kpi_card("SELESAI ≤1J", f"{pct_1:.0f}%", tone="red")

    ruled_divider()
    col_left, col_right = st.columns(2)

    with col_left:
        section_label("PASAL 5 · DISTRIBUSI WAKTU PENYELESAIAN")
        bins = [0, 1, 4, 24, 72, 168, float("inf")]
        labels = ["≤1 jam", "1-4 jam", "4-24 jam", "1-3 hari", "3-7 hari", ">7 hari"]
        sla["bucket"] = pd.cut(sla["sla_hours"], bins=bins, labels=labels, right=True)
        bucket_cnt = sla["bucket"].value_counts().reindex(labels)
        st.bar_chart(bucket_cnt.rename("jumlah"), height=300)

    with col_right:
        section_label("PASAL 6 · SLA PER KATEGORI (median jam)")
        sla_kat = sla.groupby("katalog")["sla_hours"].median().round(1).sort_values()
        st.dataframe(sla_kat.rename("median_jam"), width="stretch", height=300, hide_index=False)

    ruled_divider()
    section_label("PASAL 7 · KINERJA PER DUKTEK")
    kinerja = (
        sla.groupby("duktek")
        .agg(jumlah=("nomor_tiket", "count"), median_jam=("sla_hours", "median"), max_jam=("sla_hours", "max"))
        .round(1)
        .sort_values("jumlah", ascending=False)
    )
    st.dataframe(kinerja, width="stretch", hide_index=False)

# ────────────────────────────────────────────────────────────────
# BAB IV — EKSPLORASI
# ────────────────────────────────────────────────────────────────
else:
    st.markdown('<h1 style="font-size:1.7rem;">BAB IV · EKSPLORASI <span style="color:#A99E85;font-size:0.9rem;">// lampiran tiket</span></h1>', unsafe_allow_html=True)
    ruled_divider()

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

    st.markdown(f'<div class="sop-section">LAMPIRAN · {len(view):,} ENTRI DITAMPILKAN</div>', unsafe_allow_html=True)
    st.dataframe(
        view[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "probis", "duktek", "sla_hours", "uraian"]]
        .rename(columns={"sla_hours": "sla_jam"}),
        width="stretch", height=560, hide_index=True,
    )

    st.download_button(
        "⬇ UNDUH CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="tiket_pdad.csv",
        mime="text/csv",
    )
