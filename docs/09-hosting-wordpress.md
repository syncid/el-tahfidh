# 09 — Hosting & wp-admin (`eltahfidh.or.id`)

> Indeks: [README](./README.md) · Sebelumnya: [08 — Roadmap](./08-roadmap.md) · Berikutnya: —

Dokumen ini mencatat **fakta hosting situs produksi** dan cara mengerjakan
operasi umum **tanpa perlu panel server** (cukup lewat wp-admin).

## 9.1 Fakta hosting (hasil audit 2026-10-02)

| Item | Nilai | Sumber |
|---|---|---|
| Penyedia / jaringan | **20i Limited** (AS48254), hostname `185-146-167-193.ptr4.stackcp.net` | `ipinfo.io` |
| Panel pengelolaan | **StackCP** (panel milik 20i) — **bukan cPanel** | hostname + `mu-plugin` `StackCache` (author: *Stack CP*) |
| cPanel (2082/2083), WHM (2087), Plesk (8443), DirectAdmin (2222/2223), Webmin (10000) | **semua port tertutup** | pemindaian port langsung |
| Port terbuka | 80, 443 saja | pemindaian port |
| CDN / cache | **StackCDN** (`x-provided-by: StackCDN`), `mu-plugins/StackCache` | HTTP header |
| WordPress | **7.1.2** | Site Health |
| PHP | **8.3.35** (fpm-fcgi, 64-bit) | Site Health & `x-powered-by` |
| Database | MariaDB **10.11.18**, host `sdb-73.hosting.stackcp.net`, prefix tabel **`f1_`** | Site Health |
| Path WordPress | `/home/sites/37b/a/a01b708ac3/public_html/eltahfidh.or.id` | Site Health |
| Batas | memory 256M, upload/post 128M, `WP_MEMORY_LIMIT` 40M | Site Health |
| Tema aktif | Astra 4.11.13 (+ Astra Pro), page builder Elementor/Elementor Pro | Site Health |

**Syarat plugin `my-custom-app`:** WordPress 6.2+ → ✅ (7.1.2), PHP 8.1+ → ✅ (8.3.35),
ekstensi mbstring → ✅. **Siap dipasang, tidak perlu upgrade apa pun.**

## 9.2 "Di mana cPanel-nya?" — jawaban singkat

**Tidak ada cPanel di paket ini, dan tidak ada di dalam WordPress.** Dua hal berbeda:

- **cPanel** = panel level server, diakses lewat alamat + port terpisah (mis. `:2083`),
  dengan kredensial **hosting** — *bukan* kredensial WordPress. WordPress **tidak pernah**
  menampilkan cPanel sebagai menu, di instalasi mana pun.
- **wp-admin** = panel aplikasi WordPress (`/wp-admin`), dengan kredensial **WordPress**.

Pada hosting ini, fungsi setara cPanel dikelola lewat **akun client-area 20i / StackCP**
(alamat tidak diekspos di domain ini — cari email berisi kata `20i`/`stackcp`, atau
pakai *lupa password* di portal 20i dengan email pendaftaran).

**Penting:** untuk memasang plugin, **tidak perlu** panel hosting sama sekali — pakai
wp-admin (bagian 9.3).

## 9.3 Memasang plugin `my-custom-app` lewat wp-admin (tanpa cPanel)

Prasyarat: file `my-custom-app.zip` (dibuat dari `wp-content/plugins/my-custom-app/`,
berisi `vendor/` hasil `composer install --no-dev`, **tanpa** `tests/`).

1. Login **`https://eltahfidh.or.id/wp-admin`** (akun Administrator).
2. Menu **Plugins → Add New Plugin** → tombol **Upload Plugin** (atas).
3. **Choose File** → pilih `my-custom-app.zip` → **Install Now**.
4. Setelah selesai → klik **Activate Plugin**.
5. Pastikan menu baru **Booking Survei** muncul di sidebar kiri wp-admin.
   Tabel `f1_mca_survey_bookings` dibuat otomatis pada request pertama.

**Uji cepat setelah aktif:**

| Uji | Cara | Hasil yang benar |
|---|---|---|
| Pengaman endpoint | buka `https://eltahfidh.or.id/wp-json/my-custom-app/v1/status` di jendela *incognito* | **401** (bukan data) |
| Endpoint booking | kirim 1 data uji dari form survei | masuk ke menu **Booking Survei** |
| Ekspor | menu Booking Survei → **Ekspor CSV** | file CSV terunduh |

**Kalau gagal/ingin mundur:** Plugins → **Deactivate** → **Delete**. Situs kembali
seperti semula; tidak ada perubahan permanen pada tema/konten.

## 9.4 Operasi lain yang tetap lewat wp-admin (tanpa panel hosting)

| Kebutuhan | Jalur wp-admin |
|---|---|
| Backup penuh situs + database | Plugin **UpdraftPlus** (sudah terpasang) → *Backup Now* |
| Info server/PHP/database | **Tools → Site Health → tab Info** |
| Sisipkan kode/JS kecil | Plugin **WPCode Lite** (sudah terpasang) |
| Cache situs (StackCache) | Admin bar → **Purge Cache** |
| Ganti pengaturan dasar | **Settings → General/Permalinks** |

Kapan **panel hosting (StackCP/20i) benar-benar diperlukan**: restore backup level server,
mengubah PHP/`php.ini`, DNS/domain, email hosting, atau saat WordPress tidak bisa diakses
sama sekali (fatal error). Selama wp-admin bisa dibuka, semua pekerjaan plugin/konten
cukup dari sana.

## 9.5 Catatan risiko sebelum go-live

1. **Rate limit endpoint booking memakai `REMOTE_ADDR`.** Situs berada di belakang
   **StackCDN** — pastikan server memulihkan IP asli pengunjung (bukan IP CDN), kalau
   tidak semua pengunjung tampak satu IP dan rate limit bisa salah blokir. Uji dulu
   dengan 2 perangkat berbeda sebelum musim PPSB.
2. **`WP_MEMORY_LIMIT` = 40M** sementara PHP memory 256M. Untuk ekspor CSV besar,
   pantau bila muncul error memori.
3. **Backup dulu sebelum aktivasi** (UpdraftPlus) — walaupun plugin aman, ini kebiasaan baik.