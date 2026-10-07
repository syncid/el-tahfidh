# `tools/eltahfidh` — ekspor WordPress dan generator situs

Paket Python (pustaka standar saja) untuk:

1. **Mengekspor** konten WordPress elTAHFIDH (situs induk dan 6 subdomain) ke folder
   lokal `db/`, yaitu "database" proyek ini.
2. **Mencadangkan** berkas media ke `db/media/`.
3. **Membangun halaman jenjang** `site/smp-quran.html`, `site/sma-quran.html`, `site/ifs.html`
   (pengganti subdomain) dari `data/jenjang.json`, `data/struktur-organisasi.json`, dan `db/`.
4. **Membuat berkas impor WordPress (WXR)** per situs ke `db/wxr/<key>.xml`.

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
python -m tools.eltahfidh build-berita              # bangun halaman detail site/berita/<slug>.html
python -m tools.eltahfidh build-jenjang             # bangun 3 halaman jenjang di site/
```

Jalankan `build-berita` sebelum `build-jenjang`, karena kartu berita di halaman jenjang
menaut ke halaman detail. `build-berita` juga menulis `data/peta-tautan.json` (alamat
WordPress lama → `/berita/<slug>.html`) dan menghapus halaman detail yang artikelnya sudah
tidak ada di `db/`. Postingan alat interaktif (memuat input/kanvas/tombol) dilewati.

`build-jenjang` butuh `db/` hasil `export` (untuk berita subdomain). Isi teks halaman
diubah di `data/jenjang.json`, bukan di HTML. Thumbnail berita diunduh sekali ke
`site/assets/img/posts/<key>-<id>.<ext>`; hapus berkasnya bila ingin diunduh ulang.

Situs induk diekspor **berlogin** bila env berikut diisi (Application Password, bukan
sandi login). Tanpa itu, hanya konten terbit yang diambil. Subdomain selalu tanpa login.

```bat
:: Windows (Command Prompt), hanya untuk sesi terminal itu
set WP_USER=labib
set WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
python -m tools.eltahfidh export
```

Ekspor **hanya membaca** (GET). Ada jeda 2,5 detik antar-permintaan REST API karena server 20i
membatasi kecepatan (HTTP 429); unduhan berkas media memakai jeda 0,5 detik karena dilayani StackCDN, dan User-Agent sengaja bukan UA browser karena firewall
hosting menolaknya (lihat `docs/12-oop-plugin.md` §12.8).

## Berkas impor WordPress (WXR)

```bash
python -m tools.eltahfidh wxr      # db/wxr/utama.xml + satu berkas per subdomain
```

- Berkasnya ada di `db/` (lokal) dan **tidak boleh di-commit**: `utama.xml` memuat draf.
- Isi tiap berkas: postingan, halaman, kategori, tag, dan lampiran media (alamat aslinya).
  `utama.xml` memakai isi mentah (*raw*) karena diekspor berlogin, termasuk draf;
  berkas subdomain memakai isi hasil render dan tanpa draf.
- Postingan subdomain mendapat kategori tambahan bernama situsnya (mis. `smp-quran-putra`)
  agar tetap terkelompok setelah digabung. ID digeser per situs (`1000000 × urutan`) agar tidak
  bentrok. Halaman subdomain yang kosong (tata letak Elementor), "Sample Page", dan
  "Hello world" tidak diikutkan.
- Tata letak Elementor **tidak** ikut (tidak terbaca lewat REST API); yang terbawa adalah isinya.

Cara impor ke WordPress tujuan (butuh akun Administrator):

1. Cadangkan dulu situs tujuan (UpdraftPlus).
2. Tools → Import → WordPress (pasang importer bila diminta) → pilih berkas `.xml`.
3. Petakan penulis `eltahfidh-impor` ke akun yang ada.
4. Centang **Download and import file attachments** selama situs sumber masih hidup,
   agar gambar ikut tersalin.
5. Untuk penggabungan subdomain, impor berkas subdomain ke situs induk satu per satu.

Belum diuji pada WordPress sungguhan; uji dulu di situs staging.

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
| Repository | `repositories/data_files.py` | Membaca data publik di `data/` (isi jenjang, struktur organisasi) |
| Service | `services/jenjang_builder.py` | Merakit halaman jenjang dan mengunduh thumbnail berita |
| View | `views/layout.py` | Kerangka header/footer dari `site/kontak.html` (cara yang sama dengan `build_posts.py`) |
| View | `views/components.py` | Kartu berita, pimpinan, kampus, pilar, fakta, program; meniru markup `site/` |
| View | `views/jenjang_page.py` | Menyusun bagian-bagian halaman jenjang |
| View | `views/article_page.py` | Halaman detail berita/artikel di `site/berita/` |
| Service | `services/article_index.py` | Daftar artikel + nama berkas unik; dipakai bersama dua generator |
| Service | `services/article_builder.py` | Membangun `site/berita/*.html` dan `data/peta-tautan.json` |
| Service | `services/content_cleaner.py` | Membuang skrip, gaya sebaris, sisa shortcode dari isi postingan |
| Service | `services/wxr_exporter.py` | Membuat berkas impor WordPress (WXR 1.2) per situs ke `db/wxr/` |
| Konfigurasi | `config.py` | Daftar 7 situs, lokasi `db/`, `data/`, `site/`, User-Agent |

## Uji

```bash
python -m unittest discover -s tools/eltahfidh/tests -t .
```

Uji memakai klien HTTP palsu (`tests/fakes.py`), jadi tidak menyentuh situs sungguhan.
