import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.eltahfidh.config import MAIN_SITE, SUBSITES
from tools.eltahfidh.repositories import JsonRepository
from tools.eltahfidh.services import WxrExporter
from tools.eltahfidh.services.wxr_exporter import cdata

WP = "{http://wordpress.org/export/1.2/}"


def post(pid, status="publish", **extra):
    return {"id": pid, "type": "post", "slug": f"p{pid}", "status": status, "link": f"https://x.id/?p={pid}&a=1",
            "date": "2026-10-05T09:47:15", "date_gmt": "2026-10-05T02:47:15", "categories": [25], "tags": [3],
            "title": {"raw": "Judul ]]> & <b>", "rendered": "x"}, "featured_media": 7,
            "content": {"raw": "Isi\x0bkontrol", "rendered": "<p>x</p>"}, "excerpt": {"raw": ""}, **extra}


class WxrTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JsonRepository(Path(self.tmp.name))
        for site in (MAIN_SITE, SUBSITES[0]):
            self.store.write(site, "posts", [post(1)])
            self.store.write(site, "categories", [{"id": 25, "slug": "berita", "name": "Berita", "parent": 0}])
            self.store.write(site, "tags", [{"id": 3, "slug": "santri", "name": "Santri"}])
            self.store.write(site, "media", [{"id": 7, "source_url": "https://x.id/a.jpg", "post": 1,
                                              "title": {"rendered": "a"}, "date": "2026-10-05T09:00:00"}])
            self.store.write(site, "site", {"name": "elTAHFIDH"})
        self.store.write(MAIN_SITE, "drafts-posts", [post(2, "draft")], private=True)

    def tearDown(self):
        self.tmp.cleanup()

    def parse(self, key):
        return ET.parse(Path(self.tmp.name) / "wxr" / f"{key}.xml").getroot()

    def test_files_are_valid_xml_with_drafts_only_for_main(self):
        self.assertEqual(WxrExporter(self.store).export_all(), [("utama", 2), ("smp-quran-putra", 1)])
        main = self.parse("utama")
        statuses = sorted(i.findtext(f"{WP}status") for i in main.iter("item"))
        self.assertEqual(statuses, ["draft", "inherit", "publish"])
        title = next(i for i in main.iter("item") if i.findtext(f"{WP}post_type") == "post").findtext("title")
        self.assertEqual(title, "Judul ]]> & <b>")

    def test_subsite_ids_are_offset_and_get_jenjang_category(self):
        WxrExporter(self.store).export_all()
        sub = self.parse("smp-quran-putra")
        item = next(i for i in sub.iter("item") if i.findtext(f"{WP}post_type") == "post")
        self.assertEqual(item.findtext(f"{WP}post_id"), "1000001")
        cats = [c.get("nicename") for c in item.findall("category")]
        self.assertIn("smp-quran-putra", cats)
        thumb = item.find(f"{WP}postmeta").findtext(f"{WP}meta_value")
        self.assertEqual(thumb, "1000007")
        attachment = next(i for i in sub.iter("item") if i.findtext(f"{WP}post_type") == "attachment")
        self.assertEqual(attachment.findtext(f"{WP}attachment_url"), "https://x.id/a.jpg")

    def test_default_and_empty_subsite_pages_are_skipped(self):
        empty_page = post(5, type="page", content={"rendered": "<div class='elementor'></div>"})
        self.store.write(SUBSITES[0], "pages", [empty_page, post(6, type="page", slug="sample-page")])
        self.store.write(SUBSITES[0], "posts", [post(1), post(4, slug="hello-world")])
        self.assertEqual(WxrExporter(self.store).export(SUBSITES[0], 0), 1)

    def test_cdata_strips_control_characters(self):
        self.assertEqual(cdata("a\x0bb"), "<![CDATA[ab]]>")


if __name__ == "__main__":
    unittest.main()
