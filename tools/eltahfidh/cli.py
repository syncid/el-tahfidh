"""Perintah baris (Controller). Merakit dependensi di build_services(), satu-satunya tempat objek dibuat.

  python -m tools.eltahfidh export [--sites utama,smp-quran-putra] [--no-private]
  python -m tools.eltahfidh media --dry-run
  python -m tools.eltahfidh media --site utama [--limit 50]
  python -m tools.eltahfidh build-berita
  python -m tools.eltahfidh build-jenjang
  python -m tools.eltahfidh wxr
  python -m tools.eltahfidh status

Kredensial situs induk (opsional) dibaca dari env WP_USER dan WP_APP_PASSWORD.
Tanpa itu, situs induk diekspor tanpa login (konten terbit saja). Subdomain selalu tanpa login.
"""
import argparse
import os
import sys

from . import config
from .http import HttpError, UrllibClient
from .repositories import DataRepository, JsonRepository, WpApiRepository
from .services import ArticleBuilder, ExportService, JenjangBuilder, MediaBackupService, WxrExporter


def build_services(db_dir=None):
    client = UrllibClient(config.USER_AGENT, config.REQUEST_INTERVAL, download_interval=config.MEDIA_INTERVAL)
    store = JsonRepository(db_dir or config.DB_DIR)
    return client, store, ExportService(store), MediaBackupService(store, client)


def main_auth() -> tuple[str, str] | None:
    user, password = os.environ.get("WP_USER"), os.environ.get("WP_APP_PASSWORD")
    return (user, password) if user and password else None


def cmd_export(args) -> int:
    client, store, exporter, _ = build_services()
    sites = [config.site_by_key(k.strip()) for k in args.sites.split(",")] if args.sites else config.ALL_SITES
    auth = main_auth()
    manifest = store.read_manifest()
    manifest.setdefault("sites", {})
    failed = False
    for site in sites:
        source = WpApiRepository(site, client, auth if site.is_main else None)
        mode = "berlogin" if source.authenticated else "tanpa login"
        print(f"[{site.key}] ekspor {site.host} ({mode}) ...", flush=True)
        try:
            counts = exporter.export(source, include_private=not args.no_private)
        except HttpError as e:
            print(f"[{site.key}] GAGAL: {e}", file=sys.stderr)
            failed = True
            continue
        manifest["sites"][site.key] = {"host": site.host, "authenticated": source.authenticated, "counts": counts}
        print(f"[{site.key}] " + ", ".join(f"{k}={v}" for k, v in counts.items()), flush=True)
    store.write_manifest(manifest)
    print(f"Selesai. Data di {store.root}")
    return 1 if failed else 0


def cmd_media(args) -> int:
    _, store, _, backup = build_services()
    sites = [config.site_by_key(args.site)] if args.site else config.ALL_SITES
    for site in sites:
        if not store.exists(site, "media"):
            print(f"[{site.key}] media.json belum ada; jalankan 'export' dulu.")
            continue
        plan = backup.plan(site)
        print(f"[{site.key}] {len(plan.items)} berkas, {plan.total_bytes / 1e6:.1f} MB; "
              f"belum diunduh {len(plan.missing)} berkas, {plan.missing_bytes / 1e6:.1f} MB")
        if not args.dry_run and plan.missing:
            done, failed = backup.run(site, limit=args.limit,
                                      progress=lambda i, n, m: print(f"  {i}/{n} {m.upload_path}", flush=True))
            print(f"[{site.key}] diunduh {done} berkas, gagal {len(failed)}")
            for url, error in failed:
                print(f"  GAGAL {url} -> {error}")
    return 0


def cmd_build_jenjang(args) -> int:
    client, store, _, _ = build_services()
    if not store.read_manifest():
        print(f"Belum ada ekspor di {store.root}; jalankan 'export' dulu.")
        return 1
    builder = JenjangBuilder(store, DataRepository(config.DATA_DIR), client, config.SITE_DIR)
    for file, posts in builder.build_all():
        print(f"site/{file}: {posts} berita")
    return 0


def cmd_build_berita(args) -> int:
    _, store, _, _ = build_services()
    if not store.read_manifest():
        print(f"Belum ada ekspor di {store.root}; jalankan 'export' dulu.")
        return 1
    count = ArticleBuilder(store, config.SITE_DIR, config.DATA_DIR).build_all()
    print(f"site/berita/: {count} halaman detail; peta alamat di data/peta-tautan.json")
    return 0


def cmd_wxr(args) -> int:
    _, store, _, _ = build_services()
    if not store.read_manifest():
        print(f"Belum ada ekspor di {store.root}; jalankan 'export' dulu.")
        return 1
    for key, count in WxrExporter(store).export_all():
        print(f"db/wxr/{key}.xml: {count} postingan/halaman")
    print("Berkas WXR ada di db/ (lokal). Jangan di-commit: berkas situs induk memuat draf.")
    return 0


def cmd_status(args) -> int:
    _, store, _, _ = build_services()
    manifest = store.read_manifest()
    if not manifest:
        print(f"Belum ada ekspor di {store.root}")
        return 1
    for key, info in manifest.get("sites", {}).items():
        login = "berlogin" if info.get("authenticated") else "tanpa login"
        print(f"{key:18} {info['host']:40} {login:12} " + ", ".join(f"{k}={v}" for k, v in info["counts"].items()))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tools.eltahfidh", description="Alat ekspor dan generator elTAHFIDH.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("export", help="Ekspor WordPress ke db/ (hanya membaca dari situs).")
    p.add_argument("--sites", help="Daftar key dipisah koma. Bawaan: semua situs.")
    p.add_argument("--no-private", action="store_true", help="Lewati draf, pengguna, dan komentar.")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("media", help="Unduh berkas media ke db/media/.")
    p.add_argument("--site", help="Key situs. Bawaan: semua situs.")
    p.add_argument("--dry-run", action="store_true", help="Hanya hitung jumlah dan ukuran.")
    p.add_argument("--limit", type=int, help="Batasi jumlah unduhan per situs.")
    p.set_defaults(func=cmd_media)

    p = sub.add_parser("build-jenjang", help="Bangun site/smp-quran.html, sma-quran.html, ifs.html dari data/ dan db/.")
    p.set_defaults(func=cmd_build_jenjang)

    p = sub.add_parser("build-berita", help="Bangun halaman detail site/berita/<slug>.html dari db/.")
    p.set_defaults(func=cmd_build_berita)

    p = sub.add_parser("wxr", help="Buat berkas impor WordPress (WXR) per situs ke db/wxr/.")
    p.set_defaults(func=cmd_wxr)

    p = sub.add_parser("status", help="Ringkasan isi db/.")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)
