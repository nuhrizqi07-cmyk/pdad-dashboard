# Cara Update Dashboard CEISACare (sendiri, tanpa asisten)

App: https://ceisacare.streamlit.app
Kode + data: `C:\SaaS\My-SaaS\pdad-dashboard`
Hosting: Streamlit Community Cloud (otomatis deploy ulang setiap ada push ke GitHub).

---

## 1. Cara tercepat: dobel-klik `update.bat`

1. Buka folder `C:\SaaS\My-SaaS\pdad-dashboard`.
2. Dobel-klik **`update.bat`**.
3. Jendela hitam terbuka, biarkan. Proses **10–15 menit**.
4. Di akhir akan muncul:
   - `[OK] Update selesai dan sudah dikirim ke GitHub` → berhasil.
   - `[GAGAL] ...` → ada error, jangan tutup jendela, salin pesannya.
5. Buka https://ceisacare.streamlit.app lalu tekan **Ctrl+F5** (hard refresh).

Syarat: **koneksi jaringan kantor** (server CEISACare = 10.161.6.188, tidak bisa dari luar).

---

## 2. Apa yang dijalankan script itu

`update.bat` → `update_data.py --push`, urutannya:

| Langkah | Yang dilakukan | Durasi |
|---|---|---|
| 0 | Cek token login. Kalau hilang/kedaluwarsa → minta token baru otomatis (cukup email, **tanpa kode 2FA**) | detik |
| 1 | Tarik daftar tiket status *Penyelesaian* + detailnya (`collect_cica.py`). Hanya tiket baru yang diunduh, yang lama dipakai ulang | 10–15 mnt |
| 2 | Hitung ulang SLA per tiket → `data/tickets_clean.json` (`prep_data.py`) | detik |
| 3 | Commit + push ke GitHub → Streamlit Cloud deploy ulang sendiri | detik |

Setelah push, app online biasanya ikut ter-update dalam 1–2 menit.

---

## 3. Cek berhasil atau tidak

Di halaman app, header kanan atas menampilkan:

```
4.296 tiket · 08 Aug 2024 — 24 Nov 2026 · data segar
```

Angka tiket harus **naik** dan tanggal akhir harus mendekati hari ini. Kalau tanggal akhir masih lama, berarti push/collect gagal — lihat bagian 4.

Cek tambahan lewat terminal:

```bash
cd /c/SaaS/My-SaaS/pdad-dashboard
git log --oneline -3          # harus ada commit "chore: update data tiket <tanggal>"
git status                    # harus bersih
```

---

## 4. Kalau gagal

| Gejala di jendela hitam | Artinya | Tindakan |
|---|---|---|
| `Gagal minta token baru` / `URLError` / `timed out` | Tidak tersambung ke server CEISACare | Pastikan di jaringan kantor / VPN, lalu ulangi |
| `HTTP 401` di tengah collect | Token kedaluwarsa saat proses jalan (jarang, token 24 jam) | Ulangi `update.bat` — otomatis minta token baru & lanjut dari titik terakhir |
| `PUSH GAGAL` | Push ke GitHub ditolak | Jalankan `git pull --rebase` lalu ulangi `update.bat`; kalau masih gagal, kabari asisten |
| `GAGAL menghitung ulang SLA` | `prep_data.py` error → data lama dipertahankan & push dibatalkan (sengaja, supaya dashboard tidak tampil dengan data basi) | Kirim isi pesan error ke asisten |
| Jalan normal tapi jumlah tiket sama | Memang tidak ada tiket selesai baru | Tidak perlu apa-apa |

Data mentah hasil tarikan ada di `data/ceisacare_selesai_all.json` (tidak di-commit, hanya lokal).
Kalau proses terputus, file itu dipakai sebagai checkpoint — membuka `update.bat` lagi akan melanjutkan, bukan mengulang dari nol.

---

## 5. Versi manual (kalau `update.bat` tidak jalan)

Buka **Git Bash** di folder project:

```bash
cd /c/SaaS/My-SaaS/pdad-dashboard
venv/Scripts/python.exe update_data.py --push
```

Perintah lain yang berguna:

```bash
venv/Scripts/python.exe update_data.py --check-token   # cek token masih valid / tidak
venv/Scripts/python.exe update_data.py                 # tarik + hitung SLA, TANPA push (uji dulu)
venv/Scripts/python.exe refresh_token.py               # paksa minta token baru
venv/Scripts/python.exe update_data.py --synth --push  # + sintesis panduan baru (DeepSeek, berbayar)
```

`--push` wajib kalau ingin app online ikut berubah. Tanpa `--push`, data hanya berubah di PC ini.

---

## 6. Soal `--synth` (panduan solusi)

Tanpa `--synth`: 65 panduan lama tetap dipakai, tiket baru hanya menambah statistik/SLA dan daftar tiket.
Dengan `--synth`: masalah-masalah baru diringkas ulang jadi panduan langkah-per-langkah via LLM DeepSeek → **memakai kuota API** dan menambah waktu beberapa menit. Pakai sesekali saja (mis. sebulan sekali), bukan tiap update.

---

## 7. Yang tidak disentuh `update.bat`

- Tampilan/`app.py` — perubahan desain atau fitur tetap lewat asisten + commit terpisah.
- Riwayat data yang sudah tidak ada di API — tidak dihapus, hanya bertambah.
- Folder `venv/`, `logs/`, file mentah besar — tidak di-commit (lihat `.gitignore`).
