@echo off
rem ============================================================
rem  HTTrack mirror: kreativaglobal.sch.id (WordPress + Divi)
rem  Output : C:\el-tahfidh\referensi\kreativa-mirror
rem  Jalankan ulang untuk update (HTTrack otomatis melanjutkan/memperbarui).
rem ============================================================
setlocal
set HTTRACK="C:\Program Files\WinHTTrack\httrack.exe"
set OUT=C:\el-tahfidh\referensi\kreativa-mirror

%HTTRACK% ^
  "https://kreativaglobal.sch.id/" ^
  "https://kreativaglobal.sch.id/id/beranda/" ^
  "https://kreativaglobal.sch.id/admission/" ^
  "https://kreativaglobal.sch.id/academic-experience/" ^
  "https://kreativaglobal.sch.id/academic/" ^
  "https://kreativaglobal.sch.id/admission-info/" ^
  "https://kreativaglobal.sch.id/article-news/" ^
  "https://kreativaglobal.sch.id/author/cnt/" ^
  "https://kreativaglobal.sch.id/author/kgsid/" ^
  "https://kreativaglobal.sch.id/blank/how-to-apply/" ^
  "https://kreativaglobal.sch.id/category/blank/" ^
  "https://kreativaglobal.sch.id/category/course-catalog-content/" ^
  "https://kreativaglobal.sch.id/category/course-catalog/" ^
  "https://kreativaglobal.sch.id/category/uncategorized/" ^
  "https://kreativaglobal.sch.id/course-catalog-content/course-catalog-1/" ^
  "https://kreativaglobal.sch.id/course-catalog/subject-catalog/" ^
  "https://kreativaglobal.sch.id/faq/" ^
  "https://kreativaglobal.sch.id/home/" ^
  "https://kreativaglobal.sch.id/id/7-habits-form/" ^
  "https://kreativaglobal.sch.id/id/akademik/" ^
  "https://kreativaglobal.sch.id/id/artikel-berita/" ^
  "https://kreativaglobal.sch.id/id/beranda-lama/" ^
  "https://kreativaglobal.sch.id/id/category/uncategorized-id/" ^
  "https://kreativaglobal.sch.id/id/kehidupan-kampus/" ^
  "https://kreativaglobal.sch.id/id/kreativa-global-daily/" ^
  "https://kreativaglobal.sch.id/id/parenting-feedback/" ^
  "https://kreativaglobal.sch.id/id/tanya-jawab/" ^
  "https://kreativaglobal.sch.id/id/teachers-daily/" ^
  "https://kreativaglobal.sch.id/id/tk-kreativa-global/" ^
  "https://kreativaglobal.sch.id/id/uncategorized-id/membangun-ketangguhan-dari-kompetisi-olahraga-menuju-pendidikan-holistik/" ^
  "https://kreativaglobal.sch.id/junior-college/" ^
  "https://kreativaglobal.sch.id/kindergarten-play/" ^
  "https://kreativaglobal.sch.id/our-building/" ^
  "https://kreativaglobal.sch.id/student-life-2/" ^
  "https://kreativaglobal.sch.id/student-life/" ^
  "https://kreativaglobal.sch.id/uncategorized/building-resilience-from-sports-competitiveness-towards-holistic-education/" ^
  "https://kreativaglobal.sch.id/id/sd-kreativa-global/" ^
  "https://kreativaglobal.sch.id/id/smp-kreativa-global/" ^
  "https://kreativaglobal.sch.id/id/tk/" ^
  "https://kreativaglobal.sch.id/id/sma/" ^
  "https://kreativaglobal.sch.id/id/tentang/" ^
  "https://kreativaglobal.sch.id/id/registrasi/" ^
  "https://kreativaglobal.sch.id/id/karir/" ^
  -O "%OUT%" ^
  -a -r12 -K0 -%%P -%%k -%%v -c4 -T30 -R3 -s2 -I0 ^
  -F "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" ^
  "+kreativaglobal.sch.id/*" ^
  "+*.png" "+*.gif" "+*.jpg" "+*.jpeg" "+*.webp" "+*.svg" "+*.ico" ^
  "+*.css" "+*.js" "+*.woff" "+*.woff2" "+*.ttf" "+*.otf" "+*.eot" ^
  "+*.mp4" "+*.webm" ^
  "+cdnjs.cloudflare.com/*" "+unpkg.com/*" "+code.jquery.com/*" ^
  "+fonts.googleapis.com/*" "+fonts.gstatic.com/*" ^
  "-*/wp-admin/*" "-*/wp-login.php*" "-*xmlrpc.php*" "-*/wp-json/*" ^
  "-*/feed/*" "-*/comments/*" "-*?replytocom=*" ^
  "-*googletagmanager.com*" "-*cloudflareinsights.com*" "-ad.doubleclick.net/*"

python "%~dp0fixup.py"

echo.
echo Selesai. Buka: %OUT%\kreativaglobal.sch.id\index.html
