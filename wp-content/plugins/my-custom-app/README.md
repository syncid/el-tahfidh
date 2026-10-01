# My Custom App

Plugin WordPress untuk logika bisnis inti situs elTAHFIDH. Arsitektur: OOP ketat,
PSR-4 (Composer), pemisahan Providers / Controllers / Services / Models / Helpers.

Syarat: **PHP 8.1+** (ekstensi mbstring), **WordPress 6.2+**.

## Fitur: Booking Survei

Backend untuk form <https://eltahfidh.github.io/survei/>, menggantikan Google Apps Script.

- `POST /wp-json/my-custom-app/v1/survei/booking`: endpoint publik, kontraknya sama dengan Apps Script.
- Menu wp-admin **Booking Survei**: daftar, filter (tanggal, status, cari), ubah status
  (terjadwal / hadir / batal), ekspor CSV.
- Akses admin memakai kapabilitas `mca_manage_bookings` (otomatis untuk Administrator & Editor).
- Tabel `{prefix}mca_survey_bookings` dibuat otomatis pada request pertama setelah plugin aktif.

### Menyambungkan form GitHub

Di `index.html` form survei, ganti satu baris:

```js
API_URL: 'https://eltahfidh.or.id/wp-json/my-custom-app/v1/survei/booking',
```

Tidak ada perubahan lain: format request/respons, tiket dobel, dan pesan error tetap sama.
Data lama di Google Sheets **tidak** dipindahkan otomatis.

### Pengaman endpoint publik

Endpoint ini dipakai tamu tanpa login, jadi aturan `current_user_can()` + nonce tidak
berlaku (tidak ada sesi yang bisa dibajak). Penggantinya:

- allowlist header `Origin` (`https://eltahfidh.github.io` + domain situs; tambah lewat filter
  `my_custom_app_booking_origins`),
- honeypot `website`, rate limit 10 percobaan / 10 menit / IP, batas body 8 KB,
- validasi & normalisasi ulang di server (jenjang, kelas, WA, tanggal ≤ 60 hari, sesi).

**Catatan Cloudflare/proxy:** rate limit memakai `REMOTE_ADDR`. Jika situs di belakang proxy
yang tidak memulihkan IP asli, semua pengunjung tampak satu IP. Pastikan server memulihkan
IP asli (mis. modul `mod_remoteip` / pengaturan Cloudflare di hosting) sebelum go-live.

## Pengembangan

```bash
composer install            # autoloader
php tests/smoke-test.php    # 38 tes tanpa WordPress
```

## Deploy

```bash
composer install --no-dev --optimize-autoloader
```

Unggah folder plugin **beserta `vendor/`**, tanpa `tests/`. Aktifkan di Plugins.
Uji cepat setelah aktif:

- `GET /wp-json/my-custom-app/v1/status` tanpa login → 401.
- Login admin, buka editor, console: `await wp.apiFetch({ path: '/my-custom-app/v1/status' })`.
- Buka menu **Booking Survei**.
