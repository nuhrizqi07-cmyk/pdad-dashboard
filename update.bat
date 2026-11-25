@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=venv\Scripts\python.exe
if not exist "%PY%" set PY=python

echo ============================================================
echo   UPDATE DATA DASHBOARD CEISACARE
echo   https://ceisacare.streamlit.app
echo ============================================================
echo.
echo [info] Butuh koneksi jaringan kantor (apis-gw.beacukai.go.id).
echo [info] Proses 10-15 menit. Jangan tutup jendela ini.
echo.

"%PY%" update_data.py --push
set RC=%ERRORLEVEL%

echo.
if "%RC%"=="0" (
  echo [OK] Update selesai dan sudah dikirim ke GitHub.
  echo      Buka https://ceisacare.streamlit.app lalu tekan Ctrl+F5.
) else (
  echo [GAGAL] Ada error di atas - jangan tutup dulu, salin pesannya
  echo         lalu kirim ke asisten.
)
echo.
pause
