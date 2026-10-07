"""Cadangan berkas media: unduh berkas asli (bukan ukuran turunan) dari media.json ke db/media/."""
from dataclasses import dataclass
from pathlib import Path

from ..http import HttpClient
from ..models import Media, Site
from ..repositories import JsonRepository


@dataclass
class MediaPlan:
    items: list[tuple[Media, Path]]
    missing: list[tuple[Media, Path]]

    @property
    def total_bytes(self) -> int:
        return sum(m.filesize for m, _ in self.items)

    @property
    def missing_bytes(self) -> int:
        return sum(m.filesize for m, _ in self.missing)


class MediaBackupService:
    def __init__(self, store: JsonRepository, client: HttpClient):
        self._store = store
        self._client = client

    def plan(self, site: Site) -> MediaPlan:
        base = self._store.media_dir(site)
        items = [(m, base / m.upload_path) for m in self._store.media(site) if m.source_url]
        missing = [(m, p) for m, p in items if not p.exists()]
        return MediaPlan(items, missing)

    def run(self, site: Site, limit: int | None = None, progress=None) -> int:
        """Unduh berkas yang belum ada. Mengembalikan jumlah berkas yang diunduh."""
        todo = self.plan(site).missing[:limit] if limit else self.plan(site).missing
        for index, (media, target) in enumerate(todo, 1):
            self._client.download(media.source_url, target)
            if progress:
                progress(index, len(todo), media)
        return len(todo)
