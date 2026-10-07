# 08 — Roadmap

> Indeks: [README](./README.md) · Sebelumnya: [07 — Referensi Lokal](./07-referensi-lokal.md) · Berikutnya: [09 — Hosting & wp-admin](./09-hosting-wordpress.md)

Legenda: ✅ selesai · 🔄 berjalan · ⬜ berikutnya · 🔴 menunggu keputusan pemilik. Diperbarui: 7 Oktober 2026.

## Selesai (Okt 2026)

- ✅ Situs statis 6 halaman + pipeline berita/artikel (`build_posts.py`)
- ✅ Plugin Booking Survei (endpoint, wp-admin, CSV, rate limit) + README teknis
- ✅ Repo GitHub publik + devcontainer + GitHub Pages aktif — https://syncid.github.io/el-tahfidh/ (deploy otomatis dari `site/`)
- ✅ `referensi/` dikeluarkan dari tracking; histori git dibersihkan (`git filter-repo`; pack ±258 MB → ±20 MB)
- ✅ Dokumentasi `docs/` gaya roadmap.sh
- ✅ Alur kerja: push langsung ke `main` tanpa PR, `tools/sync.bat` untuk desktop (lihat `CLAUDE.md`, `docs/06` §6.6)
- ✅ Struktur organisasi resmi di `profil.html` dan beranda dari `data/struktur-organisasi.json` (`docs/13`)

## Selesai — Migrasi WordPress ke situs statis (Okt 2026)

- ✅ Paket `tools/eltahfidh/` (OOP, pustaka standar) untuk ekspor dan generator; lihat `tools/eltahfidh/README.md`
- ✅ Ekspor 7 situs WordPress (induk + 6 subdomain) ke `db/` lokal; `db/` tidak pernah di-commit
- ✅ Subdomain jenjang dipangkas menjadi halaman di dalam situs: `smp-quran.html`, `sma-quran.html`, `ifs.html`;
  isi SPMB digabung ke `psb.html`; menu "Profil" menaut ke dalam
- ✅ 327 halaman detail berita/artikel di `site/berita/` (293 situs induk + 34 subdomain) + peta alamat lama
  `data/peta-tautan.json`; 54 postingan alat interaktif dan "Hello world" tidak ikut
- ✅ Berkas impor WordPress (WXR) per situs di `db/wxr/` (belum diuji pada WordPress sungguhan)
- ✅ Cadangan media lengkap di desktop `C:\el-tahfidh\db\media\`: 2169 berkas, ±1,04 GB, 0 gagal
- ✅ Pemeriksa tautan internal `python -m tools.eltahfidh check-links` (berkas, jangkar `#`, `url()` di CSS)

## Berikutnya — Situs (`site/`)

- ⬜ Perbaiki 7 tautan rusak dari isi postingan WordPress (alamat absolut seperti `/pesantren-modern`)
  di `build-berita`: arahkan ke halaman statis bila ada di `data/peta-tautan.json`, selain itu ke alamat
  WordPress lengkap; hasil `check-links` 7 Okt 2026
- 🔴 Gambar berita masih diambil dari server WordPress. Bila WordPress akan dimatikan, gambar yang dipakai
  perlu disalin (dikompres) ke `site/assets/`. Butuh keputusan soal nasib WordPress dan ukuran repo
- 🔴 Halaman yang belum dimigrasi (`docs/11` §11.2): program pesantren (karakter/memanah/berkuda),
  e-brosur, dan 6 halaman alat (kalkulator zakat, QR, dan lain-lain): dibuat statis, tetap di WP, atau dimatikan
- 🔴 Pengalihan alamat lama WordPress ke halaman statis memakai `data/peta-tautan.json`; bergantung pada
  apakah domain `eltahfidh.or.id` akan diarahkan ke situs statis
- ⬜ Galeri foto (`site/galeri.html`, gaya header/footer `kontak.html`)
- ⬜ Optimasi gambar (kompresi ulang aset besar di `source-assets/` sebelum dipakai)

## Berikutnya — Plugin (`my-custom-app`)

- ⬜ Notifikasi admin tiap booking baru (email/WA) — saat ini hanya tercatat di DB
- ⬜ Halaman status booking untuk pendaftar (cek via kode/tiket)
- ⬜ Uji beban + hardening rate limiter sebelum musim PPDB
- ⬜ Migrasi data lama Google Sheets (opsional — saat ini tidak otomatis)

## Berikutnya — Operasional dan keamanan

- ⬜ Cabut dua Application Password akun `labib` yang dipakai selama ekspor (wp-admin → Profil)
- ⬜ Hapus catatan DNS mati `lp` dan `daurohsanadalfatihah` (keduanya 404)
- ⬜ Pulihkan akses email akun 20i (pemilik lupa email login)
- ⬜ CI ringan: `php -l`, uji `tools/eltahfidh`, dan `check-links` tiap push (tidak butuh Pages)
- ⬜ Jadwal backup `referensi/` lokal (bundle + salinan file) tiap ada update mirror
- ~~Branch protection + alur PR~~ — dibatalkan; pemilik memilih push langsung ke `main` (`docs/06` §6.4)

## Cara memakai roadmap ini dengan cloud session

Tempel satu item sebagai task di `claude.ai/code` dengan repo `syncid/el-tahfidh`,
misalnya: *"Kerjakan item galeri di docs/08-roadmap.md: tambah site/galeri.html …"*.
Aturan kerja Claude (diskusi dulu, push langsung ke `main`) ada di `CLAUDE.md`.
