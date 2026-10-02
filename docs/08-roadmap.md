# 08 — Roadmap

> Indeks: [README](./README.md) · Sebelumnya: [07 — Referensi Lokal](./07-referensi-lokal.md) · Berikutnya: —

Legenda: ✅ selesai · 🔄 berjalan · ⬜ berikutnya. Diperbarui: Oktober 2026.

## Selesai (Okt 2026)

- ✅ Situs statis 6 halaman + pipeline berita/artikel (`build_posts.py`)
- ✅ Plugin Booking Survei (endpoint, wp-admin, CSV, rate limit) + README teknis
- ✅ Repo GitHub privat + devcontainer + workflow Pages (siap, nonaktif)
- ✅ `referensi/` dikeluarkan dari tracking (repo ringan, tetap ada lokal + backup)
- ✅ Dokumentasi `docs/` gaya roadmap.sh (file ini)

## Berjalan / berikutnya — Situs (`site/`)

- ⬜ Galeri foto (`site/galeri.html`, gaya header/footer `kontak.html`) — kandidat task cloud session pertama
- ⬜ Validasi link internal otomatis tiap ada halaman baru (skrip kecil di `tools/`)
- ⬜ Optimasi gambar (kompresi ulang aset besar di `source-assets/` sebelum dipakai)
- ✅ GitHub Pages aktif — https://syncid.github.io/el-tahfidh/ (deploy otomatis dari `site/`)

## Berjalan / berikutnya — Plugin (`my-custom-app`)

- ⬜ Notifikasi admin tiap booking baru (email/WA) — saat ini hanya tercatat di DB
- ⬜ Halaman status booking untuk pendaftar (cek via kode/tiket)
- ⬜ Uji beban + hardening rate limiter sebelum musim PPDB
- ⬜ Migrasi data lama Google Sheets (opsional — saat ini tidak otomatis)

## Berjalan / berikutnya — Operasional

- ⬜ CI ringan: `php -l` + smoke test tiap push (tidak butuh Pages)
- ⬜ Branch protection + alur PR (repo sudah publik — proteksi siap dipasang)
- ✅ Histori git bersih dari blob `referensi/` (`git filter-repo`; pack ±258 MB → ±20 MB,
  0 objek `referensi/` di seluruh histori)
- ⬜ Jadwal backup `referensi/` lokal (bundle + salinan file) tiap ada update mirror

## Cara memakai roadmap ini dengan cloud session

Tempel satu item sebagai task di `claude.ai/code` dengan repo `syncid/el-tahfidh`,
misalnya: *"Kerjakan item galeri di docs/08-roadmap.md: tambah site/galeri.html …
Selesai = …, tulis log di SESSION_LOG.md."* Kredit cloud ($100 Pro / $250 Max)
terpakai otomatis per sesi.
