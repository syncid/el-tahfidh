"""Membuat berkas impor WordPress (WXR 1.2) dari db/, satu berkas per situs, ke db/wxr/<key>.xml.

Berkas ditaruh di db/ (lokal, tidak di-commit) karena situs induk juga memuat draf.
Impor di WordPress tujuan: Tools > Import > WordPress, centang "Download and import file attachments"
selama situs sumber masih hidup, lalu petakan penulis ke akun yang ada.

ID postingan, istilah, dan lampiran situs subdomain digeser (offset) agar tidak bentrok saat beberapa
berkas diimpor ke satu WordPress. Postingan subdomain mendapat kategori tambahan bernama situsnya
(mis. "SMP Qur'an Putra") supaya tetap terkelompok setelah digabung ke situs induk.
"""
import re
from datetime import datetime
from email.utils import format_datetime
from xml.sax.saxutils import escape, quoteattr

from .. import config
from ..models import Site
from ..models.content import plain_text
from ..repositories import JsonRepository

ID_STEP = 1_000_000
# Isi bawaan WordPress yang tidak perlu ikut diimpor.
SKIP_SLUGS = {"hello-world", "sample-page"}
AUTHOR_LOGIN = "eltahfidh-impor"
NS = ('xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/" '
      'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
      'xmlns:wfw="http://wellformedweb.org/CommentAPI/" '
      'xmlns:dc="http://purl.org/dc/elements/1.1/" '
      'xmlns:wp="http://wordpress.org/export/1.2/"')


_INVALID_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")


def cdata(value) -> str:
    text = _INVALID_XML.sub("", "" if value is None else str(value))
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def _text(field) -> str:
    if isinstance(field, dict):
        return field.get("raw") if field.get("raw") is not None else field.get("rendered", "")
    return field or ""


def _wp_date(iso: str | None) -> str:
    return (iso or "").replace("T", " ")[:19] or "0000-00-00 00:00:00"


def _pub_date(iso_gmt: str | None) -> str:
    try:
        return format_datetime(datetime.fromisoformat((iso_gmt or "")[:19]).replace(tzinfo=None), usegmt=False)
    except ValueError:
        return ""


class WxrExporter:
    def __init__(self, store: JsonRepository):
        self._store = store

    def export_all(self) -> list[tuple[str, int]]:
        out = []
        for index, site in enumerate(config.ALL_SITES):
            if self._store.exists(site, "posts"):
                out.append((site.key, self.export(site, index * ID_STEP)))
        return out

    def export(self, site: Site, offset: int) -> int:
        items = self._store.read(site, "posts", default=[]) + self._store.read(site, "pages", default=[])
        if site.is_main:
            items += self._store.read(site, "drafts-posts", private=True, default=[])
            items += self._store.read(site, "drafts-pages", private=True, default=[])
        items = [i for i in items if i.get("slug") not in SKIP_SLUGS and not self._empty_subsite_page(site, i)]
        media = self._store.read(site, "media", default=[])
        categories = self._store.read(site, "categories", default=[])
        tags = self._store.read(site, "tags", default=[])
        info = self._store.read(site, "site", default={})

        cat_by_id = {c["id"]: c for c in categories}
        tag_by_id = {t["id"]: t for t in tags}
        extra_cat = None if site.is_main else {"slug": site.key, "name": site.label}

        parts = [f'<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0" {NS}>\n<channel>',
                 f"\t<title>{cdata(info.get('name') or site.label)}</title>",
                 f"\t<link>https://{site.host}</link>",
                 f"\t<description>{cdata(info.get('description', ''))}</description>",
                 "\t<language>id</language>",
                 "\t<wp:wxr_version>1.2</wp:wxr_version>",
                 f"\t<wp:base_site_url>https://{site.host}</wp:base_site_url>",
                 f"\t<wp:base_blog_url>https://{site.host}</wp:base_blog_url>",
                 f"\t<wp:author><wp:author_id>1</wp:author_id><wp:author_login>{cdata(AUTHOR_LOGIN)}</wp:author_login>"
                 f"<wp:author_email>{cdata('')}</wp:author_email><wp:author_display_name>{cdata('elTAHFIDH')}"
                 f"</wp:author_display_name></wp:author>"]
        for c in categories:
            parent = cat_by_id.get(c.get("parent"))
            parts.append(f"\t<wp:category><wp:term_id>{c['id'] + offset}</wp:term_id>"
                         f"<wp:category_nicename>{cdata(c['slug'])}</wp:category_nicename>"
                         f"<wp:category_parent>{cdata(parent['slug'] if parent else '')}</wp:category_parent>"
                         f"<wp:cat_name>{cdata(c['name'])}</wp:cat_name></wp:category>")
        if extra_cat:
            parts.append(f"\t<wp:category><wp:term_id>{offset + 999_999}</wp:term_id>"
                         f"<wp:category_nicename>{cdata(extra_cat['slug'])}</wp:category_nicename>"
                         f"<wp:category_parent>{cdata('')}</wp:category_parent>"
                         f"<wp:cat_name>{cdata(extra_cat['name'])}</wp:cat_name></wp:category>")
        for t in tags:
            parts.append(f"\t<wp:tag><wp:term_id>{t['id'] + offset}</wp:term_id><wp:tag_slug>{cdata(t['slug'])}"
                         f"</wp:tag_slug><wp:tag_name>{cdata(t['name'])}</wp:tag_name></wp:tag>")

        for m in media:
            parts.append(self._attachment(m, offset))
        for item in items:
            parts.append(self._item(item, offset, cat_by_id, tag_by_id, extra_cat))

        parts.append("</channel>\n</rss>\n")
        path = self._store.root / "wxr" / f"{site.key}.xml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(parts), encoding="utf-8")
        return len(items)

    @staticmethod
    def _empty_subsite_page(site: Site, item: dict) -> bool:
        """Halaman subdomain yang isinya hanya tata letak Elementor (kosong lewat REST API) tidak diimpor."""
        if site.is_main or item.get("type") != "page":
            return False
        return len(plain_text(_text(item.get("content")))) < 20

    def _item(self, item: dict, offset: int, cat_by_id: dict, tag_by_id: dict, extra_cat: dict | None) -> str:
        post_type = item.get("type", "post")
        lines = [
            "\t<item>",
            f"\t\t<title>{cdata(_text(item.get('title')))}</title>",
            f"\t\t<link>{escape(item.get('link', ''))}</link>",
            f"\t\t<pubDate>{_pub_date(item.get('date_gmt'))}</pubDate>",
            f"\t\t<dc:creator>{cdata(AUTHOR_LOGIN)}</dc:creator>",
            f'\t\t<guid isPermaLink="false">{escape(_text(item.get("guid")))}</guid>',
            "\t\t<description></description>",
            f"\t\t<content:encoded>{cdata(_text(item.get('content')))}</content:encoded>",
            f"\t\t<excerpt:encoded>{cdata(_text(item.get('excerpt')) if item.get('excerpt', {}).get('raw') is not None else '')}</excerpt:encoded>",
            f"\t\t<wp:post_id>{item['id'] + offset}</wp:post_id>",
            f"\t\t<wp:post_date>{cdata(_wp_date(item.get('date')))}</wp:post_date>",
            f"\t\t<wp:post_date_gmt>{cdata(_wp_date(item.get('date_gmt')))}</wp:post_date_gmt>",
            f"\t\t<wp:post_modified>{cdata(_wp_date(item.get('modified')))}</wp:post_modified>",
            f"\t\t<wp:post_modified_gmt>{cdata(_wp_date(item.get('modified_gmt')))}</wp:post_modified_gmt>",
            f"\t\t<wp:comment_status>{cdata(item.get('comment_status', 'closed'))}</wp:comment_status>",
            f"\t\t<wp:ping_status>{cdata(item.get('ping_status', 'closed'))}</wp:ping_status>",
            f"\t\t<wp:post_name>{cdata(item.get('slug', ''))}</wp:post_name>",
            f"\t\t<wp:status>{cdata(item.get('status', 'publish'))}</wp:status>",
            f"\t\t<wp:post_parent>{(item.get('parent') or 0) and item['parent'] + offset}</wp:post_parent>",
            f"\t\t<wp:menu_order>{item.get('menu_order', 0)}</wp:menu_order>",
            f"\t\t<wp:post_type>{cdata(post_type)}</wp:post_type>",
            f"\t\t<wp:post_password>{cdata('')}</wp:post_password>",
            f"\t\t<wp:is_sticky>{1 if item.get('sticky') else 0}</wp:is_sticky>",
        ]
        for cid in item.get("categories") or []:
            if cid in cat_by_id:
                c = cat_by_id[cid]
                lines.append(f'\t\t<category domain="category" nicename={quoteattr(c["slug"])}>{cdata(c["name"])}</category>')
        if extra_cat and post_type == "post":
            lines.append(f'\t\t<category domain="category" nicename={quoteattr(extra_cat["slug"])}>{cdata(extra_cat["name"])}</category>')
        for tid in item.get("tags") or []:
            if tid in tag_by_id:
                t = tag_by_id[tid]
                lines.append(f'\t\t<category domain="post_tag" nicename={quoteattr(t["slug"])}>{cdata(t["name"])}</category>')
        if item.get("featured_media"):
            lines.append(f"\t\t<wp:postmeta><wp:meta_key>{cdata('_thumbnail_id')}</wp:meta_key>"
                         f"<wp:meta_value>{cdata(item['featured_media'] + offset)}</wp:meta_value></wp:postmeta>")
        lines.append("\t</item>")
        return "\n".join(lines)

    def _attachment(self, m: dict, offset: int) -> str:
        parent = m.get("post") or 0
        return "\n".join([
            "\t<item>",
            f"\t\t<title>{cdata(_text(m.get('title')))}</title>",
            f"\t\t<link>{escape(m.get('link', ''))}</link>",
            f"\t\t<pubDate>{_pub_date(m.get('date_gmt'))}</pubDate>",
            f"\t\t<dc:creator>{cdata(AUTHOR_LOGIN)}</dc:creator>",
            f'\t\t<guid isPermaLink="false">{escape(m.get("source_url", ""))}</guid>',
            "\t\t<description></description>",
            f"\t\t<content:encoded>{cdata(_text(m.get('description')))}</content:encoded>",
            f"\t\t<excerpt:encoded>{cdata(_text(m.get('caption')))}</excerpt:encoded>",
            f"\t\t<wp:post_id>{m['id'] + offset}</wp:post_id>",
            f"\t\t<wp:post_date>{cdata(_wp_date(m.get('date')))}</wp:post_date>",
            f"\t\t<wp:post_date_gmt>{cdata(_wp_date(m.get('date_gmt')))}</wp:post_date_gmt>",
            f"\t\t<wp:post_name>{cdata(m.get('slug', ''))}</wp:post_name>",
            f"\t\t<wp:status>{cdata('inherit')}</wp:status>",
            f"\t\t<wp:post_parent>{parent and parent + offset}</wp:post_parent>",
            f"\t\t<wp:post_type>{cdata('attachment')}</wp:post_type>",
            f"\t\t<wp:attachment_url>{cdata(m.get('source_url', ''))}</wp:attachment_url>",
            f"\t\t<wp:postmeta><wp:meta_key>{cdata('_wp_attachment_image_alt')}</wp:meta_key>"
            f"<wp:meta_value>{cdata(m.get('alt_text', ''))}</wp:meta_value></wp:postmeta>",
            "\t</item>",
        ])
