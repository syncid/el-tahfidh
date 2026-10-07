"""Membersihkan HTML isi postingan WordPress sebelum ditampilkan di situs statis."""
import re

_BLOCKS = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.S | re.I)
_STYLE_ATTR = re.compile(r'\sstyle="[^"]*"', re.I)
_EVENT_ATTR = re.compile(r'\son[a-z]+="[^"]*"', re.I)
_SHORTCODE = re.compile(r"\[/?[a-z][a-z0-9_\-]*(?:\s[^\]\n]*)?\]")
_EMPTY_P = re.compile(r"<p[^>]*>(?:\s|&nbsp;)*</p>", re.I)


def clean_content(markup: str) -> str:
    """Buang skrip, gaya sebaris, atribut event, sisa shortcode, dan paragraf kosong."""
    markup = _BLOCKS.sub("", markup)
    markup = _STYLE_ATTR.sub("", markup)
    markup = _EVENT_ATTR.sub("", markup)
    markup = _SHORTCODE.sub("", markup)
    markup = _EMPTY_P.sub("", markup)
    return re.sub(r"\n{3,}", "\n\n", markup).strip()
