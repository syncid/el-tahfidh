"""Pemeriksa tautan internal situs statis: setiap href/src/srcset lokal dan url() di CSS harus menunjuk
berkas yang ada, dan setiap #jangkar harus ada sebagai id/name di halaman tujuannya. Hanya membaca berkas."""
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_ATTRS = {"href", "src", "poster", "data-src"}
CSS_URL = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""")


@dataclass(frozen=True)
class BrokenLink:
    source: str   # berkas asal, relatif terhadap akar situs
    target: str   # nilai atribut apa adanya
    reason: str   # mis. "berkas tidak ada", "jangkar tidak ada"


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name in ("id", "name") and (name == "id" or tag == "a"):
                self.anchors.add(value)
            elif name in LINK_ATTRS:
                self.links.append(value)
            elif name == "srcset":
                self.links.extend(part.split()[0] for part in value.split(",") if part.strip())
            elif name == "style":
                self.links.extend(CSS_URL.findall(value))


def is_external(url: str) -> bool:
    url = url.strip()
    return not url or url.startswith(("//", "data:", "javascript:")) or bool(urlsplit(url).scheme)


class LinkChecker:
    def __init__(self, site_dir: Path):
        self._root = Path(site_dir)
        self._pages: dict[Path, _PageParser] = {}

    def _page(self, path: Path) -> _PageParser:
        if path not in self._pages:
            parser = _PageParser()
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            self._pages[path] = parser
        return self._pages[path]

    def files(self) -> list[Path]:
        return sorted(p for p in self._root.rglob("*") if p.suffix in (".html", ".css") and p.is_file())

    def check(self) -> tuple[int, list[BrokenLink]]:
        """Mengembalikan (jumlah tautan lokal yang diperiksa, daftar tautan rusak)."""
        checked, broken = 0, []
        for source in self.files():
            if source.suffix == ".css":
                links = CSS_URL.findall(source.read_text(encoding="utf-8", errors="replace"))
            else:
                links = self._page(source).links
            for link in links:
                if is_external(link):
                    continue
                checked += 1
                reason = self._problem(source, link)
                if reason:
                    broken.append(BrokenLink(source.relative_to(self._root).as_posix(), link, reason))
        return checked, broken

    def _problem(self, source: Path, link: str) -> str | None:
        parts = urlsplit(link.strip())
        target = source
        if parts.path:
            if parts.path.startswith("/"):
                # Situs dilayani di syncid.github.io/el-tahfidh/, jadi "/" menunjuk ke luar situs.
                return "alamat absolut (rusak di GitHub Pages)"
            target = (source.parent / unquote(parts.path)).resolve()
            if not target.is_relative_to(self._root.resolve()):
                return "di luar folder site/"
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                return "berkas tidak ada"
        fragment = unquote(parts.fragment)
        if fragment and target.suffix == ".html" and fragment not in self._page(target).anchors:
            return "jangkar tidak ada"
        return None
