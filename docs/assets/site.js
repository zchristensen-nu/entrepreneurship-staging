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
  const button = event.target.closest('button[aria-controls]');
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

// Finder: chips filter the cards (AND across facets, OR within one); counts and the empty state follow.
for (const panel of document.querySelectorAll('[data-finder]')) {
  const scope = panel.closest('section');
  const items = [...scope.querySelectorAll('[data-finder-items] > li')];
  const count = scope.querySelector('[data-finder-count]');
  const empty = scope.querySelector('[data-finder-empty]');
  const more = scope.querySelector('[data-finder-more]');
  const page = more ? Number(more.dataset.page) : Infinity;
  let limit = page;
  const apply = () => {
    const on = {};
    for (const c of panel.querySelectorAll('.nu-chip[aria-pressed="true"]')) (on[c.dataset.filter] ||= []).push(c.dataset.value);
    let shown = 0;
    for (const li of items) {
      const terms = JSON.parse(li.dataset.terms);
      const ok = Object.entries(on).every(([k, vals]) => vals.some((v) => (terms[k] || []).includes(v)));
      shown += ok;
      li.hidden = !ok || shown > limit;
    }
    if (more) more.hidden = shown <= limit;
    count.textContent = `${shown} of ${items.length} ${count.dataset.noun || 'results'}`;
    empty.hidden = shown > 0;
  };
  panel.addEventListener('click', (event) => {
    const chip = event.target.closest('.nu-chip');
    if (!chip) return;
    chip.setAttribute('aria-pressed', String(chip.getAttribute('aria-pressed') !== 'true'));
    limit = page;
    apply();
  });
  more?.addEventListener('click', () => { limit += page; apply(); });
  apply();
  panel.addEventListener('reset', () => {
    limit = page;
    for (const c of panel.querySelectorAll('.nu-chip')) c.setAttribute('aria-pressed', 'false');
    setTimeout(apply);
  });
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
