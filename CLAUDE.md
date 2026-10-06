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

## Cara mengirim perubahan (aturan dua jalur)

| Perubahan | Cara kirim |
|---|---|
| Hanya `docs/`, `README.md`, atau `CLAUDE.md` | Push langsung ke `main`, tanpa pull request |
| `site/`, `wp-content/` (plugin), `tools/`, `.github/`, atau campuran | Cabang `claude/...` lalu pull request; pemilik yang menggabung |

Alasan: push ke `site/**` di `main` langsung memicu deploy GitHub Pages, dan perubahan
plugin bisa merusak situs produksi.

- Sebelum push, tampilkan daftar berkas yang berubah.
- Identitas commit: penulis `sync.id <idsyhl@gmail.com>`, pencatat
  `Claude <noreply@anthropic.com>`:
  `git -c user.name=Claude -c user.email=noreply@anthropic.com commit --author="sync.id <idsyhl@gmail.com>"`
- Jika alat GitHub untuk membuat pull request gagal, berikan tautan
  `https://github.com/syncid/el-tahfidh/pull/new/<cabang>` agar pemilik membukanya sendiri.
- Jika pull request sebuah cabang sudah digabung, mulai ulang cabang itu dari `main` terbaru.
- Kerjakan hanya repo `syncid/el-tahfidh`.

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
