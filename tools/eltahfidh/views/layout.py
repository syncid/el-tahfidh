"""Kerangka halaman: header dan footer diambil dari site/kontak.html (cara yang sama dengan build_posts.py)."""
import html
import re


class Layout:
    def __init__(self, base_html: str):
        if '<main id="konten">' not in base_html or "</main>" not in base_html:
            raise ValueError('Kerangka tidak memuat <main id="konten"> ... </main>')
        head, rest = base_html.split('<main id="konten">', 1)
        self._head = head
        self._foot = rest.split("</main>", 1)[1]

    def render(self, file: str, title: str, description: str, main: str) -> str:
        head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", self._head, flags=re.S)
        head = re.sub(r'<meta name="description" content="[^"]*">',
                      f'<meta name="description" content="{html.escape(description)}">', head)
        head = head.replace(' aria-current="page"', "")
        head = head.replace(f'<a href="{file}">', f'<a href="{file}" aria-current="page">')
        return head + main + self._foot
