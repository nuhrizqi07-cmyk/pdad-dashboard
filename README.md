# Dashboard PDAD Interaktif

Dashboard analitik tiket CEISACare untuk KPPBC Tipe Madya Pabean A Pasuruan.

## Fitur

- **📊 Ringkasan** — tren tiket per bulan, distribusi kategori, top masalah, top perusahaan
- **⏱️ SLA & Kinerja** — median waktu penyelesaian, distribusi bucket, kinerja per Duktek
- **🔍 Search Solusi** — cari kendala → panduan penanganan (dari sintesis 65 masalah) + tiket terkait
- **📋 Eksplorasi Tiket** — tabel tiket dengan filter + download CSV

## Data

- `data/tickets_clean.json` — 3.807 tiket bersih (SLA sudah dihitung)
- `data/synth_results.json` — 65 panduan masalah hasil sintesis LLM

Sumber data mentah: tiket CEISACare KPPBC Pasuruan (status Penyelesaian).

## Cara jalan lokal

```bash
# pakai venv yang sudah ada (contoh project-perbaikan)
/run/media/noah/Data/My\ SaaS/project-perbaikan/venv/bin/streamlit run app.py
```

## Update data

```bash
# ambil ulang tiket CEISACare → prep_data.py akan regenerate tickets_clean.json
/run/media/noah/Data/My\ SaaS/project-perbaikan/venv/bin/python prep_data.py
```
