"""Membangun halaman jenjang (pengganti subdomain) ke site/: smp-quran.html, sma-quran.html, ifs.html.

Sumber: data/jenjang.json (isi kurasi), data/struktur-organisasi.json (pimpinan), dan db/jenjang/*
(berita subdomain hasil ekspor). Thumbnail berita diunduh sekali ke site/assets/img/posts/<key>-<id>.<ext>.
"""
from pathlib import Path, PurePosixPath

from .. import config
from ..http import HttpClient
from ..models import Content
from ..repositories import DataRepository, JsonRepository
from ..views import Layout, components, jenjang_page
from .article_index import ArticleIndex, is_interactive

POSTS_PER_PAGE = 6
IMAGE_SIZES = ("medium_large", "large", "medium")


class JenjangBuilder:
    def __init__(self, store: JsonRepository, data: DataRepository, client: HttpClient, site_dir: Path,
                 posts_per_page: int = POSTS_PER_PAGE):
        self._store = store
        self._data = data
        self._client = client
        self._site = Path(site_dir)
        self._limit = posts_per_page

    def build_all(self) -> list[tuple[str, int]]:
        content = self._data.jenjang()
        layout = Layout((self._site / "kontak.html").read_text(encoding="utf-8"))
        return [self.build(page, content, layout) for page in content["halaman"]]

    def build(self, page: dict, content: dict, layout: Layout) -> tuple[str, int]:
        org_cards = [self._org_card(name, content) for name in page["pimpinan"]]
        posts = self._latest_posts(page["sumber_berita"])
        internal = ArticleIndex(self._store).by_link()
        post_cards = [components.post_card(post, img, "          ",
                                           internal[post.link].href if post.link in internal else None)
                      for post, img in posts]
        main = jenjang_page.render(page, org_cards, post_cards)
        html = layout.render(page["file"], f"{page['judul']} - elTAHFIDH Indonesia", page["deskripsi"], main)
        (self._site / page["file"]).write_text(html, encoding="utf-8")
        return page["file"], len(posts)

    def _org_card(self, name: str, content: dict) -> str:
        lembaga = self._data.lembaga(name)
        pimpinan = lembaga["pimpinan"]
        foto = next((v for k, v in content.get("foto_pimpinan", {}).items() if k in pimpinan), None)
        sapaan = next((v for k, v in content.get("sapaan", {}).items() if k in pimpinan), None)
        return components.org_card(lembaga, foto, sapaan, "          ")

    def _latest_posts(self, keys: list[str]) -> list[tuple[Content, str | None]]:
        """Berita terbaru gabungan beberapa subdomain, diurutkan dari yang terbaru."""
        merged = []
        for key in keys:
            site = config.site_by_key(key)
            media = {m["id"]: m for m in self._store.read(site, "media", default=[])}
            merged += [(site, post, media.get(post.featured_media)) for post in self._store.contents(site, "posts")
                       if not is_interactive(post)]
        merged.sort(key=lambda row: row[1].date, reverse=True)
        return [(post, self._thumbnail(site, post, item)) for site, post, item in merged[:self._limit]]

    def _thumbnail(self, site, post: Content, media: dict | None) -> str | None:
        if not media:
            return None
        sizes = (media.get("media_details") or {}).get("sizes") or {}
        url = next((sizes[k]["source_url"] for k in IMAGE_SIZES if k in sizes), media.get("source_url"))
        if not url:
            return None
        ext = PurePosixPath(url.split("?")[0]).suffix.lower() or ".jpg"
        name = f"{site.key}-{post.id}{ext}"
        target = self._site / "assets" / "img" / "posts" / name
        if not target.exists():
            self._client.download(url, target)
        return f"assets/img/posts/{name}"
