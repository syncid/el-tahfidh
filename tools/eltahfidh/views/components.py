"""Potongan markup yang meniru komponen site/ apa adanya. Semua teks di-escape di sini."""
from html import escape as e

from ..models import Content


def post_card(post: Content, img: str | None, indent: str) -> str:
    """Sama dengan card() di tools/build_posts.py agar gaya kartu berita seragam."""
    media = (f'<img src="{e(img)}" alt="" loading="lazy">' if img
             else '<div class="post__noimg"><img src="assets/img/logo.png" alt="" loading="lazy"></div>')
    return (
        f'{indent}<article class="card post">\n'
        f'{indent}  <div class="post__media">{media}</div>\n'
        f'{indent}  <div class="post__body">\n'
        f'{indent}    <time datetime="{e(post.date[:10])}">{e(post.date_label)}</time>\n'
        f'{indent}    <h3><a href="{e(post.link)}" target="_blank" rel="noopener">{e(post.title)}</a></h3>\n'
        f'{indent}    <p>{e(post.excerpt())}</p>\n'
        f'{indent}  </div>\n'
        f'{indent}</article>'
    )


def org_card(lembaga: dict, foto: str | None, sapaan: str | None, indent: str) -> str:
    """Sama dengan kartu .org__card di site/profil.html."""
    nama = f"{sapaan} {lembaga['pimpinan']}" if sapaan else lembaga["pimpinan"]
    photo = (f'<img src="{e(foto)}" alt="{e(nama)}" loading="lazy">' if foto
             else f'<div class="org__ph" aria-hidden="true"><span>{e(nama)}</span></div>')
    lines = [
        f'{indent}<article class="card org__card">',
        f"{indent}  {photo}",
        f'{indent}  <p class="org__unit">{e(lembaga["nama"])}</p>',
        f"{indent}  <h3>{e(nama)}</h3>",
        f'{indent}  <p class="role">{e(lembaga.get("jabatan", ""))}</p>',
    ]
    if lembaga.get("wakil"):
        lines.append(f'{indent}  <p class="org__wakil">Wakil {e(lembaga.get("jabatan", ""))}: {e(lembaga["wakil"])}</p>')
    if lembaga.get("unit"):
        lines += [f"{indent}  <details>", f"{indent}    <summary>Lihat bagian</summary>", f"{indent}    <ul>"]
        for unit in lembaga["unit"]:
            item = f"<strong>{e(unit['nama'])}</strong>"
            if unit.get("pj"):
                item += f"<br>PJ: {e(unit['pj'])}"
            if unit.get("sub"):
                item += f"<br><small>{e(', '.join(unit['sub']))}</small>"
            lines.append(f"{indent}      <li>{item}</li>")
        lines += [f"{indent}    </ul>", f"{indent}  </details>"]
    lines.append(f"{indent}</article>")
    return "\n".join(lines)


def level_card(kampus: dict, indent: str) -> str:
    """Kartu .level seperti di beranda; gambar dan tautan opsional."""
    lines = [f'{indent}<article class="card level">']
    if kampus.get("gambar"):
        lines.append(f'{indent}  <img src="{e(kampus["gambar"])}" alt="{e(kampus["nama"])}" '
                     f'width="{kampus.get("lebar", "")}" height="{kampus.get("tinggi", "")}" loading="lazy">')
    lines.append(f'{indent}  <h3>{e(kampus["nama"])}</h3>')
    if kampus.get("teks"):
        lines.append(f'{indent}  <p>{e(kampus["teks"])}</p>')
    if kampus.get("tautan"):
        lines.append(f'{indent}  <a class="more" href="{e(kampus["tautan"])}">Selengkapnya</a>')
    lines.append(f"{indent}</article>")
    return "\n".join(lines)


def pillar_card(nomor: int, pilar: dict, indent: str) -> str:
    """Kartu .pillar seperti di site/profil.html."""
    butir = "".join(f"<li>{e(b)}</li>" for b in pilar["butir"])
    return (
        f'{indent}<article class="card pillar">\n'
        f'{indent}  <span class="icon" aria-hidden="true">{nomor:02d}</span>\n'
        f'{indent}  <h3>{e(pilar["judul"])}</h3>\n'
        f"{indent}  <ul>{butir}</ul>\n"
        f"{indent}</article>"
    )


def fact_card(fakta: dict, indent: str) -> str:
    return f'{indent}<div class="card fact"><strong>{e(fakta["angka"])}</strong><span>{e(fakta["teks"])}</span></div>'


def program_block(nomor: int, item: dict, indent: str) -> str:
    """Blok .program bergantian kiri-kanan seperti di beranda."""
    cls = "program program--rev" if nomor % 2 else "program"
    media_cls = " ".join(filter(None, ["program__media", item.get("kelas_gambar")]))
    return (
        f'{indent}<article class="{cls}">\n'
        f'{indent}  <img class="{media_cls}" src="{e(item["gambar"])}" alt="{e(item["alt"])}" '
        f'width="{item["lebar"]}" height="{item["tinggi"]}" loading="lazy">\n'
        f'{indent}  <div class="program__txt">\n'
        f'{indent}    <h3>{e(item["judul"])}</h3>\n'
        f'{indent}    <p>{e(item["teks"])}</p>\n'
        f"{indent}  </div>\n"
        f"{indent}</article>"
    )
