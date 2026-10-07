"""Entitas konten. Dibentuk dari objek REST API WordPress yang tersimpan di db/."""
import html
import re
from dataclasses import dataclass, field

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def _rendered(value) -> str:
    """REST API memberi {'rendered': ..., 'raw': ...} untuk judul/isi; ambil teksnya."""
    if isinstance(value, dict):
        return value.get("rendered") or value.get("raw") or ""
    return value or ""


def plain_text(markup: str) -> str:
    text = re.sub(r"<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


@dataclass
class Content:
    """Postingan atau halaman WordPress."""

    id: int
    type: str
    slug: str
    status: str
    date: str
    link: str
    title: str
    content_html: str
    content_raw: str = ""
    excerpt_html: str = ""
    featured_media: int = 0
    categories: list[int] = field(default_factory=list)
    tags: list[int] = field(default_factory=list)
    parent: int = 0

    @classmethod
    def from_api(cls, item: dict) -> "Content":
        content = item.get("content") or {}
        return cls(
            id=int(item["id"]),
            type=item.get("type", "post"),
            slug=item.get("slug", ""),
            status=item.get("status", "publish"),
            date=item.get("date", ""),
            link=item.get("link", ""),
            title=html.unescape(_rendered(item.get("title"))),
            content_html=_rendered(content),
            content_raw=content.get("raw", "") if isinstance(content, dict) else "",
            excerpt_html=_rendered(item.get("excerpt")),
            featured_media=int(item.get("featured_media") or 0),
            categories=list(item.get("categories") or []),
            tags=list(item.get("tags") or []),
            parent=int(item.get("parent") or 0),
        )

    @property
    def date_label(self) -> str:
        """'2026-10-05T09:47:15' -> '5 Oktober 2026' (sama dengan build_posts.py)."""
        try:
            y, m, d = (int(x) for x in self.date[:10].split("-"))
            return f"{d} {BULAN[m - 1]} {y}"
        except (ValueError, IndexError):
            return self.date[:10]

    @property
    def path(self) -> str:
        """Bagian path dari permalink, mis. '/eltahfidh-wisuda-38-daiyah/'. Dipakai untuk pengalihan."""
        match = re.match(r"https?://[^/]+(/.*)$", self.link)
        return match.group(1) if match else f"/{self.slug}/"

    def excerpt(self, limit: int = 150) -> str:
        text = re.sub(r"\s*\[(?:&hellip;|…|\.\.\.)\]\s*$", "", plain_text(self.excerpt_html or self.content_html))
        if len(text) > limit:
            text = text[:limit].rsplit(" ", 1)[0] + "…"
        return text


@dataclass
class Term:
    """Kategori atau tag."""

    id: int
    taxonomy: str
    name: str
    slug: str
    count: int = 0
    parent: int = 0

    @classmethod
    def from_api(cls, item: dict) -> "Term":
        return cls(
            id=int(item["id"]),
            taxonomy=item.get("taxonomy", "category"),
            name=html.unescape(item.get("name", "")),
            slug=item.get("slug", ""),
            count=int(item.get("count") or 0),
            parent=int(item.get("parent") or 0),
        )


@dataclass
class Media:
    """Berkas di pustaka media. Hanya metadata; berkasnya diunduh terpisah."""

    id: int
    source_url: str
    mime_type: str
    filesize: int = 0
    alt_text: str = ""
    title: str = ""
    post: int = 0

    @classmethod
    def from_api(cls, item: dict) -> "Media":
        details = item.get("media_details") or {}
        return cls(
            id=int(item["id"]),
            source_url=item.get("source_url", ""),
            mime_type=item.get("mime_type", ""),
            filesize=int(details.get("filesize") or 0),
            alt_text=item.get("alt_text", ""),
            title=html.unescape(_rendered(item.get("title"))),
            post=int(item.get("post") or 0),
        )

    @property
    def upload_path(self) -> str:
        """Path relatif di bawah wp-content/uploads/, mis. '2026/10/foto.jpg'."""
        marker = "/wp-content/uploads/"
        if marker in self.source_url:
            return self.source_url.split(marker, 1)[1].split("?", 1)[0]
        return self.source_url.rsplit("/", 1)[-1].split("?", 1)[0]
