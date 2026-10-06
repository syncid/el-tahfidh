# Aturan kerja Claude di repo elTAHFIDH

Berkas ini dibaca otomatis di setiap sesi. Isinya kesepakatan dengan pemilik repo;
ikuti tanpa perlu dijelaskan ulang.

## Cara berkomunikasi

- Pakai bahasa Indonesia dengan kalimat lengkap (subjek, predikat, objek, keterangan).
  Jangan memotong-motong penjelasan menjadi potongan kata yang mudah disalahpahami.
- Singkat dan langsung ke inti.
- **Jangan langsung mengeksekusi.** Diskusikan dulu dan tunggu konfirmasi. Kata pemicu
  eksekusi: "gas", "oke", "REVISI SEMUA", atau persetujuan yang jelas untuk usulan tertentu.
  Membaca berkas dan permintaan baca (GET) boleh tanpa konfirmasi.
- Jangan mendesak pemilik untuk segera memberi kata pemicu.
- Bedakan dengan jelas apa yang sudah terbukti dan apa yang masih dugaan.

## Cara mengirim perubahan

Keputusan pemilik (Okt 2026): **semua perubahan dikirim langsung ke `main`, tanpa pull
request**, setelah pemilik memberi "oke". Jangan membuat cabang atau pull request kecuali
pemilik memintanya.

- Sebelum push, tampilkan daftar berkas yang berubah dan tunggu "oke".
- Ingat dampaknya: push yang menyentuh `site/**` langsung men-deploy GitHub Pages
  (`syncid.github.io/el-tahfidh`). Kode plugin di `main` **tidak** otomatis terpasang di
  WordPress; plugin dipasang manual lewat wp-admin (lihat `docs/09-hosting-wordpress.md`).
- Identitas commit: penulis `sync.id <idsyhl@gmail.com>`, pencatat
  `Claude <noreply@anthropic.com>`:
  `git -c user.name=Claude -c user.email=noreply@anthropic.com commit --author="sync.id <idsyhl@gmail.com>"`
- Jangan memasang workflow GitHub Actions yang menjalankan agen AI lalu commit otomatis;
  itu melanggar aturan "diskusikan dulu".
- Kerjakan hanya repo `syncid/el-tahfidh`.

## Sinkronisasi

`main` di GitHub adalah satu-satunya sumber kebenaran. Desktop pemilik (`C:\el-tahfidh`)
dan sesi cloud hanya mengambil dari sana dan mengirim ke sana.

- Di awal sesi: jalankan `git fetch origin main` dan pastikan bekerja di atas `main` terbaru.
- Sebelum push: jalankan `git pull --ff-only origin main` agar tidak menimpa kerja pemilik.
- Setelah setiap push: ingatkan pemilik untuk menjalankan `tools\sync.bat` (atau `git pull`)
  di desktop.
- Jika sesi dimulai dari commit "WIP: uncommitted changes, moved to the cloud", jangan
  mengirimnya apa adanya; diskusikan dulu isinya dengan pemilik.

## Kredensial

- Jangan pernah menyimpan kredensial (Application Password WordPress dan sejenisnya)
  di berkas atau repo. Lewatkan hanya melalui variabel lingkungan dalam satu perintah.
- Akun WordPress yang dipakai: Editor `labib`. Akses Administrator hanya diminta bila
  benar-benar perlu, dengan alasan dan dampak yang dijelaskan dulu.
- Setiap penulisan ke WordPress wajib menunggu persetujuan pemilik.

## Peta singkat proyek

- `site/`: situs statis. `berita.html`, `artikel.html`, dan blok `<!-- POSTS:home -->` di
  `index.html` dibangun ulang oleh `tools/build_posts.py`; jangan diedit manual.
- `wp-content/plugins/my-custom-app/`: plugin WordPress OOP. Lihat `docs/12-oop-plugin.md`.
- `docs/`: dokumentasi bernomor (01, 02, ...), satu topik satu berkas, dengan navigasi
  Sebelumnya/Berikutnya dan indeks di `docs/README.md`.
- `referensi/`: hanya ada di komputer lokal pemilik, tidak di-track git.
