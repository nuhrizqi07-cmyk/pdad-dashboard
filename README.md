# Recap CEISACare

Rekap & Solusi Tiket CEISACare — dashboard analitik untuk Duktek PDAD KPPBC Tipe Madya Pabean A Pasuruan.

## Fitur

- **🔍 Cari Solusi** — cari kendala → panduan penanganan (dari sintesis 65 masalah) + tiket terkait
- **📊 Ringkasan** — tren tiket per bulan, distribusi kategori, top masalah, top perusahaan
- **⏱ SLA & Kinerja** — median waktu penyelesaian, distribusi bucket, kinerja per Duktek
- **📋 Eksplorasi Tiket** — tabel tiket dengan filter + download CSV

## Data

- `data/tickets_clean.json` — 4.296 tiket bersih (SLA sudah dihitung), rentang 08 Aug 2024 – 24 Nov 2026
- `data/synth_results.json` — 65 panduan masalah hasil sintesis LLM

Sumber data mentah: tiket CEISACare KPPBC Pasuruan (status Penyelesaian).

## Cara jalan lokal

```bash
cd /c/SaaS/My-SaaS/pdad-dashboard
venv/Scripts/python.exe -m streamlit run app.py
```

## Update data

**Cara untuk Mas (tanpa asisten): lihat [CARA-UPDATE.md](CARA-UPDATE.md).**
Paling singkat: dobel-klik `update.bat` di folder ini.

```bash
cd /c/SaaS/My-SaaS/pdad-dashboard
PY=venv/Scripts/python.exe

$PY update_data.py --check-token   # cek status token CEISACare
$PY update_data.py                 # collect + hitung SLA, tanpa push
$PY update_data.py --push          # + commit & push ke GitHub (app online ikut update)
$PY update_data.py --push --synth  # + sintesis panduan baru (DeepSeek, berbayar)
$PY refresh_token.py               # paksa minta token baru (email saja, tanpa 2FA)
```

### Alur update
1. **Token** — berlaku 24 jam. Kalau hilang/expired, `update_data.py` minta token baru otomatis lewat `refresh_token.py` (cukup email, tanpa kode 2FA — tapi harus di jaringan kantor).
2. **Collect** — `collect_cica.py` ambil semua tiket Penyelesaian (paralel 5 worker + retry + resume dari checkpoint).
3. **Prep** — `prep_data.py` hitung ulang SLA → `data/tickets_clean.json`.
4. **Synth** (opsional) — `synth_llm.py` sintesis masalah baru via DeepSeek → `data/synth_results.json`.
5. **Push** (wajib untuk app online) — commit + push ke GitHub → Streamlit Cloud deploy ulang sendiri.


> Catatan: `data/ceisacare_selesai_all.json` (raw ~15MB) tidak di-commit (di .gitignore).
> Yang di-commit: `tickets_clean.json` (2.7MB) + `synth_results.json` (96KB).

