# `tools/eltahfidh` — ekspor WordPress dan generator situs

Paket Python (pustaka standar saja) untuk:

1. **Mengekspor** konten WordPress elTAHFIDH (situs induk dan 6 subdomain) ke folder
   lokal `db/`, yaitu "database" proyek ini.
2. **Mencadangkan** berkas media ke `db/media/`.
3. (fase berikutnya) Membangun halaman statis `site/` dan berkas impor WordPress (WXR) dari `db/`.

`tools/build_posts.py` tetap berdiri sendiri dan tidak bergantung pada paket ini.

## Aturan `db/`

- `db/` **hanya ada di lokal** (desktop `C:\el-tahfidh\db\` atau sesi cloud) dan
  **diabaikan Git** (`.gitignore`: `/db/`). Jangan pernah di-commit.
- Isinya mencakup draf yang belum terbit dan daftar pengguna. Email pengguna, email/IP
  komentator, dan email admin **dibuang** sebelum disimpan.
- Lokasi lain bisa dipakai lewat env `ELTAHFIDH_DB`.

```text
db/
  README.txt, manifest.json
  utama/                  situs induk: site, settings, posts, pages, categories, tags, media, menus, menu-items
  utama/private/          drafts-posts, drafts-pages, users, comments
  jenjang/<key>/          6 subdomain: site, posts, pages, categories, tags, media
  media/<host>/<yyyy>/<mm>/   berkas media hasil `media`
```

## Perintah (jalankan dari akar repo)

```bash
python -m tools.eltahfidh export                    # semua situs
python -m tools.eltahfidh export --sites utama,spmb # sebagian
python -m tools.eltahfidh export --no-private       # tanpa draf/pengguna/komentar
python -m tools.eltahfidh status                    # ringkasan isi db/
python -m tools.eltahfidh media --dry-run           # hitung jumlah dan ukuran media
python -m tools.eltahfidh media --site utama        # unduh media situs induk
```

Situs induk diekspor **berlogin** bila env berikut diisi (Application Password, bukan
sandi login). Tanpa itu, hanya konten terbit yang diambil. Subdomain selalu tanpa login.

```bat
:: Windows (Command Prompt), hanya untuk sesi terminal itu
set WP_USER=labib
set WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
python -m tools.eltahfidh export
```

Ekspor **hanya membaca** (GET). Ada jeda 2,5 detik antar-permintaan karena server 20i
membatasi kecepatan (HTTP 429), dan User-Agent sengaja bukan UA browser karena firewall
hosting menolaknya (lihat `docs/12-oop-plugin.md` §12.8).

## Susunan kode

Lapisannya meniru plugin `my-custom-app`:

| Lapisan | Berkas | Peran |
|---|---|---|
| Model | `models/site.py`, `models/content.py` | `Site`, `Content` (postingan/halaman), `Term`, `Media` |
| Repository | `repositories/wp_api.py` | Membaca REST API WordPress, termasuk paginasi |
| Repository | `repositories/json_store.py` | Satu-satunya yang tahu tata letak `db/` |
| Service | `services/exporter.py` | Alur ekspor dan aturan privasi |
| Service | `services/media_backup.py` | Unduh media yang belum ada (berkas sementara lalu ganti nama) |
| Controller | `cli.py` | Perintah baris; merakit semua objek di `build_services()` |
| Infrastruktur | `http.py` | Kontrak `HttpClient` dan implementasi `UrllibClient` (jeda, 429) |
| Konfigurasi | `config.py` | Daftar 7 situs, lokasi `db/`, User-Agent |

## Uji

```bash
python -m unittest discover -s tools/eltahfidh/tests -t .
```

Uji memakai klien HTTP palsu (`tests/fakes.py`), jadi tidak menyentuh situs sungguhan.
