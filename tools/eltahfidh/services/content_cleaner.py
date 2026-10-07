"""Membersihkan HTML isi postingan WordPress sebelum ditampilkan di situs statis."""
import re

_BLOCKS = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.S | re.I)
_STYLE_ATTR = re.compile(r'\sstyle="[^"]*"', re.I)
_EVENT_ATTR = re.compile(r'\son[a-z]+="[^"]*"', re.I)
_SHORTCODE = re.compile(r"\[/?[a-z][a-z0-9_\-]*(?:\s[^\]\n]*)?\]")
_EMPTY_P = re.compile(r"<p[^>]*>(?:\s|&nbsp;)*</p>", re.I)


_URL_ATTR = re.compile(r'\s(href|src)="([^"]*)"', re.I)


def link_key(url: str) -> str:
    """Kunci pembanding alamat WordPress: tanpa skema, 'www.', kueri, jangkar, dan garis miring akhir."""
    url = re.sub(r"^https?://(www\.)?", "", url.strip(), flags=re.I)
    return re.split(r"[?#]", url, maxsplit=1)[0].rstrip("/").lower()


def rewrite_links(markup: str, host: str, pages: dict[str, str]) -> str:
    """Sesuaikan alamat di isi postingan untuk situs statis.

    - Alamat absolut-akar ('/pesantren-modern') menjadi alamat lengkap di situs WordPress asal (`host`),
      karena di GitHub Pages '/' menunjuk ke luar situs.
    - Tautan ke postingan yang punya halaman statis diganti nama berkasnya di site/berita/ (`pages`:
      link_key(alamat lama) -> nama berkas), jangkar '#...' dipertahankan.
    """
    def replace(match: re.Match) -> str:
        attr, url = match.group(1), match.group(2)
        if url.startswith("/") and not url.startswith("//"):
            url = f"https://{host}{url}"
        if attr.lower() == "href":
            page = pages.get(link_key(url))
            if page:
                fragment = url.partition("#")[2]
                url = f"{page}#{fragment}" if fragment else page
        return f' {attr}="{url}"'
    return _URL_ATTR.sub(replace, markup)


def clean_content(markup: str) -> str:
    """Buang skrip, gaya sebaris, atribut event, sisa shortcode, dan paragraf kosong."""
    markup = _BLOCKS.sub("", markup)
    markup = _STYLE_ATTR.sub("", markup)
    markup = _EVENT_ATTR.sub("", markup)
    markup = _SHORTCODE.sub("", markup)
    markup = _EMPTY_P.sub("", markup)
    return re.sub(r"\n{3,}", "\n\n", markup).strip()
