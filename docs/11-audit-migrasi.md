# 11 — Audit Migrasi: 32 Halaman + 327 Postingan

> Indeks: [README](./README.md) · Sebelumnya: [10 — Peta API](./10-api-wordpress.md) · Berikutnya: [12 — Panduan OOP Plugin](./12-oop-plugin.md)

Inventaris penuh dari REST API publik (Okt 2026): **32 halaman**, **327 postingan**
(206 Berita + 108 Artikel + 13 lintas/arsip lain), **20 kategori**.
Kolom "Keputusan" = rekomendasi awal — angka final menunggu 3 keputusan pemilik
(halaman tool, 326 arsip, akses 20i).

## 11.1 Ringkasan angka

| Kelompok | Jumlah | Format konten | Catatan |
|---|---|---|---|
| Halaman WP | 32 | mayoritas Elementor (`chars` kecil = layout di DB, bukan di `content`) | 4 halaman nyaris kosong di `content` (layout 100% Elementor) |
| Berita (kat. 25) | 206 | **0 blok Gutenberg** — klasik/shortcode/Elementor | rentang Agu 2025 → Okt 2026 |
| Artikel (kat. 59) | 108 | sama | sama |
| Gambar unggulan | 277/327 punya | — | 50 postingan tanpa gambar → pakai fallback |
| Excerpt | semua ada (≥20 char) | — | siap jadi ringkasan kartu |

## 11.2 Peta 32 halaman → situs statis

Legenda: 🟢 tulis manual sekali · 🟡 otomatis dari API · 🔴 butuh keputusan.

| # | Slug WP | Isi (perkiraan) | Pasangan di `site/` | Keputusan |
|---|---|---|---|---|
| 1 | `home-ei` (= `/`) | Beranda 65 ribu char — Elementor penuh | `index.html` ✅ ada | 🟢 sinkron manual berkala |
| 2 | `profil` | Profil | `profil.html` ✅ ada | 🟢 |
| 3 | `psb` | PSB (8 ribu char) | `psb.html` ✅ ada | 🟢 |
| 4 | `kontak-kami` | Kontak (teks pendek — form/widget Elementor?) | `kontak.html` ✅ ada | 🟢 cek form kontaknya |
| 5 | `home-page-eltahfidh-indonesia` | Duplikat beranda lama (64 ribu char) | — | 🔴 arsipkan/redirect ke `/` |
| 6 | `program` | konten kosong (menu container?) | — | 🔴 cek menu WP, mungkin hapus |
| 7 | `spmb-sitem-penerimaan-murid-baru-…` | SPMB panjang | gabung ke `psb.html`? | 🟢 gabung manual |
| 8 | `e-brochure` | e-brosur (teks pendek — file unduhan?) | link aset di `psb.html`? | 🔴 cek file unduhannya |
| 9–16 | `smp/sma-quran-…-putra/putri` (4), `boarding-school-islam-2`, `smp/sma-islam-boarding`, `islamic-fullday-school-…` | Halaman tiap jenjang (2–15 ribu char) | nav statis menaut ke subdomain (`smpquran.eltahfidh.or.id` …) | 🔴 putuskan: tetap di WP/subdomain, atau dibuatkan halaman statis |
| 17–19 | `pesantren-karakter/memanah/berkuda`, `full-day-school-islam` | Program pesantren (14–17 ribu char) | belum ada | 🟢 buat bila program aktif |
| 20 | `pp-17-agustus-2025-eltahfidh` | Event sekali jalan | — | 🔴 arsipkan |
| 21–23 | `rencana-kegiatan`, `rencana-kegiatan-dan-bahan-berita`, `bahan-berita-baru` | Halaman kerja internal (bukan untuk publik) | — | 🔴 **jangan migrasi**; sembunyikan dari sitemap |
| 24 | `ujian-tulisan-dauroh-sanad-alfatihah-…` | Halaman ujian internal | — | 🔴 sama seperti 21–23 |
| 25 | `2-2` | Tidak jelas (54 char) | — | 🔴 hapus/redirect |
| 26–31 | 6 halaman tool (`kalkulator-zakat`, `alquran-digital`, `convert-to-webp`, `generator-qr`, `generator-stiker-wa`, `voice-to-text-note`) | Utilitas JS, semua Elementor | — | 🔴 **keputusan pemilik**: pindah sebagai halaman JS statis / tetap di WP / matikan |
| 32 | `islamic-fullday-school-eltahfidh` | Duplikat tema fullday | gabung ke program? | 🟢 |

## 11.3 Peta 327 postingan → situs statis

- **12 Berita + 12 Artikel terbaru** → `berita.html`, `artikel.html`, 3 kartu di beranda
  (mekanisme ini **sudah jalan** via `tools/build_posts.py`).
- **Halaman detail per postingan** (`/berita/<slug>/`) → dibuat generator (rencana Cara A).
  Perhatian: **0 postingan memakai blok Gutenberg** — isi adalah HTML klasik/shortcode,
  jadi generator harus membersihkan shortcode sisa, bukan mengandalkan parser blok.
- **±300 arsip lama** (Agu 2025 ke belakang) → opsi: (a) tetap dilayani WP sebagai arsip,
  (b) migrasikan semua jadi statis. Lihat keputusan pemilik #2.
- **Kategori non-berita/artikel** (program, akademik, latihan-kepemimpinan, boarding-*,
  kajian, ubudiyah, taekwondo, …) → **jangan ikut** ke `berita.html`/`artikel.html`;
  kalau mau ditampilkan, buat indeks tersendiri per kebutuhan.
- **50 postingan tanpa gambar unggulan** → kartu memakai gambar fallback.

## 11.4 Yang harus dibersihkan di WP (terlepas dari arah migrasi)

1. Halaman `2-2`, `program` (kosong), `home-page-eltahfidh-indonesia` (duplikat beranda).
2. Halaman kerja internal (21–24) sebaiknya di-`noindex`/dijadikan privat.
3. 3 plugin nonaktif (Elfsight WhatsApp, Quotes and Tips, Site Mailer) aman dihapus.
4. Kategori kosong (`berenang`, `berkuda-memanah` = 0 postingan) bisa dihapus.

## 11.5 Jejak verifikasi (bukti, bukan klaim)

- `GET /wp-json/` → 355 rute (per-namespace: `wp` 124, `rankmath` 86, `site-kit` 58,
  `elementor` 33, `rttpg` 16, `wp-site-health` 8, `astra` 5, `mcp` 3, `eltahfidh` 2…).
- `POST /wp/v2/settings` tanpa login → 401; `POST /wp/v2/plugins` → 400 (tulis wajib login).
- `sdb-73.hosting.stackcp.net` tidak resolve publik; port 3306 tertutup dari luar.
- Siklus tulis aman terbukti: draf `UJI-API-HAPUS` id 5947 dibuat → trash → terverifikasi.
- Kredensial dipakai: Application Password akun **Editor** `labib` (bukan admin);
  **tidak disimpan di repo**, revoke setelah RnD.
