"""Membangun halaman detail berita/artikel ke site/berita/<slug>.html dari db/.

Gambar tetap menaut ke server WordPress asal (tidak diunduh ke repo agar ukurannya kecil).
Peta alamat lama -> baru ditulis ke data/peta-tautan.json sebagai bahan pengalihan (redirect) nanti.
"""
import json
import re
from pathlib import Path, PurePosixPath

from ..repositories import JsonRepository
from ..views import Layout, article_page
from .article_index import ArticleIndex
from .content_cleaner import clean_content

FEATURED_SIZES = ("large", "medium_large", "full")


def _image_stem(url: str) -> str:
    """'.../foto-1024x552.jpeg' -> 'foto': nama berkas tanpa akhiran ukuran WordPress dan ekstensi."""
    stem = PurePosixPath(url.split("?")[0]).stem
    return re.sub(r"-\d+x\d+$", "", re.sub(r"-scaled$", "", stem))


class ArticleBuilder:
    def __init__(self, store: JsonRepository, site_dir: Path, data_dir: Path):
        self._store = store
        self._site = Path(site_dir)
        self._data = Path(data_dir)

    def build_all(self) -> int:
        layout = Layout((self._site / "kontak.html").read_text(encoding="utf-8"))
        out_dir = self._site / "berita"
        out_dir.mkdir(exist_ok=True)
        entries = ArticleIndex(self._store).entries()
        media = self._media_maps({entry.site for entry in entries})

        expected = set()
        for entry in entries:
            content = clean_content(entry.post.content_html)
            featured = self._featured(media[entry.site.key].get(entry.post.featured_media))
            if featured and _image_stem(featured) in content:
                featured = None  # gambar unggulan sudah ada di dalam isi; jangan ditampilkan dua kali
            main = article_page.render(entry, content, featured)
            html = layout.render(entry.back_page, f"{entry.post.title} - elTAHFIDH Indonesia",
                                 entry.post.excerpt(155), main, depth=1)
            (out_dir / entry.file).write_text(html, encoding="utf-8")
            expected.add(entry.file)

        # Hapus halaman lama yang artikelnya sudah tidak ada di db/.
        for stale in out_dir.glob("*.html"):
            if stale.name not in expected:
                stale.unlink()

        links = {entry.post.link: f"/berita/{entry.file}" for entry in entries}
        (self._data / "peta-tautan.json").write_text(
            json.dumps(dict(sorted(links.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return len(entries)

    def _media_maps(self, sites) -> dict[str, dict]:
        return {s.key: {m["id"]: m for m in self._store.read(s, "media", default=[])} for s in sites}

    @staticmethod
    def _featured(media: dict | None) -> str | None:
        if not media:
            return None
        sizes = (media.get("media_details") or {}).get("sizes") or {}
        return next((sizes[k]["source_url"] for k in FEATURED_SIZES if k in sizes), media.get("source_url"))
