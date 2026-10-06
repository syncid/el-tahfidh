# 12 — Panduan OOP Plugin `my-custom-app`

> Indeks: [README](./README.md) · Sebelumnya: [11 — Audit Migrasi](./11-audit-migrasi.md) · Berikutnya: —

Dokumen ini menjelaskan **cara kode plugin disusun secara berorientasi objek (OOP)**:
siapa mewarisi siapa, siapa memanggil siapa, dan bagaimana menambah fitur baru dengan
pola yang sama. Untuk fitur dan cara deploy, rujuk
[05 — Plugin WordPress](./05-plugin-wordpress.md) dan
`wp-content/plugins/my-custom-app/README.md`.

Semua keterangan di bawah diambil dari kode di `wp-content/plugins/my-custom-app/src/`
(namespace `MyCustomApp\`, PHP 8.1+, `declare(strict_types=1)` di setiap berkas).

## 12.1 Gambaran besar

Plugin memakai pola berlapis. Setiap lapisan hanya boleh memanggil lapisan di bawahnya.

```text
WordPress Core
   │  (hook: rest_api_init, admin_menu, init, admin_post_*)
   ▼
Provider      → mendaftarkan hook ke WordPress, tanpa logika bisnis
   ▼
Controller    → menerima request, memeriksa izin/asal, memanggil Service
   ▼
Service       → logika bisnis: anti-spam, validasi, aturan, pembuatan kode
   ▼
Repository    → satu-satunya lapisan yang menyentuh database ($wpdb)
   ▼
Tabel {prefix}mca_survey_bookings
```

`Helpers/` berisi alat bantu tanpa status (sanitasi, keamanan, format respons, tampilan)
yang boleh dipakai semua lapisan.

## 12.2 Peta kelas

### Kontrak (interface dan kelas abstrak)

| Nama | Jenis | Tugas | Dipenuhi oleh |
|---|---|---|---|
| `HookableInterface` | interface | Kelas yang mendaftarkan hook lewat `register_hooks()` | `InstallProvider`, `RestProvider`, `AdminProvider` |
| `RestControllerInterface` | interface | Controller REST dengan `register_routes()` | `AbstractRestController` |
| `AbstractRestController` | abstrak | Basis controller REST: `route()`, `require_capability()`, `handle()`, `log_exception()` | `StatusController`, `SurveyBookingController` |
| `SchemaInterface` | interface | Model yang punya tabel kustom (`schema_sql()`) | `SurveyBookingRepository` |
| `SurveyBookingRepositoryInterface` | interface | Operasi data booking yang dibutuhkan Service; memuat konstanta status | `SurveyBookingRepository` |
| `AbstractRepository` | abstrak | Basis akses tabel: `find`, `insert`, `update`, `delete` dengan whitelist kolom | `SurveyBookingRepository` |
| `ClockInterface` | interface | Sumber waktu "sekarang" | `WpClock` |

### Kelas konkret

| Lapisan | Kelas | Peran |
|---|---|---|
| Inti | `Plugin` | *Composition root*: merakit semua objek di `create()`, mengaktifkan provider di `boot()` |
| Provider | `InstallProvider` | Memasang `Installer::maybe_upgrade` pada hook `init` |
| Provider | `RestProvider` | Memanggil `register_routes()` semua controller pada `rest_api_init` |
| Provider | `AdminProvider` | Mendaftarkan menu dan dua handler `admin_post_*` |
| Controller | `StatusController` | `GET /status`, khusus administrator |
| Controller | `SurveyBookingController` | `POST /survei/booking`, publik dengan pengaman |
| Controller | `Admin\SurveyBookingAdminController` | Halaman wp-admin: daftar, ubah status, ekspor CSV |
| Service | `SurveyBookingService` | Alur booking utuh |
| Service | `SurveyBookingValidator` | Validasi dan normalisasi input |
| Service | `RateLimiter` | Membatasi percobaan per IP (transient) |
| Service | `Installer` | Membuat tabel (`dbDelta`) dan memberi kapabilitas |
| Service | `StatusService` | Menyusun info versi plugin, PHP, WordPress |
| Service | `WpClock` | Jam produksi, memakai zona waktu situs |
| Objek nilai | `BookingResult` | Hasil booking: `kode`, `sesi`, `dobel` (properti `readonly`) |
| Pengecualian | `ValidationException` | Input ditolak; pesannya aman ditampilkan ke pengguna |
| Model | `SurveyBookingRepository` | Tabel `mca_survey_bookings`, kueri filter dan paginasi |
| Helper | `Sanitizer`, `Security`, `Capabilities`, `ResponseFormatter`, `DateFormatter`, `View` | Alat bantu statis |

## 12.3 Diagram pewarisan dan ketergantungan

Pewarisan (`extends`) dan implementasi (`implements`):

```text
RestControllerInterface
   └── AbstractRestController
          ├── StatusController
          └── SurveyBookingController

AbstractRepository ◀── SurveyBookingRepository ──▶ SchemaInterface
                                              └──▶ SurveyBookingRepositoryInterface

HookableInterface ◀── InstallProvider | RestProvider | AdminProvider
ClockInterface    ◀── WpClock
RuntimeException  ◀── ValidationException
```

Ketergantungan (siapa menerima siapa lewat constructor), sesuai `Plugin::create()`:

```text
Plugin
 ├─ InstallProvider ── Installer ── SurveyBookingRepository
 ├─ RestProvider
 │    ├─ StatusController ── StatusService
 │    └─ SurveyBookingController ── SurveyBookingService
 │                                   ├─ SurveyBookingRepository
 │                                   ├─ SurveyBookingValidator ── WpClock
 │                                   ├─ RateLimiter
 │                                   └─ WpClock
 └─ AdminProvider ── SurveyBookingAdminController ── SurveyBookingRepository, WpClock
```

Satu objek `SurveyBookingRepository` dan satu `WpClock` dibuat sekali, lalu dibagikan.

## 12.4 Alur satu permintaan booking

1. Form di `eltahfidh.github.io/survei` mengirim `POST` JSON ke
   `/wp-json/my-custom-app/v1/survei/booking`.
2. WordPress memicu `rest_api_init`; `RestProvider` sudah mendaftarkan rutenya.
3. `SurveyBookingController::check_origin` memeriksa header Origin terhadap daftar izin.
4. `SurveyBookingController::store` menolak body lebih dari 8 KB atau JSON yang bentuknya salah.
5. `SurveyBookingService::book` menjalankan, berurutan:
   honeypot, `RateLimiter` (10 percobaan per IP per 10 menit), `SurveyBookingValidator`,
   pencarian booking ganda, `insert`, lalu `update` untuk mengisi kode.
6. Hasilnya dibungkus `BookingResult`; controller menjawab `201` (baru) atau `200` (ganda).
7. Jika Validator melempar `ValidationException`, controller menjawab dengan status dari
   pengecualian itu (422, 429, atau 400). Pengecualian lain dicatat ke log dan dijawab `500`
   dengan pesan umum.

## 12.5 Prinsip OOP yang dipakai, dengan contoh nyata

- **Enkapsulasi.** Kelas konkret bersifat `final`, properti memakai `private readonly`,
  dan helper bergaya statis menyembunyikan constructor (`private function __construct`)
  agar tidak bisa dibuat objeknya. `AbstractRepository::columns()` bersifat `protected`
  sehingga hanya turunannya yang menentukan kolom yang boleh ditulis.
- **Abstraksi.** `ClockInterface` menyembunyikan *dari mana* waktu berasal;
  `SurveyBookingRepositoryInterface` menyembunyikan *bagaimana* data disimpan.
  Service hanya tahu kontraknya.
- **Pewarisan.** `StatusController` dan `SurveyBookingController` mewarisi
  `AbstractRestController` sehingga `route()` (yang mewajibkan `permission_callback`) dan
  penanganan error terpusat tidak ditulis ulang. `SurveyBookingRepository` mewarisi
  `AbstractRepository` untuk operasi dasar tabel.
- **Polimorfisme.** `RestProvider` menerima daftar `RestControllerInterface` dan memanggil
  `register_routes()` tanpa peduli controller mana. `Plugin` memperlakukan semua
  `HookableInterface` sama. `Installer` menerima daftar `SchemaInterface`.
- **Injeksi ketergantungan (DI).** Objek tidak membuat kolaboratornya sendiri; semuanya
  masuk lewat constructor dan dirakit di satu tempat, `Plugin::create()`. Karena itu
  `SurveyBookingValidator` bisa diuji dengan jam palsu.
- **Pola metode templat.** `AbstractRepository` memanggil `table_suffix()` dan `columns()`
  yang abstrak dari metode konkret seperti `insert()`; turunan hanya mengisi dua bagian itu.
  `table()` bersifat `final` agar tidak bisa diubah.
- **Tanggung jawab tunggal.** Provider hanya mendaftarkan hook, Controller hanya mengurus
  request, Service hanya mengurus aturan, Repository hanya mengurus SQL.
- **Objek nilai tak berubah.** `BookingResult` hanya berisi properti `readonly`.

Catatan penyimpangan kecil: `SurveyBookingAdminController` menerima kelas konkret
`SurveyBookingRepository`, bukan `SurveyBookingRepositoryInterface`, karena memakai
`paginate()` dan `all()` yang tidak ada di interface. Itu wajar sekarang, tetapi perlu
dipikirkan jika ingin menguji controller admin dengan repository palsu.

## 12.6 Cara menambah fitur baru dengan pola yang sama

Contoh: fitur "Pendaftaran".

1. **Model.** Buat `Models/RegistrationRepository` yang `extends AbstractRepository`
   dan `implements SchemaInterface`. Isi `table_suffix()`, `columns()`, dan `schema_sql()`.
   Tambahkan interface-nya jika Service perlu diuji.
2. **Service.** Buat `Services/RegistrationService` (aturan bisnis) dan, bila perlu,
   `RegistrationValidator`. Terima dependensi lewat constructor.
3. **Controller.** Buat `Controllers/RegistrationController` yang `extends AbstractRestController`.
   Daftarkan rute dengan `route()` dan selalu berikan `permission_callback`. Rute yang sengaja
   publik harus mendokumentasikan alasan dan pengamannya, seperti pada `SurveyBookingController`.
4. **Rakit.** Di `Plugin::create()`, buat objek barunya, masukkan controller ke `RestProvider`,
   dan masukkan repository ke `Installer` agar tabelnya dibuat.
5. **Versi tabel.** Naikkan `Installer::DB_VERSION` agar `maybe_upgrade()` menjalankan `dbDelta`.
6. **Aksi admin (jika ada).** Ikuti urutan di `Security`: verifikasi nonce, lalu kapabilitas,
   baru sanitasi input dan panggil Service.

## 12.7 Glosarium

| Istilah | Arti sederhana |
|---|---|
| Kelas | Cetakan untuk membuat objek |
| Objek | Hasil dari cetakan itu, yang punya data dan perilaku |
| Interface | Daftar janji: "kelas ini pasti punya metode X" tanpa menulis isinya |
| Kelas abstrak | Kelas setengah jadi yang tidak bisa dipakai langsung, hanya diwarisi |
| `final` | Kelas atau metode yang tidak boleh diwarisi atau ditimpa |
| `readonly` | Properti yang tidak bisa diubah setelah diisi |
| Pewarisan | Kelas anak otomatis punya kemampuan kelas induk |
| Polimorfisme | Beberapa kelas berbeda dipanggil dengan cara yang sama |
| DI (injeksi ketergantungan) | Bahan yang dibutuhkan sebuah kelas diberikan dari luar |
| Composition root | Satu tempat tempat semua objek dirakit (`Plugin::create()`) |
| Hook | Titik di WordPress tempat kode kita boleh "menumpang" |
| Repository | Kelas khusus yang mengurus baca-tulis database |
| Service | Kelas khusus yang mengurus aturan bisnis |

## 12.8 Catatan RnD (Oktober 2026)

Hasil uji koneksi dan audit baca-saja. **Tidak ada kredensial yang disimpan di repo**;
semua kode akses yang pernah dipakai dalam percobaan wajib dicabut setelah RnD.

**Terbukti**
- Akun Editor `labib` (id 16) diterima REST API `eltahfidh.or.id` dengan HTTP 200; peran
  `editor`, kemampuan `manage_options` bernilai salah (bukan administrator).
- **Plugin `my-custom-app` tidak aktif di produksi (diuji 2026-10-06).** Daftar rute
  berlogin memuat 27 namespace tanpa `my-custom-app/v1`, dan `GET /my-custom-app/v1/status`
  dijawab `404 rest_no_route`. Dengan akun Editor belum bisa dibedakan apakah plugin
  terpasang-tetapi-nonaktif atau belum terpasang sama sekali (daftar plugin butuh hak
  `activate_plugins`).
- **Form `eltahfidh.github.io/survei` masih memakai Google Apps Script** (`API_URL` mengarah
  ke `script.google.com`), jadi form tetap berfungsi walau plugin tidak aktif.
- **Penyebab 403: firewall hosting menyaring User-Agent, bukan login atau asal IP.**
  Permintaan dengan UA persis `Mozilla/5.0` atau UA browser Chrome lengkap ditolak
  `403 text/html`, baik berlogin maupun tidak. UA lain lolos `200 JSON`: tanpa UA,
  `curl/8.5.0`, dan UA `build_posts.py` (`Mozilla/5.0 (elTAHFIDH static site builder)`).
  Artinya `tools/build_posts.py` berjalan normal dari cloud. **Jangan mengganti UA skrip
  menjadi UA browser.**
- Ekspor CSV sudah menangkal injeksi rumus lewat `csv_cell()` (sel yang diawali `=`, `+`,
  `-`, `@` diberi awalan).

**Dari pembacaan kode (belum diuji di situs)**
- `Installer` memberi kapabilitas `mca_manage_bookings` kepada peran `administrator` dan
  `editor` (`DEFAULT_ROLES`). Jika plugin aktif, Editor seharusnya dapat membuka halaman
  wp-admin "Booking Survei", sedangkan rute REST `/status` hanya untuk administrator.

**Belum diverifikasi**
- Apakah plugin belum terpasang atau terpasang-tetapi-nonaktif (perlu dilihat di wp-admin
  oleh administrator).
- Perilaku rute `POST /survei/booking` di produksi (baru bisa diuji setelah plugin aktif).

**Temuan audit kode (usulan perbaikan, belum dikerjakan)**
1. `RateLimiter` memakai `REMOTE_ADDR`; jika situs di belakang proxy atau Cloudflare, semua
   pengunjung berbagi satu batas 10 percobaan per 10 menit.
2. Pemeriksaan booking ganda dan penyimpanan tidak atomik, dan tabel tidak punya kunci unik
   pada `wa`, `santri`, `tanggal`; klik ganda yang cepat bisa menyimpan dua baris.
3. Kode booking dibuat dalam dua langkah (`insert` lalu `update`); kegagalan langkah kedua
   meninggalkan baris tanpa kode.
4. `build_posts.py` menganggap berkas thumbnail yang sudah ada sebagai utuh; unduhan yang
   terputus meninggalkan berkas rusak. Tulis ke berkas sementara lalu ganti namanya.
5. Pengujian baru berupa `tests/smoke-test.php`; `SurveyBookingValidator` murni dan paling
   mudah diuji unit.
