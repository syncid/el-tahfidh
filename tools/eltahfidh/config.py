"""Konfigurasi tetap: daftar situs dan lokasi db/."""
import os
from pathlib import Path

from .models import Site

REPO = Path(__file__).resolve().parents[2]

# Data publik yang dikurasi (di-commit) dan folder situs statis.
DATA_DIR = REPO / "data"
SITE_DIR = REPO / "site"

# "Database" lokal. Diabaikan git (.gitignore: /db/); boleh dipindah lewat env ELTAHFIDH_DB.
DB_DIR = Path(os.environ.get("ELTAHFIDH_DB") or REPO / "db")

# Firewall hosting menolak UA browser ("Mozilla/5.0" persis atau UA Chrome lengkap) dengan 403.
# UA ini terbukti lolos (docs/12 §12.8). Jangan diganti menjadi UA browser.
USER_AGENT = "Mozilla/5.0 (elTAHFIDH static site builder)"

# Jeda minimum antar-permintaan ke server 20i. Sekitar 30 permintaan beruntun dijawab 429.
REQUEST_INTERVAL = 2.5

MAIN_SITE = Site("utama", "eltahfidh.or.id", "elTAHFIDH Indonesia")

SUBSITES = [
    Site("smp-quran-putra", "smpquran.eltahfidh.or.id", "SMP Qur'an Putra", "smp"),
    Site("smp-quran-putri", "smpquranputri.eltahfidh.or.id", "SMP Qur'an Putri", "smp"),
    Site("sma-quran-putra", "smaquran.eltahfidh.or.id", "SMA Qur'an Putra", "sma"),
    Site("sma-quran-putri", "smaquranputri.eltahfidh.or.id", "SMA Qur'an Putri", "sma"),
    Site("ifs", "islamicfulldayschool.eltahfidh.or.id", "Islamic Full Day School", "ifs"),
    Site("spmb", "spmb.eltahfidh.or.id", "SPMB elTAHFIDH", "psb"),
]

ALL_SITES = [MAIN_SITE, *SUBSITES]


def site_by_key(key: str) -> Site:
    for site in ALL_SITES:
        if site.key == key:
            return site
    raise KeyError(f"Situs tidak dikenal: {key}. Pilihan: {', '.join(s.key for s in ALL_SITES)}")
