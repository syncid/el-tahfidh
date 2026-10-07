import json
import tempfile
import unittest
from pathlib import Path

from tools.eltahfidh.config import SUBSITES
from tools.eltahfidh.repositories import DataRepository, JsonRepository
from tools.eltahfidh.services import JenjangBuilder
from tools.eltahfidh.tests.fakes import FakeClient
from tools.eltahfidh.views import Layout, components

BASE = """<html><head><title>Kontak</title><meta name="description" content="x"></head><body>
<nav><a href="index.html" aria-current="page">Beranda</a><a href="smp-quran.html">SMP Qur'an</a></nav>
<main id="konten">lama</main><footer>kaki</footer></body></html>"""

PAGE = {
    "file": "smp-quran.html", "label": "SMP Qur'an", "judul": "SMP Qur'an elTAHFIDH",
    "deskripsi": "Desk <b>", "lead": "Lead & teks",
    "kampus": [{"nama": "Ikhwan", "teks": "t"}, {"nama": "Full Day", "teks": "t", "tautan": "ifs.html"}],
    "pilar": [{"judul": "Al-Qur'an", "butir": ["Tahfidh"]}],
    "fakta": [{"angka": "20 Juz", "teks": "Target"}],
    "pimpinan": ["SMPQ elTAHFIDH", "Pesantren Qur'an Akhwat"],
    "sumber_berita": ["smp-quran-putra", "smp-quran-putri"],
}
STRUKTUR = {"lembaga_mandiri": [
    {"nama": "SMPQ elTAHFIDH", "jabatan": "Direktur", "pimpinan": "Fathurrahman Aziz, S.Pd.I., Al-Hafidh",
     "unit": [{"nama": "Al-Qur'an", "pj": "Ganjar Muharom, S.Pd.I., Al-Hafidh"}]},
    {"nama": "Pesantren Qur'an Akhwat", "jabatan": "Direktur", "pimpinan": "Hj. Zuriati, S.Pd., M.Ag.",
     "unit": [{"nama": "SMP Qur'an", "pj": None, "sub": ["Al-Qur'an"]}]},
]}


def post(pid, date, media=0):
    return {"id": pid, "date": date, "link": f"https://x.id/{pid}/", "title": {"rendered": f"Berita {pid}"},
            "excerpt": {"rendered": "Ringkas"}, "content": {"rendered": ""}, "featured_media": media}


class LayoutTest(unittest.TestCase):
    def test_render_sets_title_description_and_current_link(self):
        out = Layout(BASE).render("smp-quran.html", "Judul <1>", 'Desk "2"', "<main>baru</main>")
        self.assertIn("<title>Judul &lt;1&gt;</title>", out)
        self.assertIn('content="Desk &quot;2&quot;"', out)
        self.assertIn('<a href="smp-quran.html" aria-current="page">', out)
        self.assertNotIn('index.html" aria-current', out)
        self.assertIn("<main>baru</main><footer>kaki</footer>", out)

    def test_base_without_main_is_rejected(self):
        with self.assertRaises(ValueError):
            Layout("<html></html>")


class ComponentTest(unittest.TestCase):
    def test_org_card_with_photo_salutation_and_units(self):
        html = components.org_card(STRUKTUR["lembaga_mandiri"][1], "assets/img/umi.png", "Umi", "")
        self.assertIn('alt="Umi Hj. Zuriati, S.Pd., M.Ag."', html)
        self.assertIn("<small>Al-Qur&#x27;an</small>", html)
        self.assertNotIn("PJ:", html)

    def test_org_card_without_photo_uses_placeholder(self):
        html = components.org_card(STRUKTUR["lembaga_mandiri"][0], None, None, "")
        self.assertIn('class="org__ph"', html)
        self.assertIn("PJ: Ganjar Muharom", html)


class JenjangBuilderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.site, data = root / "site", root / "data"
        self.site.mkdir(); data.mkdir()
        (self.site / "kontak.html").write_text(BASE, encoding="utf-8")
        (data / "jenjang.json").write_text(json.dumps({"foto_pimpinan": {"Hj. Zuriati": "assets/img/umi.png"},
                                                      "sapaan": {"Hj. Zuriati": "Umi"}, "halaman": [PAGE]}), encoding="utf-8")
        (data / "struktur-organisasi.json").write_text(json.dumps(STRUKTUR), encoding="utf-8")
        self.store = JsonRepository(root / "db")
        putra, putri = SUBSITES[0], SUBSITES[1]
        self.store.write(putra, "posts", [post(1, "2025-10-03T10:00:00", media=9), post(2, "2025-08-01T10:00:00")])
        self.store.write(putra, "media", [{"id": 9, "source_url": "https://x.id/a.jpg",
                                           "media_details": {"sizes": {"medium": {"source_url": "https://x.id/a-300.jpg"}}}}])
        self.store.write(putri, "posts", [post(3, "2025-11-13T10:00:00")])
        self.client = FakeClient({})
        self.builder = JenjangBuilder(self.store, DataRepository(data), self.client, self.site, posts_per_page=2)

    def tearDown(self):
        self.tmp.cleanup()

    def test_builds_page_with_latest_posts_from_all_sources(self):
        self.assertEqual(self.builder.build_all(), [("smp-quran.html", 2)])
        html = (self.site / "smp-quran.html").read_text(encoding="utf-8")
        self.assertLess(html.index("Berita 3"), html.index("Berita 1"))
        self.assertNotIn("Berita 2", html)
        self.assertIn("Lead &amp; teks", html)
        self.assertIn('content="Desk &lt;b&gt;"', html)
        self.assertIn("Fathurrahman Aziz", html)
        self.assertIn('href="ifs.html"', html)
        self.assertIn('<a href="smp-quran.html" aria-current="page">', html)

    def test_thumbnail_downloaded_once_with_preferred_size(self):
        self.builder.build_all()
        self.builder.build_all()
        self.assertEqual(self.client.downloads, ["https://x.id/a-300.jpg"])
        self.assertTrue((self.site / "assets/img/posts/smp-quran-putra-1.jpg").exists())


if __name__ == "__main__":
    unittest.main()
