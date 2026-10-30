// Disclosure behaviour for the presentational components: any button with aria-controls toggles its target's `hidden`.
// Escape or a click outside closes what is open; focus returns to the button.
const open = new Set();

function setOpen(button, target, state) {
  button.setAttribute('aria-expanded', String(state));
  target.hidden = !state;
  state ? open.add(button) : open.delete(button);
  if (state && target.getAttribute('role') === 'dialog') target.querySelector('button, a')?.focus();
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('button[aria-controls]:not([data-drawer-open])');
  const close = event.target.closest('[data-close]');
  if (close) {
    for (const b of open) if (document.getElementById(b.getAttribute('aria-controls'))?.contains(close)) { setOpen(b, document.getElementById(b.getAttribute('aria-controls')), false); b.focus(); }
    return;
  }
  if (button) {
    const target = document.getElementById(button.getAttribute('aria-controls'));
    if (target && target.hasAttribute('hidden') !== undefined) {
      for (const b of [...open]) if (b !== button) setOpen(b, document.getElementById(b.getAttribute('aria-controls')), false);
      setOpen(button, target, button.getAttribute('aria-expanded') !== 'true');
      return;
    }
  }
  for (const b of [...open]) {
    const target = document.getElementById(b.getAttribute('aria-controls'));
    if (!target.contains(event.target)) setOpen(b, target, false);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  for (const b of [...open]) { setOpen(b, document.getElementById(b.getAttribute('aria-controls')), false); b.focus(); }
});

// Finder: chips and checkboxes filter the cards (AND across facets, OR within one); counts, paging and the phone drawer follow.
for (const panel of document.querySelectorAll('[data-finder]')) {
  const scope = panel.closest('section');
  const items = [...scope.querySelectorAll('[data-finder-items] > li')];
  const count = scope.querySelector('[data-finder-count]');
  const empty = scope.querySelector('[data-finder-empty]');
  const badge = scope.querySelector('[data-finder-badge]');
  const total = scope.querySelector('[data-finder-total]');
  const drawer = scope.querySelector('[data-drawer]');
  const opener = scope.querySelector('[data-drawer-open]');
  const more = scope.querySelector('[data-finder-more]');
  const page = more ? Number(more.dataset.page) : Infinity;
  let limit = page;
  const active = () => {
    const on = {};
    for (const c of panel.querySelectorAll('.nu-chip[aria-pressed="true"]')) (on[c.dataset.filter] ||= []).push(c.dataset.value);
    for (const c of panel.querySelectorAll('input[data-filter]:checked')) (on[c.dataset.filter] ||= []).push(c.value);
    return on;
  };
  const apply = () => {
    const on = active();
    let shown = 0;
    for (const li of items) {
      const terms = JSON.parse(li.dataset.terms);
      const ok = Object.entries(on).every(([k, vals]) => vals.some((v) => (terms[k] || []).includes(v)));
      shown += ok;
      li.hidden = !ok || shown > limit;
    }
    const n = Object.values(on).flat().length;
    count.textContent = `${shown} of ${items.length} ${count.dataset.noun || 'results'}`;
    total.textContent = shown;
    badge.textContent = n;
    badge.hidden = n === 0;
    empty.hidden = shown > 0;
    if (more) more.hidden = shown <= limit;
  };
  panel.addEventListener('click', (event) => {
    const chip = event.target.closest('.nu-chip');
    const all = event.target.closest('[data-show-all]');
    if (all) {
      const open = all.getAttribute('aria-expanded') !== 'true';
      all.setAttribute('aria-expanded', String(open));
      for (const o of all.parentElement.querySelectorAll('[data-more]')) o.hidden = !open;
      return;
    }
    if (!chip) return;
    chip.setAttribute('aria-pressed', String(chip.getAttribute('aria-pressed') !== 'true'));
    limit = page;
    apply();
  });
  panel.addEventListener('change', () => { limit = page; apply(); });
  panel.addEventListener('reset', () => {
    for (const c of panel.querySelectorAll('.nu-chip')) c.setAttribute('aria-pressed', 'false');
    limit = page;
    setTimeout(apply);
  });
  more?.addEventListener('click', () => { limit += page; apply(); });
  // Phone drawer: the same form, opened over the page below 960px.
  const close = () => { drawer.removeAttribute('data-open'); opener.setAttribute('aria-expanded', 'false'); document.documentElement.classList.remove('st-locked'); opener.focus(); };
  opener.addEventListener('click', (event) => {
    event.stopPropagation();
    drawer.setAttribute('data-open', '');
    opener.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.add('st-locked');
    panel.querySelector('button, input')?.focus();
  });
  scope.querySelector('[data-drawer-close]').addEventListener('click', close);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && drawer.hasAttribute('data-open')) close(); });
  apply();
}

// Staging forms never submit: show the notice instead.
for (const form of document.querySelectorAll('[data-staging-form]')) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const sent = form.querySelector('[data-staging-sent]');
    sent.hidden = false;
    sent.scrollIntoView({ block: 'center' });
  });
}

// Film bands: play muted unless the visitor prefers reduced motion; the toggle pauses and resumes.
for (const video of document.querySelectorAll('[data-film]')) {
  const toggle = video.closest('section').querySelector('[data-film-toggle]');
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const set = (paused) => {
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.setAttribute('aria-label', paused ? 'Play the film' : 'Pause the film');
  };
  if (still) set(true); else video.play().then(() => set(false)).catch(() => set(true));
  toggle.addEventListener('click', () => {
    if (video.paused) { video.play(); set(false); } else { video.pause(); set(true); }
  });
}

// Long documents: mark the section being read in every table of contents on the page.
const tocs = document.querySelectorAll('[data-toc]');
if (tocs.length) {
  const links = [...tocs].flatMap((t) => [...t.querySelectorAll('a[href^="#"]')]);
  const heads = [...new Set(links.map((a) => document.getElementById(a.hash.slice(1))))].filter(Boolean);
  const mark = (id) => {
    for (const a of links) {
      if (a.hash === `#${id}`) a.setAttribute('aria-current', 'location');
      else a.removeAttribute('aria-current');
    }
    const cur = document.querySelector('[data-toc-current]');
    const hit = links.find((a) => a.hash === `#${id}`);
    if (cur && hit) cur.textContent = hit.textContent;
  };
  const seen = new IntersectionObserver((entries) => {
    const top = entries.filter((x) => x.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (top) mark(top.target.id);
  }, { rootMargin: '0px 0px -70% 0px' });
  heads.forEach((h) => seen.observe(h));
  for (const d of document.querySelectorAll('[data-toc] details')) d.addEventListener('click', (ev) => { if (ev.target.closest('a')) d.open = false; });
}

// --- el (Experiential Learning) ---
// LogoWall --open: Show all N partners reveals the rest of the wall (el-13).
for (const button of document.querySelectorAll('[data-el-show-all]')) {
  button.addEventListener('click', () => {
    const wall = document.getElementById(button.dataset.elShowAll);
    for (const li of wall.querySelectorAll('[data-more]')) li.hidden = false;
    button.closest('.nu-logo-wall__foot').remove();
  });
}
// CampusMap --index (el-09): the Select (and a pin) choose the campus shown in the panel.
const elCampuses = document.getElementById('el-campuses');
if (elCampuses) {
  const data = JSON.parse(elCampuses.textContent);
  const map = elCampuses.previousElementSibling;
  const select = map.querySelector('[data-el-campus]');
  const panel = map.querySelector('.nu-campus-map__panel');
  const pins = [...map.querySelectorAll('.nu-campus-map__pin')];
  const photo = panel.querySelector('img');
  const base = photo.getAttribute('src').replace(/[^/]+$/, '');
  const show = (name) => {
    const c = data[name];
    if (!c) return;
    photo.src = base + c.img;
    panel.querySelector('h3').textContent = name;
    panel.querySelector('.nu-meta-list span').textContent = c.place;
    panel.querySelector('.nu-campus-map__body > p.nu-text').textContent = c.text;
    const link = panel.querySelector('.nu-arrow-link');
    link.href = c.href;
    link.firstChild.textContent = `Explore ${name}`;
    for (const pin of pins) pin.setAttribute('aria-pressed', String(pin.getAttribute('aria-label').includes(name)));
  };
  select.addEventListener('change', () => show(select.value));
  for (const pin of pins) {
    pin.addEventListener('click', () => {
      const name = Object.keys(data).find((n) => pin.getAttribute('aria-label').includes(n));
      if (name) { select.value = name; show(name); }
    });
  }
}
// --- end el ---

// --- ge (Entrepreneurship) ---
// ExpandingCards: exactly one card open. The toggle opens its card everywhere; hover (fine pointers, after a short delay) and focus open it too.
// Clicks stop here so the kit's generic aria-controls disclosure never hides a card body.
for (const row of document.querySelectorAll('[data-ge-cards]')) {
  const toggles = [...row.querySelectorAll('.nu-expanding-cards__toggle')];
  const open = (t) => { for (const x of toggles) x.setAttribute('aria-expanded', String(x === t)); };
  row.addEventListener('click', (event) => {
    const t = event.target.closest('.nu-expanding-cards__toggle');
    if (t) { event.stopPropagation(); open(t); }
  });
  row.addEventListener('focusin', (event) => {
    const card = event.target.closest('.nu-expanding-cards__card');
    if (card && !event.target.matches('.nu-expanding-cards__toggle')) open(card.querySelector('.nu-expanding-cards__toggle'));
  });
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    let timer;
    for (const t of toggles) {
      const card = t.closest('.nu-expanding-cards__card');
      card.addEventListener('pointerenter', () => { clearTimeout(timer); timer = setTimeout(() => open(t), 180); });
      card.addEventListener('pointerleave', () => clearTimeout(timer));
    }
  }
}

// Venture directory (DirectoryGrid in the finder layout): name search + industry checkboxes, 30 at a time, Grid / List, the phone drawer.
for (const scope of document.querySelectorAll('[data-ge-dir]')) {
  const panel = scope.querySelector('[data-ge-panel]');
  const grid = scope.querySelector('[data-ge-grid]');
  const items = [...scope.querySelectorAll('[data-ge-items] > li')];
  const q = scope.querySelector('[data-ge-q]');
  const count = scope.querySelector('[data-ge-count]');
  const total = scope.querySelector('[data-ge-total]');
  const badge = scope.querySelector('[data-ge-badge]');
  const empty = scope.querySelector('[data-ge-empty]');
  const more = scope.querySelector('[data-ge-more]');
  const drawer = scope.querySelector('[data-drawer]');
  const opener = scope.querySelector('[data-drawer-open]');
  const page = Number(scope.dataset.page) || 30;
  let limit = page;
  const apply = () => {
    const term = q.value.trim().toLowerCase();
    const on = [...panel.querySelectorAll('input[data-filter]:checked')].map((c) => c.value);
    let shown = 0;
    for (const li of items) {
      const inds = JSON.parse(li.dataset.terms).industries || [];
      const ok = (!term || li.dataset.name.includes(term)) && (!on.length || on.some((v) => inds.includes(v)));
      shown += ok;
      li.hidden = !ok || shown > limit;
    }
    const visible = Math.min(shown, limit);
    count.innerHTML = shown ? `Showing <b>1–${visible}</b> of <b>${shown}</b> ventures` : 'No ventures match';
    total.textContent = shown;
    badge.textContent = on.length + (term ? 1 : 0);
    badge.hidden = !(on.length || term);
    empty.hidden = shown > 0;
    more.hidden = shown <= limit;
  };
  panel.addEventListener('submit', (event) => event.preventDefault());
  panel.addEventListener('input', () => { limit = page; apply(); });
  panel.addEventListener('change', () => { limit = page; apply(); });
  panel.addEventListener('reset', () => { limit = page; setTimeout(apply); });
  panel.addEventListener('click', (event) => {
    const all = event.target.closest('[data-show-all]');
    if (all) {
      const open = all.getAttribute('aria-expanded') !== 'true';
      all.setAttribute('aria-expanded', String(open));
      for (const o of all.parentElement.querySelectorAll('[data-more]')) o.hidden = !open;
    }
    if (event.target.closest('[data-ge-q-clear]')) { q.value = ''; q.focus(); limit = page; apply(); }
  });
  more.addEventListener('click', () => { limit += page; apply(); });
  for (const chip of scope.querySelectorAll('[data-ge-view]')) {
    chip.addEventListener('click', () => {
      for (const c of scope.querySelectorAll('[data-ge-view]')) c.setAttribute('aria-pressed', String(c === chip));
      grid.classList.toggle('nu-directory-grid--list', chip.dataset.geView === 'list');
      try { localStorage.setItem('ge-dir-view', chip.dataset.geView); } catch (e) { /* storage blocked: the default view stands */ }
    });
  }
  try { if (localStorage.getItem('ge-dir-view') === 'list') scope.querySelector('[data-ge-view="list"]').click(); } catch (e) { /* default view */ }
  const close = () => { drawer.removeAttribute('data-open'); opener.setAttribute('aria-expanded', 'false'); document.documentElement.classList.remove('st-locked'); opener.focus(); };
  opener.addEventListener('click', (event) => {
    event.stopPropagation();
    drawer.setAttribute('data-open', '');
    opener.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.add('st-locked');
    q.focus();
  });
  scope.querySelector('[data-drawer-close]').addEventListener('click', close);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && drawer.hasAttribute('data-open')) close(); });
  apply();
}
// --- end ge ---
