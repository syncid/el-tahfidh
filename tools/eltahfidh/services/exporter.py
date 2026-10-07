"""Ekspor satu situs WordPress ke db/: konten terbit, metadata media, dan (bila berlogin) data privat.

Aturan privasi ditegakkan di sini, bukan di Repository: email pengguna, email/IP komentator,
dan email admin di pengaturan dibuang sebelum disimpan.
"""
from datetime import datetime, timezone

from ..repositories import JsonRepository, WpApiRepository

PRIVATE_STATUSES = "draft,pending,private,future"
USER_FIELDS = ("id", "name", "slug", "roles", "registered_date", "description")
COMMENT_DROP = ("author_email", "author_ip", "author_user_agent", "author_avatar_urls")
SETTINGS_DROP = ("email",)


class ExportService:
    def __init__(self, store: JsonRepository, now=lambda: datetime.now(timezone.utc)):
        self._store = store
        self._now = now

    def export(self, source: WpApiRepository, include_private: bool = True) -> dict:
        site = source.site
        counts: dict[str, int | str] = {}
        skipped: list[str] = []

        info = source.root() | {"key": site.key, "host": site.host, "label": site.label,
                                "jenjang": site.jenjang, "exported_at": self._now().isoformat(timespec="seconds")}
        self._store.write(site, "site", info)

        for name, endpoint, params in (
            ("posts", "/wp/v2/posts", {"status": "publish"}),
            ("pages", "/wp/v2/pages", {"status": "publish"}),
            ("categories", "/wp/v2/categories", {}),
            ("tags", "/wp/v2/tags", {}),
            ("media", "/wp/v2/media", {}),
        ):
            items = source.collection(endpoint, **params)
            self._store.write(site, name, items)
            counts[name] = len(items)

        if source.authenticated:
            # Tiap bagian berlogin dicoba sendiri-sendiri: rute yang tertutup untuk peran akun
            # (mis. pengaturan dan menu untuk Editor) dicatat sebagai dilewati, bukan menggagalkan ekspor.
            settings = source.settings()
            if settings is None:
                skipped.append("settings")
            else:
                self._store.write(site, "settings", {k: v for k, v in settings.items() if k not in SETTINGS_DROP})
            for name, endpoint in (("menus", "/wp/v2/menus"), ("menu-items", "/wp/v2/menu-items")):
                self._save_optional(source, name, endpoint, {}, counts, skipped)
            if include_private:
                self._export_private(source, counts, skipped)

        if skipped:
            counts["dilewati"] = ",".join(skipped)
        return counts

    def _export_private(self, source: WpApiRepository, counts: dict, skipped: list) -> None:
        for name, endpoint in (("drafts-posts", "/wp/v2/posts"), ("drafts-pages", "/wp/v2/pages")):
            self._save_optional(source, name, endpoint, {"status": PRIVATE_STATUSES}, counts, skipped, private=True)
        self._save_optional(source, "users", "/wp/v2/users", {}, counts, skipped, private=True,
                            clean=lambda u: {k: u.get(k) for k in USER_FIELDS})
        self._save_optional(source, "comments", "/wp/v2/comments", {"status": "approve"}, counts, skipped,
                            private=True, clean=lambda c: {k: v for k, v in c.items() if k not in COMMENT_DROP})

    def _save_optional(self, source, name, endpoint, params, counts, skipped, private=False, clean=None) -> None:
        items = source.try_collection(endpoint, **params)
        if items is None:
            skipped.append(name)
            return
        if clean:
            items = [clean(item) for item in items]
        self._store.write(source.site, name, items, private=private)
        counts[name] = len(items)
