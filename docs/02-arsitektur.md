# 02 — Arsitektur & Struktur Repo

> Indeks: [README](./README.md) · Sebelumnya: [01 — Ringkasan](./01-ringkasan.md) · Berikutnya: [03 — Menjalankan & Deploy](./03-menjalankan-deploy.md)

## 2.1 Peta repo (setelah `referensi/` dikeluarkan dari tracking)

```text
el-tahfidh/
├── site/                    # A. SITUS STATIS (di-deploy)
│   ├── index.html           # Beranda (blok <!-- POSTS:home --> diisi 3 berita)
│   ├── profil.html psb.html kontak.html
│   ├── berita.html artikel.html   # DIBANGUN ULANG oleh tools/build_posts.py
│   └── assets/
│       ├── img/posts/       # Thumbnail hasil unduhan build_posts.py
│       └── ...              # CSS, JS, font, gambar statis
├── wp-content/plugins/my-custom-app/  # B. PLUGIN WORDPRESS (di-deploy ke WP)
│   ├── my-custom-app.php    # Bootstrap plugin
│   ├── src/                 # PSR-4 MyCustomApp\ (Controllers, Services, Models, ...)
│   ├── views/admin/         # Layar wp-admin Booking Survei
│   ├── tests/smoke-test.php
│   ├── composer.json/.lock  # vendor/ TIDAK di-track
│   └── README.md            # Dokumentasi teknis plugin (rujukan utama)
├── tools/
│   ├── build_posts.py       # WP API publik → berita.html/artikel.html + thumbnail
│   ├── fixup.py             # Perbaikan pasca-HTTrack (dipakai .bat di bawah)
│   ├── mirror-kreativa.bat  # Update cermin Kreativa (Windows + WinHTTrack)
│   └── sync.bat             # Sinkron desktop ↔ GitHub main (lihat 06 §6.6)
├── source-assets/           # Aset mentah unduhan eltahfidh.or.id (arsip kerja)
├── docs/                    # Dokumentasi ini (gaya roadmap.sh)
├── .github/workflows/pages.yml  # Deploy site/ → Pages (AKTIF, lihat 06)
├── .devcontainer/           # Codespace: PHP 8.3 + Composer, Python 3, gh CLI
├── referensi/               # ⚠️ LOKAL SAJA, tidak di-track (lihat 07)
└── README.md                # Ringkasan umum + cara kerja cloud
```

Ukuran (Okt 2026): repo GitHub **~12 MB / ±130 file**; folder lokal `referensi/` **~379 MB / 1579 file** (di luar git).

## 2.2 Alur data

```text
[eltahfidh.or.id WP API publik] ──tools/build_posts.py──▶ site/berita.html, site/artikel.html,
                                                          site/index.html (3 berita), assets/img/posts/*

[Pengunjung form survei] ──POST JSON──▶ [eltahfidh.or.id/wp-json/my-custom-app/v1/survei/booking]
                                            │ (plugin: validasi → rate limit → simpan)
                                            ▼
                                    [tabel {prefix}mca_survey_bookings]
                                            │ dibaca via wp-admin "Booking Survei"
                                            ▼ (ekspor CSV)
```

Form publik di-host di `https://eltahfidh.github.io/survei/` (repo terpisah, bukan repo ini);
kontrak request/respons disamakan dengan Google Apps Script lama — detail di README plugin.

## 2.3 Dependensi antar bagian

| Dari → ke | Sifat | Keterangan |
|---|---|---|
| `tools/build_posts.py` → `site/*.html` | Tulis langsung | `berita.html`/`artikel.html` **jangan diedit manual** — akan ditimpa |
| `site/index.html` → WP API | Runtime build-time | Hanya saat skrip dijalankan; situs hasil statis penuh |
| Plugin → WordPress core | Runtime | WP 6.2+, PHP 8.1+, ekstensi mbstring |
| Plugin → form GitHub | Kontrak API | Satu baris `API_URL` di `index.html` form |
| `.bat`/`fixup.py` → `referensi/` | Lokal saja | Tidak ada ketergantungan dari produk A/B ke `referensi/` |
| Codespace → plugin | Setup | `composer install` otomatis via `onCreateCommand` |

**Aturan emas:** tidak ada bagian produk (site/plugin/tools inti) yang membaca `referensi/` —
folder itu murni bahan perbandingan tata letak untuk manusia.
