"""Kerangka halaman: header dan footer diambil dari site/kontak.html (cara yang sama dengan build_posts.py)."""
import html
import re

# href/src relatif: bukan skema (https:, mailto:, data:), bukan jangkar, bukan path absolut atau ../
_RELATIVE = re.compile(r'\b(href|src)="(?![a-zA-Z][a-zA-Z0-9+.\-]*:|#|/|\.\./)')


def prefix_relative(markup: str, prefix: str) -> str:
    """Awali semua href/src relatif, mis. 'assets/...' menjadi '../assets/...' untuk halaman di subfolder."""
    return _RELATIVE.sub(lambda m: f'{m.group(1)}="{prefix}', markup) if prefix else markup


class Layout:
    def __init__(self, base_html: str):
        if '<main id="konten">' not in base_html or "</main>" not in base_html:
            raise ValueError('Kerangka tidak memuat <main id="konten"> ... </main>')
        head, rest = base_html.split('<main id="konten">', 1)
        self._head = head
        self._foot = rest.split("</main>", 1)[1]

    def render(self, file: str, title: str, description: str, main: str, depth: int = 0) -> str:
        """file: halaman yang ditandai aktif di menu. depth: kedalaman folder (0 = akar site/)."""
        head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", self._head, flags=re.S)
        head = re.sub(r'<meta name="description" content="[^"]*">',
                      f'<meta name="description" content="{html.escape(description)}">', head)
        head = head.replace(' aria-current="page"', "")
        head = head.replace(f'<a href="{file}">', f'<a href="{file}" aria-current="page">')
        prefix = "../" * depth
        return prefix_relative(head, prefix) + main + prefix_relative(self._foot, prefix)
