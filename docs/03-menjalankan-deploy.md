# 03 — Panduan Menjalankan & Deploy

> Indeks: [README](./README.md) · Sebelumnya: [02 — Arsitektur](./02-arsitektur.md) · Berikutnya: [04 — Situs Statis](./04-situs-statis.md)

## 3.1 Pratinjau lokal (Windows)

```bash
python -m http.server 8081 --directory site
# buka http://127.0.0.1:8081/
```

Tanpa server pun bisa: buka `site\index.html` langsung — situs tanpa build step.
`tools\build_posts.py` butuh internet (menarik WP API publik + mengunduh thumbnail).

## 3.2 Sesi cloud (GitHub Codespaces)

1. Buka `https://codespaces.new/syncid/el-tahfidh` → *Create codespace on main*.
2. Container otomatis berisi PHP 8.3 + Composer, Python 3, GitHub CLI;
   `composer install` plugin berjalan sendiri via `onCreateCommand`.
3. Perintah sama seperti lokal:
   ```bash
   python -m http.server 8081 --directory site   # port 8081 auto-forward (tab Ports)
   python tools/build_posts.py
   ```
4. Setelah commit dari Codespace, set identitas sekali per codespace:
   ```bash
   git config user.email idsyhl@gmail.com && git config user.name sync.id
   ```
   (Config git lokal tidak ikut ter-clone.)
5. `tools\mirror-kreativa.bat` **tidak jalan** di Codespace (butuh Windows + WinHTTrack) —
   mirror referensi hanya dikerjakan dari laptop, dan memang tidak di-track git.

## 3.3 Deploy situs statis

| Tujuan | Cara |
|---|---|
| Hosting statis apa pun (cPanel, Netlify, dsb.) | Unggah isi `site/` apa adanya |
| GitHub Pages | **Belum aktif** (repo privat + akun Free). Kalau repo dipublikkan / akun di-upgrade: hapus `if: false` di `.github/workflows/pages.yml` + *Enable* workflow di tab Actions — deploy otomatis tiap push ke `site/`. Detail: `docs/06-operasional.md` |

## 3.4 Deploy plugin WordPress

1. Di Codespace/lokal: `cd wp-content/plugins/my-custom-app && composer install --no-dev --optimize-autoloader`
   (di Codespace langkah ini sudah otomatis saat pembuatan container).
2. Salin folder `my-custom-app/` **beserta `vendor/` hasil install** ke
   `wp-content/plugins/` di server `eltahfidh.or.id` (via SFTP/manajer file — `vendor/` tidak ada di repo).
3. Aktifkan plugin di wp-admin. Tabel `{prefix}mca_survey_bookings` dibuat otomatis
   pada request pertama.
4. Arahkan form survei ke endpoint baru (satu baris `API_URL` di `index.html` form):
   `https://eltahfidh.or.id/wp-json/my-custom-app/v1/survei/booking`
5. Smoke test: buka `.../wp-json/my-custom-app/v1/status` (atau jalankan `tests/smoke-test.php`
   sesuai README plugin), coba kirim 1 booking uji, cek muncul di menu **Booking Survei**.
