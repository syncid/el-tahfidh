"""Klien HTTP dengan jeda antar-permintaan dan penanganan 429.

HttpClient adalah kontrak; UrllibClient implementasi produksinya. Service dan Repository
hanya bergantung pada kontrak, sehingga uji unit bisa memakai klien palsu.
"""
import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class HttpError(RuntimeError):
    def __init__(self, status: int, url: str, body: str = ""):
        super().__init__(f"HTTP {status} untuk {url}")
        self.status = status
        self.url = url
        self.body = body


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self):
        return json.loads(self.body)


class HttpClient(Protocol):
    def get(self, url: str, auth: tuple[str, str] | None = None) -> Response: ...

    def download(self, url: str, target) -> int: ...


class UrllibClient:
    """Klien produksi berbasis urllib. Kredensial hanya dipakai di header, tidak pernah dicatat."""

    def __init__(self, user_agent: str, interval: float, retries: int = 3, sleep=time.sleep, now=time.monotonic):
        self._ua = user_agent
        self._interval = interval
        self._retries = retries
        self._sleep = sleep
        self._now = now
        self._last = 0.0

    def get(self, url: str, auth: tuple[str, str] | None = None) -> Response:
        headers = {"User-Agent": self._ua, "Accept": "application/json"}
        if auth:
            token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        for attempt in range(self._retries + 1):
            self._pace()
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                    return Response(r.status, {k.lower(): v for k, v in r.headers.items()}, r.read())
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < self._retries:
                    wait = int(e.headers.get("Retry-After") or 0) or 30 * (attempt + 1)
                    self._sleep(wait)
                    continue
                raise HttpError(e.code, url, e.read().decode("utf-8", "replace")[:300]) from None
        raise HttpError(429, url)

    def download(self, url: str, target) -> int:
        """Unduh ke berkas sementara lalu ganti nama, agar unduhan terputus tidak meninggalkan berkas rusak."""
        self._pace()
        tmp = target.with_name(target.name + ".part")
        target.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url, headers={"User-Agent": self._ua})
        with urllib.request.urlopen(request, timeout=120) as r, open(tmp, "wb") as out:
            while chunk := r.read(1 << 16):
                out.write(chunk)
        tmp.replace(target)
        return target.stat().st_size

    def _pace(self) -> None:
        wait = self._interval - (self._now() - self._last)
        if wait > 0:
            self._sleep(wait)
        self._last = self._now()
