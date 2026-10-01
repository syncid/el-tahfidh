"""Perbaikan pasca-HTTrack untuk mirror kreativaglobal.sch.id.

HTTrack menulis ulang string JS '/id/' menjadi path file ('id/index.html',
'../id/index.html', '../index.html', ...). Akibatnya deteksi bahasa EN/ID
(tombol Enroll/Daftar dan footer) salah. Skrip ini mengembalikannya ke '/id/'.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "referensi" / "kreativa-mirror" / "kreativaglobal.sch.id"
PATTERN = re.compile(r"includes\('(?:\.\./)*(?:id/)?index\.html'\)")

fixed = 0
for page in ROOT.rglob("*.html"):
    text = page.read_text(encoding="utf-8", errors="ignore")
    new, n = PATTERN.subn("includes('/id/')", text)
    if n:
        page.write_text(new, encoding="utf-8")
        fixed += n

print(f"fixup: {fixed} literal JS dikembalikan ke '/id/'")
sys.exit(0)
