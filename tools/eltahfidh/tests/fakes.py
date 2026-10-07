"""Klien HTTP palsu untuk uji: tidak ada permintaan jaringan sungguhan."""
import json
import urllib.parse

from tools.eltahfidh.http import HttpError, Response


class FakeClient:
    def __init__(self, routes: dict):
        """routes: {'/wp/v2/posts': [[item, ...], [item, ...]]} (daftar halaman) atau {'/': {...}}."""
        self.routes = routes
        self.calls: list[tuple[str, tuple | None]] = []
        self.downloads: list[str] = []

    def get(self, url, auth=None):
        self.calls.append((url, auth))
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.split("/wp-json", 1)[1]
        query = urllib.parse.parse_qs(parsed.query)
        if path not in self.routes:
            raise HttpError(404, url)
        data = self.routes[path]
        if isinstance(data, list):
            page = int(query.get("page", ["1"])[0])
            body = data[page - 1] if page <= len(data) else []
            return Response(200, {"x-wp-totalpages": str(len(data))}, json.dumps(body).encode())
        return Response(200, {}, json.dumps(data).encode())

    def download(self, url, target):
        self.downloads.append(url)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x")
        return 1
