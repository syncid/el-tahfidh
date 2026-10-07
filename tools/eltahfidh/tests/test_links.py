import tempfile
import unittest
from pathlib import Path

from tools.eltahfidh.services import LinkChecker


class LinkCheckerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "assets").mkdir()
        (self.root / "berita").mkdir()
        (self.root / "assets" / "logo.png").write_bytes(b"x")
        (self.root / "assets" / "style.css").write_text("a{background:url('logo.png')} b{background:url(hilang.png)}")
        (self.root / "profil.html").write_text('<section id="visi-misi"></section><a name="lama"></a>')
        (self.root / "index.html").write_text(
            '<a href="profil.html#visi-misi">ok</a><a href="profil.html#lama">ok</a>'
            '<a href="#atas">jangkar hilang</a><a href="https://a.id/x.html">luar</a><a href="mailto:a@b.c">m</a>'
            '<img src="assets/logo.png" srcset="assets/logo.png 1x, assets/logo@2x.png 2x">'
            '<a href="psb.html">hilang</a><a href="/program">absolut</a><a href="profil.html#tidak-ada">x</a>'
            '<a href="berita/">folder tanpa index</a>')
        (self.root / "berita" / "a.html").write_text('<a href="../index.html">ok</a><a href="../../luar.html">x</a>')

    def tearDown(self):
        self.tmp.cleanup()

    def test_reports_each_broken_link_with_reason(self):
        checked, broken = LinkChecker(self.root).check()
        found = {(b.source, b.target): b.reason for b in broken}
        self.assertEqual(found, {
            ("assets/style.css", "hilang.png"): "berkas tidak ada",
            ("index.html", "#atas"): "jangkar tidak ada",
            ("index.html", "assets/logo@2x.png"): "berkas tidak ada",
            ("index.html", "psb.html"): "berkas tidak ada",
            ("index.html", "/program"): "alamat absolut (rusak di GitHub Pages)",
            ("index.html", "profil.html#tidak-ada"): "jangkar tidak ada",
            ("index.html", "berita/"): "berkas tidak ada",
            ("berita/a.html", "../../luar.html"): "di luar folder site/",
        })
        self.assertEqual(checked, 14)

    def test_clean_site_has_no_broken_links(self):
        (self.root / "index.html").write_text('<a href="profil.html#visi-misi">ok</a><a href="https://a.id">x</a>')
        (self.root / "assets" / "style.css").write_text("a{background:url(logo.png)}")
        (self.root / "berita" / "a.html").write_text('<a href="../index.html">ok</a>')
        self.assertEqual(LinkChecker(self.root).check(), (3, []))


if __name__ == "__main__":
    unittest.main()
