# elTAHFIDH

| Folder | Isi |
|---|---|
| `site\` | Website statis elTAHFIDH (index, profil, psb, kontak, berita, artikel). Buka `site\index.html`. |
| `wp-content\plugins\my-custom-app\` | Plugin WordPress (backend Booking Survei untuk eltahfidh.github.io/survei). Lihat README di dalamnya. |
| `tools\` | Skrip pendukung (lihat di bawah). |
| `source-assets\` | Aset asli yang diunduh dari eltahfidh.or.id (sebelum diganti nama/dipakai di `site\`). |
| `docs\` | Dokumentasi proyek gaya roadmap.sh — mulai dari [docs/README.md](docs/README.md). |
| `referensi\` | ⚠️ **Hanya di laptop ini, tidak di GitHub.** Salinan kreativaglobal.sch.id (HTTrack) sebagai referensi tata letak. Lihat [docs/07-referensi-lokal.md](docs/07-referensi-lokal.md). |

## Skrip di `tools\`

```bash
python tools/build_posts.py
```
Menarik 12 berita & 12 artikel terbaru dari eltahfidh.or.id, mengunduh thumbnail, lalu
memperbarui `site\berita.html`, `site\artikel.html`, dan 3 berita di beranda.

```bash
tools\mirror-kreativa.bat
```
Memperbarui salinan Kreativa di `referensi\kreativa-mirror\` (butuh WinHTTrack, hanya Windows),
lalu menjalankan `tools\fixup.py` untuk memperbaiki deteksi bahasa EN/ID di salinan.
Hasilnya tidak di-commit (folder lokal saja).

## Pratinjau lokal

```bash
python -m http.server 8081 --directory site
```
Buka `http://127.0.0.1:8081/`. Lihat juga **situs live**: https://syncid.github.io/el-tahfidh/ (deploy otomatis tiap push ke `site/`).

## Kerja di cloud (GitHub Codespaces)

Repo ini sudah menyertakan `.devcontainer/devcontainer.json` (PHP 8.3 + Composer, Python 3,
GitHub CLI), jadi tidak perlu setup manual.

1. Di halaman repo di GitHub: **Code → Codespaces → Create codespace on main**.
2. Di terminal Codespace, jalankan pratinjau situs:
   ```bash
   python -m http.server 8081 --directory site
   ```
   Port 8081 diteruskan otomatis — klik tautan yang muncul di tab **Ports**.
3. Perintah lain tetap sama: `python tools/build_posts.py`, dan seterusnya.
   (`tools\mirror-kreativa.bat` hanya jalan di Windows + WinHTTrack, jadi tidak tersedia di Codespace.)
4. Setelah commit dari Codespace, set identitas sekali:
   ```bash
   git config user.email idsyhl@gmail.com && git config user.name sync.id
   ```

