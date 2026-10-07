"""Isi <main> halaman detail berita/artikel di site/berita/. Semua tautan internal memakai awalan ../"""
from html import escape as e


def render(entry, content_html: str, featured: str | None) -> str:
    post = entry.post
    figure = (f'        <figure class="artikel__media"><img src="{e(featured)}" alt="{e(post.title)}"></figure>\n'
              if featured else "")
    return f"""<main id="konten">
    <section class="page-hero">
      <div class="wrap">
        <ol class="crumbs" aria-label="Breadcrumb"><li><a href="../index.html">Beranda</a></li><li><a href="../{e(entry.back_page)}">{e(entry.section)}</a></li></ol>
        <h1>{e(post.title)}</h1>
        <p><time datetime="{e(post.date[:10])}">{e(post.date_label)}</time></p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <article class="prose narrow artikel">
{figure}{content_html}
          <p class="note">Pertama terbit di <a href="{e(post.link)}" target="_blank" rel="noopener">{e(entry.site.host)}</a>.</p>
        </article>
        <p class="center more-all"><a class="btn btn--primary" href="../{e(entry.back_page)}">Kembali ke {e(entry.section)}</a></p>
      </div>
    </section>
  </main>"""
