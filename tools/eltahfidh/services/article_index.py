"""Daftar artikel yang dibuatkan halaman detail, beserta nama berkas unik masing-masing.

Dipakai bersama oleh ArticleBuilder (membangun halaman) dan JenjangBuilder (menautkan kartu berita),
sehingga keduanya selalu sepakat soal alamat halaman.
"""
import re
from dataclasses import dataclass

from .. import config
from ..models import Content, Site
from ..repositories import JsonRepository

# Kategori situs induk yang ditampilkan di situs statis (sama dengan PAGES di build_posts.py).
MAIN_CATEGORIES = {25: ("Berita", "berita.html"), 59: ("Artikel", "artikel.html")}
SKIP_SLUGS = {"hello-world"}
JENJANG_PAGES = {"smp": "smp-quran.html", "sma": "sma-quran.html", "ifs": "ifs.html", "psb": "psb.html"}

# Postingan yang sebenarnya alat interaktif (generator bingkai foto profil, edu-game): memuat elemen
# formulir/kanvas yang tidak berfungsi tanpa skripnya, jadi bukan berita.
_INTERACTIVE = re.compile(r"<(input|canvas|textarea|select|button)\b", re.I)


def is_interactive(post: Content) -> bool:
    return bool(_INTERACTIVE.search(post.content_html))


@dataclass(frozen=True)
class ArticleEntry:
    site: Site
    post: Content
    file: str          # nama berkas di site/berita/, mis. 'wisuda-38-daiyah.html'
    section: str       # label remah roti, mis. 'Berita' atau "SMP Qur'an Putra"
    back_page: str     # halaman induk, mis. 'berita.html' atau 'smp-quran.html'

    @property
    def href(self) -> str:
        """Tautan dari halaman di akar site/."""
        return f"berita/{self.file}"


class ArticleIndex:
    def __init__(self, store: JsonRepository):
        self._store = store

    def entries(self) -> list[ArticleEntry]:
        rows: list[tuple[Site, Content, str, str]] = []
        for post in self._store.contents(config.MAIN_SITE, "posts"):
            category = next((MAIN_CATEGORIES[c] for c in post.categories if c in MAIN_CATEGORIES), None)
            if category:
                rows.append((config.MAIN_SITE, post, *category))
        for site in config.SUBSITES:
            back = JENJANG_PAGES.get(site.jenjang, "berita.html")
            rows += [(site, post, site.label, back) for post in self._store.contents(site, "posts")]

        used: set[str] = set()
        entries = []
        for site, post, section, back in rows:
            if post.slug in SKIP_SLUGS or not post.slug or is_interactive(post):
                continue
            name = post.slug if post.slug not in used else f"{post.slug}-{site.key}"
            used.add(name)
            entries.append(ArticleEntry(site, post, f"{name}.html", section, back))
        return entries

    def by_link(self) -> dict[str, ArticleEntry]:
        return {e.post.link: e for e in self.entries()}
