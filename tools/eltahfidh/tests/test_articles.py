import json
import tempfile
import unittest
from pathlib import Path

from tools.eltahfidh.config import MAIN_SITE, SUBSITES
from tools.eltahfidh.repositories import JsonRepository
from tools.eltahfidh.services import ArticleBuilder, ArticleIndex
from tools.eltahfidh.services.content_cleaner import clean_content
from tools.eltahfidh.views.layout import prefix_relative

BASE = """<html><head><title>K</title><meta name="description" content="x">
<link rel="stylesheet" href="assets/css/style.css"></head><body>
<a href="index.html">Beranda</a><a href="berita.html">Berita</a><a href="https://wa.link/x">WA</a>
<main id="konten">lama</main><footer><img src="assets/img/logo.png"></footer></body></html>"""


def post(pid, slug, cats=(), date="2026-10-01T10:00:00", media=0):
    return {"id": pid, "slug": slug, "date": date, "link": f"https://x.id/{pid}/{slug}/", "categories": list(cats),
            "title": {"rendered": f"Judul {pid}"}, "excerpt": {"rendered": "Ringkas"}, "featured_media": media,
            "content": {"rendered": '<p style="color:red">Isi</p><script>alert(1)</script><p> </p>[gallery id="3"]'}}


class CleanerTest(unittest.TestCase):
    def test_strips_scripts_styles_shortcodes_and_empty_paragraphs(self):
        self.assertEqual(clean_content(post(1, "a")["content"]["rendered"]), "<p>Isi</p>")

    def test_keeps_normal_brackets_text(self):
        self.assertIn("[1]", clean_content("<p>Catatan [1] dan [Ar-Rum: 21]</p>"))


class PrefixTest(unittest.TestCase):
    def test_only_relative_urls_are_prefixed(self):
        out = prefix_relative('<a href="index.html"></a><a href="https://a.id"></a><a href="#x"></a>'
                              '<img src="assets/a.png"><a href="mailto:a@b.c"></a>', "../")
        self.assertIn('href="../index.html"', out)
        self.assertIn('src="../assets/a.png"', out)
        self.assertIn('href="https://a.id"', out)
        self.assertIn('href="#x"', out)
        self.assertIn('href="mailto:a@b.c"', out)


class ArticleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.site, self.data = root / "site", root / "data"
        self.site.mkdir(); self.data.mkdir()
        (self.site / "kontak.html").write_text(BASE, encoding="utf-8")
        self.store = JsonRepository(root / "db")
        self.store.write(MAIN_SITE, "posts", [post(1, "wisuda", [25], media=7), post(2, "kajian", [59]),
                                              post(3, "alat-qr", [99]), post(4, "hello-world", [25])])
        self.store.write(MAIN_SITE, "media", [{"id": 7, "source_url": "https://x.id/w.jpg", "media_details": {
            "sizes": {"large": {"source_url": "https://x.id/w-1024x552.jpg"}}}}])
        self.store.write(SUBSITES[0], "posts", [post(10, "wisuda"), post(11, "osis")])

    def tearDown(self):
        self.tmp.cleanup()

    def test_index_filters_categories_and_resolves_slug_collisions(self):
        entries = ArticleIndex(self.store).entries()
        self.assertEqual([e.file for e in entries],
                         ["wisuda.html", "kajian.html", "wisuda-smp-quran-putra.html", "osis.html"])
        self.assertEqual([e.back_page for e in entries], ["berita.html", "artikel.html", "smp-quran.html", "smp-quran.html"])

    def test_interactive_tool_posts_are_skipped(self):
        tool = post(20, "pp-hari-santri", [25])
        tool["content"]["rendered"] = '<canvas id="c"></canvas><input type="file">'
        self.store.write(MAIN_SITE, "posts", [post(1, "wisuda", [25]), tool])
        self.assertEqual([e.post.slug for e in ArticleIndex(self.store).entries()], ["wisuda", "wisuda", "osis"])

    def test_featured_image_already_in_content_is_not_repeated(self):
        dup = post(1, "wisuda", [25], media=7)
        dup["content"]["rendered"] = '<figure><img src="https://x.id/w.jpg"></figure><p>Isi</p>'
        self.store.write(MAIN_SITE, "posts", [dup])
        ArticleBuilder(self.store, self.site, self.data).build_all()
        html = (self.site / "berita" / "wisuda.html").read_text(encoding="utf-8")
        self.assertNotIn("w-1024x552.jpg", html)
        self.assertEqual(html.count("<img"), 2)  # logo footer + gambar di isi

    def test_builder_writes_pages_with_prefixed_links_and_map(self):
        out = self.site / "berita"
        out.mkdir()
        (out / "usang.html").write_text("x", encoding="utf-8")
        self.assertEqual(ArticleBuilder(self.store, self.site, self.data).build_all(), 4)
        html = (out / "wisuda.html").read_text(encoding="utf-8")
        self.assertIn('href="../assets/css/style.css"', html)
        self.assertIn('src="../assets/img/logo.png"', html)
        self.assertIn('href="https://wa.link/x"', html)
        self.assertIn('<a href="../berita.html" aria-current="page">', html)
        self.assertIn('src="https://x.id/w-1024x552.jpg"', html)
        self.assertNotIn("<script", html)
        self.assertFalse((out / "usang.html").exists())
        links = json.loads((self.data / "peta-tautan.json").read_text(encoding="utf-8"))
        self.assertEqual(links["https://x.id/1/wisuda/"], "/berita/wisuda.html")


if __name__ == "__main__":
    unittest.main()
