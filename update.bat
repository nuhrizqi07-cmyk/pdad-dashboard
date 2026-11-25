@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=venv\Scripts\python.exe
if not exist "%PY%" set PY=python

REM Git TIDAK ada di PATH registry PC ini, dan git bawaan Hermes tidak bisa
REM dipanggil dari cmd. Tambahkan Git for Windows sendiri di depan PATH,
REM kalau tidak, langkah push akan gagal ("Access is denied" / not found).
for %%G in ("%ProgramFiles%\Git\cmd" "%ProgramFiles(x86)%\Git\cmd" "%LOCALAPPDATA%\Programs\Git\cmd") do (
  if exist "%%~G\git.exe" if not defined GITDIR set "GITDIR=%%~G"
)
if defined GITDIR set "PATH=%GITDIR%;%PATH%"

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
