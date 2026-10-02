# 06 — Operasional Repo & Cloud

> Indeks: [README](./README.md) · Sebelumnya: [05 — Plugin WordPress](./05-plugin-wordpress.md) · Berikutnya: [07 — Referensi Lokal](./07-referensi-lokal.md)

## 6.1 Git & GitHub

- Repo: `syncid/el-tahfidh` (**publik**), branch `main`, remote `origin` (HTTPS + credential manager).
- Identitas commit repo-lokal: `sync.id <idsyhl@gmail.com>` (diset via `git config` lokal;
  tidak ikut ter-clone — set ulang di tiap Codespace baru, lihat `docs/03`).
  Akun mengizinkan push email asli (pengaturan *"Block command line pushes that expose my email"*
  dimatikan agar atribusi ke akun tetap jalan).
- Ukuran GitHub: **±130 file / ~12 MB** (setelah `referensi/` dikeluarkan, Okt 2026).
  Clone cloud session jadi ringan; riwayat commit lama tetap menyimpan `referensi/`
  (±258 MB pack) sampai histori dibersihkan bila diinginkan.

## 6.2 GitHub Pages (aktif)

Status: **aktif** — situs live di https://syncid.github.io/el-tahfidh/. Workflow
`.github/workflows/pages.yml` menyebarkan folder `site/` tiap push ke `site/**`
atau manual via *workflow_dispatch*. Repo kini publik, sehingga Pages tersedia di
akun Free.

Mengaktifkan nanti (pilih satu):

Riwayat singkat: deploy pertama gagal karena repo privat di akun Free
(`422 Your current plan does not support GitHub Pages…`, run `36913681239`).
Setelah repo dipublikkan dan Pages dibuat lewat API, deploy berjalan normal.

Workflow memakai **sparse checkout** (hanya `site/`) + action resmi
`configure-pages` (dengan `enablement: true`) / `upload-pages-artifact` /
`deploy-pages`, trigger tiap push ke `site/`.

## 6.3 Actions

- Workflow aktif: hanya `pages.yml` (nonaktif). Run gagal pertama (saat Pages belum ada)
  bersifat historis dan tidak akan terulang.
- Menambah CI (mis. `php -l`, smoke test) aman dilakukan kapan saja — tidak butuh Pages.

## 6.4 Branch protection

Tidak tersedia di plan Free untuk repo privat (`403` via API). Pengganti saat ini:
kerja di branch fitur + PR manual ke `main`, hindari push langsung ke `main` dari cloud.
Pasang proteksi (wajib PR + status check) begitu repo publik / akun upgrade.

## 6.5 Backup folder lokal (`referensi/` di luar git)

| Jenis | Lokasi | Isi |
|---|---|---|
| Full git bundle (pra-pembersihan) | `%USERPROFILE%\git-backup\el-tahfidh-full-<timestamp>.gitbundle` | Seluruh histori termasuk `referensi/` — bisa `git clone` kembali kapan saja |
| Salinan file | `C:\el-tahfidh-backup-<timestamp>-referensi` | 1579 file cermin, untuk dipakai langsung / restore |

Detail + cara restore: [07 — Referensi Lokal](./07-referensi-lokal.md).
