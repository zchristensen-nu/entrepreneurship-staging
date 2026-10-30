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
from kit import (Site, band, contact_items, e, hero_page, hero_title, href, i,  # noqa: E402
                 link_row, not_found, section_header)

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
    if max(im.size) > limit:
        im.thumbnail((limit, limit))
    photo = not logo and src.suffix.lower() == ".png" and src.stat().st_size > 400_000 and im.mode in ("RGB", "RGBA", "P")
    if photo:
        name = src.stem + ".jpg"
        im = im.convert("RGB")
    out = OUT_IMG / name
    if not out.exists():
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
def facet(key, label, values, records, getter):
    chips = "".join(f'<button class="nu-chip" type="button" aria-pressed="false" data-filter="{key}" data-value="{e(v)}">{e(v)} <span class="nu-chip-group__count">{sum(v in getter(r) for r in records)}</span></button>' for v in values)
    return f'''<div class="nu-filter-panel__facet"><div class="nu-chip-group" role="group" aria-labelledby="fp-{key}">
  <div class="nu-chip-group__head"><p class="nu-chip-group__label" id="fp-{key}">{e(label)}</p></div>
  <div class="nu-chip-group__chips">{chips}</div></div></div>'''


def finder(title, noun, facets, items_html, list_cls="st-program-grid", page=0):
    return f'''<section class="st-band st-finder" aria-labelledby="finder-h">
  <div class="st-finder__layout">
    <form class="nu-filter-panel nu-filter-panel--sidebar" aria-labelledby="finder-h" data-finder>
      <div class="nu-filter-panel__head"><h2 class="nu-heading nu-heading--h4" id="finder-h">{e(title)}</h2><button class="nu-filter-panel__clear" type="reset">Clear all</button></div>
      {facets}
    </form>
    <div class="st-finder__results">
      <p class="nu-text nu-text--meta" aria-live="polite" data-finder-count data-noun="{noun}">{items_html.count("<li data-terms")} {noun}</p>
      <ul class="{list_cls}" role="list" data-finder-items>{items_html}</ul>
      <p class="nu-text" data-finder-empty hidden>Nothing matches those filters. Clear one to see more.</p>
      {f'<div class="st-actions"><button class="nu-button nu-button--outline" type="button" data-finder-more data-page="{page}">Show more {noun}</button></div>' if page else ""}
    </div>
  </div>
</section>'''


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
      <div class="nu-program-card__tags">{"".join(f'<span class="nu-tag">{e(c)}</span>' for c in p["categories"])}</div>
      <span class="nu-arrow-link nu-arrow-link--sm nu-arrow-link--external nu-program-card__cue" aria-hidden="true">Visit {i("external")}</span>
    </div>
  </div>
</article></li>'''
    facets = "".join(facet(k, l, sorted({t for p in progs for t in p[k]}), progs, lambda r, k=k: r[k]) for k, l in keys)
    body = hero_title(texts(items, "h1")[0], texts(items, "p")[-1], [(UNIT, "")]) + finder("Filter programs", "programs", facets, cards)
    site.page("offerings", "Programs and offerings", texts(items, "p")[-1], body, "offerings/")


def portfolio():
    items = sec("ventures__portfolio", 0)
    vs = sorted(R["partners"], key=lambda p: clean(p["name_as_shown"] or p["title"]).lower())
    rows = ""
    for v in vs:
        name = clean(v["name_as_shown"] or v["title"])
        ind = v.get("industries") or []
        terms = json.dumps({"industries": ind})
        logo = (v.get("logo") or {}).get("local")
        mark = pic(logo, "", "natural", logo=True) if logo else f'<span class="st-venture__initial" aria-hidden="true">{e(name[:1])}</span>'
        site_url = v.get("website") or ""
        bad = (not site_url) or site_url.startswith(LIVE)  # six ventures link to empty pages on the live site
        title = e(name) if bad else f'<a class="st-venture__link" href="{e(site_url)}">{e(name)}</a>'
        rows += f'''<li data-terms='{e(terms)}'><article class="st-venture">
  <span class="st-venture__mark" data-mode="light">{mark}</span>
  <div class="st-venture__body"><h3 class="nu-heading nu-heading--h4">{title}</h3><p class="nu-text nu-text--small">{e(clean(v["description"]))}</p></div>
  <div class="st-venture__meta">{"".join(f'<span class="nu-tag">{e(t)}</span>' for t in ind)}</div>
</article></li>'''
    inds = sorted({t for v in vs for t in v.get("industries") or [] if not t.lower().startswith("lorem")})
    hero = hero_page(texts(items, "h1")[0], items[0]["local"] and asset(items[0]["local"]), texts(items, "p")[-1], [(UNIT, "")])
    hero = hero.replace(f'src="{{{{base}}}}assets/img/{asset(items[0]["local"])}"', f'src="{{{{base}}}}assets/img/{asset(items[0]["local"])}"')
    site.page("ventures/portfolio", "Venture portfolio", texts(items, "p")[-1],
              finder("Filter by industry", "ventures", facet("industries", "Industry", inds, vs, lambda r: r.get("industries") or []), rows, "st-ventures", page=24),
              "ventures/portfolio/", hero)


# ---------- home ----------
def home():
    h = sec("home", 0)
    hero = hero_page(texts(h, "h1")[0], asset(next(c["local"] for c in h if c["kind"] == "image")), texts(h, "p")[-1],
                     button=("Explore your options", "offerings/"))
    st = sec("home", 1)
    ps = texts(st, "p")
    stats = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--xl">{e(v)}</p><p class="nu-stat__text">{e(l)}</p></div>' for v, l in zip(ps[1::2], ps[2::2]))
    body = band(section_header(clean(texts(st, "h2")[0]), ps[0], hid="h-stats") + f'<div class="nu-stat-band"><div class="nu-stat-band__stats">{stats}</div></div>')
    pw = sec("home", 2)
    body += band(f'<p class="st-statement st-statement--body">{e(texts(pw, "p")[0])}</p>', "st-band--statement")
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
    for n, b in enumerate(blocks):
        im = imgs[n]
        body += f'''<section class="nu-media-text{" nu-media-text--reverse" if n % 2 else ""} st-tight" aria-labelledby="pw-{n}">
  <figure class="nu-media-text__media">{pic(im)}</figure>
  <div class="nu-media-text__copy">
    <h2 class="nu-heading nu-heading--h2" id="pw-{n}">{e(b["title"])}</h2>
    <p class="nu-text nu-text--meta">{e(b["label"])}</p>
    <p class="nu-text">{e(b["text"])}</p>
    <div class="nu-media-text__actions">{button(*b["button"])}</div>
  </div>
</section>'''
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
    body += band(section_header(texts(fo, "h2")[0], hid="h-founders") + f'<ul class="st-program-grid" role="list">{cards}</ul>')
    # awards: white marks, so the band is Night
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
    body += f'<section class="st-band st-awards" data-mode="dark" aria-labelledby="h-awards">{section_header("Recognition", hid="h-awards", split=False)}<ul class="st-awards__list" role="list">{tiles}</ul></section>'
    site.page("", UNIT, PAGES["home"]["meta_description"], body, "", hero)


# ---------- 300 Startup Hub ----------
def hub():
    intro = sec("300-startup-hub", 1)
    vals = sec("300-startup-hub", 2)
    pairs = list(zip(texts(vals, "h3"), texts(vals, "p")))
    body = band(f'<p class="st-statement">{e(clean(texts(intro, "h3")[0]))}</p><div class="st-more"><p class="nu-text nu-text--lead">{e(texts(intro, "p")[0])}</p></div>', "st-band--statement")
    body += band('<ul class="st-values" role="list">' + "".join(f'<li><h2 class="nu-heading nu-heading--h3">{e(clean(h))}</h2><p class="nu-text">{e(p)}</p></li>' for h, p in pairs) + "</ul>", "st-band--tight")
    ws = sec("300-startup-hub", 3)
    body += band(section_header(clean(texts(ws, "h2")[0]), texts(ws, "p")[0], hid="h-space"), "st-band--tight")
    labels, heads, paras, imgs = texts(ws, "text")[1:], texts(ws, "h3"), texts(ws, "p")[1:], [(c["local"], c.get("alt") or "") for c in ws if c["kind"] == "image"]
    for n in range(len(heads)):
        body += f'''<section class="nu-media-text{" nu-media-text--reverse" if n % 2 else ""} st-tight" aria-labelledby="ws-{n}">
  <figure class="nu-media-text__media">{pic(imgs[n][0], imgs[n][1])}</figure>
  <div class="nu-media-text__copy"><h3 class="nu-heading nu-heading--h2" id="ws-{n}">{e(heads[n])}</h3><p class="nu-text nu-text--meta">{e(labels[n])}</p><p class="nu-text">{e(paras[n])}</p></div>
</section>'''
    nw = sec("300-startup-hub", 4)
    rows = ""
    for c in nw:
        if c["kind"] == "link":
            m = re.match(r"(300 Startup Hub \| \w+)\s+(.*?)\s*→?$", clean(c["text"]))
            rows += link_row(m.group(1), c["href"], m.group(2), "Visit", external=True)
    soon = [(h, p) for h, p in zip(texts(nw, "h3"), texts(nw, "p")[2:])]
    for h, p in soon:
        rows += f'<article class="nu-link-row st-link-row--static"><h3 class="nu-heading nu-heading--h3 nu-link-row__title">{e(h)}</h3><div class="nu-link-row__body"><p class="nu-text">{e(p)}</p><span class="nu-tag">Coming soon</span></div></article>'
    body += band(section_header(texts(nw, "h2")[0], clean(texts(nw, "p")[1]), hid="h-network") + f'<div class="st-rows">{rows}</div>')
    body += band(staging_form(texts(sec("300-startup-hub", 5), "h3")[0], "hub"), "", None)
    ops = sec("300-startup-hub", 6)
    hours = texts(ops, "p")[0]
    addr = texts(ops, "p")[2]
    body += f'''<section class="st-band" aria-labelledby="h-ops">
  <section class="nu-contact-block" aria-labelledby="h-ops">
    <div class="nu-contact-block__label"><h2 class="nu-heading nu-heading--h4" id="h-ops">{e(texts(ops, "h3")[0])}</h2><p class="nu-text nu-text--small">{e(texts(ops, "p")[1])}</p></div>
    <div class="nu-contact-block__body"><div class="nu-contact-block__items">
      <address class="nu-contact-item">{i("location")}<span class="nu-contact-item__label">Address</span><span class="nu-contact-item__value">{e(addr).replace(chr(10), "<br>")}</span></address>
      <div class="nu-contact-item">{i("clock")}<span class="nu-contact-item__label">Hours</span><span class="nu-contact-item__value">{"<br>".join(e(x) for x in hours.split(chr(10)) if x.strip() and x.strip() != "Hours of Operation")}</span></div>
    </div>
    <div class="st-accordion">{accordion(directions(ops), "hub-dir")}</div></div>
  </section>
</section>'''
    site.page("300-startup-hub", "300 Startup Hub Boston", clean(texts(intro, "h3")[0]),
              hero_title("300 Startup Hub Boston", None, [(UNIT, "")]) + body, "300-startup-hub/")


# ---------- Launch Week open house (event) ----------
def open_house():
    top = sec("300-mass-ave-open-house", 1)
    reg = next(c["href"] for c in top if c["kind"] == "link")
    meta = f'''<ul class="nu-meta-list st-hero-meta">
  <li>{i("calendar")}<time datetime="2026-11-18">November 18–19, 2026</time></li>
  <li>{i("clock")}<span>9 a.m.–6 p.m.</span></li>
  <li>{i("location")}<span>{e(texts(top, "p")[0])}</span></li>
</ul>'''
    hero = hero_page("300 Mass Ave. Launch Week open house", asset(sec("300-mass-ave-open-house", 0)[0]["local"]), texts(top, "text")[0])
    hero = hero.replace("</h1>", "</h1>" + meta, 1).replace("</div>\n</section>", f'<a class="nu-button nu-button--accent" href="{e(reg)}">Register now {i("external")}</a></div>\n</section>', 1)
    body = band(f'<p class="st-statement st-statement--body">{e(texts(top, "p")[1])}</p>', "st-band--statement")
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
        lis = "".join(f'''<li class="nu-timeline-item"><span class="nu-timeline-item__date">{e(it["time"])}</span><span class="nu-timeline-item__rail" aria-hidden="true"></span>
  <div class="nu-timeline-item__body"><h4 class="nu-heading nu-heading--h4">{e(it["title"])}</h4>{f'<p class="nu-text nu-text--meta">{e(it["tag"])}</p>' if it["tag"] else ""}{"".join(f'<p class="nu-text">{e(p)}</p>' for p in it["p"])}</div></li>''' for it in d["items"])
        dhtml += f'<div class="nu-timeline__day"><h3 class="nu-heading nu-heading--h4 nu-timeline__day-title"><time datetime="{dates.get(d["day"], "")}">{e(d["day"])}</time></h3><ol class="nu-timeline__list">{lis}</ol></div>'
    body += f'''<section class="st-band"><section class="nu-timeline nu-timeline--agenda" aria-labelledby="h-agenda">
  <div class="nu-timeline__head"><h2 class="nu-heading nu-heading--h2" id="h-agenda">{e(texts(ag, "h2")[0])}</h2><p class="nu-text">{e(texts(ag, "p")[1])}</p></div>
  <div class="nu-timeline__days">{dhtml}</div>
</section></section>'''
    fx = sec("300-mass-ave-open-house", 3)
    ps, lis = texts(fx, "p"), texts(fx, "li")
    topics, hack = lis[:10], lis[10:]
    connect = f'''<section class="st-feature" aria-labelledby="h-connect">
  <h2 class="nu-heading nu-heading--h2" id="h-connect">{e(texts(fx, "h2")[0])}</h2>
  <ul class="nu-meta-list nu-meta-list--inline"><li>{e(ps[0])}</li><li>{e(ps[1])}</li><li>November 19, 9–11 a.m.</li></ul>
  <p class="nu-text">{e(ps[2])}</p><p class="nu-text">{e(ps[3])}</p>
  <h3 class="nu-heading nu-heading--h4">{e(texts(fx, "h3")[1])}</h3><p class="nu-text">{e(ps[4])}</p>
  <ul class="st-tags" role="list">{"".join(f'<li><span class="nu-tag">{e(t)}</span></li>' for t in topics)}</ul>
  <p class="nu-text nu-text--small">{e(ps[5])}</p>
</section>'''
    rows = ""
    for t in hack:
        m = re.match(r"^(Nov \d+(?:–\d+)?)([A-Z0-9 .]+?)([A-Z][a-z].*)$", t)
        d, label, desc = (m.group(1), m.group(2).strip().capitalize(), m.group(3)) if m else ("", "", t)
        label = label.replace("300 open house", "300 Open House").replace("Demo day 1.0", "Demo Day 1.0")
        rows += f'<li class="nu-timeline-item"><span class="nu-timeline-item__date">{e(d)}</span><span class="nu-timeline-item__rail" aria-hidden="true"></span><div class="nu-timeline-item__body"><h4 class="nu-heading nu-heading--h4">{e(label)}</h4><p class="nu-text">{e(desc)}</p></div></li>'
    apply = next(c for c in fx if c["kind"] == "link")
    hackathon = f'''<section class="st-feature" aria-labelledby="h-hack">
  <h2 class="nu-heading nu-heading--h2" id="h-hack">{e(texts(fx, "h2")[1])}</h2>
  <p class="nu-text nu-text--lead">{e(ps[6])}</p><p class="nu-text">{e(ps[7])}</p>
  <ol class="nu-timeline__list st-hack">{rows}</ol>
  <p class="nu-text nu-text--small">{e(ps[8])}</p>
  <div>{button("Apply to build", apply["href"])}</div>
</section>'''
    body += band(f'<div class="st-features">{connect}{hackathon}</div>')
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
  <section class="nu-contact-block" aria-labelledby="h-park">
    <div class="nu-contact-block__label"><h2 class="nu-heading nu-heading--h4" id="h-park">Parking and directions</h2></div>
    <div class="nu-contact-block__body"><div class="st-accordion">{accordion(directions(pk), "oh-dir")}</div></div>
  </section>
  <section class="nu-contact-block" aria-labelledby="h-q">
    <div class="nu-contact-block__label"><h2 class="nu-heading nu-heading--h4" id="h-q">Questions?</h2><p class="nu-text nu-text--small">{e(m.group(1))}, {e(m.group(2))}</p></div>
    <div class="nu-contact-block__body"><div class="nu-contact-block__items">{contact_items(email=m.group(3))}</div>
      {"".join(f'<p class="nu-text nu-text--small st-fine">{e(p)}</p>' for p in ps if p.startswith(("There may be", "Event registration")))}</div>
  </section>
</section>'''
    site.page("300-mass-ave-open-house", "300 Mass Ave. Launch Week", texts(top, "p")[1][:155], body, "300-mass-ave-open-house/", hero)


# ---------- Next Up Founders Prize (campaign) ----------
NU = "ventures/next-up-2026/"


def next_up():
    h = sec("ventures__next-up-2026", 0)
    hp = texts(h, "p")
    # The live hero image is the Next Up wordmark (text in an image): it sits beside the title, not behind it.
    hero = ""
    lead_band = hero_title("Your first venture. Before your first semester.", hp[1], [(UNIT, "")], figure=pic(h[0]["local"], "Next Up Founders Prize", "natural"), here="Next Up Founders Prize")
    notice = f'''<div class="nu-notice nu-notice--info">{i("info").replace('class="nu-icon"', 'class="nu-icon nu-notice__icon"')}
  <div class="nu-notice__body"><p class="nu-notice__title">Applications for 2026 are closed</p><p class="nu-text nu-text--small">{e(hp[0])}</p>
  <a class="nu-arrow-link nu-arrow-link--sm" href="#h-dates">What happens next {i("arrow")}</a></div></div>'''
    st = texts(sec("ventures__next-up-2026", 1), "p")
    facts = key_values([(st[1], st[2]), (st[3], st[4].replace("\n", " ")), (st[5], (st[6] + " " + st[7]).replace("\n", " "))], "nu-key-value--inline")
    prize = f'''<div class="st-prize"><p class="nu-text nu-text--meta">Up to</p><p class="nu-numeral nu-numeral--xl">$100K</p><p class="nu-text nu-text--lead">{e(st[0])}</p></div>'''
    net = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--md">{e(v)}</p><p class="nu-stat__text">{e(l)}</p></div>' for v, l in zip(st[9::2], st[10::2]))
    body = lead_band + band(notice, "st-band--tight") + band(f'<div class="st-prize-row">{prize}{facts}</div>')
    body += band(section_header(st[8], hid="h-net", split=False) + f'<div class="nu-stat-band"><div class="nu-stat-band__stats">{net}</div></div>', "st-band--sunken")
    el = sec("ventures__next-up-2026", 2)
    ep = texts(el, "p")
    body += band(section_header(clean(texts(el, "h3")[0]), ep[1], hid="h-elig") + key_values([(k[:1].upper() + k[1:], v) for k, v in zip(ep[2::2], ep[3::2])], "nu-key-value--inline st-kv-rows"))
    hw = sec("ventures__next-up-2026", 3)
    steps = "".join(f'<li class="nu-step nu-step--row"><span class="nu-numeral nu-numeral--md nu-step__numeral" aria-hidden="true">{n + 1}</span><h3 class="nu-heading nu-heading--h4">{e(t)}</h3><p class="nu-text">{e(p)}</p></li>'
                    for n, (t, p) in enumerate(zip(texts(hw, "h3")[1:], texts(hw, "p")[1:])))
    body += band(f'''<section class="nu-steps nu-steps--rows" aria-labelledby="h-how">
  <div class="nu-steps__head"><h2 class="nu-heading nu-heading--h2" id="h-how">How it works</h2><p class="nu-text">{e(texts(hw, "h3")[0])}</p></div>
  <ol class="nu-steps__list">{steps}</ol>
</section>''')
    dt = sec("ventures__next-up-2026", 4)
    dp = texts(dt, "p")
    tl = "".join(f'<li class="nu-timeline-item"><span class="nu-timeline-item__date">{e(v)}</span><span class="nu-timeline-item__rail" aria-hidden="true"></span><div class="nu-timeline-item__body"><h3 class="nu-heading nu-heading--h4">{e(k)}</h3></div></li>' for k, v in zip(dp[1::2], dp[2::2]))
    body += band(f'''<section class="nu-timeline nu-timeline--index" aria-labelledby="h-dates">
  <div class="nu-timeline__head"><h2 class="nu-heading nu-heading--h2" id="h-dates">Important dates</h2><p class="nu-timeline__note">{e(texts(dt, "h3")[0])}</p></div>
  <ol class="nu-timeline__list">{tl}</ol>
</section>''')
    fq = sec("ventures__next-up-2026", 5)
    groups, cur, pending = [("General", [])], None, None
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
    rules = next(c for c in fq if c["kind"] == "button")
    body += band(f'''<section class="nu-accordion" aria-labelledby="h-faq">
  <div class="nu-accordion__head"><h2 class="nu-heading nu-heading--h2" id="h-faq">FAQ</h2></div>
  <div class="nu-accordion__groups">{gh}</div>
</section><div class="st-actions">{arrow(rules["text"], rules["href"])}{arrow("Application guide", NU + "application-guide/")}</div>''')
    site.page("ventures/next-up-2026", "Next Up Founders Prize 2026", hp[1][:155], body, NU, hero)


def rules():
    top = sec("ventures__next-up-2026__program-parameters-rules", 0)
    ps = texts(sec("ventures__next-up-2026__program-parameters-rules", 1), "p")
    prose = ""
    for p in ps:
        if re.match(r"^\d+\.?\s", p) and len(p) < 70:
            prose += f"<h2>{e(p)}</h2>"
        elif re.match(r"^[a-z]\.\s", p) or re.match(r"^i\.", p):
            prose += f'<p class="st-clause">{e(p).replace(chr(10), "<br>")}</p>'
        else:
            prose += f"<p>{e(p).replace(chr(10), '<br>')}</p>"
    tp = texts(top, "p")
    body = hero_title(tp[0], tp[1], [(UNIT, ""), ("Next Up Founders Prize", NU)]) + band(f'<div class="st-policy"><div class="nu-prose">{prose}</div></div>')
    site.page("ventures/next-up-2026/program-parameters-rules", "Official rules · Next Up Founders Prize", tp[1], body, NU)


def guide():
    s = sec("ventures__next-up-2026__application-guide", 1)
    prose, in_list = "", False
    for c in s:
        k, t = c["kind"], c.get("text", "")
        if k != "li" and in_list:
            prose += "</ul>"
            in_list = False
        if k == "h3":
            prose += f"<h2>{e(t)}</h2>"
        elif k == "h4":
            prose += f"<h3>{e(t)}</h3>"
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
    body = hero_title("Application guide", "Next Up Founders Prize", [(UNIT, ""), ("Next Up Founders Prize", NU)]) + band(f'<div class="st-policy"><div class="nu-prose">{prose}</div></div>')
    site.page("ventures/next-up-2026/application-guide", "Application guide · Next Up Founders Prize", "How to apply to the Next Up Founders Prize.", body, NU)


def submission():
    frame = next((x for x in C["embeds"]["iframes"] if "qualtrics" in json.dumps(x).lower()), {})
    src = frame.get("src") if isinstance(frame, dict) else None
    body = hero_title("Submission", "Next Up Founders Prize 2026", [(UNIT, ""), ("Next Up Founders Prize", NU)]) + band(f'''<div class="nu-notice nu-notice--info">{i("info").replace('class="nu-icon"', 'class="nu-icon nu-notice__icon"')}
  <div class="nu-notice__body"><p class="nu-notice__title">Applications for 2026 closed on September 30</p>
  <p class="nu-text nu-text--small">The live site still embeds the submission form. Finalists will be notified in November.</p>
  <a class="nu-arrow-link nu-arrow-link--sm" href="{href(NU)}#h-dates">Important dates {i("arrow")}</a></div></div>
  {f'<div class="st-actions">{arrow("Open the submission form", src)}</div>' if src else ""}''')
    site.page("ventures/next-up-2026/submission", "Submission · Next Up Founders Prize", "Next Up Founders Prize submission.", body, NU)


# ---------- events archive ----------
def events():
    h = sec("events", 0)
    evs = [x for x in R["events"] if x["slug"] != "sample-event-2"]
    evs.sort(key=lambda x: (x.get("event_year") or 0, datetime.strptime(x["date_as_shown"] + " 2000", "%b %d %Y")), reverse=True)
    cards = ""
    for x in evs:
        d = datetime.strptime(f'{x["date_as_shown"]} {x["event_year"]}', "%b %d %Y")
        loc = x.get("location_as_shown") or ""
        loc = "" if loc.startswith("http") else loc
        link = x.get("registration_or_info_link")
        title = f'<a class="nu-event-card__link" href="{e(link)}">{e(clean(x["title"]))}</a>' if link and not link.startswith(LIVE) else e(clean(x["title"]))
        tags = "".join(f'<span class="nu-tag">{e(t)}</span>' for t in (x.get("locations_taxonomy") or []) + (x.get("types") or []))
        cards += f'''<li><article class="nu-event-card">
  <time class="nu-date-block" datetime="{d:%Y-%m-%d}"><span class="nu-date-block__month">{d:%b}</span><span class="nu-date-block__day">{d.day}</span></time>
  <div class="nu-event-card__body">
    <h3 class="nu-heading nu-heading--h4">{title}</h3>
    <ul class="nu-meta-list">
      <li>{i("calendar")}<span>{d:%B} {d.day}, {d.year}</span></li>
      {f'<li>{i("clock")}<span>{e(x["time_as_shown"])}</span></li>' if x.get("time_as_shown") else ""}
      {f'<li>{i("location")}<span>{e(loc)}</span></li>' if loc else ""}
    </ul>
    <div class="nu-event-card__tags">{tags}</div>
  </div>
</article></li>'''
    upcoming = "".join(link_row(t, u, d, c) for t, u, d, c in [
        ("300 Mass Ave. Launch Week", "300-mass-ave-open-house/", "The open house for Northeastern’s flagship entrepreneurship hub, November 18–19, 2026.", "See the agenda"),
        ("Next Up Founders Prize finals", NU, "High school founders pitch during Global Entrepreneurship Week, November 17–20.", "About the prize"),
        ("Events on Luma", "https://luma.com/eship", "The entrepreneurship calendar across Northeastern’s global network.", "Open the calendar")])
    hero = hero_page(clean(texts(h, "h1")[0]), asset(h[0]["local"]), None, [(UNIT, "")])
    body = band(section_header("Coming up", hid="h-up", split=False) + f'<div class="st-rows">{upcoming}</div>')
    body += band(section_header("Past events", "Events from 2023, kept for reference.", hid="h-past") + f'<ul class="st-events" role="list">{cards}</ul>', "st-band--sunken")
    site.page("events", "Events", "Entrepreneurship events across Northeastern’s global network.", body, "events/", hero)


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
