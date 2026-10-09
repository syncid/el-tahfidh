# 16 — Plan dan RnD

> Indeks: [README](./README.md) · Sebelumnya: [15 — Aturan Kerja](./15-aturan-kerja.md) · Berikutnya: —

Rencana kerja lanjutan setelah migrasi tahap pertama dan audit server StackCP (Okt 2026).
Dokumen ini versi **publik**: rincian per situs (nama domain yang rentan, jalur berkas, nama
database) ada di dokumen internal `internal/audit-stackcp-2026-10.md` yang tidak di-commit
(aturan S1 di [15](./15-aturan-kerja.md)). Daftar butir harian tetap di
[08 — Roadmap](./08-roadmap.md).

Pelaksana: **P** = pemilik (StackCP, wp-admin, DNS) · **C** = Claude di repo · **L** = Claude sesi
lokal laptop. Setiap langkah P dan setiap tulisan ke server menunggu persetujuan (A1, W1, W2).

## 16.1 Kondisi saat ini

| Lapisan | Keadaan (9 Okt 2026) | Sumber |
|---|---|---|
| Situs statis | 9 halaman utama + 330 halaman detail berita; `check-links` 0 rusak; 33 uji lulus. Gambar berita masih diambil dari server WordPress. | `python -m tools.eltahfidh check-links`, uji unit |
| Server StackCP | Satu akun: 49 instalasi WordPress (versi 6.8.1–7.1.3) dan 2 Moodle; 85 database di 12 server database. Hanya 7 situs yang selama ini dikelola repo ini. | Salinan file manager ±7 Okt 2026; `docs/14` |
| Keamanan | **Bersih dari malware**: 0 webshell di ±256 ribu PHP non-inti; 0 berkas inti WordPress yang berbeda dari checksum resmi. | Audit sesi lokal, 7 Okt 2026 |
| Cadangan | Hanya situs induk yang punya cadangan (UpdraftPlus 1–2 Okt 2026, termasuk DB). | Isi `wp-content/updraft/` |
| Data lokal | `db/` (ekspor 7 situs), cadangan media 2.169 berkas (±1 GB), salinan file manager 23,75 GB + zip 15,2 GB. | Laptop pemilik |

Risiko yang tersisa bersifat operasional, bukan peretasan:

1. Salinan server berisi sandi database 49 situs masih berada di dalam folder repo di laptop.
2. Dua ZIP plugin berbayar dan satu installer aplikasi tersimpan di folder uploads yang bisa diunduh publik.
3. Tiga situs masih berjalan di PHP 7.4 dan beberapa situs memakai Elementor versi lama serta plugin formulir yang tidak dirawat.
4. Ada duplikasi plugin (klon Elementor Pro, dua plugin SEO aktif bersamaan) dan berkas sisa (log PHP lama, halaman "under construction").
5. 48 situs tanpa cadangan.

## 16.2 Fase kerja

### Fase 0 — Pengamanan (±1–2 hari, bisa segera)

| # | Langkah | Pelaksana | Selesai bila |
|---|---|---|---|
| 0.1 | Pindahkan salinan file manager dan zip-nya ke luar `C:\el-tahfidh`; aktifkan BitLocker bila tersedia. | L/P | Folder repo hanya berisi repo, `db/`, `referensi/`, `internal/`. |
| 0.2 | Cabut dua Application Password akun `labib` yang pernah ditulis di chat. | P | Daftar Application Password bersih. |
| 0.3 | Hapus ZIP plugin berbayar dan installer aplikasi dari folder uploads (lokasi di dokumen internal). | P | URL berkas menghasilkan 404. |
| 0.4 | Hapus berkas sisa (log PHP lama, halaman "under construction"). | P | Berkas tidak ada lagi. |
| 0.5 | Putuskan aturan S5: rincian `docs/14` dipindah ke `internal/`. | C (setelah setuju) | Repo publik tanpa nama DB/server. |
| 0.6 | Pulihkan email login akun 20i dan aktifkan 2FA. | P | Pemilik bisa mengatur ulang sandi sendiri. |

### Fase 1 — Inventaris dan keputusan per situs (±3–5 hari)

| # | Langkah | Pelaksana | Selesai bila |
|---|---|---|---|
| 1.1 | Lengkapi peta folder → domain → database → status hidup untuk 49 + 2 instalasi. | L, C | Tabel internal lengkap tanpa kolom kosong. |
| 1.2 | Tandai pemilik tiap situs: inti elTAHFIDH, lembaga terkait, pihak lain, atau kosong/duplikat. | P | Setiap situs punya pemilik. |
| 1.3 | Keputusan per situs: **migrasi ke statis**, **pertahankan di WP**, **arsipkan** (ekspor lalu matikan), atau **serahkan** ke pemiliknya. | P + C | Daftar keputusan disetujui. |
| 1.4 | Identifikasi database yatim (ada di daftar 85, tidak dipakai instalasi) dan rencanakan ekspor + penghapusan. | L, P | Daftar DB yatim beserta keputusan. |

### Fase 2 — Situs inti elTAHFIDH (±1–2 minggu)

| # | Langkah | Pelaksana | Selesai bila |
|---|---|---|---|
| 2.1 | Salin gambar berita yang dipakai ke situs statis (WebP terkompresi) dari `db\media`; generator memakai salinan lokal. | C, L | Situs statis tidak bergantung pada server WP untuk gambar (R2). |
| 2.2 | Halaman tersisa: program pesantren, e-brosur, 6 halaman alat. | C (setelah keputusan) | Tiap halaman berstatus statis / tetap di WP / dimatikan. |
| 2.3 | Manfaatkan cadangan DB situs induk untuk menu, pengaturan, dan tata letak Elementor (R1). | L, C | Ringkasan isi halaman yang tidak terbaca lewat REST. |
| 2.4 | Rencana peralihan domain `eltahfidh.or.id` ke situs statis + pengalihan alamat lama dengan `data/peta-tautan.json` (R3). | C, P | Keputusan + uji di subdomain uji. |
| 2.5 | Tentukan rumah plugin booking `my-custom-app` bila WP induk tidak lagi jadi situs utama (R4). | C, P | Endpoint booking tetap hidup. |

### Fase 3 — Pengerasan WordPress yang dipertahankan (±1 minggu, per situs)

- Naikkan PHP 7.4 ke 8.2/8.3 setelah cadangan, mulai dari situs dengan risiko tertinggi.
- Perbarui Elementor, Elementor Pro, Astra, Rank Math; ganti plugin formulir yang tidak dirawat.
- Hapus duplikasi plugin, tema dan plugin nonaktif.
- Pasang cadangan otomatis ke luar server dan uji pemulihan sekali (W4).
- Catat lisensi plugin berbayar dan pastikan sumbernya resmi.

### Fase 4 — Konsolidasi hosting (setelah Fase 1 disetujui)

- Arsipkan lalu matikan situs kosong atau duplikat (W3).
- Hapus database yatim setelah diekspor.
- Rapikan DNS: hapus catatan mati (`lp`, `daurohsanadalfatihah`, dan temuan Fase 1).

### Fase 5 — Operasional berkelanjutan

- CI ringan di GitHub Actions: uji `tools/eltahfidh`, `check-links`, `php -l` plugin tiap push.
- Pemantauan hidup situs untuk situs yang dipertahankan.
- Jadwal sinkron konten (`build_posts.py`, `build-berita`, `build-jenjang`).
- Pemindaian keamanan berkala (checksum inti + pola), alatnya disimpan di luar repo publik (R7).

## 16.3 RnD

| # | Topik | Pertanyaan | Metode | Keluaran |
|---|---|---|---|---|
| R1 | Tata letak Elementor dari cadangan DB | Bisakah `_elementor_data` diubah menjadi teks/struktur untuk halaman statis? | Pulihkan DB ke MariaDB lokal (Docker di laptop), baca JSON Elementor per halaman. | Skrip ekstraksi + contoh 3 halaman. |
| R2 | Gambar di situs statis | Berapa ukuran gambar yang dipakai bila dikompres? Muat di repo (batas lunak Pages 1 GB) atau perlu tempat lain? | Hitung dari `db\media` hanya gambar yang dirujuk `site/`; uji WebP kualitas 75–80, lebar maks 1200 px. | Angka ukuran + rekomendasi (repo / Git LFS / CDN). |
| R3 | Peralihan domain | Bagaimana mengarahkan domain ke GitHub Pages tanpa memutus email dan tanpa kehilangan SEO? | Kaji DNS (A/CNAME vs MX); Pages tidak mendukung 301 dari server, jadi perlu halaman pengalihan atau Cloudflare. | Langkah peralihan + rencana mundur. |
| R4 | Backend booking | Di mana endpoint booking hidup bila WP induk tidak dipakai? | Bandingkan: WP di subdomain aplikasi, layanan formulir, atau fungsi serverless. | Rekomendasi + biaya. |
| R5 | Aplikasi non-WP | Moodle, aplikasi absensi, aplikasi sekolah, CBT: masih dipakai? Siapa pemiliknya? | Cek tanggal data terakhir bersama pemilik. | Status pakai + keputusan. |
| R6 | Penyatuan situs lembaga lain | Apakah situs jenjang di domain terpisah ikut digabung seperti 6 subdomain? | Bandingkan isi dan trafik (Site Kit / Search Console). | Daftar gabung/tidak. |
| R7 | Alat audit berulang | Bisakah pemindaian pola + checksum menjadi satu perintah cepat? | Rapikan skrip audit sesi lokal; baca paralel, kemajuan, laporan CSV. | Alat audit (di luar repo publik). |
| R8 | Uji WXR | Apakah `db/wxr/*.xml` berhasil diimpor ke WordPress? | Impor ke WordPress lokal (Docker) sebagai staging. | Laporan + perbaikan generator. |

## 16.4 Keputusan yang perlu pemilik

1. Nasib WordPress situs induk: tetap sebagai CMS, atau dimatikan setelah migrasi selesai? (menentukan R2–R4)
2. Apakah domain `eltahfidh.or.id` diarahkan ke situs statis?
3. Situs non-inti: mana milik elTAHFIDH, mana milik lembaga lain, mana boleh diarsipkan?
4. Aturan S5: setuju rincian `docs/14` dipindah ke `internal/`?
5. Halaman yang belum dimigrasi (program, e-brosur, 6 alat): statis, tetap di WP, atau dimatikan?
6. Lokasi cadangan: drive lokal terenkripsi, Google Drive, atau keduanya?
7. Aplikasi non-WP (Moodle, absensi, CBT): masih dipakai?
8. Siapa pemegang akun 20i, dan perlukah akun tambahan untuk staf teknis?

## 16.5 Riwayat

| Tanggal | Perubahan |
|---|---|
| 9 Okt 2026 | Versi pertama: fase 0–5, RnD R1–R8, keputusan pemilik. Peta folder → domain → database (Fase 1.1) sedang dikerjakan sesi lokal. |
