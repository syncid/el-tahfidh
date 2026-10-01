"""Tarik berita & artikel terbaru dari eltahfidh.or.id lalu bangun ulang halamannya.

Jalankan ulang kapan saja untuk memperbarui:  python tools/build_posts.py

- site/berita.html dan site/artikel.html dibuat dari kerangka kontak.html
  (header/footer sama), isinya kartu postingan terbaru.
- Blok <!-- POSTS:home --> di site/index.html diisi 3 berita terbaru.
- Thumbnail diunduh sekali ke site/assets/img/posts/<id>.<ext>.
"""
import html
import json
import pathlib
import re
import urllib.request

SITE = pathlib.Path(__file__).resolve().parent.parent / "site"
POST_IMG = SITE / "assets" / "img" / "posts"
API = "https://eltahfidh.or.id/wp-json/wp/v2/posts"
UA = {"User-Agent": "Mozilla/5.0 (elTAHFIDH static site builder)"}
PER_PAGE = 12
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

PAGES = [
    {
        "file": "berita.html", "category": 25, "label": "Berita",
        "title": "Berita - elTAHFIDH Indonesia",
        "description": "Berita dan kegiatan terbaru santri dan lembaga elTAHFIDH Indonesia.",
        "heading": "Berita elTAHFIDH",
        "lead": "Kabar terbaru kegiatan santri, prestasi, dan program elTAHFIDH Indonesia.",
        "all_url": "https://eltahfidh.or.id/category/berita/",
    },
    {
        "file": "artikel.html", "category": 59, "label": "Artikel",
        "title": "Artikel - elTAHFIDH Indonesia",
        "description": "Artikel seputar tahfidz Al-Qur'an, pesantren, dan pendidikan anak dari elTAHFIDH Indonesia.",
        "heading": "Artikel",
        "lead": "Wawasan seputar tahfidz Al-Qur'an, pesantren, dan pendidikan anak.",
        "all_url": "https://eltahfidh.or.id/category/artikel/",
    },
]


def get_json(url: str):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def fetch_posts(category: int) -> list[dict]:
    url = f"{API}?categories={category}&per_page={PER_PAGE}&_embed=wp:featuredmedia"
    posts = []
    for p in get_json(url):
        media = (p.get("_embedded", {}).get("wp:featuredmedia") or [{}])[0]
        sizes = media.get("media_details", {}).get("sizes", {})
        img = next((sizes[k]["source_url"] for k in ("medium_large", "large", "medium") if k in sizes),
                   media.get("source_url"))
        y, m, d = (int(x) for x in p["date"][:10].split("-"))
        excerpt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p["excerpt"]["rendered"]))).strip()
        excerpt = re.sub(r"\s*\[(?:&hellip;|…|\.\.\.)\]\s*$", "", excerpt)
        if len(excerpt) > 150:
            excerpt = excerpt[:150].rsplit(" ", 1)[0] + "…"
        posts.append({
            "id": p["id"],
            "title": html.unescape(p["title"]["rendered"]),
            "link": p["link"],
            "date_iso": p["date"][:10],
            "date": f"{d} {BULAN[m - 1]} {y}",
            "excerpt": excerpt,
            "img": download(p["id"], img) if img else None,
        })
    return posts


def download(post_id: int, url: str) -> str:
    ext = pathlib.Path(url.split("?")[0]).suffix.lower() or ".jpg"
    target = POST_IMG / f"{post_id}{ext}"
    if not target.exists():
        POST_IMG.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            target.write_bytes(r.read())
    return f"assets/img/posts/{target.name}"


def card(p: dict, indent: str) -> str:
    e = html.escape
    media = (f'<img src="{p["img"]}" alt="" loading="lazy">' if p["img"]
             else '<div class="post__noimg"><img src="assets/img/logo.png" alt="" loading="lazy"></div>')
    return (
        f'{indent}<article class="card post">\n'
        f'{indent}  <div class="post__media">{media}</div>\n'
        f'{indent}  <div class="post__body">\n'
        f'{indent}    <time datetime="{p["date_iso"]}">{p["date"]}</time>\n'
        f'{indent}    <h3><a href="{e(p["link"])}" target="_blank" rel="noopener">{e(p["title"])}</a></h3>\n'
        f'{indent}    <p>{e(p["excerpt"])}</p>\n'
        f'{indent}  </div>\n'
        f'{indent}</article>'
    )


def grid(posts: list[dict], indent: str) -> str:
    cards = "\n".join(card(p, indent + "  ") for p in posts)
    return f'{indent}<div class="posts">\n{cards}\n{indent}</div>'


def build_page(cfg: dict, posts: list[dict], base: str) -> str:
    head, rest = base.split('<main id="konten">', 1)
    _, foot = rest.split("</main>", 1)
    head = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{html.escape(cfg["description"])}">', head)
    head = head.replace(' aria-current="page"', "")
    head = head.replace(f'<a href="{cfg["file"]}">', f'<a href="{cfg["file"]}" aria-current="page">')
    main = f"""<main id="konten">
    <section class="page-hero">
      <div class="wrap">
        <ol class="crumbs" aria-label="Breadcrumb"><li><a href="index.html">Beranda</a></li><li>{cfg['label']}</li></ol>
        <h1>{cfg['heading']}</h1>
        <p>{cfg['lead']}</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
{grid(posts, '        ')}
        <p class="center more-all"><a class="btn btn--primary" href="{cfg['all_url']}" target="_blank" rel="noopener">Lihat Arsip {cfg['label']} Lengkap</a></p>
      </div>
    </section>
  </main>"""
    return head + main + foot


def main() -> None:
    base = (SITE / "kontak.html").read_text(encoding="utf-8")
    latest_berita: list[dict] = []
    for cfg in PAGES:
        posts = fetch_posts(cfg["category"])
        if cfg["category"] == 25:
            latest_berita = posts
        (SITE / cfg["file"]).write_text(build_page(cfg, posts, base), encoding="utf-8")
        print(f"{cfg['file']}: {len(posts)} postingan")

    index = SITE / "index.html"
    text = index.read_text(encoding="utf-8")
    block = f"        <!-- POSTS:home -->\n{grid(latest_berita[:3], '        ')}\n        <!-- /POSTS:home -->"
    text, n = re.subn(r"[ \t]*<!-- POSTS:home -->.*?<!-- /POSTS:home -->", lambda _: block, text, flags=re.S)
    if n != 1:
        raise SystemExit("Penanda <!-- POSTS:home --> tidak ditemukan di index.html")
    index.write_text(text, encoding="utf-8")
    print("index.html: 3 berita terbaru diperbarui")


if __name__ == "__main__":
    main()
