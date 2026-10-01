# 05 — Panduan Plugin WordPress (`my-custom-app`)

> Indeks: [README](./README.md) · Sebelumnya: [04 — Situs Statis](./04-situs-statis.md) · Berikutnya: [06 — Operasional](./06-operasional.md)

Rujukan teknis utama tetap `wp-content/plugins/my-custom-app/README.md` —
file ini ringkasannya + peta jalan.

## 5.1 Arsitektur (OOP ketat, PSR-4 `MyCustomApp\`)

```text
my-custom-app.php          # bootstrap
src/
├── Providers/             # InstallProvider, RestProvider, AdminProvider (+ HookableInterface)
├── Controllers/           # StatusController, SurveyBookingController (+ Admin/*, interface)
├── Services/              # SurveyBookingService, Validator, RateLimiter, StatusService, ...
├── Models/                # SurveyBookingRepository (+ interface), AbstractRepository
├── Helpers/               # Capabilities, Sanitizer, Security, ResponseFormatter, ...
└── views/admin/           # Layar wp-admin (survey-bookings.php)
```

Syarat: **PHP 8.1+** + ekstensi mbstring, **WordPress 6.2+**.

## 5.2 Fitur: Booking Survei

- Endpoint publik `POST /wp-json/my-custom-app/v1/survei/booking` — kontrak
  request/respons identik dengan Google Apps Script lama (tiket ganda, pesan error sama).
- Pengaman: validasi input, rate limit, sanitasi (lihat `Services/` + `Helpers/Security.php`).
- wp-admin **Booking Survei**: daftar + filter (tanggal, status, cari), ubah status
  (terjadwal / hadir / batal), **ekspor CSV**. Kapabilitas `mca_manage_bookings`
  (otomatis untuk Administrator & Editor).
- Tabel `{prefix}mca_survey_bookings` dibuat otomatis pada request pertama setelah aktif.
- Data lama di Google Sheets **tidak** dimigrasi otomatis.

## 5.3 Menyambungkan form

Di `index.html` form survei (repo `eltahfidh.github.io/survei`, terpisah):

```js
API_URL: 'https://eltahfidh.or.id/wp-json/my-custom-app/v1/survei/booking',
```

Tidak ada perubahan lain di sisi form.

## 5.4 Alur kerja pengembang plugin

1. Ubah kode di `src/` (ikuti pola Providers → Controllers → Services → Models yang ada).
2. Cek sintaks: `php -l` per file; smoke test via `tests/smoke-test.php`.
3. `composer install --no-dev --optimize-autoloader` sebelum deploy (folder `vendor/`
   tidak masuk repo — lihat `docs/06-operasional.md` soal deploy).
4. Deploy → aktifkan → uji 1 booking end-to-end → cek wp-admin + CSV.

Peta jalan pengembangan ada di [08 — Roadmap](./08-roadmap.md) bagian plugin.
