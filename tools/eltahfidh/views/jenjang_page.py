"""Isi <main> halaman jenjang. Hanya menyusun markup; data sudah disiapkan oleh Service."""
from html import escape as e

from . import components as c

IND = "        "


def render(page: dict, org_cards: list[str], post_cards: list[str]) -> str:
    sections = [_hero(page), _subnav(page, bool(post_cards)), _kampus(page)]
    if page.get("visi"):
        sections.append(_visi_misi(page))
    sections.append(_program(page))
    if page.get("unggulan"):
        sections.append(_unggulan(page))
    sections.append(_pimpinan(page, org_cards))
    if post_cards:
        sections.append(_berita(page, post_cards))
    sections.append(_cta(page))
    return '<main id="konten">\n' + "\n\n".join(sections) + "\n  </main>"


def _hero(page: dict) -> str:
    return f"""    <section class="page-hero">
      <div class="wrap">
        <ol class="crumbs" aria-label="Breadcrumb"><li><a href="index.html">Beranda</a></li><li><a href="profil.html">Profil</a></li><li>{e(page['label'])}</li></ol>
        <h1>{e(page['judul'])}</h1>
        <p>{e(page['lead'])}</p>
      </div>
    </section>"""


def _subnav(page: dict, has_posts: bool) -> str:
    links = [("kampus", "Kampus"), ("program", "Program"), ("pimpinan", "Pimpinan")]
    if has_posts:
        links.append(("berita", "Berita"))
    items = "\n".join(f'          <li><a href="#{a}">{t}</a></li>' for a, t in links)
    return f"""    <nav class="subnav" aria-label="Bagian halaman {e(page['label'])}">
      <div class="wrap">
        <ul>
{items}
        </ul>
      </div>
    </nav>"""


def _head(eyebrow: str, title: str, lead: str = "") -> str:
    p = f"\n          <p>{e(lead)}</p>" if lead else ""
    return f"""        <header class="section__head">
          <p class="eyebrow eyebrow--dark">{e(eyebrow)}</p>
          <h2>{e(title)}</h2>{p}
        </header>"""


def _kampus(page: dict) -> str:
    cards = "\n".join(c.level_card(k, IND + "  ") for k in page["kampus"])
    return f"""    <section class="section" id="kampus">
      <div class="wrap">
{_head("Pilihan Kampus", f"Belajar di {page['label']}")}
        <div class="grid grid--3">
{cards}
        </div>
      </div>
    </section>"""


def _visi_misi(page: dict) -> str:
    misi = "\n".join(f"              <li>{e(m)}</li>" for m in page["misi"])
    return f"""    <section class="section section--soft" id="visi-misi">
      <div class="wrap">
{_head("Visi & Misi", f"Visi dan Misi {page['judul']}")}
        <div class="vm">
          <div class="card vm__visi">
            <h3>Visi</h3>
            <p>{e(page['visi'])}</p>
          </div>
          <div class="card vm__misi">
            <h3>Misi</h3>
            <ol>
{misi}
            </ol>
          </div>
        </div>
      </div>
    </section>"""


def _program(page: dict) -> str:
    soft = "" if page.get("visi") else " section--soft"
    pillars = "\n".join(c.pillar_card(i, p, IND + "  ") for i, p in enumerate(page["pilar"], 1))
    facts = ""
    if page.get("fakta"):
        rows = "\n".join(c.fact_card(f, IND + "  ") for f in page["fakta"])
        facts = f'\n        <div class="facts facts--mini">\n{rows}\n        </div>'
    return f"""    <section class="section{soft}" id="program">
      <div class="wrap">
{_head("Program", "Tiga Pilar Pendidikan", "Al-Qur'an, akademik, dan pembentukan karakter berjalan bersama.")}
        <div class="pillars">
{pillars}
        </div>{facts}
      </div>
    </section>"""


def _unggulan(page: dict) -> str:
    blocks = "\n".join(c.program_block(i, item, IND) for i, item in enumerate(page["unggulan"]))
    return f"""    <section class="section section--soft" id="unggulan">
      <div class="wrap">
{_head("Program Unggulan", "Program Lengkap dan Menyeluruh untuk Ananda")}
{blocks}
      </div>
    </section>"""


def _pimpinan(page: dict, org_cards: list[str]) -> str:
    cards = "\n".join(org_cards)
    return f"""    <section class="section" id="pimpinan">
      <div class="wrap">
{_head("Pimpinan", f"Pimpinan {page['label']}", "Sesuai struktur organisasi resmi elTAHFIDH Indonesia.")}
        <div class="org__grid">
{cards}
        </div>
      </div>
    </section>"""


def _berita(page: dict, post_cards: list[str]) -> str:
    cards = "\n".join(post_cards)
    return f"""    <section class="section section--soft" id="berita">
      <div class="wrap">
{_head("Berita", f"Kabar Terbaru {page['label']}")}
        <div class="posts">
{cards}
        </div>
        <p class="center more-all"><a class="btn btn--primary" href="berita.html">Lihat Semua Berita</a></p>
      </div>
    </section>"""


def _cta(page: dict) -> str:
    return f"""    <section class="cta">
      <div class="wrap center">
        <h2>Ingin diberi mahkota cahaya kemuliaan oleh Ananda di surga?</h2>
        <p>Daftarkan Ananda di {e(page['judul'])} atau tanyakan informasi penerimaan murid baru melalui WhatsApp.</p>
        <div class="hero__cta hero__cta--center">
          <a class="btn btn--accent" href="psb.html#jalur">Daftar Sekarang</a>
          <a class="btn btn--ghost" href="https://wa.link/g9jplc" target="_blank" rel="noopener">Tanya via WhatsApp</a>
        </div>
      </div>
    </section>"""
