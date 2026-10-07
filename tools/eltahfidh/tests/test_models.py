import unittest

from tools.eltahfidh.models import Content, Media


class ContentTest(unittest.TestCase):
    def test_from_api_and_labels(self):
        c = Content.from_api({
            "id": 5938, "type": "post", "slug": "wisuda", "status": "publish",
            "date": "2026-10-05T09:47:15", "link": "https://eltahfidh.or.id/wisuda/",
            "title": {"rendered": "Wisuda &amp; Sanad"},
            "content": {"rendered": "<p>Isi</p>", "raw": "Isi"},
            "excerpt": {"rendered": "<p>Ringkas [&hellip;]</p>"},
            "categories": [25],
        })
        self.assertEqual(c.title, "Wisuda & Sanad")
        self.assertEqual(c.date_label, "5 Oktober 2026")
        self.assertEqual(c.path, "/wisuda/")
        self.assertEqual(c.content_raw, "Isi")
        self.assertEqual(c.excerpt(), "Ringkas")

    def test_excerpt_is_cut_on_word_boundary(self):
        c = Content.from_api({"id": 1, "excerpt": {"rendered": "kata " * 60}})
        self.assertTrue(c.excerpt(20).endswith("…"))
        self.assertLessEqual(len(c.excerpt(20)), 21)


class MediaTest(unittest.TestCase):
    def test_upload_path(self):
        m = Media.from_api({"id": 1, "source_url": "https://x.id/wp-content/uploads/2026/10/a.jpg",
                            "media_details": {"filesize": 70206}})
        self.assertEqual(m.upload_path, "2026/10/a.jpg")
        self.assertEqual(m.filesize, 70206)


if __name__ == "__main__":
    unittest.main()
