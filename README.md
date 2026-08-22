# Recap CEISACare

Rekap & Solusi Tiket CEISACare — dashboard analitik untuk Duktek PDAD KPPBC Tipe Madya Pabean A Pasuruan.

## Fitur

- **🔍 Cari Solusi** — cari kendala → panduan penanganan (dari sintesis 65 masalah) + tiket terkait
- **📊 Ringkasan** — tren tiket per bulan, distribusi kategori, top masalah, top perusahaan
- **⏱ SLA & Kinerja** — median waktu penyelesaian, distribusi bucket, kinerja per Duktek
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
# pakai venv project-perbaikan
VPY="/run/media/noah/Data/My SaaS/project-perbaikan/venv/bin/python"

# cek status token CEISACare
"$VPY" update_data.py --check-token

# update lengkap (collect + SLA), tanpa push
"$VPY" update_data.py

# update + commit push ke GitHub
"$VPY" update_data.py --push

# update + sintesis masalah baru (LLM DeepSeek)
"$VPY" update_data.py --push --synth
```

### Alur update
1. **Token** — CEISACare token 24 jam. Kalau expired, login ulang dulu (minta asisten: "login CEISACare" — butuh kode 2FA).
2. **Collect** — `collect_cica.py` ambil semua tiket Penyelesaian (paralel 5 worker + retry + resume).
3. **Prep** — `prep_data.py` hitung ulang SLA → `data/tickets_clean.json`.
4. **Synth** (opsional) — `synth_llm.py` sintesis masalah baru via DeepSeek → `data/synth_results.json`.
5. **Push** (opsional) — commit + push ke GitHub.

> Catatan: `data/ceisacare_selesai_all.json` (raw ~15MB) tidak di-commit (di .gitignore).
> Yang di-commit: `tickets_clean.json` (2.7MB) + `synth_results.json` (96KB).

