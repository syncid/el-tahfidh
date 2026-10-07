"""Paket alat elTAHFIDH: ekspor WordPress ke "database" lokal dan generator situs statis.

Pola lapisannya meniru plugin my-custom-app (lihat docs/12-oop-plugin.md):
  models/        entitas data (Model)
  repositories/  sumber dan penyimpanan data (Repository)
  services/      logika kerja (Service)
  cli.py         perintah baris (Controller)

Hanya memakai pustaka standar Python, sama seperti tools/build_posts.py.
Jalankan dari akar repo:  python -m tools.eltahfidh --help
"""
