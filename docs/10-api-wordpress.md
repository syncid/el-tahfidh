# 10 — Peta API WordPress (`eltahfidh.or.id`)

> Indeks: [README](./README.md) · Sebelumnya: [09 — Hosting](./09-hosting-wordpress.md) · Berikutnya: [11 — Audit Migrasi](./11-audit-migrasi.md)

Dipetakan langsung dari indeks API hidup (`GET /wp-json/`, Okt 2026).
Total **355 rute**. Situs ini **WordPress self-hosted** — API ini milik situs sendiri,
bukan WordPress.com (lihat `docs/09` soal hosting 20i/StackCP).

## 10.1 Cara memakai API ini

Tanpa login (publik): baca konten — dipakai `tools/build_posts.py`.

```bash
curl 'https://eltahfidh.or.id/wp-json/wp/v2/posts?per_page=5&_fields=id,slug,title,link'
```

Dengan login (Application Password akun **Editor** — jangan Administrator):

```bash
# verifikasi identitas: harus terbaca roles=["editor"]
curl -u 'labib:KODE-APLIKASI' 'https://eltahfidh.or.id/wp-json/wp/v2/users/me'
```

Aturan main kredensial (detail di `docs/09`): buat dari akun Editor, simpan hanya di chat
(jangan di repo), **Revoke** setelah RnD selesai. Operasi tulis selalu minta izin dulu;
install plugin / kelola user / ubah pengaturan **tidak pernah** lewat kredensial ini —
itu tetap klik manual di wp-admin.

## 10.2 Kelompok rute (per namespace)

Legenda akses: 🌐 publik-baca · 🔑 perlu login (sesuai peran) · ⚠️ khusus.

| Namespace | Jumlah | Isi & fungsi | Akses |
|---|---|---|---|
| `wp/v2` (inti) | 124 | posts, pages, media, categories, tags, comments, users, menus, widgets, templates, settings, plugins, themes | 🌐 baca konten · 🔑 tulis & kelola |
| `rankmath/v1` | 86 | SEO: analisis on-page, sitemap, skema, redirections, AI-visibility | 🔑 |
| `google-site-kit/v1` | 58 | Analytics/Search Console/PSI: baca data & pengaturan modul | 🔑 |
| `elementor/v1` + `elementor-pro/v1` | 33 | template, globals (warna/tipografi), kit-defaults, site-editor, form-submissions | 🔑 (+ editor visual untuk desain) |
| `rttpg/v1` | 16 | The Post Grid (blok grid postingan) | 🔑 |
| `wp-site-health/v1` | 8 | tes server, ukuran direktori, cache | 🔑 |
| `wp-block-editor/v1`, `wp-abilities/v1` | 10 | kemampuan & tipe blok editor | 🔑 |
| `astra/v1` + `astra-addon/v1` | 5 | pengaturan tema Astra, custom layout | 🔑 |
| `bsf-core/v1` | 2 | lisensi/pengaturan produk Brainstorm Force | 🔑 |
| `nps-survey/v1` | 3 | survei internal plugin | 🔑 |
| `oembed/1.0` | 3 | embed konten WP di situs lain | 🌐 |
| `batch/v1` | 1 | gabung banyak request jadi satu | 🔑 |
| `mcp` | 3 | `mcp-adapter-default-server`, `mcp-oauth-server`, root | ⚠️ non-standar, abaikan untuk RnD |
| `eltahfidh/v1` | 2 | root + `elementor-clear-cache` (kemungkinan dari Landingplus) | 🔑 |

## 10.3 Rute inti yang dipakai RnD kita

| Kebutuhan | Endpoint | Catatan |
|---|---|---|
| Daftar berita/artikel | `GET /wp/v2/posts?categories=25&per_page=100&page=N` | header `X-WP-Total` / `X-WP-TotalPages` untuk loop; kategori 25=Berita (207), 59=Artikel (108) |
| 1 postingan | `GET /wp/v2/posts/<id>?_fields=id,slug,title,content,featured_media,…` | `content.rendered` = HTML siap tampil |
| Halaman statis | `GET /wp/v2/pages?per_page=100` | 32 halaman; konten pendek = layout di Elementor, bukan di `content` |
| Media | `GET /wp/v2/media?per_page=100` | upload 2,46 GB — unduh seperlunya saja |
| Uji tulis aman | `POST /wp/v2/posts` (status `draft`) → `DELETE /wp/v2/posts/<id>` (trash) | terbukti jalan Okt 2026 (draf `UJI-API-HAPUS` id 5947) |
| Info akun sendiri | `GET /wp/v2/users/me` | verifikasi role kredensial |

## 10.4 Batasan yang terbukti (bukan tebakan)

Terverifikasi langsung Okt 2026:

- `POST /wp/v2/settings` tanpa login → **401**; `POST /wp/v2/plugins` tanpa login → **400**.
  Tulis & kelola **wajib Application Password**.
- Rute `wp-site-health` untuk info server **tidak bisa diakses publik** (404 tanpa login) —
  fakta hosting di `docs/09` berasal dari paste Site Health manual, bukan API.
- Database (`sdb-73.hosting.stackcp.net`) **tidak resolve dari internet** (Non-existent
  domain di 8.8.8.8/1.1.1.1/9.9.9.9) dan port **3306 tertutup** dari luar — hanya bisa
  dijangkau dari dalam jaringan 20i. Bukti database hidup: situs HTTP 200 + query per
  ID (`/wp/v2/posts/5938`) mengembalikan data + `modified` terbaru.
- Tidak ada API untuk: ganti versi PHP, DNS/domain, file di luar `wp-content/uploads`,
  backup full server, password hosting — itu wilayah panel StackCP.

## 10.5 Pola kerja tetap (anti-tertinggal-update)

1. **Baca publik tiap sesi RnD** — indeks `/wp-json/` + daftar konten; kalau namespace
   baru muncul (plugin baru) atau kategori berubah, catat di sini.
2. **Tulis hanya dengan izin per tindakan**, mulai dari draf, verifikasi, lalu hapus.
3. **Jangan simpan kredensial di repo** — hanya di chat, revoke setelah selesai.
