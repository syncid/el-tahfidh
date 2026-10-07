"""Data publik yang dikurasi di repo (folder data/): isi halaman jenjang dan struktur organisasi.

Berbeda dengan db/ (lokal, tidak di-commit), folder data/ berisi konten publik yang sengaja di-commit.
"""
import json
from pathlib import Path


class DataRepository:
    def __init__(self, root: Path):
        self.root = Path(root)

    def _read(self, name: str) -> dict:
        return json.loads((self.root / name).read_text(encoding="utf-8"))

    def jenjang(self) -> dict:
        return self._read("jenjang.json")

    def lembaga(self, nama: str) -> dict:
        """Satu entri lembaga_mandiri dari struktur organisasi, berdasarkan nama persisnya."""
        for item in self._read("struktur-organisasi.json")["lembaga_mandiri"]:
            if item["nama"] == nama:
                return item
        raise KeyError(f"Lembaga tidak ada di struktur-organisasi.json: {nama}")
