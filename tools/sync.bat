@echo off
REM Sinkronkan salinan desktop dengan GitHub (cabang main).
REM Pakai: klik dua kali sebelum mulai kerja dan setiap kali Claude selesai push.
cd /d "%~dp0.."

REM Berhenti jika masih ada perubahan yang belum di-commit.
for /f "delims=" %%i in ('git status --porcelain') do goto kotor

git checkout main || goto gagal
git pull --ff-only origin main || goto gagal
git worktree prune

echo.
echo Selesai. Tiga commit terakhir:
git log --oneline -3
pause
exit /b 0

:kotor
echo Masih ada perubahan yang belum di-commit:
git status --short
echo Commit atau buang dulu perubahan itu, lalu jalankan lagi.
pause
exit /b 1

:gagal
echo Sinkron gagal. Baca pesan di atas.
pause
exit /b 1
