# Entrepreneurship — staging

A migration of [entrepreneurship.northeastern.edu](https://entrepreneurship.northeastern.edu/) onto the Northeastern Design System (NUEAC-413), for review. Not the live site; every page is `noindex`.

- `build/build.py` composes every page from the system's organisms; content is the live site's (`build/content.json`). Crawled images live in `build/img/` (not committed); the build copies only what pages use, resized and recompressed. The page shell comes from `~/Projects/nu-site-kit`.
- `docs/` is the built output that GitHub Pages serves.

```bash
python3 build/build.py
```

## Decisions made on staging
- **Programs, ventures and events have no detail pages** on the live site (the single templates render empty), so they are filterable directories: 29 programs on Programs and offerings (category, location, interest, "I am a"), 142 ventures on the Venture portfolio (industry, 24 at a time). Cards link where the live cards link.
- **Events**: all eleven are from 2023, so Events shows what is coming up (Launch Week, Next Up finals, the Luma calendar) and keeps the 2023 events as a dated archive. The stale "Global Entrepreneurship Week begins November 13th, 2023" notice and its dead link are dropped; `sample-event-2` is dropped.
- **Next Up 2026**: applications are closed, so the Submission page explains that and links to the form instead of embedding it. The Application Guide (redirected on the live site) is rebuilt as a page, without the Outlook safelinks wrappers.
- **Dropped**: the kitchen-sink page, "Hello world!", the five news items (not linked from any live page; their bodies are lorem ipsum), "Lorem Partner Industry" terms.
- **Normalised**: duplicated filter terms (Accelerators → Accelerator, Investors → Investor). Six ventures whose live link points back to an empty page on this site show their name without a link.
- **Kept as published, needs an owner's check**: the home page says "26 entrepreneurship programs" and the directory has 29; the venture slugged `max-thalheimer` is titled GetFynd; two ventures have no logo and three no industry; VITAL has no program category.
- **Forms** (Get involved, 300 Startup Hub tour) are rebuilt with the system's Form organism; on staging they show a notice instead of sending.
