"""Cadangan berkas media: unduh berkas asli (bukan ukuran turunan) dari media.json ke db/media/."""
from dataclasses import dataclass
from pathlib import Path

from ..http import HttpClient, HttpError
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

    def run(self, site: Site, limit: int | None = None, progress=None) -> tuple[int, list[tuple[str, str]]]:
        """Unduh berkas yang belum ada. Berkas yang gagal dicatat lalu dilewati agar proses tetap berjalan.

        Mengembalikan (jumlah berhasil, daftar (alamat, galat) yang gagal).
        """
        todo = self.plan(site).missing[:limit] if limit else self.plan(site).missing
        done, failed = 0, []
        for index, (media, target) in enumerate(todo, 1):
            try:
                self._client.download(media.source_url, target)
                done += 1
            except (OSError, ValueError, HttpError) as e:  # URLError dan HTTPError turunan OSError
                failed.append((media.source_url, f"{type(e).__name__}: {e}"))
            if progress:
                progress(index, len(todo), media)
        return done, failed
