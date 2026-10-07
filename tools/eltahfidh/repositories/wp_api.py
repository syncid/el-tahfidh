"""Sumber data: REST API WordPress satu situs. Hanya membaca (GET)."""
import urllib.parse

from ..http import HttpClient, HttpError
from ..models import Site

PER_PAGE = 100
# Rute yang tertutup untuk peran akun (mis. Editor tidak boleh membaca pengaturan atau menu).
CLOSED = (400, 401, 403, 404)


class WpApiRepository:
    def __init__(self, site: Site, client: HttpClient, auth: tuple[str, str] | None = None):
        self.site = site
        self._client = client
        self._auth = auth

    @property
    def authenticated(self) -> bool:
        return self._auth is not None

    def root(self) -> dict:
        data = self._client.get(f"{self.site.api_base}/").json()
        return {k: data.get(k) for k in ("name", "description", "url", "home", "gmt_offset", "timezone_string")}

    def settings(self) -> dict | None:
        """Pengaturan situs. None bila peran akun tidak mengizinkan (hanya administrator)."""
        try:
            return self._get("/wp/v2/settings")
        except HttpError as e:
            if e.status in CLOSED:
                return None
            raise

    def collection(self, endpoint: str, **params) -> list[dict]:
        """Ambil semua halaman sebuah koleksi, mis. collection('/wp/v2/posts', status='publish')."""
        params.setdefault("per_page", PER_PAGE)
        if self.authenticated:
            params.setdefault("context", "edit")
        items, page = [], 1
        while True:
            params["page"] = page
            response = self._client.get(self._url(endpoint, params), auth=self._auth)
            batch = response.json()
            items.extend(_strip_links(item) for item in batch)
            total_pages = int(response.headers.get("x-wp-totalpages") or 1)
            if page >= total_pages or not batch:
                return items
            page += 1

    def try_collection(self, endpoint: str, **params) -> list[dict] | None:
        """Seperti collection(), tetapi mengembalikan None bila rute tertutup (401/403/404)."""
        try:
            return self.collection(endpoint, **params)
        except HttpError as e:
            if e.status in CLOSED:
                return None
            raise

    def _get(self, endpoint: str, **params) -> dict:
        return _strip_links(self._client.get(self._url(endpoint, params), auth=self._auth).json())

    def _url(self, endpoint: str, params: dict) -> str:
        query = urllib.parse.urlencode(params, doseq=True)
        return f"{self.site.api_base}{endpoint}" + (f"?{query}" if query else "")


def _strip_links(item):
    if isinstance(item, dict):
        item.pop("_links", None)
    return item
