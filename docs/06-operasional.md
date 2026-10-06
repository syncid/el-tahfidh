# 06 — Operasional Repo & Cloud

> Indeks: [README](./README.md) · Sebelumnya: [05 — Plugin WordPress](./05-plugin-wordpress.md) · Berikutnya: [07 — Referensi Lokal](./07-referensi-lokal.md)

## 6.1 Git & GitHub

- Repo: `syncid/el-tahfidh` (**publik**), branch `main`, remote `origin` (HTTPS + credential manager).
- Identitas commit repo-lokal: `sync.id <idsyhl@gmail.com>` (diset via `git config` lokal;
  tidak ikut ter-clone — set ulang di tiap Codespace baru, lihat `docs/03`).
  Akun mengizinkan push email asli (pengaturan *"Block command line pushes that expose my email"*
  dimatikan agar atribusi ke akun tetap jalan).
- Ukuran GitHub: **138 file / ~20 MB** (histori sudah dibersihkan dari `referensi/`
  via `git filter-repo`; pack lokal ±258 MB → ±20 MB, 0 objek `referensi/`).

## 6.2 GitHub Pages (aktif)

Status: **aktif** — situs live di https://syncid.github.io/el-tahfidh/. Workflow
`.github/workflows/pages.yml` menyebarkan folder `site/` tiap push ke `site/**`
atau manual via *workflow_dispatch*. Repo kini publik, sehingga Pages tersedia di
akun Free.

Riwayat singkat: deploy pertama gagal karena repo privat di akun Free
(`422 Your current plan does not support GitHub Pages…`, run `36913681239`).
Setelah repo dipublikkan dan Pages dibuat lewat API, deploy berjalan normal.

Workflow memakai **sparse checkout** (hanya `site/`) + action resmi
`configure-pages` (dengan `enablement: true`) / `upload-pages-artifact` /
`deploy-pages`, trigger tiap push ke `site/`.

## 6.3 Actions

- Workflow aktif: hanya `pages.yml`. Run gagal pertama (saat Pages belum ada)
  bersifat historis dan tidak terulang — run berikutnya `36991846771` hijau
  (`conclusion=success`).
- Menambah CI (mis. `php -l`, smoke test) aman dilakukan kapan saja — tidak butuh Pages.

## 6.4 Branch protection

Repo sekarang **publik**, jadi branch protection tersedia di akun Free (dulu gagal `403`
saat repo masih privat). **Terverifikasi 2026-10-02:** run deploy `36991846771` hijau
(`conclusion=success`), Pages `built`, situs live `HTTP 200`.

**Dibatalkan (Okt 2026):** rencana "wajib PR + status check untuk `main`" tidak dipasang.
Pemilik memutuskan semua perubahan dikirim langsung ke `main` (lihat 6.6 dan `CLAUDE.md`);
aturan wajib PR akan membuat push langsung ditolak GitHub. Terverifikasi 2026-10-06:
push langsung ke `main` berhasil, artinya belum ada branch protection.

## 6.5 Backup folder lokal (`referensi/` di luar git)

| Jenis | Lokasi | Isi |
|---|---|---|
| Full git bundle (pra-pembersihan) | `%USERPROFILE%\git-backup\el-tahfidh-full-<timestamp>.gitbundle` | Seluruh histori termasuk `referensi/` — bisa `git clone` kembali kapan saja |
| Backup pra-publikasi | bundle + salinan folder (di atas) | dipakai bila rollback histori diperlukan |
| Salinan file | `C:\el-tahfidh-backup-<timestamp>-referensi` | 1579 file cermin, untuk dipakai langsung / restore |

Detail + cara restore: [07 — Referensi Lokal](./07-referensi-lokal.md).

## 6.6 Sinkronisasi desktop, cloud, dan GitHub

| Tempat | Peran |
|---|---|
| GitHub `main` | Satu-satunya sumber kebenaran |
| Desktop `C:\el-tahfidh` | Mengambil sebelum kerja, mengirim sesudah kerja |
| Sesi Claude di cloud | Selalu mulai dari GitHub; mengirim langsung ke `main` begitu tugas dari pemilik selesai |

Rutinitas pemilik:

1. Sebelum kerja dan setiap kali Claude selesai push: jalankan `tools\sync.bat`
   (pindah ke `main`, `git pull --ff-only`, `git worktree prune`). Skrip berhenti dengan
   pesan jika masih ada perubahan yang belum di-commit.
2. Sesudah kerja: `git add -A`, `git commit`, `git push`. Jangan meninggalkan perubahan
   yang belum di-commit; bila sesi desktop dipindah ke cloud, perubahan itu terbawa sebagai
   commit "WIP: uncommitted changes, moved to the cloud".
3. Worktree lama di `.claude\worktrees\` dihapus dengan `git worktree remove <folder>`
   setelah isinya masuk ke `main`.

Aturan pengiriman untuk Claude ada di `CLAUDE.md` di akar repo, yang dibaca otomatis di
setiap sesi.

Catatan alat: pada sesi 2026-10-06 alat GitHub (pembuat pull request) di sesi cloud
gagal dengan galat `invalid session`, sedangkan `git push`/`fetch` tetap berjalan. Karena
pengiriman kini langsung ke `main`, alat itu tidak lagi diperlukan.
