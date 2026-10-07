"""Penyimpanan: folder db/ berisi berkas JSON. Satu-satunya lapisan yang tahu tata letak db/.

db/
  manifest.json                 waktu ekspor, jumlah per situs
  utama/<nama>.json             situs induk
  utama/private/<nama>.json     draf, pengguna, komentar (data pribadi)
  jenjang/<key>/<nama>.json     enam subdomain
  media/<host>/<yyyy>/<mm>/...  berkas media hasil unduhan
"""
import json
from pathlib import Path

from ..models import Content, Media, Site, Term

README = """Folder ini adalah "database" lokal hasil ekspor WordPress elTAHFIDH.

JANGAN di-commit ke GitHub. Folder ini sudah diabaikan oleh .gitignore (/db/).
Isinya mencakup draf yang belum terbit dan data pengguna.

Dibuat ulang dengan:  python -m tools.eltahfidh export
Lihat tools/eltahfidh/README.md untuk rinciannya.
"""


class JsonRepository:
    def __init__(self, root: Path):
        self.root = Path(root)

    def site_dir(self, site: Site, private: bool = False) -> Path:
        base = self.root / "utama" if site.is_main else self.root / "jenjang" / site.key
        return base / "private" if private else base

    def media_dir(self, site: Site) -> Path:
        return self.root / "media" / site.host

    def write(self, site: Site, name: str, data, private: bool = False) -> Path:
        path = self.site_dir(site, private) / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)
        return path

    def read(self, site: Site, name: str, private: bool = False, default=None):
        path = self.site_dir(site, private) / f"{name}.json"
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def exists(self, site: Site, name: str, private: bool = False) -> bool:
        return (self.site_dir(site, private) / f"{name}.json").exists()

    # --- akses bertipe untuk Service ---

    def contents(self, site: Site, name: str) -> list[Content]:
        return [Content.from_api(item) for item in self.read(site, name, default=[])]

    def terms(self, site: Site, name: str) -> list[Term]:
        return [Term.from_api(item) for item in self.read(site, name, default=[])]

    def media(self, site: Site) -> list[Media]:
        return [Media.from_api(item) for item in self.read(site, "media", default=[])]

    # --- berkas di akar db/ ---

    def write_manifest(self, manifest: dict) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "README.txt").write_text(README, encoding="utf-8")
        path = self.root / "manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        return path

    def read_manifest(self) -> dict:
        path = self.root / "manifest.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
