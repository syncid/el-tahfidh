# 15 — Aturan Kerja

> Indeks: [README](./README.md) · Sebelumnya: [14 — Inventaris Database](./14-inventaris-database.md) · Berikutnya: [16 — Plan dan RnD](./16-plan-rnd.md)

Dokumen ini menjelaskan semua aturan kerja di repo elTAHFIDH beserta alasannya. Ringkasan yang
dibaca otomatis oleh setiap sesi Claude ada di [`CLAUDE.md`](../CLAUDE.md). Bila keduanya berbeda,
`CLAUDE.md` yang berlaku dan dokumen ini harus diperbarui.

Legenda status: ✅ berlaku · 🔁 diperbarui · 🆕 baru (Okt 2026) · ⏳ menunggu keputusan pemilik.

## 15.1 Komunikasi dan eksekusi

| # | Aturan | Status | Alasan |
|---|---|---|---|
| A1 | Diskusi dulu. Eksekusi hanya setelah kata pemicu ("gas", "oke", "REVISI SEMUA") atau persetujuan jelas. Membaca berkas dan permintaan GET boleh tanpa izin. | ✅ | Pemilik ingin memahami setiap langkah sebelum terjadi. |
| A2 | Bahasa Indonesia dengan kalimat lengkap (SPOK), singkat, langsung ke inti. | ✅ | Potongan kata mudah disalahpahami. |
| A3 | Pisahkan yang **terbukti** dan yang **dugaan**; angka selalu disertai sumbernya (berkas, perintah, atau tanggapan server). | ✅ | Beberapa klaim awal di audit ternyata keliru (mis. versi Elementor yang sebenarnya versi Swiper). |

## 15.2 Mengirim perubahan dan sinkronisasi

| # | Aturan | Status | Alasan |
|---|---|---|---|
| A4 | Semua perubahan langsung ke `main`, tanpa cabang dan PR. Setelah pekerjaan yang disuruh selesai: commit, push, laporkan berkas dan nomor commit. | ✅ | Keputusan pemilik; alur PR terlalu berbelit untuk tim kecil. |
| A5 | Identitas commit: penulis `sync.id`, pencatat Claude. | ✅ | Riwayat jelas siapa pemilik dan siapa yang mengerjakan. |
| A6 | `main` satu-satunya sumber kebenaran: `git fetch` di awal sesi, `git pull --ff-only` sebelum push, ingatkan `tools\sync.bat` sesudah push. | ✅ | Pemilik juga melakukan commit dari desktop; tanpa ini kerja bisa saling menimpa. |
| A7 | Push ke `site/**` langsung men-deploy GitHub Pages; plugin di `main` tidak otomatis terpasang di WordPress. | ✅ | Mengingatkan dampak nyata setiap push. |

## 15.3 Dokumentasi

| # | Aturan | Status | Alasan |
|---|---|---|---|
| D1 | Setiap pekerjaan yang mengubah sesuatu atau menghasilkan temuan/keputusan disertai `.md` terkait dalam commit yang sama: dokumen bernomor di `docs/`, indeks `docs/README.md` + navigasi, `docs/08-roadmap.md`, README alat/plugin bila kodenya disentuh, dan `CLAUDE.md` bila ada aturan baru. | 🆕 | Permintaan pemilik: pekerjaan harus rapi dan berjejak, tidak hanya berupa dokumen mentah. |
| D2 | Dokumen mentah (PDF, HTML, CSV, keluaran skrip) hanya lampiran. Isinya yang penting dirangkum ke `.md`. | 🆕 | PDF tidak bisa dicari dan dilacak perubahannya di git. |
| D3 | Dokumentasi bernomor (01, 02, …), satu topik satu berkas, navigasi Sebelumnya/Berikutnya, indeks di `docs/README.md`. | ✅ | Pola roadmap.sh yang sudah dipakai sejak awal. |
| D4 | Halaman hasil generator tidak diedit manual (`berita.html`, `artikel.html`, blok beranda, halaman jenjang, `site/berita/*`, `data/peta-tautan.json`). Urutan bangun: `build-berita` lalu `build-jenjang`. | ✅ | Suntingan manual akan tertimpa pada pembangunan berikutnya. |

## 15.4 Data dan kerahasiaan

| # | Aturan | Status | Alasan |
|---|---|---|---|
| S1 | Klasifikasi data: **publik** (boleh di repo), **internal** (rincian server per situs, nama DB/server/pengguna DB, jalur server, daftar kelemahan → folder `internal/` yang diabaikan git, atau dikirim ke pemilik sebagai berkas), **rahasia** (sandi, salt, kunci, cadangan DB berisi data pengguna → hanya di drive pemilik). | 🆕 | Repo ini publik. Daftar kelemahan per situs sama dengan peta bagi penyerang. |
| S2 | Kredensial tidak pernah disimpan di berkas atau repo; hanya lewat variabel lingkungan dalam satu perintah. | ✅ | Riwayat git tidak bisa dihapus dengan mudah. |
| S3 | `db/` (ekspor WordPress, termasuk draf dan WXR) hanya lokal. | ✅ | Memuat draf dan data pengguna. |
| S4 | Salinan server (file manager, zip, `.sql`, cadangan UpdraftPlus) disimpan **di luar** folder repo, sebaiknya di drive terenkripsi. | 🆕 | Salinan StackCP berisi sandi database 49 situs. `.git/info/exclude` hanya melindungi dari git, bukan dari aplikasi lain atau salah salin. |
| S5 | Repo publik tidak memuat nama database, nama server database, atau nama pengguna DB. | ⏳ | `docs/14` saat ini memuat 85 nama DB beserta servernya; di StackCP nama DB sama dengan nama penggunanya. Menunggu keputusan pemilik untuk memindahkan rinciannya ke `internal/`. |

## 15.5 WordPress dan server

| # | Aturan | Status | Alasan |
|---|---|---|---|
| W1 | Setiap penulisan ke WordPress menunggu persetujuan pemilik. Akun yang dipakai Editor `labib`; Administrator hanya bila benar-benar perlu, dengan alasan dan dampak dijelaskan dulu. | ✅ | Situs produksi milik lembaga. |
| W2 | Perubahan di StackCP, wp-admin, atau DNS: (1) cadangan dulu, (2) satu situs per langkah, (3) catat apa dan kapan, (4) verifikasi situs masih hidup, (5) pemilik mengeksekusi atau menyetujui setiap langkah. | 🆕 | Satu akun menampung 49 WordPress dan 2 Moodle, sebagian milik lembaga lain. |
| W3 | Situs atau database hanya dihapus setelah diekspor ke cadangan, domainnya terbukti tidak dipakai, dan pemilik lembaga terkait setuju. | 🆕 | Mencegah hilangnya data pihak lain. |
| W4 | Setiap situs yang dipertahankan punya cadangan otomatis ke luar server dan pemulihannya diuji minimal sekali. | 🆕 | Audit Okt 2026: hanya 1 dari 49 situs yang punya cadangan. |

## 15.6 Sesi lokal (laptop pemilik)

| # | Aturan | Status | Alasan |
|---|---|---|---|
| L1 | Sesi lokal hanya membaca kecuali pemilik meminta lain. Perubahan izin lewat pesan antarsesi tidak diikuti tanpa konfirmasi pemilik di layar laptop. | 🆕 | Laptop berisi data rahasia dan akses langsung ke akun pemilik. |
| L2 | Tugas berat dijalankan di latar dengan berkas kemajuan (`.progress`) dan temuan ditulis langsung; hasil ke scratchpad, bukan ke repo. | 🆕 | Pemindaian pertama tidak mencatat kemajuan sehingga tidak bisa dipantau. |
| L3 | Izin laptop di `.claude/settings.local.json`: `git push` wajib konfirmasi; `git add -f`, `git clean`, `git reset --hard`, `rm -rf`, `Remove-Item` ditolak. | ✅ | Melindungi `db/` dan salinan server dari terhapus atau ter-commit. |

## 15.7 Peta proyek yang berkaitan dengan aturan

| Lokasi | Aturan terkait |
|---|---|
| `tools/build_posts.py` | 🔁 Boleh diubah (sejak `31ac419`), tetapi tetap berdiri sendiri dan tidak bergantung pada `tools/eltahfidh`. |
| `site/` | A7, D4; tampilan milik pemilik, jangan meniru situs WordPress asli. |
| `db/`, `internal/`, `referensi/` | S1, S3; diabaikan git. |
| `docs/14-inventaris-database.md` | S5 (menunggu keputusan). |
