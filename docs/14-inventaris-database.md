# 14 — Inventaris Database (StackCP/20i)

> Indeks: [README](./README.md) · Sebelumnya: [13 — Struktur Organisasi](./13-struktur-organisasi.md) · Berikutnya: [15 — Aturan Kerja](./15-aturan-kerja.md)

Jawaban singkat: **tidak**. Menarik dari `MySQL Host Selection` 1x TIDAK
menarik 85 DB sekaligus. 1x `Sign in` = masuk 1 server saja.

## 14.1 Dua halaman, satu barang yang sama

`Manage MySQL Databases`: 1 baris = 1 database (total 85 baris, bersambung
ke halaman berikut). Kolom `Server` = gedungnya, `Database/Username` = nama
DB (= nama user), `Usage x / 1024 MB` = ukuran DB itu saja, `Actions >
Options` = aksi per DB (phpMyAdmin 1 DB, export, hapus).

`MySQL Host Selection`: 1 baris = 1 server (total 12 baris). Kolom
`Hostname` = nama server, `Databases` = daftar nama yang numpang di server
itu, `Sign in` = login SSO ke phpMyAdmin server itu saja.

Total kedua halaman sama: 85 DB dipecah 20i ke 12 server demi performa
(*your databases have been split across multiple MySQL servers*).

## 14.2 Isi per server (dari screenshot, Okt 2026)

sdb-j (10): wordpress-3139304c5d, wordpress-3139300c43,
wordpress-pqe2022-313930a666, toko-novia-31393075a9,
wordpress-313930a6fb, wordpress-313930c816, wordpress-313930db5a,
wordpress-313930ae66, wordpress-313930d53e, wordpress-313930ee1f.

sdb-i (2): tokoamira-frozen-313839cacd, wordpress-3138394081.

sdb-l (9): wordpress-313932e342, wordpress-3139328cdb,
wordpress-313932b77b, wordpress-313932e7d6, wordpress-313932a14e,
wordpress-31393206da, wordpress-3139328826, wordpress-313932acfc,
wordpress-3139325bee.

sdb-k (6): wordpress-3139319ec3, wordpress-313931d426,
wordpress-3139314778, wordpress-313931ae9e, wordpress-313931a9a5,
wordpress-313931ad97.

sdb-73 (1): wordpress-3530363398cc = DB utama eltahfidh.or.id (86 MB).

sdb-72 (4): wordpress-353036316848, wordpress-35303631a466,
wordpress-353036315b0f, wordpress-35303631dd8e.

sdb-74 (4): wordpress-353036354e3f, wordpress-353036358700,
wordpress-353036354a5c, wordpress-3530363599d4.

sdb-71 (5): wordpress-35303539bfee, wordpress-35303539ad99,
wordpress-35303539f659, wordpress-35303539893f, wordpress-35303539c183.

sdb-84 (11): wordpress-35303936275d, wordpress-353039360425,
wordpress-353039364c2e, wordpress-35303936abd2, wordpress-353039365498,
wordpress-353039367eb3, wordpress-35303936267a, wordpress-353039366819,
wordpress-3530393666f, wordpress-35303936bc37,
dbapp_sekolah-35303936bf63.

sdb-85 (9): wordpress-35303938d31f, wordpress-353039383ff9,
wordpress-35303938bcd8, wordpress-3530393881e8, wordpress-35303938495e,
wordpress-353039389b53, wordpress-353039388442, wordpress-353039385b0a,
wordpress-353039387143.

sdb-86 (8): wordpress-35313030315b, wordpress-35313030cab,
wordpress-35313030027a, wordpress-35313030bf90, wordpress-353130304751,
wordpress-3531303016b8, wordpress-353130309c0d, moodle-35313030d040.

sdb-83 (9): wordpress-35303934ef69, wordpress-353039341963,
wordpress-3530393405bf, wordpress-35303934e679, wordpress-353039345519,
wordpress-353039346ad7, wordpress-353039345656, moodle-3530393429ad,
db_absensi-35303934df01.

Ukuran contoh dari halaman Manage: wordpress-3139304c5d 2,91 MB,
wordpress-3139300c43 21,02 MB, wordpress-pqe2022-313930a666 128,53 MB,
toko-novia-31393075a9 2,33 MB, wordpress-313930a6fb 2,08 MB,
tokoamira-frozen-313839cacd 3,31 MB, wordpress-3138394081 3,45 MB,
wordpress-313932e342 4,61 MB, wordpress-3139319ec3 42,14 MB.

## 14.3 Mekanisme tarik yang benar

1. `Sign in` 1 baris = masuk lobi 1 gedung saja, bukan unduh otomatis.
Contoh klik sdb-73: panel kiri phpMyAdmin hanya menampilkan 1 DB
wordpress-3530363398cc. Export > Go = 1 file .sql.

2. Klik sdb-j: panel kiri menampilkan 10 DB itu. Export tetap 1 per 1
(klik DB 1 > Export > Go, ulangi 10x). Tidak ada tombol 1x jadi 10 file.

3. Isi .sql SAMA PERSIS lewat pintu mana pun karena sumbernya satu.
Manage > Options > phpMyAdmin untuk 1 DB = Host Selection > Sign in >
pilih DB yang sama.

4. Analogi: Manage = pintu per kamar, Host Selection = pintu per gedung.
Masuk gedung J hanya dapat 10 kamar di gedung J.

## 14.4 Yang perlu ditarik untuk elTAHFIDH

Tidak perlu 85 DB. Tiap DB isinya beda (toko-novia = toko, pqe2022 =
situs lain, moodle/db_absensi = aplikasi belajar/absensi). Cukup:

- sdb-73 > Sign in > Export wordpress-3530363398cc (DB eltahfidh.or.id).

Menyusul setelah pemilik cek kolom situs di Manage: 4 DB subdomain
(smp/smaquran putra/putri), islamicfulldayschool, spmb, db_absensi,
dbapp_sekolah, moodle bila resmi milik pesantren.

## 14.5 Cara export aman

1. Masuk StackCP via my.20i.com, buka bagian database.
2. Host Selection > sdb-73 > Sign in > pilih wordpress-3530363398cc >
Export > Go (SQL). Simpan .sql di luar repo (jangan di-commit, berisi
data pengguna).
3. Jangan pakai Change Password di Manage kecuali siap update
wp-config.php situs itu, karena situs langsung putus koneksi.



