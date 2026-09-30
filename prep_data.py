#!/usr/bin/env python3
"""Prep data untuk Dashboard PDAD.
Baca ceisacare_selesai_all.json → hitung SLA (Submit→Penyelesaian) → data bersih.
Output: tickets_clean.json (kompak) untuk dibaca app.py."""
import json
import os
import re
import datetime

# Path relatif ke lokasi script ini, supaya tidak rusak kalau folder dipindah.
# (Sebelumnya hardcoded ke path lama ".../My SaaS/..." yang pakai spasi dan sudah
#  tidak ada — akibatnya prep gagal diam-diam & tickets_clean.json jadi basi.)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "data", "ceisacare_selesai_all.json")
OUT = os.path.join(BASE_DIR, "data", "tickets_clean.json")

def parse(w):
    if not w:
        return None
    w = str(w).strip()
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(w, fmt)
        except ValueError:
            continue
    return None

def clean(t):
    if not t:
        return ""
    t = re.sub(r"<br\s*/?>", " ", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"&nbsp;", " ", t)
    t = re.sub(r"&amp;", "&", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def main():
    with open(SRC) as f:
        data = json.load(f)

    rows = []
    for t in data:
        # ambil waktu Submit (user) & Penyelesaian (IKC)
        submit_t = None
        resolve_t = None
        escalated = False
        for p in t.get("proseses", []):
            status = p.get("status") or ""
            wt = parse(p.get("waktu"))
            if status == "Submit" and wt and (submit_t is None or wt < submit_t):
                submit_t = wt
            if status in ("Penyelesaian", "Push Penyelesaian") and wt and (resolve_t is None or wt > resolve_t):
                resolve_t = wt
            if "IKC" in status or "Layer" in status:
                escalated = True

        sla_hours = None
        if submit_t and resolve_t:
            sla_hours = round((resolve_t - submit_t).total_seconds() / 3600, 2)
        elif submit_t:
            # belum ada penyelesaian? (tidak mungkin di dataset selesai, tapi jaga-jaga)
            sla_hours = None

        # parse tanggal tiket untuk sorting
        tgl = parse(t.get("tanggal"))
        rows.append({
            "nomor_tiket": t.get("nomor_tiket"),
            "tanggal": t.get("tanggal"),
            "tanggal_dt": tgl.isoformat() if tgl else None,
            "pelapor": clean(t.get("pelapor")),
            "katalog": t.get("katalog"),
            "masalah": t.get("masalah"),
            "probis": t.get("probis"),
            "duktek": t.get("duktek"),
            "uraian": clean(t.get("uraian")),
            "submit_time": submit_t.isoformat() if submit_t else None,
            "resolve_time": resolve_t.isoformat() if resolve_t else None,
            "sla_hours": sla_hours,
            "escalated": escalated,
            "n_conversations": len(t.get("conversations", [])),
        })

    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(rows, f, ensure_ascii=False)

    # statistik singkat
    with_sla = [r for r in rows if r["sla_hours"] is not None]
    import statistics
    med = statistics.median(r["sla_hours"] for r in with_sla) if with_sla else 0
    print(f"Total tiket: {len(rows)}")
    print(f"Dengan SLA: {len(with_sla)}")
    print(f"Median SLA: {med:.1f} jam")
    print(f"Output: {OUT}")

if __name__ == "__main__":
    main()
