#!/usr/bin/env python3
"""Recap CEISACare — Rekap & Solusi Tiket CEISACare.
KPPBC Tipe Madya Pabean A Pasuruan · Duktek PDAD.
World: clean minimal work dashboard (canon played straight, user-requested simple).
Data: data/tickets_clean.json + data/synth_results.json
"""
import html
import json
import os
import re

import pandas as pd
import streamlit as st

# ────────────────────────────────────────────────────────────────
# KONFIGURASI + KONTRAK ARAH (Simple Clean — user-requested)
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Recap CEISACare",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DIRECTION_CONTRACT = """<!--
THESIS: Dashboard PDAD is a calm, legible work surface: the Duktek reads the numbers and finds the answer without fighting the furniture. It refuses heavy metaphors (no stamp, no barcode, no chapter book) — clarity is the whole identity.
OWN-WORLD: Near-white neutral ground (#FAFAF8) with hairline-bordered white cards; one dignified blue accent (#2563EB) for actions and focus; system-ui type at comfortable sizes with tabular numerals; generous whitespace; simple 8px cards.
STORY: The Duktek opens the dashboard, sees the four key numbers, types the kendala into the search field, and reads the answer in a clean list — seconds, no noise.
FIRST VIEWPORT: Slim header with app name and a muted readout line. Four KPI cards. Below: the search field as the hero (large input + button), then clean result rows and a tidy table.
FORM: Simple Clean work dashboard (user-requested; follows Buku SOP and Data Terminal rounds).
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
-->
"""
st.markdown(DIRECTION_CONTRACT, unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ────────────────────────────────────────────────────────────────
# CSS — SIMPLE CLEAN WORLD
# ────────────────────────────────────────────────────────────────
CSS = """
<style>
:root {
  --sc-bg: #FAFAF8;
  --sc-card: #FFFFFF;
  --sc-line: #E6E6E1;
  --sc-line-strong: #D4D4CE;
  --sc-ink: #1A1D21;
  --sc-ink-dim: #6B7280;
  --sc-ink-faint: #9CA3AF;
  --sc-blue: #2563EB;
  --sc-blue-soft: #EFF4FF;
  --sc-green: #16A34A;
  --sc-amber: #B45309;
  --sc-red: #DC2626;
}

html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--sc-bg) !important;
  color: var(--sc-ink) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
}
[data-testid="stAppViewContainer"] { background: var(--sc-bg) !important; }

/* tabular numerals */
.stApp * { font-feature-settings: "tnum" 1, "zero" 1; }

/* sidebar */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background: #FFFFFF !important;
  border-right: 1px solid var(--sc-line) !important;
}
[data-testid="stSidebar"] * { color: var(--sc-ink) !important; }

/* inputs */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input {
  background: #FFFFFF !important;
  color: var(--sc-ink) !important;
  border: 1px solid var(--sc-line-strong) !important;
  border-radius: 8px !important;
  padding: 10px 14px !important;
  font-size: 0.95rem !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus, [data-testid="stDateInput"] input:focus {
  border-color: var(--sc-blue) !important;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--sc-ink-faint) !important; }

/* selectbox & multiselect */
[data-baseweb="select"] > div {
  background: #FFFFFF !important;
  border: 1px solid var(--sc-line-strong) !important;
  border-radius: 8px !important;
  color: var(--sc-ink) !important;
}
[data-baseweb="popover"] { background: #FFFFFF !important; border-radius: 8px !important; }

/* buttons */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {
  background: var(--sc-blue) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 10px 18px !important;
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
  background: #1D4ED8 !important;
  color: #FFFFFF !important;
}

/* radio nav */
[data-testid="stSidebar"] [role="radiogroup"] label { font-weight: 500; border-radius: 8px; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: var(--sc-blue-soft); }

/* dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--sc-line) !important;
  border-radius: 10px !important;
  overflow: hidden;
}

/* headings */
h1 { font-weight: 700 !important; letter-spacing: -0.02em; color: var(--sc-ink) !important; }
h2, h3 { font-weight: 650 !important; color: var(--sc-ink) !important; letter-spacing: -0.01em; }

/* tabs */
[data-testid="stTabs"] button { border-radius: 8px !important; font-weight: 500; }
[data-testid="stTabs"] button[aria-selected="true"] { background: var(--sc-blue-soft) !important; color: var(--sc-blue) !important; }

[data-testid="stCaptionContainer"], .stCaption { color: var(--sc-ink-dim) !important; }

/* slim header */
.sc-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 0 18px 0; margin-bottom: 8px;
  border-bottom: 1px solid var(--sc-line);
}
.sc-header .brand { font-weight: 700; font-size: 1.05rem; color: var(--sc-ink); letter-spacing: -0.01em; }
.sc-header .brand .dot { color: var(--sc-blue); }
.sc-header .readout { font-size: 0.75rem; color: var(--sc-ink-dim); }

/* KPI card */
.sc-kpi {
  background: var(--sc-card); border: 1px solid var(--sc-line); border-radius: 10px;
  padding: 16px 18px; margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}
.sc-kpi .label { font-size: 0.7rem; color: var(--sc-ink-dim); font-weight: 600; letter-spacing: 0.02em; }
.sc-kpi .value { font-size: 1.7rem; font-weight: 700; color: var(--sc-ink); line-height: 1.2; margin: 2px 0; letter-spacing: -0.02em; }
.sc-kpi .value.blue { color: var(--sc-blue); }
.sc-kpi .value.green { color: var(--sc-green); }
.sc-kpi .value.amber { color: var(--sc-amber); }
.sc-kpi .sub { font-size: 0.72rem; color: var(--sc-ink-faint); }

/* result card */
.sc-result {
  background: var(--sc-card); border: 1px solid var(--sc-line); border-radius: 10px;
  padding: 14px 18px; margin: 8px 0;
  transition: border-color 0.12s ease;
}
.sc-result:hover { border-color: var(--sc-line-strong); }
.sc-result .r-head { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
.sc-result .r-title { font-weight: 600; font-size: 0.98rem; color: var(--sc-ink); }
.sc-result .r-count { font-size: 0.72rem; color: var(--sc-amber); font-weight: 600; white-space: nowrap; }
.sc-result .r-domain { font-size: 0.7rem; color: var(--sc-blue); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin: 3px 0 8px 0; }
.sc-result .r-summary { color: var(--sc-ink-dim); font-size: 0.87rem; line-height: 1.55; margin-bottom: 10px; }
.sc-result ol { margin: 0 0 0 20px; padding: 0; }
.sc-result ol li { color: var(--sc-ink); font-size: 0.87rem; line-height: 1.6; margin-bottom: 3px; }
.sc-result .r-note { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--sc-line); color: var(--sc-amber); font-size: 0.8rem; }

/* section label */
.sc-section {
  font-size: 0.72rem; color: var(--sc-ink-dim); font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; margin: 20px 0 8px 0;
}

/* empty state */
.sc-empty {
  border: 1.5px dashed var(--sc-line-strong); color: var(--sc-ink-faint);
  padding: 24px; text-align: center; font-size: 0.85rem; border-radius: 10px;
  background: var(--sc-card);
}

/* metrics cleanup */
[data-testid="stMetric"] { background: var(--sc-card); border: 1px solid var(--sc-line); border-radius: 10px; padding: 14px; }
[data-testid="stMetricLabel"] { color: var(--sc-ink-dim) !important; }
[data-testid="stMetricValue"] { color: var(--sc-ink) !important; }

/* info/warning flattened */
[data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stError"], [data-testid="stSuccess"] {
  background: var(--sc-card) !important; border: 1px solid var(--sc-line) !important;
  border-radius: 10px !important; color: var(--sc-ink) !important;
}

/* charts */
[data-testid="stArrowVegaLiteChart"], [data-testid="stVegaLiteChart"] {
  background: var(--sc-card) !important; border: 1px solid var(--sc-line) !important;
  border-radius: 10px !important; padding: 8px;
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
    mn = df["tanggal_dt"].min().strftime("%d %b %Y") if df["tanggal_dt"].notna().any() else "--"
    mx = df["tanggal_dt"].max().strftime("%d %b %Y") if df["tanggal_dt"].notna().any() else "--"
    st.markdown(
        f"""
        <div class="sc-header">
          <div class="brand">Recap <span class="dot">CEISACare</span> <span style="color:#9CA3AF;font-weight:400;">· Rekap & Solusi Tiket</span></div>
          <div class="readout">{n:,} tiket · {mn} — {mx} · data segar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, sub="", tone=""):
    tone = tone if tone in ("blue", "green", "amber") else ""
    st.markdown(
        f"""
        <div class="sc-kpi">
          <div class="label">{esc(label)}</div>
          <div class="value {tone}">{esc(value)}</div>
          <div class="sub">{esc(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(f'<div class="sc-section">{esc(text)}</div>', unsafe_allow_html=True)


def empty_state(text):
    st.markdown(f'<div class="sc-empty">{esc(text)}</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────
# SIDEBAR — NAV + FILTER
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-weight:700;font-size:1.02rem;letter-spacing:-0.01em;">Recap CEISACare</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#9CA3AF;margin-bottom:12px;">Rekap & Solusi Tiket · Duktek PDAD · KPPBC Pasuruan</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigasi",
        ["🔍 Cari Solusi", "📊 Ringkasan", "⏱ SLA & Kinerja", "📋 Eksplorasi Tiket"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;letter-spacing:0.08em;color:#6B7280;font-weight:600;">FILTER</div>', unsafe_allow_html=True)

    min_date = df["tanggal_dt"].min()
    max_date = df["tanggal_dt"].max()
    date_range = st.date_input(
        "Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date,
        label_visibility="collapsed",
    )
    katalog_list = sorted(df["katalog"].dropna().unique())
    sel_katalog = st.multiselect("Kategori", katalog_list, default=[], label_visibility="collapsed",
                                 placeholder="pilih kategori…")
    duktek_list = sorted(df["duktek"].dropna().unique())
    sel_duktek = st.multiselect("Duktek", duktek_list, default=[], label_visibility="collapsed",
                                placeholder="pilih duktek…")

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
        f'<div style="font-size:0.7rem;color:#9CA3AF;">{len(fdf):,} dari {len(df):,} tiket</div>',
        unsafe_allow_html=True,
    )

header_bar()

# ────────────────────────────────────────────────────────────────
# HALAMAN: CARI SOLUSI (HERO)
# ────────────────────────────────────────────────────────────────
if page == "🔍 Cari Solusi":
    st.markdown('<h1 style="font-size:1.45rem;">Cari Solusi</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6B7280;font-size:0.9rem;">Ketik kendala untuk melihat panduan penanganan dan tiket terkait.</div>', unsafe_allow_html=True)

    _total = len(fdf)
    _kat = fdf["katalog"].nunique()
    _masalah = fdf["masalah"].nunique()
    _sla = fdf["sla_hours"].dropna()
    _med = _sla.median() if len(_sla) else 0
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1:
        kpi_card("Total Tiket", f"{_total:,}", sub="sesuai filter", tone="blue")
    with ck2:
        kpi_card("Kategori", str(_kat), sub="katalog")
    with ck3:
        kpi_card("Jenis Masalah", str(_masalah), sub="masalah unik", tone="amber")
    with ck4:
        kpi_card("Median SLA", f"{_med:.1f} jam", sub="penyelesaian", tone="green")

    if st.session_state.pop("scan_fill", None):
        st.session_state["scan_input"] = st.session_state["scan_fill"]

    query = st.text_input(
        "Cari kendala",
        placeholder="cth: PIB reject validasi, MFA looping login, CK-5 stuck…",
        label_visibility="collapsed", key="scan_input",
    )

    if query.strip():
        q = query.lower()
        tokens = [t for t in re.split(r"\W+", q) if len(t) > 2]

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

        section_label(f"Panduan ({len(results)})")

        if results:
            for score, key, d in results[:8]:
                domain = d.get("domain", "")
                cnt = d.get("jumlah", "?")
                title = d.get("masalah", key)
                body = f"""
                <div class="sc-result">
                  <div class="r-head">
                    <span class="r-title">{esc(title)}</span>
                    <span class="r-count">{esc(cnt)} tiket</span>
                  </div>
                  <div class="r-domain">{esc(domain)}</div>
                """
                if d.get("ringkasan"):
                    body += f'<div class="r-summary">{esc(d["ringkasan"])}</div>'
                if d.get("langkah"):
                    body += "<ol>"
                    for s in d["langkah"]:
                        body += f"<li>{esc(s)}</li>"
                    body += "</ol>"
                if d.get("catatan"):
                    body += f'<div class="r-note">💡 {esc(d["catatan"])}</div>'
                st.markdown(body + "</div>", unsafe_allow_html=True)
        else:
            empty_state("Tidak ada panduan yang cocok. Coba kata kunci lain, atau lihat tiket terkait di bawah.")

        section_label("Tiket terkait")
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

# ────────────────────────────────────────────────────────────────
# HALAMAN: RINGKASAN
# ────────────────────────────────────────────────────────────────
elif page == "📊 Ringkasan":
    st.markdown('<h1 style="font-size:1.45rem;">Ringkasan</h1>', unsafe_allow_html=True)

    total = len(fdf)
    total_kat = fdf["katalog"].nunique()
    total_masalah = fdf["masalah"].nunique()
    with_sla = fdf["sla_hours"].dropna()
    med_sla = with_sla.median() if len(with_sla) else 0
    pct24 = (with_sla <= 24).mean() * 100 if len(with_sla) else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Tiket", f"{total:,}", sub="sesuai filter", tone="blue")
    with c2:
        kpi_card("Kategori", str(total_kat), sub="katalog")
    with c3:
        kpi_card("Jenis Masalah", str(total_masalah), sub="masalah unik", tone="amber")
    with c4:
        kpi_card("Median SLA", f"{med_sla:.1f} jam", sub=f"≤24 jam: {pct24:.0f}%", tone="green")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_label("Tren tiket per bulan")
        tren = fdf.groupby("bulan").size().reset_index(name="jumlah")
        st.line_chart(tren, x="bulan", y="jumlah", height=300)

        section_label("Distribusi per kategori")
        kat = fdf["katalog"].value_counts().reset_index()
        kat.columns = ["kategori", "jumlah"]
        st.bar_chart(kat.set_index("kategori"), height=260)

    with col_right:
        section_label("Top masalah")
        top_masalah = fdf["masalah"].value_counts().head(12)
        st.dataframe(top_masalah.rename("jumlah"), width="stretch", height=320, hide_index=False)

        section_label("Top pelapor")
        top_perusahaan = fdf["pelapor"].value_counts().head(10)
        st.dataframe(top_perusahaan.rename("tiket"), width="stretch", height=280, hide_index=False)

# ────────────────────────────────────────────────────────────────
# HALAMAN: SLA & KINERJA
# ────────────────────────────────────────────────────────────────
elif page == "⏱ SLA & Kinerja":
    st.markdown('<h1 style="font-size:1.45rem;">SLA & Kinerja</h1>', unsafe_allow_html=True)

    sla = fdf[fdf["sla_hours"].notna()].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Median SLA", f"{sla['sla_hours'].median():.1f} jam", tone="amber")
    with c2:
        kpi_card("Rata-rata", f"{sla['sla_hours'].mean():.1f} jam")
    with c3:
        pct_24 = (sla["sla_hours"] <= 24).mean() * 100
        kpi_card("Selesai ≤24 jam", f"{pct_24:.0f}%", tone="green")
    with c4:
        pct_1 = (sla["sla_hours"] <= 1).mean() * 100
        kpi_card("Selesai ≤1 jam", f"{pct_1:.0f}%", tone="blue")

    col_left, col_right = st.columns(2)

    with col_left:
        section_label("Distribusi waktu penyelesaian")
        bins = [0, 1, 4, 24, 72, 168, float("inf")]
        labels = ["≤1 jam", "1-4 jam", "4-24 jam", "1-3 hari", "3-7 hari", ">7 hari"]
        sla["bucket"] = pd.cut(sla["sla_hours"], bins=bins, labels=labels, right=True)
        bucket_cnt = sla["bucket"].value_counts().reindex(labels)
        st.bar_chart(bucket_cnt.rename("jumlah"), height=300)

    with col_right:
        section_label("SLA per kategori (median jam)")
        sla_kat = sla.groupby("katalog")["sla_hours"].median().round(1).sort_values()
        st.dataframe(sla_kat.rename("median_jam"), width="stretch", height=300, hide_index=False)

    section_label("Kinerja per duktek")
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
    st.markdown('<h1 style="font-size:1.45rem;">Eksplorasi Tiket</h1>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        q_pelapor = st.text_input("Filter pelapor", placeholder="mengandung…", label_visibility="collapsed")
    with col2:
        q_masalah = st.text_input("Filter masalah", placeholder="mengandung…", label_visibility="collapsed")
    with col3:
        q_nomor = st.text_input("Nomor tiket", placeholder="cth: JFBC…", label_visibility="collapsed")

    view = fdf.copy()
    if q_pelapor:
        view = view[view["pelapor"].str.contains(q_pelapor, case=False, na=False)]
    if q_masalah:
        view = view[view["masalah"].str.contains(q_masalah, case=False, na=False)]
    if q_nomor:
        view = view[view["nomor_tiket"].str.contains(q_nomor, case=False, na=False)]

    st.markdown(f'<div style="font-size:0.75rem;color:#6B7280;margin-bottom:8px;">{len(view):,} tiket ditampilkan</div>', unsafe_allow_html=True)
    st.dataframe(
        view[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "probis", "duktek", "sla_hours", "uraian"]]
        .rename(columns={"sla_hours": "sla_jam"}),
        width="stretch", height=560, hide_index=True,
    )

    st.download_button(
        "Download CSV",
        view.to_csv(index=False).encode("utf-8"),
        file_name="tiket_pdad.csv",
        mime="text/csv",
    )
