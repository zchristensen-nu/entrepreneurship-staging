"""Build the Entrepreneurship staging site on the Northeastern Design System (NUEAC-413).

Content is the live entrepreneurship.northeastern.edu content (scraped into build/content.json; images in build/img/).
Every page is composed from the system's organisms; the shell comes from ~/Projects/nu-site-kit. Only the images a page
uses are copied into docs/, resized and recompressed.
    python3 build/build.py            # writes docs/
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path.home() / "Projects/nu-site-kit"))
from kit import (CUR, Site, band, breadcrumb, contact_items, document, e, facet_checks, facet_chips, finder, hero_page, hero_title,  # noqa: E402
                 href, i, link_row, not_found, section_header)

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "build/content.json").read_text())
R = C["records"]
LIVE = "https://entrepreneurship.northeastern.edu/"
UNIT = "Entrepreneurship"
PAGES = {p["slug"]: p for p in C["pages"]}
OUT_IMG = ROOT / "docs/assets/img"


def sec(slug, n):
    return PAGES[slug]["sections"][n]["content"]


def texts(items, kind):
    return [c.get("text") or "" for c in items if c.get("kind") == kind]


def clean(s):
    return re.sub(r"\s*\n\s*", " ", (s or "").replace("\xa0", " ")).strip()


def local(u):
    if not u:
        return "#"
    if u.startswith(LIVE):
        u = u[len(LIVE):].split("#")[0]
        return {"ventures/": "", "global-entrepreneurship-week/": "events/"}.get(u, u)
    return u


def asset(path, logo=False):
    """Copy one crawled image into docs/, at most 1600px (logos 480px); large PNG photographs become JPEG."""
    src = ROOT / "build" / path
    name = src.name
    im = Image.open(src)
    limit = 480 if logo else 1600
    if logo and im.mode in ("RGBA", "LA", "P"):
        im = im.crop(im.convert("RGBA").getchannel("A").getbbox())  # padded artwork makes marks read small
    if max(im.size) > limit:
        im.thumbnail((limit, limit))
    photo = not logo and src.suffix.lower() == ".png" and src.stat().st_size > 400_000 and im.mode in ("RGB", "RGBA", "P")
    if photo:
        name = src.stem + ".jpg"
        im = im.convert("RGB")
    out = OUT_IMG / name
    if logo or not out.exists():
        OUT_IMG.mkdir(parents=True, exist_ok=True)
        if photo or src.suffix.lower() in (".jpg", ".jpeg"):
            im.convert("RGB").save(out, "JPEG", quality=82, optimize=True, progressive=True)
        else:
            im.save(out, optimize=True)
    return name


def pic(path, alt="", ratio="3x2", logo=False):
    cls = "nu-image" if ratio == "natural" else f"nu-image nu-image--{ratio}"
    return f'<img class="{cls}" src="{{{{base}}}}assets/img/{asset(path, logo)}" alt="{e(alt)}" loading="lazy">'


def button(text, url, kind=""):
    t = local(url)
    ext = t.startswith("http")
    return f'<a class="nu-button{" nu-button--" + kind if kind else ""}" href="{href(t)}">{e(text)} {i("external" if ext else "arrow")}</a>'


def arrow(text, url):
    t = local(url)
    return f'<a class="nu-arrow-link" href="{href(t)}">{e(text)} {i("external" if t.startswith("http") else "arrow")}</a>'


def accordion(items, idp):
    """items: [(title, [paragraphs])]"""
    out = ""
    for n, (title, paras) in enumerate(items):
        body = "".join(f'<p class="nu-text">{e(p).replace(chr(10), "<br>")}</p>' for p in paras)
        out += f'''<details class="nu-accordion-item" id="{idp}-{n}">
  <summary class="nu-accordion-item__summary"><h3 class="nu-heading nu-heading--h4 nu-accordion-item__title">{e(title)}</h3><span class="nu-icon-button nu-accordion-item__icon" aria-hidden="true">{i("plus")}</span></summary>
  <div class="nu-accordion-item__panel">{body}</div>
</details>'''
    return out


def directions(items):
    """Directions / Parking Info accordion items from a run of summary + p items."""
    groups, cur = [], None
    for c in items:
        if c["kind"] == "summary":
            cur = (c["text"], [])
            groups.append(cur)
        elif cur and c["kind"] == "p":
            cur[1].append(c["text"])
        elif c["kind"] == "h2":
            cur = None
    return groups


def key_values(pairs, cls=""):
    rows = "".join(f'<div class="nu-key-value__row"><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in pairs)
    return f'<dl class="nu-key-value {cls}">{rows}</dl>'


def staging_form(heading, idp, note=""):
    req = '<span class="nu-label__req">(required)</span>'
    return f'''<form class="nu-form nu-form--split" data-staging-form novalidate>
  <div class="nu-form__head">
    <h2 class="nu-heading nu-heading--h2">{e(heading)}</h2>
    <p class="nu-form__note">Fields marked (required) must be filled in.</p>
  </div>
  <div class="nu-form__body">
    <div class="nu-notice" role="status" hidden data-staging-sent><p class="nu-text">This is the staging site, so nothing was sent. On the live site the entrepreneurship team receives this form.</p></div>
    <fieldset class="nu-form__group">
      <legend>About you</legend>
      <div class="nu-form__row">
        <div class="nu-field"><label class="nu-label" for="{idp}-first">First name {req}</label><input class="nu-input" id="{idp}-first" autocomplete="given-name" required></div>
        <div class="nu-field"><label class="nu-label" for="{idp}-last">Last name {req}</label><input class="nu-input" id="{idp}-last" autocomplete="family-name" required></div>
      </div>
      <div class="nu-form__row">
        <div class="nu-field"><label class="nu-label" for="{idp}-email">Email {req}</label><input class="nu-input" id="{idp}-email" type="email" autocomplete="email" required></div>
        <div class="nu-field"><label class="nu-label" for="{idp}-phone">Phone</label><span class="nu-hint" id="{idp}-phone-hint">Include the country code outside the US.</span><input class="nu-input" id="{idp}-phone" type="tel" autocomplete="tel" aria-describedby="{idp}-phone-hint"></div>
      </div>
      <div class="nu-form__row">
        <div class="nu-field"><label class="nu-label" for="{idp}-org">Organization</label><input class="nu-input" id="{idp}-org" autocomplete="organization"></div>
        <div class="nu-field"><label class="nu-label" for="{idp}-url">Website or URL</label><input class="nu-input" id="{idp}-url" type="url" autocomplete="url"></div>
      </div>
    </fieldset>
    <fieldset class="nu-form__group">
      <legend>What you’re working on</legend>
      <div class="nu-field"><label class="nu-label" for="{idp}-interests">Please share more about your interests.</label><textarea class="nu-input" id="{idp}-interests" rows="5"></textarea></div>
    </fieldset>
    <div class="nu-form__foot"><div class="nu-form__actions"><button class="nu-button nu-button--accent" type="submit">Submit</button>{f'<p class="nu-form__note">{note}</p>' if note else ""}</div></div>
  </div>
</form>'''


NAV = [("Programs and offerings", "offerings/"), ("Venture portfolio", "ventures/portfolio/"), ("300 Startup Hub", "300-startup-hub/"),
       ("Global events", [("All events", "events/"), ("300 Mass Ave. Launch Week", "300-mass-ave-open-house/"),
                          ("Next Up Founders Prize", "ventures/next-up-2026/"), ("GLS Venture Forum", "https://www.northeastern.edu/gls2026recap/"),
                          ("Events on Luma", "https://luma.com/eship")]),
       ("Get involved", "contact-us/")]
site = Site(ROOT, UNIT, "entrepreneurship-staging", "entrepreneurship.northeastern.edu", NAV,
            [("Entrepreneurship", [("Programs and offerings", "offerings/"), ("Venture portfolio", "ventures/portfolio/"), ("300 Startup Hub", "300-startup-hub/"), ("Get involved", "contact-us/")]),
             ("Global events", [("All events", "events/"), ("300 Mass Ave. Launch Week", "300-mass-ave-open-house/"), ("Next Up Founders Prize", "ventures/next-up-2026/"),
                                ("GLS Venture Forum", "https://www.northeastern.edu/gls2026recap/"), ("Events on Luma", "https://luma.com/eship")])],
            address=["300 Massachusetts Ave.", "Boston, MA 02115"])


# ---------- finder (programs, ventures) ----------
SAME = {"Accelerators": "Accelerator", "Investors": "Investor"}  # duplicated terms on the live site


def norm(terms):
    return sorted({SAME.get(t, t) for t in terms})


def offerings():
    items = sec("offerings", 0)
    progs = sorted(R["programs"], key=lambda p: p["title"].lower())
    keys = [("categories", "Categories"), ("locations", "Locations"), ("interests", "I’m interested in"), ("i_am", "I am a")]
    for p in progs:
        for k, _ in keys:
            p[k] = norm(p.get(k, []))
    cards = ""
    for p in progs:
        terms = json.dumps({k: p[k] for k, _ in keys})
        im = (p.get("image") or p.get("featured_media") or {}).get("local")
        cards += f'''<li data-terms='{e(terms)}'><article class="nu-program-card">
  {f'<span class="nu-program-card__media">{pic(im, "")}</span>' if im else ""}
  <div class="nu-program-card__body">
    <h3 class="nu-heading nu-heading--h4 nu-program-card__title"><a class="nu-program-card__link" href="{e(p["external_link"])}">{e(p["title"])}</a></h3>
    <p class="nu-text nu-text--small">{e(clean(p["description"]))}</p>
    <div class="nu-program-card__foot">
      <div class="nu-program-card__tags">{"".join(f'<span class="nu-tag">{e(c)}</span>' for c in p["categories"][:1])}</div>
      <span class="nu-arrow-link nu-arrow-link--sm nu-arrow-link--external nu-program-card__cue" aria-hidden="true">Visit {i("external")}</span>
    </div>
  </div>
</article></li>'''
    def counter(k):
        return lambda v: sum(v in p[k] for p in progs)
    facets = "".join((facet_chips if k == "categories" else facet_checks)(k, l, sorted({t for p in progs for t in p[k]}), counter(k)) for k, l in keys)
    body = hero_title(texts(items, "h1")[0], texts(items, "p")[-1], [(UNIT, "")]) + finder("Filter programs", "programs", facets, cards)
    site.page("offerings", "Programs and offerings", texts(items, "p")[-1], body, "offerings/")


def portfolio():
    """DirectoryGrid in the finder layout: a name search and the industry list in the FilterPanel (a drawer below 960px), a dense logo
    grid with a Grid / List toggle, 30 at a time. The kit's finder() has no search, so this is a local variant driven by the ge block in site.js."""
    items = sec("ventures__portfolio", 0)
    vs = sorted(R["partners"], key=lambda p: clean(p["name_as_shown"] or p["title"]).lower())
    lis = ""
    for v in vs:
        name = clean(v["name_as_shown"] or v["title"])
        ind = [t for t in (v.get("industries") or []) if not t.lower().startswith("lorem")]
        logo = (v.get("logo") or {}).get("local")
        tile = (f'<img class="nu-logo-tile__mark" src="{{{{base}}}}assets/img/{asset(logo, logo=True)}" alt="">' if logo
                else f'<span class="nu-logo-tile__name">{e(name)}</span>')
        site_url = v.get("website") or ""
        bad = (not site_url) or site_url.startswith(LIVE)  # six ventures link to empty pages on the live site
        title = e(name) if bad else f'<a class="nu-directory-grid__link" href="{e(site_url)}" target="_blank" rel="noopener">{e(name)}<span class="u-vh"> (opens in a new tab)</span></a>'
        lis += f'''<li data-terms=\'{e(json.dumps({"industries": ind}))}\' data-name="{e(name.lower())}"><article class="nu-directory-grid__item">
  <div class="nu-logo-tile">{tile}</div>
  <div class="nu-directory-grid__body"><h3 class="nu-heading nu-heading--h5">{title}</h3>{f'<p class="nu-text nu-text--meta">{e(" · ".join(ind))}</p>' if ind else ""}</div>
  <p class="nu-text nu-text--small nu-directory-grid__desc">{e(clean(v["description"]))}</p>
</article></li>'''
    inds = sorted({t for v in vs for t in v.get("industries") or [] if not t.lower().startswith("lorem")})
    facet = facet_checks("industries", "Industries", inds, lambda x: sum(x in (r.get("industries") or []) for r in vs), visible=8)
    n = len(vs)
    finder_html = f'''<section class="st-band st-finder" aria-labelledby="finder-h" data-ge-dir data-page="30">
  <div class="st-finder__layout">
    <div class="st-finder__drawer" id="finder-drawer" data-drawer>
      <form class="nu-filter-panel nu-filter-panel--sidebar" aria-labelledby="finder-h" data-ge-panel>
        <div class="nu-filter-panel__head"><h2 class="nu-heading nu-heading--h4" id="finder-h">Find a venture</h2><button class="nu-filter-panel__clear" type="reset">Clear all</button></div>
        <div class="nu-filter-panel__facet"><div class="nu-search-field" role="search">
          <label class="u-vh" for="v-q">Search ventures by name</label>
          <span class="nu-search-field__box"><input class="nu-input" id="v-q" type="search" placeholder="Venture name" autocomplete="off" data-ge-q>
            <span class="nu-search-field__actions"><button class="nu-icon-button nu-search-field__clear" type="button" aria-label="Clear search" data-ge-q-clear>{i("close")}</button><span class="nu-icon-button" aria-hidden="true">{i("search")}</span></span></span>
        </div></div>
        {facet}
        <div class="nu-filter-panel__foot st-finder__foot"><button class="nu-button" type="button" data-drawer-close>Show <span data-ge-total>{n}</span> ventures</button></div>
      </form>
    </div>
    <div class="st-finder__results">
      <section class="nu-directory-grid" aria-label="Ventures" data-ge-grid>
        <div class="nu-list-toolbar">
          <p class="nu-list-toolbar__count" role="status" data-ge-count>Showing <b>1–30</b> of <b>{n}</b> ventures</p>
          <div class="nu-list-toolbar__controls">
            <button class="nu-button nu-button--sm nu-button--outline st-finder__open" type="button" aria-controls="finder-drawer" aria-expanded="false" data-drawer-open>{i("filter")} Filters <span class="nu-filter-panel__badge" data-ge-badge hidden>0</span></button>
            <div class="nu-chip-group" role="group" aria-label="View"><div class="nu-chip-group__chips">
              <button class="nu-chip" type="button" aria-pressed="true" data-ge-view="grid">{i("grid")} Grid</button>
              <button class="nu-chip" type="button" aria-pressed="false" data-ge-view="list">{i("list")} List</button>
            </div></div>
          </div>
        </div>
        <ul class="nu-directory-grid__items" role="list" data-ge-items>{lis}</ul>
        <p class="nu-text" data-ge-empty hidden>No venture matches that name and industry. Clear one to see more.</p>
        <div class="nu-directory-grid__foot"><button class="nu-button nu-button--outline" type="button" data-ge-more>Show more ventures</button></div>
      </section>
    </div>
  </div>
</section>'''
    hero = hero_page(texts(items, "h1")[0], asset(items[0]["local"]), texts(items, "p")[-1], [(UNIT, "")])
    site.page("ventures/portfolio", "Venture portfolio", texts(items, "p")[-1], finder_html, "ventures/portfolio/", hero)


# ---------- shared pieces (ge: local variants; the kit stays untouched) ----------
HALL = "img/Screenshot-2026-09-21-at-11.57.56-AM-1536x863-f4f0e3.png"  # the 300 Mass Ave. hall, from the Launch Week page
DESK = "img/300MassAveDesk-scaled-0fa63d.jpg"
PITCH = "img/Annabelle_Collette_ROUX_Venture_Showcase-153-1536x1025-4a6e05.jpg"
LAUNCH = "300-mass-ave-open-house/"


def mark(path, limit=1200):
    """A sub-brand lockup: kept as a transparent PNG (asset() would turn a large PNG into a JPEG), at most `limit` px wide."""
    src = ROOT / "build" / path
    out = OUT_IMG / src.name
    if not out.exists():
        im = Image.open(src)
        if im.width > limit:
            im = im.resize((limit, round(im.height * limit / im.width)), Image.LANCZOS)
        OUT_IMG.mkdir(parents=True, exist_ok=True)
        im.save(out, optimize=True)
    return "{{base}}assets/img/" + src.name


def grouped_accordion(title, hid, items):
    """The FAQ pattern (kept from the review): the group's name in columns 1–4 on the same rule as its rows from column 5."""
    return (f'<section class="nu-accordion" aria-labelledby="{hid}"><div class="nu-accordion__groups"><div class="nu-accordion__group">'
            f'<h2 class="nu-heading nu-heading--h4 nu-accordion__group-title" id="{hid}">{e(title)}</h2><div class="nu-accordion__items">{items}</div></div></div></section>')


def statement(line, lead=None, link=None):
    """Statement: one pull-line (two lines at most), the rest as a lead from column 5."""
    a = f'<a class="nu-arrow-link" href="{href(link[1])}">{e(link[0])} {i("arrow")}</a>' if link else ""
    body = f'<div class="nu-statement__body"><p class="nu-text nu-text--lead">{e(lead)}</p>{a}</div>' if lead else a
    return f'<div class="nu-statement"><p class="nu-heading nu-heading--h1 nu-statement__line">{e(line)}</p>{body}</div>'


def poster(title, url, image, caption):
    return f'''<a class="nu-poster-card" href="{href(url)}">
  <span class="nu-poster-card__frame" data-mode="dark"><img class="nu-image nu-image--fill" src="{{{{base}}}}assets/img/{asset(image)}" alt=""><span class="nu-scrim nu-scrim--poster"></span><span class="nu-poster-card__title">{e(title)}</span></span>
  <span class="nu-text nu-text--meta nu-poster-card__caption">{e(caption)}</span>
</a>'''


def campus_map():
    """The CampusMap's dot map and pins, lifted from the system's specimen as a picture of the network (the 14 campuses the stat names).
    Decorative here: no Select, no panel, no selected pin, so nothing on it is interactive."""
    from kit import DS, _block
    src = (DS / "components/organisms/campus-map.html").read_text().split("<!--code-->")[0]
    m = _block(src, '<div class="nu-campus-map__map"', "div")
    m = re.sub(r'<button class="(nu-campus-map__pin[^"]*)"[^>]*?(style="[^"]*")[^>]*>', r'<span class="\1" \2>', m).replace("</button>", "</span>")
    return m.replace('<div class="nu-campus-map__map"', '<div class="nu-campus-map__map" aria-hidden="true"', 1)


# ---------- home ----------
def home():
    h = sec("home", 0)
    # HeroFilm on its photograph (there is no film): the site's line, and what is happening in November as PosterCards.
    posters = "".join(poster(*p) for p in [
        ("300 Mass Ave. Launch Week", LAUNCH, HALL, "November 18–19"),
        ("Next Up Founders Prize finals", NU, PITCH, "November 17–20"),
        ("Hackathon finals", LAUNCH + "#h-hack", DESK, "November 12–19")])
    hero = f'''<section class="nu-hero-film ge-hero-film" data-mode="dark" aria-labelledby="h-home">
  <div class="nu-hero-film__media">
    {pic(next(c["local"] for c in h if c["kind"] == "image"), "", "fill")}
    <span class="nu-scrim nu-scrim--left"></span><span class="nu-scrim nu-scrim--scene"></span><span class="nu-scrim nu-scrim--grain"></span><span class="nu-scrim nu-scrim--full nu-hero-film__phone-scrim"></span>
  </div>
  <div class="nu-hero-film__stage">
    <div class="nu-hero-film__copy">
      <h1 class="nu-heading nu-heading--display-xl nu-hero-film__title" id="h-home">{e(texts(h, "h1")[0])}</h1>
      <p class="nu-text nu-text--lead">{e(texts(h, "p")[-1])}</p>
      <a class="nu-button" href="{href("offerings/")}">Explore your options {i("arrow")}</a>
    </div>
    <nav class="nu-hero-film__lineup" aria-label="Happening in November">{posters}</nav>
  </div>
</section>'''
    st = sec("home", 1)
    ps = texts(st, "p")
    pw = sec("home", 2)
    first = texts(pw, "p")[0]
    cut = first.index(" It’s experiential")
    body = f'<section class="st-band" aria-labelledby="h-paths">{statement(first[:cut], first[cut + 1:])}'
    # three pathway blocks: label, title, text, button, image (image order on the live page varies)
    blocks, cur = [], {}
    for c in pw[1:]:
        if c["kind"] == "image":
            cur.setdefault("imgs", []).append(c["local"])
        elif c["kind"] == "p" and "title" not in cur and "label" not in cur:
            cur["label"] = c["text"]
        elif c["kind"] == "h3":
            cur["title"] = c["text"]
        elif c["kind"] == "p":
            cur["text"] = c["text"]
        elif c["kind"] == "button":
            cur["button"] = (c["text"], c["href"])
            blocks.append(cur)
            cur = {}
    imgs = [c["local"] for c in pw if c["kind"] == "image"]
    # Three doors in one ExpandingCards row (22a's research row): the photo and a short name closed, the line and the way in open.
    tags = ["Programs", "Venture portfolio", "Next Up Founders Prize"]
    cards = ""
    for n, b in enumerate(blocks):
        on = "true" if n == 0 else "false"
        cards += f'''<li class="nu-expanding-cards__card" data-mode="dark">
    {pic(imgs[n], "", "fill")}
    <span class="nu-scrim nu-scrim--bottom"></span><span class="nu-scrim nu-scrim--poster"></span>
    <button class="nu-expanding-cards__toggle" type="button" aria-expanded="{on}" aria-controls="pw-{n}"><span class="nu-expanding-cards__tag">{tags[n]}</span></button>
    <div class="nu-expanding-cards__body" id="pw-{n}">
      <h3 class="nu-heading nu-heading--h3">{e(b["title"])}</h3>
      <p class="nu-text">{e(b["text"])}</p>
      <a class="nu-arrow-link" href="{href(local(b["button"][1]))}">{e("About the prize" if n == 2 else b["button"][0])} {i("arrow")}</a>
    </div>
  </li>'''
    body += f'<h2 class="u-vh" id="h-paths">Where to start</h2><ul class="nu-expanding-cards ge-paths" data-ge-cards>{cards}</ul></section>'
    # The network on Night: what the ecosystem is, the 14 campuses on the map, the figures, then the recognition it has earned.
    stats = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--xl">{e(v)}</p><p class="nu-stat__text">{e(l)}</p></div>' for v, l in zip(ps[1::2], ps[2::2]))
    network = section_header(clean(texts(st, "h2")[0]), ps[0], hid="h-stats") + f'<div class="ge-network__map">{campus_map()}</div><div class="nu-stat-band"><div class="nu-stat-band__stats">{stats}</div></div>'
    # founders
    fo = sec("home", 3)
    people, cur = [], None
    for c in fo[1:]:
        if c["kind"] == "image":
            cur = {"img": c["local"], "p": []}
            people.append(cur)
        elif c["kind"] == "p" and cur is not None:
            cur["p"].append(c["text"])
        elif c["kind"] == "button" and cur is not None and c.get("href"):
            cur["href"] = c["href"]
    cards = ""
    for pr in people:
        name, role, story = pr["p"][0], pr["p"][1].replace("\n", " · "), pr["p"][2]
        cards += f'''<li><article class="nu-person-card st-founder">
  <span class="nu-person-card__media">{pic(pr["img"], "", "4x5")}</span>
  <div class="nu-person-card__body">
    <h3 class="nu-heading nu-heading--h4"><a class="nu-person-card__link" href="{e(pr["href"])}">{e(name)}</a></h3>
    <p class="nu-text nu-text--small nu-person-card__title">{e(role)}</p>
    <p class="nu-text nu-text--small">{e(story)}</p>
    <span class="nu-arrow-link nu-arrow-link--sm nu-arrow-link--external" aria-hidden="true">Read the story {i("external")}</span>
  </div>
</article></li>'''
    founders = band(section_header(texts(fo, "h2")[0], hid="h-founders") + f'<ul class="st-program-grid" role="list">{cards}</ul>')
    # awards: white marks, so they sit in the Night network band
    aw = sec("home", 4)
    awards, cur = [], None
    for c in aw:
        if c["kind"] == "image":
            cur = {"img": c["local"], "p": []}
            awards.append(cur)
        elif c["kind"] == "p" and cur is not None:
            cur["p"].append(c["text"])
    tiles = "".join(f'''<li class="st-award"><img class="st-award__mark" src="{{{{base}}}}assets/img/{asset(a["img"], logo=True)}" alt="{e(a["p"][1])}" loading="lazy">
  <p class="nu-text"><strong>{e(a["p"][0].rstrip(":"))}</strong></p><p class="nu-text nu-text--small">{e(a["p"][1])}</p></li>''' for a in awards)
    body += f'''<section class="st-band ge-network" data-mode="dark" aria-labelledby="h-stats">{network}
  <div class="ge-network__awards">{section_header("Recognition", hid="h-awards", split=False)}<ul class="st-awards__list" role="list">{tiles}</ul></div>
</section>''' + founders
    site.page("", UNIT, PAGES["home"]["meta_description"], body, "", hero)


# ---------- 300 Startup Hub ----------
def hub():
    intro = sec("300-startup-hub", 1)
    ops = sec("300-startup-hub", 6)
    hours = [x.strip() for x in texts(ops, "p")[0].split("\n") if x.strip() and x.strip() != "Hours of Operation"]
    addr = texts(ops, "p")[2].split("\n")
    # VenueHeader: the 300 mark as the H1 over the hall, the statement, the tour, then address, hours and the way in on the first screen.
    hero = f'''<header class="nu-venue-header" data-mode="dark">
  <div class="nu-venue-header__stage">
    <div class="nu-venue-header__media">
      {pic(HALL, "", "fill")}
      <span class="nu-scrim nu-scrim--left"></span><span class="nu-scrim nu-scrim--scene"></span><span class="nu-scrim nu-scrim--grain"></span><span class="nu-scrim nu-scrim--full nu-venue-header__phone-scrim"></span>
    </div>
    <div class="nu-venue-header__copy">
      {breadcrumb([(UNIT, "")], "300 Startup Hub")}
      <h1 class="nu-venue-header__title"><img class="nu-venue-header__mark" src="{mark(sec("300-startup-hub", 0)[0]["local"])}" alt="300 Startup Hub Boston"></h1>
      <p class="nu-text nu-text--lead">{e(clean(texts(intro, "h3")[0]))}</p>
      <a class="nu-button" href="#tour">Tour the space {i("arrow")}</a>
    </div>
  </div>
  <dl class="nu-key-value nu-venue-header__facts">
    <div class="nu-key-value__row"><dt>{i("location")}Address</dt><dd>{e(addr[0])}<span>{e(addr[1].replace("-5000", ""))}</span></dd></div>
    <div class="nu-key-value__row"><dt>{i("clock")}Hours</dt><dd>{e(hours[0].rstrip(":").replace(" – ", "–"))}, {e(hours[1]).replace(" – ", "–")}<span>{e(hours[2]).replace(":", ",", 1).replace(" – ", "–")}</span></dd></div>
    <div class="nu-key-value__row"><dt>{i("globe")}Getting here</dt><dd>{e(texts(ops, "p")[1].replace("Entrance", "entrance"))}<span>{e(next(x for x in texts(ops, "p") if x.startswith("No on-site")).rstrip("."))}</span></dd></div>
  </dl>
</header>'''
    # The Founders Network: what membership connects you to, as claim rows on the reading edge.
    vals = sec("300-startup-hub", 2)
    pairs = list(zip(texts(vals, "h3"), texts(vals, "p")))
    points = "".join(f'<li class="nu-point-list__item"><h3 class="nu-heading nu-heading--h4 nu-point-list__claim">{e(clean(h))}</h3><p class="nu-text nu-point-list__body">{e(p)}</p></li>' for h, p in pairs)
    body = band(section_header("Northeastern’s Founders Network", texts(intro, "p")[0], hid="h-network-fn")
                + f'<section class="nu-point-list" aria-labelledby="h-network-fn"><ul class="nu-point-list__items">{points}</ul></section>')
    # The workspace: the four kinds of space as a 2x2 SpaceMosaic (photo, name, one line).
    ws = sec("300-startup-hub", 3)
    labels, paras, imgs = texts(ws, "text")[1:], texts(ws, "p")[1:], [(c["local"], c.get("alt") or "") for c in ws if c["kind"] == "image"]
    tiles = "".join(f'''<li><figure class="nu-figure">{pic(imgs[n][0], imgs[n][1])}
    <figcaption class="nu-space-mosaic__caption"><h3 class="nu-heading nu-heading--h4">{e(labels[n])}</h3><p class="nu-text">{e(paras[n])}</p></figcaption></figure></li>''' for n in range(len(labels)))
    body += band(section_header(clean(texts(ws, "h2")[0]), texts(ws, "p")[0], hid="h-space") + f'<ul class="nu-space-mosaic">{tiles}</ul>')
    # The 300 network: the other hubs, on Night (the page's one feature band after the opener).
    nw = sec("300-startup-hub", 4)
    rows = ""
    for c in nw:
        if c["kind"] == "link":
            m = re.match(r"(300 Startup Hub \| \w+)\s+(.*?)\s*→?$", clean(c["text"]))
            rows += link_row(m.group(1).replace(" | ", " "), c["href"], m.group(2), "Visit", external=True)
    for h, p in zip(texts(nw, "h3"), texts(nw, "p")[2:]):
        rows += f'<article class="nu-link-row st-link-row--static"><h3 class="nu-heading nu-heading--h3 nu-link-row__title">{e(h.replace(" | ", " "))}</h3><div class="nu-link-row__body"><p class="nu-text">{e(p)}</p><span class="nu-tag">Coming soon</span></div></article>'
    body += f'<section class="st-band" data-mode="dark" aria-labelledby="h-network">{section_header(texts(nw, "h2")[0], clean(texts(nw, "p")[1]), hid="h-network")}<div class="st-rows">{rows}</div></section>'
    body += f'<section class="st-band" id="tour" aria-label="Tour the space">{staging_form(texts(sec("300-startup-hub", 5), "h3")[0], "hub")}</section>'
    body += band(grouped_accordion("Directions and parking", "h-ops", accordion(directions(ops), "hub-dir")))
    site.page("300-startup-hub", "300 Startup Hub Boston", clean(texts(intro, "h3")[0]), body, "300-startup-hub/", hero)


# ---------- Launch Week open house (event) ----------
SESSION_TITLES = {  # the live agenda is in Title Case; the system sets sentence case
    "Interactive Showcase of Global Entrepreneurship at Northeastern": "Interactive showcase of global entrepreneurship at Northeastern",
    "Brewing Connections": "Brewing connections",
    "From Lab to Launch: Commercialization Broken Down": "From lab to launch: commercialization broken down",
    "Inside the Creator Economy: Brands, Audiences, and Businesses": "Inside the creator economy: brands, audiences, and businesses",
    "Leaders @300: It’s Never Been Easier to Start a Company, and Never Been Harder to Scale One": "Leaders @300: It’s never been easier to start a company, and never been harder to scale one",
    "The Quantum Opportunity: Building the Next Generation of Startups": "The quantum opportunity: building the next generation of startups",
    "How to Raise Venture Capital: The Real Rules of How Investors Actually Think": "How to raise venture capital: the real rules of how investors actually think",
    "Hackathon Finals": "Hackathon finals",
}


def speaker(p):
    """'Name, role' agenda lines to (name, role); a class year (DMSB’76, E’26) stays with the name."""
    lead = ""
    for pre, lab in (("With ", ""), ("Facilitated by ", "Facilitator; ")):
        if p.startswith(pre):
            p, lead = p[len(pre):], lab
    name, _, role = p.partition(", ")
    m = re.match(r"^([A-Z]+’\d\d), (.*)$", role)
    if m:
        name, role = f"{name} {m.group(1)}", m.group(2)
    role = lead + role[:1].upper() + role[1:] if not lead else lead + role
    return name, role


def speakers_html(people):
    return '<ul class="nu-timeline-item__speakers">' + "".join(
        f'<li class="nu-timeline-item__speaker"><span class="nu-timeline-item__speaker-name">{e(n)}</span><span class="nu-timeline-item__speaker-role">{e(r)}</span></li>' for n, r in people) + "</ul>"


def open_house():
    top = sec("300-mass-ave-open-house", 1)
    reg = next(c["href"] for c in top if c["kind"] == "link")
    meta = f'''<ul class="nu-meta-list st-hero-meta">
  <li>{i("calendar")}<time datetime="2026-11-18">November 18–19, 2026</time></li>
  <li>{i("clock")}<span>9 a.m.–6 p.m.</span></li>
  <li>{i("location")}<span>{e(texts(top, "p")[0])}</span></li>
</ul>'''
    hero = hero_page("300 Mass Ave. Launch Week open house", asset(sec("300-mass-ave-open-house", 0)[0]["local"]))
    hero = hero.replace("</h1>", "</h1>" + meta, 1).replace("</div>\n</section>", f'<a class="nu-button nu-button--accent" href="{e(reg)}">Register now {i("external")}</a></div>\n</section>', 1)
    # Statement: the page's own line as the pull-line, the launch paragraph as its lead.
    body = f'<section class="st-band" aria-label="About Launch Week">{statement(texts(top, "text")[0], texts(top, "p")[1])}</section>'
    ag = sec("300-mass-ave-open-house", 2)
    days, cur, item = [], None, None
    for c in ag[3:]:
        k, t = c["kind"], c.get("text", "")
        if k == "h3":
            cur = {"day": t, "items": []}
            days.append(cur)
        elif k == "text" and re.match(r"^(All day|\d)", t):
            item = {"time": t, "tag": None, "title": None, "p": []}
            cur["items"].append(item)
        elif k == "text":
            item["tag"] = t
        elif k == "h4":
            item["title"] = t
        elif k == "p":
            item["p"].append(t)
    dates = {"Wednesday, November 18": "2026-11-18", "Thursday, November 19": "2026-11-19"}
    dhtml = ""
    for d in days:
        lis = ""
        for it in d["items"]:
            title = SESSION_TITLES.get(it["title"], it["title"])
            tag, featured, text, people = "", False, "", []
            if it["tag"] == "Featured event":
                featured = True
                tag = '<span class="nu-tag nu-tag--solid">Featured event</span>'
                m = re.match(r"A conversation with (.+?), (.+?), (on .*)$", it["p"][0])
                people = [(m.group(1), m.group(2)[:1].upper() + m.group(2)[1:])]
                text = "A conversation " + m.group(3)
            elif it["tag"]:
                tag = f'<span class="nu-tag">{e(it["tag"][:1] + it["tag"][1:].lower())}</span>'
                for p in it["p"]:
                    p, _, rest = p.partition(" on what ")  # one speaker line carries the session’s description
                    people.append(speaker(p))
                    if rest:
                        text = "On what " + rest
            else:
                text = " ".join(it["p"])
            hcls = "nu-heading--h3" if featured else "nu-heading--h4"
            lis += f'''<li class="nu-timeline-item{" nu-timeline-item--featured" if featured else ""}"{' id="leaders-300"' if featured else ""}><span class="nu-timeline-item__date">{e(it["time"])}</span><span class="nu-timeline-item__rail" aria-hidden="true"></span>
  <div class="nu-timeline-item__body"><h4 class="nu-heading {hcls}">{e(title)}</h4>{tag}{f'<p class="nu-text">{e(text)}</p>' if text else ""}{speakers_html(people) if people else ""}</div></li>'''
        dhtml += f'<div class="nu-timeline__day"><h3 class="nu-heading nu-heading--h4 nu-timeline__day-title"><time datetime="{dates.get(d["day"], "")}">{e(d["day"])}</time></h3><ol class="nu-timeline__list">{lis}</ol></div>'
    body += f'''<section class="st-band" id="agenda"><section class="nu-timeline nu-timeline--agenda" aria-labelledby="h-agenda">
  <div class="nu-timeline__head"><h2 class="nu-heading nu-heading--h2" id="h-agenda">{e(texts(ag, "h2")[0])}</h2><p class="nu-text">{e(texts(ag, "p")[1])}</p></div>
  <div class="nu-timeline__days">{dhtml}</div>
</section></section>'''
    fx = sec("300-mass-ave-open-house", 3)
    ps, lis = texts(fx, "p"), texts(fx, "li")
    topics, hack = lis[:10], lis[10:]
    # 300 Connect: its own chapter, heading in columns 1–4, everything else on the reading edge.
    connect_body = f'''<ul class="nu-meta-list nu-meta-list--inline"><li>{i("calendar")}<time datetime="2026-11-19T09:00">November 19, 9–11 a.m.</time></li><li>Open to all founders</li></ul>
  <p class="nu-text">{e(ps[2])} {e(ps[3])}</p>
  <h3 class="nu-heading nu-heading--h4">{e(texts(fx, "h3")[1])}</h3><p class="nu-text">{e(ps[4])}</p>
  <ul class="st-tags" role="list">{"".join(f'<li><span class="nu-tag">{e(t)}</span></li>' for t in topics)}</ul>
  <p class="nu-text nu-text--small">{e(ps[5])}</p>'''
    body += band(section_header(e(texts(fx, "h2")[0]), hid="h-connect", extra=connect_body), "ge-chapter")
    # Hackathon: its own chapter as an index Timeline; the SCION co-brand, the deadline and the action in the head.
    labels = {"CLOCK STARTS": "Clock starts", "WHEEL OF PITCHES": "Wheel of Pitches", "PRACTICE DEMOS": "Practice demos",
              "DEMO DAY 1.0": "Demo Day 1.0", "THE 300 OPEN HOUSE": "The 300 open house"}
    rows = ""
    for t in hack:
        m = re.match(r"^(Nov\s\d+(?:–\d+)?)([A-Z0-9 .]+)((?:[A-Z][a-z]|A\s).*)$", " ".join(t.split()))
        d, label, desc = m.group(1), labels[m.group(2).strip()], m.group(3)
        rows += f'<li class="nu-timeline-item"><span class="nu-timeline-item__date">{e(d)}</span><span class="nu-timeline-item__rail" aria-hidden="true"></span><div class="nu-timeline-item__body"><h3 class="nu-heading nu-heading--h4">{e(label)}</h3><p class="nu-text">{e(desc)}</p></div></li>'
    apply = next(c for c in fx if c["kind"] == "link")
    logo = next(c["local"] for c in fx if c["kind"] == "image")
    body += f'''<section class="st-band ge-chapter" aria-labelledby="h-hack"><section class="nu-timeline nu-timeline--index" aria-labelledby="h-hack" id="hackathon">
  <div class="nu-timeline__head">
    <h2 class="nu-heading nu-heading--h2" id="h-hack">{e(texts(fx, "h2")[1])}</h2>
    <p class="nu-text nu-text--lead">{e(ps[6])}</p>
    <p class="nu-text">{e(ps[7])}</p>
    <div class="nu-logo-tile ge-cobrand"><img class="nu-logo-tile__mark" src="{mark(logo, 800)}" alt="Northeastern University and SCION Events"></div>
    <p class="nu-text nu-text--small">{e(ps[8])}</p>
    {button("Apply to build", apply["href"])}
  </div>
  <ol class="nu-timeline__list">{rows}</ol>
</section></section>'''
    cta = sec("300-mass-ave-open-house", 4)
    body += f'''<section class="nu-action-band" data-mode="dark" aria-labelledby="h-join">
  <div class="nu-action-band__inner">
    <div class="nu-action-band__copy"><h2 class="nu-heading nu-heading--h1" id="h-join">{e(texts(cta, "h2")[0])}</h2><p class="nu-text nu-text--lead">{e(texts(cta, "p")[0]).replace(chr(10), "<br>")}</p></div>
    <div class="nu-action-band__actions"><a class="nu-button nu-button--accent" href="{e(reg)}">Register now {i("external")}</a></div>
  </div>
</section>'''
    pk = sec("300-mass-ave-open-house", 5)
    ps = texts(pk, "p")
    q = next(p for p in ps if p.startswith("Contact "))
    m = re.match(r"Contact (.*?), (.*?): (\S+@\S+)", q)
    body += f'''<section class="st-band" aria-labelledby="h-park">
  {grouped_accordion("Parking and directions", "h-park", accordion(directions(pk), "oh-dir"))}
  <section class="nu-contact-block" aria-labelledby="h-q">
    <div class="nu-contact-block__label"><h2 class="nu-heading nu-heading--h4" id="h-q">Questions?</h2><p class="nu-text nu-text--small">{e(m.group(1))}, {e(m.group(2))}</p></div>
    <div class="nu-contact-block__body"><div class="nu-contact-block__items">{contact_items(email=m.group(3))}</div>
      {"".join(f'<p class="nu-text nu-text--small st-fine">{e(p)}</p>' for p in ps if p.startswith(("There may be", "Event registration")))}</div>
  </section>
</section>'''
    site.page("300-mass-ave-open-house", "300 Mass Ave. Launch Week", texts(top, "p")[1][:155], body, "300-mass-ave-open-house/", hero)


# ---------- Next Up Founders Prize (campaign) ----------
NU = "ventures/next-up-2026/"


NU_PAGES = [("Overview", NU), ("How it works", NU + "#h-how"), ("Dates", NU + "#h-dates"), ("FAQ", NU + "#h-faq"),
            ("Rules", NU + "program-parameters-rules/"), ("Application guide", NU + "application-guide/")]


def nu_nav(current):
    """SiblingNav (SectionNav --horizontal): the campaign's own pages and chapters, the same row on every Next Up page."""
    lis = "".join(f'<li><a class="nu-section-nav__link nu-nav-link" href="{href(u)}"{CUR if u == current else ""}>{e(l)}</a></li>' for l, u in NU_PAGES)
    return f'''<div class="ge-sibling"><nav class="nu-section-nav nu-section-nav--horizontal" aria-label="Next Up Founders Prize">
  <p class="nu-text nu-text--meta nu-section-nav__label">Next Up Founders Prize</p><ul class="nu-section-nav__list">{lis}</ul>
</nav></div>'''


def next_up():
    h = sec("ventures__next-up-2026", 0)
    hp = texts(h, "p")
    st = texts(sec("ventures__next-up-2026", 1), "p")
    # Campaign template: Night opens with the campaign's own lockup over the line, the status Tag and the headline figure over its facts;
    # the status Notice closes the opening. The Submission page folds into the Notice (its URL redirects here).
    sentences = [x.strip() for x in hp[1].split(". ") if x.strip()]
    lead = sentences[0] + "."
    facts = key_values([(st[1], st[2].replace("\n", " ")), (st[3], st[4].replace("\n", " ")), (st[5], (st[6] + " " + st[7]).replace("\n", " "))], "nu-key-value--inline")
    opener = f'''<header class="nu-hero-title" data-mode="dark">
  <div class="nu-hero-title__main">
    {breadcrumb([(UNIT, "")], "Next Up Founders Prize")}
    <img class="nu-hero-title__mark" src="{mark(h[0]["local"])}" alt="Northeastern University Next Up Founders Prize">
    <h1 class="nu-heading nu-heading--h1">Your first venture. Before your first semester.</h1>
    <p class="nu-text nu-text--lead">{e(lead)}</p>
    <ul class="nu-meta-list nu-meta-list--inline"><li><span class="nu-tag nu-tag--closed">2026 applications closed</span></li><li>Finals <time datetime="2026-11-17/2026-11-20">November 17–20</time></li></ul>
  </div>
  <div class="nu-hero-title__facts">
    <div class="nu-stat nu-hero-title__figure"><p class="nu-numeral nu-numeral--xl"><span class="nu-hero-title__qualifier">Up to</span>$100K</p><p class="nu-stat__text">{e(st[0])}</p></div>
    {facts}
  </div>
  <hr class="nu-rule nu-hero-title__rule">
</header>
<div class="nu-campaign__status" data-mode="dark" id="status">
  <div class="nu-notice nu-notice--info" role="status">{i("info").replace('class="nu-icon"', 'class="nu-icon nu-notice__icon"')}<div class="nu-notice__body"><p class="nu-notice__title">Applications for 2026 closed on September 30</p><p class="nu-text nu-text--small">{e(hp[0])}</p><a class="nu-arrow-link nu-arrow-link--sm" href="#h-dates">What happens next {i("arrow")}</a></div></div>
</div>'''
    rest = "".join(f"<p class=\"nu-text\">{e(x)}{'' if x.endswith('.') else '.'}</p>" for x in sentences[1:])
    about = f'<section class="nu-campaign__band" aria-labelledby="h-about">{section_header("About the prize", hid="h-about", extra=rest)}</section>'
    net = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--md">{e(v)}</p><p class="nu-stat__text">{e(l)}</p></div>' for v, l in zip(st[9::2], st[10::2]))
    body = opener + nu_nav(NU) + about
    # Four figures need the full width at Numeral md (the --lead form leaves them too little room for 2,600+ and $900M+).
    body += f'<section class="nu-campaign__band" aria-labelledby="h-net">{section_header(e(st[8]), hid="h-net", split=False)}<div class="nu-stat-band"><div class="nu-stat-band__stats">{net}</div></div></section>'
    # Who can enter: the short label is the heading, the long sentence the lead, and the rows start level with the heading.
    el = sec("ventures__next-up-2026", 2)
    ep = texts(el, "p")
    rows = key_values([(k[:1].upper() + k[1:], v) for k, v in zip(ep[2::2], ep[3::2])], "nu-key-value--inline")
    body += f'''<section class="nu-campaign__band" aria-labelledby="h-elig"><div class="nu-campaign__index">
  <div class="nu-campaign__index-head"><h2 class="nu-heading nu-heading--h2" id="h-elig">{e(ep[0])}</h2><p class="nu-text nu-text--lead">{e(clean(texts(el, "h3")[0]))}</p><p class="nu-text">{e(ep[1])}</p></div>
  {rows}
</div></section>'''
    # How it works, closed: steps 1–4 are behind every entrant; step 5 (semifinals, then the Boston finals) is where the prize is now.
    hw = sec("ventures__next-up-2026", 3)
    pairs = list(zip(texts(hw, "h3")[1:], texts(hw, "p")[1:]))
    now = ' aria-current="step"'
    steps = "".join(f'<li class="nu-step nu-step--row"{now if n == len(pairs) - 1 else ""}><span class="nu-numeral nu-numeral--md nu-step__numeral" aria-hidden="true">{n + 1}</span><h3 class="nu-heading nu-heading--h4">{e(sentence(t))}</h3><p class="nu-text">{e(p)}</p></li>'
                    for n, (t, p) in enumerate(pairs))
    body += f'''<section class="nu-campaign__band"><section class="nu-steps nu-steps--rows ge-steps--closed" aria-labelledby="h-how">
  <div class="nu-steps__head"><h2 class="nu-heading nu-heading--h2" id="h-how">How it works</h2><p class="nu-text">{e(texts(hw, "h3")[0])}</p></div>
  <ol class="nu-steps__list">{steps}</ol>
</section></section>'''
    # Important dates as a status Timeline: prose dates under the titles, led by Done, Now or Next (as of late October 2026).
    dt = sec("ventures__next-up-2026", 4)
    dp = texts(dt, "p")
    stages = [("Applications closed", '<time datetime="2026-09-30">September 30</time>', "Done")]
    stages += [(k.replace("Celebration", "celebration"), e(v), s) for (k, v), s in zip(zip(dp[1::2], dp[2::2]), ["Now", "Next", "Next"])]
    tl = "".join(f'<li class="nu-timeline-item"{now if s == "Now" else ""}><span class="nu-timeline-item__rail" aria-hidden="true"></span><div class="nu-timeline-item__body"><h3 class="nu-heading nu-heading--h4">{e(k)}</h3><p class="nu-timeline-item__date"><span class="nu-timeline__status">{s}</span>{v}</p></div></li>'
                 for k, v, s in stages)
    body += f'''<section class="nu-campaign__band"><section class="nu-timeline nu-timeline--index nu-timeline--status" aria-labelledby="h-dates">
  <div class="nu-timeline__head"><h2 class="nu-heading nu-heading--h2" id="h-dates">Important dates</h2><p class="nu-timeline__note">{e(texts(dt, "h3")[0])}</p></div>
  <ol class="nu-timeline__list">{tl}</ol>
</section></section>'''
    fq = sec("ventures__next-up-2026", 5)
    groups = [("General", [])]
    seq = [c for c in fq if c["kind"] in ("p", "separator")]
    k = 0
    while k < len(seq):
        c = seq[k]
        if c["kind"] == "p":
            nxt = seq[k + 1] if k + 1 < len(seq) else None
            if nxt and nxt["kind"] == "p":
                groups[-1][1].append((c["text"], [nxt["text"]]))
                k += 2
                continue
            groups.append((c["text"], []))
        k += 1
    gh = "".join(f'<div class="nu-accordion__group"><h3 class="nu-heading nu-heading--h4 nu-accordion__group-title">{e(g)}</h3><div class="nu-accordion__items">{accordion(items, "faq" + str(n))}</div></div>' for n, (g, items) in enumerate(groups) if items)
    body += f'''<section class="nu-campaign__band"><section class="nu-accordion" aria-labelledby="h-faq">
  <div class="nu-accordion__head"><h2 class="nu-heading nu-heading--h2" id="h-faq">FAQ</h2></div>
  <div class="nu-accordion__groups">{gh}</div>
</section></section>'''
    site.page("ventures/next-up-2026", "Next Up Founders Prize 2026", hp[1][:155], f'<div class="nu-campaign">{body}</div>', NU)


def sentence(t):
    """Title Case headings to sentence case, keeping acronyms."""
    keep = {"Boston", "Northeastern", "Global", "Entrepreneurship", "Week"}  # proper nouns stay capitalised
    words = t.split()
    return " ".join(w if (n == 0 or (w.isupper() and len(w) > 1) or w.strip(",.") in keep) else w.lower() for n, w in enumerate(words))


def rules():
    top = sec("ventures__next-up-2026__program-parameters-rules", 0)
    ps = texts(sec("ventures__next-up-2026__program-parameters-rules", 1), "p")
    prose, toc = "", []
    for p in ps:
        m = re.match(r"^(\d+)\.?\s+(.*)$", p)
        if m and len(p) < 70:
            aid = f"clause-{m.group(1)}"
            toc.append((aid, m.group(1) + ".", sentence(m.group(2))))
            prose += f'<h2 id="{aid}"><span class="ge-clause-num">{m.group(1)}.</span>{e(sentence(m.group(2)))}</h2>'
        elif re.match(r"^[a-z]\.\s", p) or re.match(r"^i\.", p):
            prose += f'<p class="st-clause">{e(p).replace(chr(10), "<br>")}</p>'
        else:
            prose += f"<p>{e(p).replace(chr(10), '<br>')}</p>"
    tp = texts(top, "p")
    body = hero_title("Official rules", tp[1], [(UNIT, ""), ("Next Up Founders Prize", NU)]) + nu_nav(NU + "program-parameters-rules/") + document(prose, toc)
    site.page("ventures/next-up-2026/program-parameters-rules", "Official rules · Next Up Founders Prize", tp[1], body, NU)


def guide():
    s = sec("ventures__next-up-2026__application-guide", 1)
    prose, in_list, toc = "", False, []
    for c in s:
        k, t = c["kind"], c.get("text", "")
        if k != "li" and in_list:
            prose += "</ul>"
            in_list = False
        if k == "h3":
            aid = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
            toc.append((aid, "", sentence(t)))
            prose += f'<h2 id="{aid}">{e(sentence(t))}</h2>'
        elif k == "h4":
            prose += f"<h3>{e(sentence(t))}</h3>"
        elif k == "li":
            if not in_list:
                prose += "<ul>"
                in_list = True
            prose += f"<li>{e(t)}</li>"
        elif k in ("p", "text") and t.strip():
            for para in t.split("\n\n"):
                if para.strip() and not set(para.strip()) <= set("—–-"):
                    prose += f"<p>{e(para.strip())}</p>"
    if in_list:
        prose += "</ul>"
    body = hero_title("Application guide", "Next Up Founders Prize", [(UNIT, ""), ("Next Up Founders Prize", NU)]) + nu_nav(NU + "application-guide/") + document(prose, toc)
    site.page("ventures/next-up-2026/application-guide", "Application guide · Next Up Founders Prize", "How to apply to the Next Up Founders Prize.", body, NU)


def submission():
    """Folded into the Overview's status Notice (ge-08): applications are closed, so the old URL redirects there."""
    out = site.out / "ventures/next-up-2026/submission/index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">
<title>Next Up Founders Prize · Entrepreneurship · Northeastern University</title>
<link rel="canonical" href="../"><meta http-equiv="refresh" content="0; url=../#status"></head>
<body><p>Applications for the 2026 Next Up Founders Prize are closed. <a href="../#status">Go to the Next Up Founders Prize</a>.</p></body></html>
''')


# ---------- events: Global Entrepreneurship Week, then what's coming up (the 2023 archive is dropped) ----------
def series_event(time, title, url, part_of, tba=False):
    ext = url.startswith("http")
    return (f'<li class="nu-event-series__event{" nu-event-series__event--tba" if tba else ""}"><p class="nu-event-series__time">{e(time)}</p>'
            f'<h4 class="nu-heading nu-heading--h4"><a class="nu-event-series__link" href="{href(url)}">{e(title)}</a>{i("external" if ext else "arrow")}</h4>'
            f'<p class="nu-text nu-text--meta">{e(part_of)}</p></li>')


def series_day(iso, month, day, weekday, events_html, all_week=False):
    pre = '<span class="u-vh">All week, </span>' if all_week else ""
    return (f'<li class="nu-event-series__day"><h3 class="nu-heading nu-heading--h4">{pre}<time class="nu-date-block" datetime="{iso}">'
            f'<span class="nu-date-block__month">{month}</span><span class="nu-date-block__day">{day}</span><span class="nu-date-block__weekday">{weekday}</span></time></h3>'
            f'<ul class="nu-event-series__events">{events_html}</ul></li>')


def event_card(iso, month, day, label, title, url, meta, tags):
    lis = "".join(f'<li>{i(ic)}<span>{e(t)}</span></li>' for ic, t in meta)
    return f'''<li><article class="nu-event-card">
  <time class="nu-date-block" datetime="{iso}" aria-label="{e(label)}"><span class="nu-date-block__month">{month}</span><span class="nu-date-block__day">{day}</span></time>
  <div class="nu-event-card__body">
    <h3 class="nu-heading nu-heading--h4"><a class="nu-event-card__link" href="{href(url)}">{e(title)}</a></h3>
    <ul class="nu-meta-list">{lis}</ul>
    <div class="nu-event-card__tags">{"".join(f'<span class="nu-tag">{e(t)}</span>' for t in tags)}</div>
  </div>
</article></li>'''


def events():
    h = sec("events", 0)
    lw = "300 Mass Ave. Launch Week"
    hack = LAUNCH + "#h-hack"
    # Every event here is on the live Launch Week agenda, the hackathon timeline or the Next Up dates.
    days = series_day("2026-11-17/2026-11-20", "Nov", "17–20", "All week",
                      series_event("Day to be announced", "Next Up Founders Prize finals", NU + "#h-dates", "High school founders pitch in Boston or by video", tba=True), True)
    days += series_day("2026-11-18", "Nov", "18", "Wednesday", "".join(series_event(*x) for x in [
        ("All day", "Interactive showcase of global entrepreneurship", LAUNCH + "#agenda", lw),
        ("10 a.m.", "From lab to launch: commercialization broken down", LAUNCH + "#agenda", lw),
        ("3:30 p.m.", "Leaders @300 with Brian Halligan", LAUNCH + "#leaders-300", lw),
        ("All day", "Hackathon Demo Day 2.0", hack, "Co-hosted with SCION")]))
    days += series_day("2026-11-19", "Nov", "19", "Thursday", "".join(series_event(*x) for x in [
        ("9–11 a.m.", "300 Connect: Live", LAUNCH + "#h-connect", lw),
        ("3 p.m.", "How to raise venture capital", LAUNCH + "#agenda", lw),
        ("4:30 p.m.", "Hackathon finals", hack, "Co-hosted with SCION")]))
    gew = f'''<section class="nu-event-series" aria-labelledby="h-gew">
  <header class="nu-event-series__head">
    <h2 class="nu-heading nu-heading--h2" id="h-gew">Global Entrepreneurship Week</h2>
    <div class="nu-event-series__intro">
      <p class="nu-event-series__dates"><time datetime="2026-11-17/2026-11-20">November 17–20, 2026</time></p>
      <p class="nu-text nu-text--lead">Launch Week at 300 Mass Ave., the hackathon finals and the Next Up Founders Prize finals, in one week in Boston.</p>
      <a class="nu-arrow-link nu-arrow-link--external" href="https://luma.com/eship">Events on Luma<span class="u-vh">, on another site</span>{i("external")}</a>
    </div>
  </header>
  <ol class="nu-event-series__days">{days}</ol>
</section>'''
    cards = "".join(event_card(*x) for x in [
        ("2026-11-12", "Nov", "12", "November 12 to 19, 2026", "300 Hackathon", hack,
         [("calendar", "November 12–19, 2026"), ("clock", "Applications close Sunday, November 1, at 11:59 p.m."), ("location", "300 Massachusetts Ave., Boston")], ["Students"]),
        ("2026-11-17", "Nov", "17", "November 17 to 20, 2026", "Next Up Founders Prize finals", NU,
         [("calendar", "Between November 17 and 20, 2026"), ("location", "Boston campus, or by video")], ["High school founders"]),
        ("2026-11-18", "Nov", "18", "November 18 to 19, 2026", "300 Mass Ave. Launch Week open house", LAUNCH,
         [("calendar", "November 18–19, 2026"), ("clock", "9 a.m.–6 p.m."), ("location", "300 Massachusetts Ave., Boston")], ["Open to all"])])
    upcoming = f'''<section class="nu-event-list" aria-labelledby="h-up">
  <div class="nu-event-list__head"><h2 class="nu-heading nu-heading--h2" id="h-up">Coming up</h2></div>
  <div class="nu-event-list__months">
    <section class="nu-event-list__month" aria-labelledby="m-2026-11">
      <div class="nu-event-list__month-head"><h3 class="nu-heading nu-heading--h3" id="m-2026-11">November</h3><p class="nu-event-list__count">3 events</p></div>
      <ul class="nu-event-list__events" role="list">{cards}</ul>
    </section>
  </div>
</section>
<div class="st-actions">{arrow("The full calendar on Luma", "https://luma.com/eship")}</div>'''
    hero = hero_page(clean(texts(h, "h1")[0]), asset(h[0]["local"]), None, [(UNIT, "")])
    body = band(gew) + band(upcoming)
    site.page("events", "Events", "Global Entrepreneurship Week and entrepreneurship events across Northeastern’s global network.", body, "events/", hero)


def contact():
    s = sec("contact-us", 0)
    site.page("contact-us", "Get involved", "Let us know what you’re working on.", hero_title("Get involved", None, [(UNIT, "")]) + band(staging_form(clean(texts(s, "h2")[0]), "ct")), "contact-us/")


def main():
    for fn in (home, offerings, portfolio, hub, open_house, next_up, rules, guide, submission, events, contact):
        fn()
    not_found(site, [("Home", "", "Entrepreneurship at Northeastern."), ("Programs and offerings", "offerings/", "Funding, networking, accelerators and more."),
                     ("Venture portfolio", "ventures/portfolio/", "The companies built in Northeastern’s ecosystem."), ("Get involved", "contact-us/", "Tell us what you’re working on.")])
    site.finish()


if __name__ == "__main__":
    main()
