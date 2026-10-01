# 07 — Folder Referensi Lokal (`referensi/`)

> Indeks: [README](./README.md) · Sebelumnya: [06 — Operasional](./06-operasional.md) · Berikutnya: [08 — Roadmap](./08-roadmap.md)

## 7.1 Status: LOKAL SAJA

`referensi/` **tidak di-track git** (`/referensi/` di `.gitignore`) dan **tidak ada di GitHub**.
Alasan: cermin HTTrack situs pihak lain (`kreativaglobal.sch.id`, ±379 MB / 1579 file) —
berat untuk clone/cloud session dan bukan karya repo ini. Tidak ada kode produk yang
membacanya; murni bahan perbandingan tata letak untuk manusia.

Isi:

| Folder | Isi |
|---|---|
| `referensi/kreativa-mirror/` (~282 MB) | Cermin aktif (dijalankan ulang via `tools\mirror-kreativa.bat`), termasuk `hts-cache/` file kerja HTTrack |
| `referensi/kreativa-template/` (~97 MB) | Cermin HTTrack pertama (dari `/id/`), arsip pembanding |

## 7.2 Backup yang tersedia

| Jenis | Lokasi | Cara pakai |
|---|---|---|
| Full git bundle | `%USERPROFILE%\git-backup\el-tahfidh-full-<timestamp>.gitbundle` | `git clone <file> folder-baru` → dapat seluruh histori + `referensi/` versi saat backup |
| Salinan file | `C:\el-tahfidh-backup-<timestamp>-referensi` | Copy kembali ke `C:\el-tahfidh\referensi\` bila folder lokal terhapus |

## 7.3 Skrip mirror (hanya laptop Windows)

```bat
tools\mirror-kreativa.bat
```

Menjalankan ulang HTTrack (`C:\Program Files\WinHTTrack\httrack.exe`) ke
`referensi\kreativa-mirror`, lalu `tools\fixup.py` mengembalikan literal JS
deteksi bahasa EN/ID yang ditulis ulang HTTrack menjadi `/id/`.
Tidak jalan di Codespace (butuh Windows + WinHTTrack) — dan tidak perlu,
karena hasilnya memang tidak di-commit.

## 7.4 Aturan main

1. Jangan pindahkan file produk (site/plugin/tools/docs) ke dalam `referensi/`.
2. Jangan commit `referensi/` — `.gitignore` sudah menjaganya; bila `git status`
   menampilkannya, berarti baris `/referensi/` terhapus dari `.gitignore`.
3. Backup ulang sesekali bila cermin diperbarui: copy folder + (opsional) `git bundle`
   dari repo lokal — riwayat `referensi/` versi baru tidak akan ada di GitHub.
