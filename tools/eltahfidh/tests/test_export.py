import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.eltahfidh.config import MAIN_SITE, SUBSITES
from tools.eltahfidh.repositories import JsonRepository, WpApiRepository
from tools.eltahfidh.services import ExportService, MediaBackupService
from tools.eltahfidh.tests.fakes import FakeClient

ROUTES = {
    "/": {"name": "elTAHFIDH", "description": "d", "url": "u", "home": "h", "namespaces": ["wp/v2"]},
    "/wp/v2/posts": [[{"id": 1, "_links": {}}, {"id": 2}], [{"id": 3}]],
    "/wp/v2/pages": [[{"id": 10}]],
    "/wp/v2/categories": [[{"id": 25, "name": "Berita"}]],
    "/wp/v2/tags": [[]],
    "/wp/v2/media": [[{"id": 7, "source_url": "https://x.id/wp-content/uploads/2026/10/a.jpg",
                       "media_details": {"filesize": 5}}]],
    "/wp/v2/settings": {"title": "elTAHFIDH", "email": "rahasia@contoh.id"},
    "/wp/v2/users": [[{"id": 16, "slug": "labib", "roles": ["editor"], "email": "rahasia@contoh.id"}]],
    "/wp/v2/comments": [[{"id": 3, "author_name": "A", "author_email": "a@contoh.id", "author_ip": "1.2.3.4"}]],
}
NOW = lambda: datetime(2026, 10, 7, tzinfo=timezone.utc)


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = JsonRepository(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_pagination_and_links_are_stripped(self):
        repo = WpApiRepository(MAIN_SITE, FakeClient(ROUTES))
        items = repo.collection("/wp/v2/posts", status="publish")
        self.assertEqual([i["id"] for i in items], [1, 2, 3])
        self.assertNotIn("_links", items[0])

    def test_unauthenticated_export_has_no_private_data(self):
        counts = ExportService(self.store, NOW).export(WpApiRepository(SUBSITES[0], FakeClient(ROUTES)))
        self.assertEqual(counts["posts"], 3)
        self.assertFalse(self.store.site_dir(SUBSITES[0], private=True).exists())
        self.assertTrue((self.store.root / "jenjang" / "smp-quran-putra" / "posts.json").exists())
        self.assertEqual(self.store.read(SUBSITES[0], "site")["exported_at"], "2026-10-07T00:00:00+00:00")

    def test_authenticated_export_strips_personal_data(self):
        client = FakeClient(ROUTES)
        ExportService(self.store, NOW).export(WpApiRepository(MAIN_SITE, client, ("labib", "kode")))
        users = self.store.read(MAIN_SITE, "users", private=True)
        comments = self.store.read(MAIN_SITE, "comments", private=True)
        settings = self.store.read(MAIN_SITE, "settings")
        self.assertNotIn("email", users[0])
        self.assertNotIn("author_email", comments[0])
        self.assertNotIn("author_ip", comments[0])
        self.assertNotIn("email", settings)
        self.assertIn("context=edit", client.calls[1][0])

    def test_closed_route_is_skipped(self):
        counts = ExportService(self.store, NOW).export(WpApiRepository(MAIN_SITE, FakeClient(ROUTES), ("u", "p")))
        self.assertNotIn("menus", counts)
        self.assertIn("menus", counts["dilewati"])

    def test_editor_role_without_settings_still_exports(self):
        routes = {k: v for k, v in ROUTES.items() if k not in ("/wp/v2/settings", "/wp/v2/users")}
        counts = ExportService(self.store, NOW).export(WpApiRepository(MAIN_SITE, FakeClient(routes), ("u", "p")))
        self.assertEqual(counts["posts"], 3)
        self.assertIn("settings", counts["dilewati"])
        self.assertIn("users", counts["dilewati"])
        self.assertEqual(counts["comments"], 1)

    def test_media_backup_downloads_only_missing(self):
        client = FakeClient(ROUTES)
        ExportService(self.store, NOW).export(WpApiRepository(MAIN_SITE, client), include_private=False)
        backup = MediaBackupService(self.store, client)
        self.assertEqual(backup.plan(MAIN_SITE).total_bytes, 5)
        self.assertEqual(backup.run(MAIN_SITE), 1)
        self.assertEqual(backup.run(MAIN_SITE), 0)
        self.assertTrue((self.store.media_dir(MAIN_SITE) / "2026/10/a.jpg").exists())


if __name__ == "__main__":
    unittest.main()
