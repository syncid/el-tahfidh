# 01 — Ringkasan Proyek elTAHFIDH

> Dokumen ini bagian dari seri dokumentasi proyek di folder `docs/`.
> Indeks: [README](./README.md) · Sebelumnya: — · Berikutnya: [02 — Arsitektur & Struktur Repo](./02-arsitektur.md)

## 1.1 Apa ini?

**elTAHFIDH** adalah paket kerja web milik lembaga pendidikan tahfidz elTAHFIDH Indonesia.
Isinya dua produk dalam satu repo:

| Produk | Lokasi | Teknologi | Target jalan |
|---|---|---|---|
| **A. Situs statis** — profil lembaga, PPDB/PSB, kontak, berita, artikel | `site/` | HTML + CSS + JS murni, tanpa build step | Browser langsung / hosting statis apa pun |
| **B. Plugin WordPress `my-custom-app`** — backend Booking Survei (pengganti Google Apps Script) | `wp-content/plugins/my-custom-app/` | PHP 8.1+, OOP + PSR-4 (Composer), WP REST API | WordPress 6.2+ di `eltahfidh.or.id` |

Pendukung: skrip Python di `tools/` (ambil berita/artikel dari WP API publik, bangun ulang halaman) dan aset mentah di `source-assets/`.

## 1.2 Status saat ini (Oktober 2026)

- Situs statis: **6 halaman aktif** — `index`, `profil`, `psb`, `kontak`, `berita`, `artikel` — plus pipeline `tools/build_posts.py` yang menarik 12 berita + 12 artikel terbaru dari `eltahfidh.or.id/wp-json/wp/v2/posts`.
- Plugin: endpoint `POST /wp-json/my-custom-app/v1/survei/booking`, wp-admin **Booking Survei** (daftar, filter tanggal/status/cari, ubah status terjadwal/hadir/batal, ekspor CSV), kapabilitas `mca_manage_bookings`, tabel `{prefix}mca_survey_bookings` dibuat otomatis. Form publik dilayani dari `https://eltahfidh.github.io/survei/`.
- Repo: privat `syncid/el-tahfidh`, branch `main`, devcontainer + workflow Pages siap (Pages nonaktif menunggu keputusan visibilitas — lihat `docs/06-operasional.md`).

## 1.3 Batasan & keputusan penting

1. **Folder `referensi/` HANYA lokal** — cermin HTTrack situs pihak lain (~379 MB). Diabaikan git (`/referensi/` di `.gitignore`), tidak ada di GitHub/klon cloud. Detail: `docs/07-referensi-lokal.md`.
2. **`vendor/` plugin tidak di-track** — dibuat ulang via `composer install` (otomatis di Codespace).
3. **Repo privat + akun Free** — GitHub Pages dan branch protection API tidak tersedia sampai repo dipublikkan atau akun di-upgrade (lihat `docs/06-operasional.md`).
4. **Situs statis tanpa build step** — disengaja agar bisa dibuka langsung (`site/index.html`) dan di-host di mana saja; konsekuensinya konten berita/artikel diperbarui lewat skrip, bukan CMS.

## 1.4 Lisensi

| Bagian | Lisensi | File |
|---|---|---|
| Plugin WordPress `my-custom-app` | **GPL-2.0-or-later** (wajib kompatibel dengan WordPress) | `wp-content/plugins/my-custom-app/LICENSE` |
| Isi repo lain (situs statis, `tools/`, `docs/`) | **MIT** | `LICENSE` di akar repo |

Ditambahkan oleh kolaborator `AzizHanafi` (Okt 2026). Konsekuensi praktis: kode boleh
dipakai ulang/dimodifikasi pihak lain **dengan tetap menyertakan lisensinya** — jadi ini
bukan bagian dari pembatasan akses (lihat diskusi privasi di `docs/06`).

## 1.5 Cara memakai dokumentasi ini

| Saya mau… | Baca |
|---|---|
| Menjalankan / deploy | [03 — Panduan Menjalankan & Deploy](./03-menjalankan-deploy.md) |
| Mengubah situs statis | [04 — Panduan Situs Statis](./04-situs-statis.md) |
| Mengubah plugin WP | [05 — Panduan Plugin WordPress](./05-plugin-wordpress.md) |
| Operasional repo/cloud/CI | [06 — Operasional](./06-operasional.md) |
| Memulihkan folder referensi lokal | [07 — Referensi Lokal](./07-referensi-lokal.md) |
| Rencana kerja ke depan | [08 — Roadmap](./08-roadmap.md) |
