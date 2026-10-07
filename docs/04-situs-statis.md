# 04 — Panduan Situs Statis (`site/`)

> Indeks: [README](./README.md) · Sebelumnya: [03 — Menjalankan & Deploy](./03-menjalankan-deploy.md) · Berikutnya: [05 — Plugin WordPress](./05-plugin-wordpress.md)

## 4.1 Anatomi halaman

Semua halaman berbagi kerangka header/footer yang sama (disalin dari `kontak.html`
sebagai acuan). Daftar halaman: `index.html` (beranda), `profil.html`, `psb.html`
(penerimaan santri), `kontak.html`, `berita.html`, `artikel.html`, serta tiga halaman
jenjang pengganti subdomain: `smp-quran.html`, `sma-quran.html`, `ifs.html`.

- **Edit manual yang aman:** `index.html`, `profil.html`, `psb.html`, `kontak.html`,
  dan segala di `assets/` kecuali `assets/img/posts/`.
- **JANGAN edit manual:** `berita.html`, `artikel.html`, dan blok
  `<!-- POSTS:home -->` di `index.html` — ketiganya ditulis ulang oleh
  `tools/build_posts.py`.
- **JANGAN edit manual:** `smp-quran.html`, `sma-quran.html`, `ifs.html` — dibangun
  oleh `python -m tools.eltahfidh build-jenjang` dari `data/jenjang.json` (isi),
  `data/struktur-organisasi.json` (pimpinan), dan berita subdomain di `db/` lokal.
  Ubah isinya di `data/jenjang.json`, lalu bangun ulang (lihat `tools/eltahfidh/README.md`).
- Menu "Profil" di semua halaman menaut ke ketiga halaman jenjang itu, bukan lagi ke
  subdomain `smpquran`, `smpquranputri`, `smaquran`, `smaquranputri`, dan IFS.

## 4.2 Pipeline berita & artikel

```bash
python tools/build_posts.py
```

Kerja skrip (stdlib Python saja — `urllib`, `html`, `json`, `re`, `pathlib`):

1. `GET https://eltahfidh.or.id/wp-json/wp/v2/posts` — 12 terbaru kategori 25 (Berita)
   dan 59 (Artikel), dengan label, judul, deskripsi, dan heading per konfigurasi `PAGES`.
2. Unduh thumbnail **sekali saja** ke `site/assets/img/posts/<id>.<ext>` (dilewati bila sudah ada).
3. Bangun ulang `berita.html` + `artikel.html` dari kerangka `kontak.html`.
4. Isi 3 berita terbaru ke blok `<!-- POSTS:home -->` di `index.html`.

Jalankan ulang kapan saja untuk refresh konten. Bulan tampil berbahasa Indonesia
(daftar `BULAN`: Januari–Desember).

## 4.3 Aset

| Lokasi | Isi | Catatan |
|---|---|---|
| `assets/img/posts/` | Thumbnail hasil skrip | Hasil generate — boleh dihapus, dibuat ulang saat skrip jalan |
| `assets/` lainnya | CSS, JS, font (woff/woff2), gambar | Edit manual, ikut di-deploy |
| `source-assets/` (root) | File mentah unduhan `eltahfidh.or.id` | Arsip kerja sebelum dipakai di `site/`; bukan bagian deploy |

Konvensi penamaan aset mengikuti sumber unduhan (mis. `*-1024x682.jpg`) agar mudah
dilacak kembali ke aslinya.
