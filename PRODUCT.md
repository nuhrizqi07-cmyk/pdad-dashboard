# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Duktek (dukungan teknis) KPPBC Tipe Madya Pabean A Pasuruan. Situasi: sedang menangani tiket/permintaan bantuan CEISACare dari pengguna, butuh jawaban cepat atas kendala yang sedang dihadapi — "bagaimana cara menangani ini".

## Product Purpose

Dashboard kerja internal yang mengubah 3.800+ tiket CEISACare + 65 panduan solusi hasil sintesis menjadi alat kerja harian: mencari solusi atas kendala teknis, memantau volume & SLA penanganan, dan menelusuri riwayat tiket. Sukses = Duktek menemukan panduan penanganan yang tepat dalam hitungan detik, bukan menit.

## Positioning

Search engine solusi yang dilatih dari pengalaman nyata tiket internal — bukan sekadar statistik. Nilai uniknya: jawaban operasional siap pakai (langkah penanganan) yang bersumber dari masalah yang benar-benar terjadi di unit ini.

## Operating Context

- Dipakai di jam kerja, di depan layar, sambil menangani panggilan/chat bantuan.
- Sering dibuka cepat: "ini kendalanya, cari solusinya" → harus langsung ketemu.
- Data diperbarui berkala (collect + SLA + sintesis LLM DeepSeek) via `update_data.py`.
- Di-host Streamlit Community Cloud (ceisacare.streamlit.app), diakses via browser.

## Capabilities and Constraints

- 4 area: Ringkasan, SLA & Kinerja, Search Solusi, Eksplorasi Tiket.
- Search Solusi = fitur inti: pencarian fuzzy (token) atas 65 panduan + tiket terkait.
- Data statis dari JSON (tickets_clean.json, synth_results.json), di-cache 1 jam.
- Stack: Streamlit (>=1.60) + pandas (>=3.0). Tanpa backend/database eksternal.
- Tanpa autentikasi — dashboard internal, ekspos publik via Streamlit Cloud.
- SLA dihitung dalam jam (sla_hours).

## Brand Commitments

Belum ada identitas visual yang mengikat. Pengguna memberi kebebasan penuh untuk redesign ("surprised me") — tema baru boleh menyimpang dari tampilan Streamlit default.

## Evidence on Hand

- `data/tickets_clean.json` — 3.807 tiket bersih (status Penyelesaian), kolom: nomor_tiket, tanggal, tanggal_dt, pelapor, katalog, masalah, probis, duktek, uraian, sla_hours, submit_time, resolve_time, bulan.
- `data/synth_results.json` — 65 panduan masalah (masalah, ringkasan, langkah[], catatan, jumlah).
- Repo GitHub publik: nuhrizqi07-cmyk/pdad-dashboard.

## Product Principles

1. Jawaban di depan: kendala → solusi dalam <3 detik interaksi.
2. Scanability di atas segalanya: dashboard kerja, bukan pameran.
3. Data nyata unit sendiri adalah sumber kebenaran; jangan mengarang angka.
4. Tiap klik harus membawa nilai — tidak ada halaman mati.
5. Konsisten dan tenang: tidak ada yang berkedip-kedip tanpa alasan.

## Accessibility & Inclusion

- Kontras teks vs latar memadai untuk penggunaan di kantor dengan pencahayaan beragam.
- Hierarki visual jelas tanpa mengandalkan warna saja (label ikon + teks).
