#!/usr/bin/env python3
"""Dashboard PDAD Interaktif — KPPBC Tipe Madya Pabean A Pasuruan.
Analitik tiket CEISACare + search engine solusi.
Data: data/tickets_clean.json + data/synth_results.json"""
import json
import os
import re

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard PDAD", page_icon="📊", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ================= LOAD DATA (cached) =================
@st.cache_data(ttl=3600)
def load_tickets():
    with open(os.path.join(DATA_DIR, "tickets_clean.json")) as f:
        rows = json.load(f)
    df = pd.DataFrame(rows)
    # kolom datetime
    df["tanggal_dt"] = pd.to_datetime(df["tanggal_dt"], errors="coerce")
    df["submit_time"] = pd.to_datetime(df["submit_time"], errors="coerce")
    df["resolve_time"] = pd.to_datetime(df["resolve_time"], errors="coerce")
    # bulan untuk agregasi
    df["bulan"] = df["tanggal_dt"].dt.to_period("M").astype(str)
    return df

@st.cache_data(ttl=3600)
def load_synth():
    with open(os.path.join(DATA_DIR, "synth_results.json")) as f:
        return json.load(f)

df = load_tickets()
synth = load_synth()

# ================= SIDEBAR =================
st.sidebar.title("📊 Dashboard PDAD")
page = st.sidebar.radio(
    "Navigasi",
    ["📊 Ringkasan", "⏱️ SLA & Kinerja", "🔍 Search Solusi", "📋 Eksplorasi Tiket"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter Global")

# filter tanggal
min_date = df["tanggal_dt"].min()
max_date = df["tanggal_dt"].max()
date_range = st.sidebar.date_input(
    "Rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# filter katalog
katalog_list = sorted(df["katalog"].dropna().unique())
sel_katalog = st.sidebar.multiselect("Kategori", katalog_list, default=[])

# filter duktek
duktek_list = sorted(df["duktek"].dropna().unique())
sel_duktek = st.sidebar.multiselect("Duktek", duktek_list, default=[])

# apply filter
mask = pd.Series(True, index=df.index)
if len(date_range) == 2:
    start, end = date_range
    mask &= (df["tanggal_dt"] >= pd.Timestamp(start)) & (df["tanggal_dt"] <= pd.Timestamp(end))
if sel_katalog:
    mask &= df["katalog"].isin(sel_katalog)
if sel_duktek:
    mask &= df["duktek"].isin(sel_duktek)

fdf = df[mask]

st.sidebar.markdown("---")
st.sidebar.caption(f"Data: {len(fdf):,} tiket (dari {len(df):,})")

# ================= HELPER =================
def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div style="background:#f2f6fa;border-radius:10px;padding:16px;margin:4px 0;">
            <div style="font-size:13px;color:#555;">{label}</div>
            <div style="font-size:26px;font-weight:bold;color:#0b5394;">{value}</div>
            <div style="font-size:11px;color:#888;">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ================= PAGE 1: RINGKASAN =================
if page == "📊 Ringkasan":
    st.title("📊 Ringkasan Tiket CEISACare")

    c1, c2, c3, c4 = st.columns(4)
    total = len(fdf)
    total_kat = fdf["katalog"].nunique()
    total_masalah = fdf["masalah"].nunique()
    with_sla = fdf["sla_hours"].dropna()
    med_sla = with_sla.median() if len(with_sla) else 0
    with c1:
        kpi_card("Total Tiket", f"{total:,}")
    with c2:
        kpi_card("Kategori", str(total_kat))
    with c3:
        kpi_card("Jenis Masalah", str(total_masalah))
    with c4:
        kpi_card("Median SLA", f"{med_sla:.1f} jam")

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Tren Tiket per Bulan")
        tren = fdf.groupby("bulan").size().reset_index(name="jumlah")
        st.line_chart(tren, x="bulan", y="jumlah", height=320)

        st.subheader("Distribusi per Kategori")
        kat = fdf["katalog"].value_counts().reset_index()
        kat.columns = ["kategori", "jumlah"]
        st.bar_chart(kat.set_index("kategori"), height=280)

    with col_right:
        st.subheader("Top Masalah")
        top_masalah = fdf["masalah"].value_counts().head(12)
        st.dataframe(
            top_masalah.rename("jumlah"),
            width="stretch",
            height=340,
        )

        st.subheader("Top Perusahaan (Pelapor)")
        top_perusahaan = fdf["pelapor"].value_counts().head(10)
        st.dataframe(
            top_perusahaan.rename("tiket"),
            width="stretch",
            height=280,
        )

# ================= PAGE 2: SLA & KINERJA =================
elif page == "⏱️ SLA & Kinerja":
    st.title("⏱️ SLA & Kinerja Penanganan")

    sla = fdf[fdf["sla_hours"].notna()].copy()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Median SLA", f"{sla['sla_hours'].median():.1f} jam")
    with c2:
        kpi_card("Rata-rata", f"{sla['sla_hours'].mean():.1f} jam")
    with c3:
        pct_24 = (sla['sla_hours'] <= 24).mean() * 100
        kpi_card("Selesai ≤24 jam", f"{pct_24:.0f}%")
    with c4:
        pct_1 = (sla['sla_hours'] <= 1).mean() * 100
        kpi_card("Selesai ≤1 jam", f"{pct_1:.0f}%")

    st.markdown("---")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Distribusi Waktu Penyelesaian")
        # histogram bucket
        bins = [0, 1, 4, 24, 72, 168, float("inf")]
        labels = ["≤1 jam", "1-4 jam", "4-24 jam", "1-3 hari", "3-7 hari", ">7 hari"]
        sla["bucket"] = pd.cut(sla["sla_hours"], bins=bins, labels=labels, right=True)
        bucket_cnt = sla["bucket"].value_counts().reindex(labels)
        st.bar_chart(bucket_cnt.rename("jumlah"), height=320)

    with col_right:
        st.subheader("SLA per Kategori (median jam)")
        sla_kat = sla.groupby("katalog")["sla_hours"].median().round(1).sort_values()
        st.dataframe(sla_kat.rename("median_jam"), width="stretch", height=320)

    st.markdown("---")
    st.subheader("Kinerja per Duktek")
    kinerja = (
        sla.groupby("duktek")
        .agg(jumlah=("nomor_tiket", "count"), median_jam=("sla_hours", "median"))
        .round(1)
        .sort_values("jumlah", ascending=False)
    )
    st.dataframe(kinerja, width="stretch")

# ================= PAGE 3: SEARCH SOLUSI =================
elif page == "🔍 Search Solusi":
    st.title("🔍 Search Engine Solusi")
    st.caption("Ketik kendala → dapatkan panduan penanganan + tiket terkait.")

    query = st.text_input("Cari kendala (contoh: CK-5 stuck, login MFA, PIB reject)", placeholder="cth: PIB stuck validasi")

    if query:
        q = query.lower()
        tokens = [t for t in re.split(r"\W+", q) if len(t) > 2]

        # --- search di synth_results (65 panduan) ---
        results = []
        for key, d in synth.items():
            hay = (d.get("masalah", "") + " " + d.get("ringkasan", "") + " " +
                   " ".join(d.get("langkah", [])) + " " + d.get("catatan", "")).lower()
            score = 0
            if q in hay:
                score += 10  # exact phrase
            for tok in tokens:
                if tok in hay:
                    score += 1
            if score > 0:
                results.append((score, d))

        results.sort(key=lambda x: -x[0])

        if results:
            st.markdown(f"### 🔎 {len(results)} panduan cocok")
            for score, d in results[:8]:
                with st.expander(f"{d['masalah']} ({d['jumlah']} tiket)", expanded=(score == results[0][0])):
                    if d.get("ringkasan"):
                        st.markdown(f"*{d['ringkasan']}*")
                    if d.get("langkah"):
                        st.markdown("**Langkah penanganan:**")
                        for i, s in enumerate(d["langkah"], 1):
                            st.markdown(f"{i}. {s}")
                    if d.get("catatan"):
                        st.markdown(f"---\n💡 *Catatan:* {d['catatan']}")
        else:
            st.info("Tidak ada panduan yang cocok. Coba kata kunci lain.")

        # --- search di tiket mentah ---
        st.markdown("### 📄 Tiket terkait")
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
            top_tickets = fdf2[fdf2["_score"] > 0].sort_values("_score", ascending=False).head(15)
            if len(top_tickets):
                st.dataframe(
                    top_tickets[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "duktek", "sla_hours"]]
                    .rename(columns={"sla_hours": "sla_jam"}),
                    width="stretch",
                )
            else:
                st.info("Tidak ada tiket terkait.")

# ================= PAGE 4: EKSPLORASI =================
else:
    st.title("📋 Eksplorasi Tiket")

    col1, col2, col3 = st.columns(3)
    with col1:
        q_pelapor = st.text_input("Filter pelapor (mengandung)")
    with col2:
        q_masalah = st.text_input("Filter masalah (mengandung)")
    with col3:
        q_nomor = st.text_input("Nomor tiket")

    view = fdf.copy()
    if q_pelapor:
        view = view[view["pelapor"].str.contains(q_pelapor, case=False, na=False)]
    if q_masalah:
        view = view[view["masalah"].str.contains(q_masalah, case=False, na=False)]
    if q_nomor:
        view = view[view["nomor_tiket"].str.contains(q_nomor, case=False, na=False)]

    st.caption(f"{len(view):,} tiket ditampilkan")
    st.dataframe(
        view[["nomor_tiket", "tanggal", "pelapor", "katalog", "masalah", "probis", "duktek", "sla_hours", "uraian"]]
        .rename(columns={"sla_hours": "sla_jam"}),
        width="stretch",
        height=600,
    )

    st.download_button(
        "⬇️ Download hasil (CSV)",
        view.to_csv(index=False).encode("utf-8"),
        file_name="tiket_pdad.csv",
        mime="text/csv",
    )
