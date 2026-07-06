/* ═══════════════════════════════════════════════════════════════════
   CLYR address autocomplete + street sanity guard (July 2026)

   WHY: two real pharmacy rejections in one week from split/incomplete
   street fields: Sharon 241 (street="4314", name in Apt) hit BondRx
   "Invalid patient address"; Jon 229 ("1523C 17th Ave S") failed USPS
   DPV at TPH because the unit letter rode the primary number.

   WHAT:
   1) Always on: street sanity hint. A street that is digits-only, or
      has no real word in it, gets an inline nudge on blur. Each intake
      form's own step validator also blocks Continue on this pattern.
   2) When window.CLYR_MAPS_KEY is set: Google Places (New) autocomplete
      on #address with a custom dropdown. Selecting a suggestion fills
      street/apt/city/state/zip correctly (unit letters go to Apt, never
      welded to the street number). Uses session tokens so a full
      autocomplete->details flow bills as one session.
   3) No key or Google unreachable: forms behave exactly as before.

   Forms served: intake.html, intake-wellness.html, intake-niagen.html
   (shared field IDs: address, apt, city, state, zip).
   ═══════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var addr = document.getElementById('address');
  if (!addr) return;
  var $ = function (id) { return document.getElementById(id); };

  /* ── 1. Street sanity (always on) ─────────────────────────────── */
  function streetLooksIncomplete(s) {
    s = String(s || '').trim();
    if (!s) return null;
    if (!/[0-9]/.test(s)) return 'Please include your street number.';
    if (!/[A-Za-z]{2,}/.test(s)) return 'Looks like just a number. Please include the street name too (for example "4314 Pullet Ct").';
    return null;
  }
  window.clyrStreetLooksIncomplete = streetLooksIncomplete;

  var hint = document.createElement('div');
  hint.setAttribute('data-clyr-addr-hint', '1');
  hint.style.cssText = 'display:none;color:#c2410c;font-size:12.5px;margin-top:6px;line-height:1.4;';
  if (addr.parentNode) addr.parentNode.appendChild(hint);
  function refreshHint() {
    var msg = streetLooksIncomplete(addr.value);
    hint.textContent = msg || '';
    hint.style.display = msg ? 'block' : 'none';
  }
  addr.addEventListener('blur', refreshHint);
  addr.addEventListener('input', function () { if (hint.style.display === 'block') refreshHint(); });

  /* ── 2. Google Places (New) autocomplete ──────────────────────── */
  var KEY = window.CLYR_MAPS_KEY || '';
  if (!KEY) return; /* guard-only mode until the key is provisioned */

  var box = document.createElement('div');
  box.style.cssText = 'position:absolute;z-index:99999;background:#ffffff;border:1px solid #e5e7eb;' +
    'border-radius:10px;box-shadow:0 10px 28px rgba(0,0,0,.14);overflow:hidden;display:none;' +
    'font-size:14px;color:#111827;text-align:left;';
  document.body.appendChild(box);

  var items = [], active = -1, timer = null, session = null;
  function newSession() {
    session = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : 's' + Date.now() + Math.random().toString(16).slice(2);
  }
  newSession();

  function positionBox() {
    var r = addr.getBoundingClientRect();
    box.style.left = Math.round(r.left + window.scrollX) + 'px';
    box.style.top = Math.round(r.bottom + window.scrollY + 4) + 'px';
    box.style.width = Math.round(r.width) + 'px';
  }
  function hideBox() { box.style.display = 'none'; active = -1; }

  function render() {
    if (!items.length) { hideBox(); return; }
    var html = '';
    for (var i = 0; i < items.length; i++) {
      var t = items[i].text && items[i].text.text ? items[i].text.text : '';
      html += '<div data-i="' + i + '" style="padding:10px 14px;cursor:pointer;' +
        (i === active ? 'background:#f3f4f6;' : '') + '">' +
        t.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</div>';
    }
    html += '<div style="padding:6px 14px;font-size:10.5px;color:#9ca3af;border-top:1px solid #f3f4f6;">powered by Google</div>';
    box.innerHTML = html;
    positionBox();
    box.style.display = 'block';
  }

  box.addEventListener('mousedown', function (e) {
    var el = e.target.closest ? e.target.closest('[data-i]') : null;
    if (!el) return;
    e.preventDefault();
    choose(parseInt(el.getAttribute('data-i'), 10));
  });

  function fetchSuggestions(q) {
    fetch('https://places.googleapis.com/v1/places:autocomplete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Goog-Api-Key': KEY },
      body: JSON.stringify({ input: q, sessionToken: session, includedRegionCodes: ['us'] })
    }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) { hideBox(); return; }
        items = (d.suggestions || []).map(function (s) { return s.placePrediction; }).filter(Boolean).slice(0, 5);
        active = -1;
        render();
      })
      .catch(hideBox);
  }

  function comp(cs, type, useShort) {
    for (var i = 0; i < cs.length; i++) {
      if ((cs[i].types || []).indexOf(type) >= 0) return useShort ? (cs[i].shortText || '') : (cs[i].longText || '');
    }
    return '';
  }
  function setVal(el, v) {
    if (!el || v === undefined || v === null) return;
    el.value = v;
    try {
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (e) { /* older browsers: values are still set */ }
  }

  function choose(i) {
    var p = items[i];
    hideBox();
    if (!p || !p.placeId) return;
    var closingSession = session;
    newSession(); /* details call below closes the billing session */
    fetch('https://places.googleapis.com/v1/places/' + encodeURIComponent(p.placeId) +
          '?sessionToken=' + encodeURIComponent(closingSession), {
      headers: { 'X-Goog-Api-Key': KEY, 'X-Goog-FieldMask': 'addressComponents' }
    }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !d.addressComponents) return;
        var cs = d.addressComponents;
        var num = comp(cs, 'street_number');
        var route = comp(cs, 'route');
        var sub = comp(cs, 'subpremise');
        var city = comp(cs, 'locality') || comp(cs, 'sublocality_level_1') ||
                   comp(cs, 'postal_town') || comp(cs, 'administrative_area_level_3');
        var st = comp(cs, 'administrative_area_level_1', true);
        var zip = comp(cs, 'postal_code');
        var street = (num + ' ' + route).trim();
        if (street) setVal(addr, street);
        if (sub) {
          var aptEl = $('apt');
          if (aptEl && !aptEl.value.trim()) setVal(aptEl, sub);
        }
        if (city) setVal($('city'), city);
        if (zip) setVal($('zip'), zip);
        var stEl = $('state');
        if (stEl && st) {
          var has = false;
          for (var j = 0; j < stEl.options.length; j++) { if (stEl.options[j].value === st) { has = true; break; } }
          if (has) setVal(stEl, st); /* excluded states stay unpickable: their options do not exist */
        }
        refreshHint();
      }).catch(function () { /* silent: manual entry still works */ });
  }

  addr.addEventListener('input', function () {
    var q = addr.value.trim();
    if (timer) clearTimeout(timer);
    if (q.length < 4) { hideBox(); return; }
    timer = setTimeout(function () { fetchSuggestions(q); }, 250);
  });
  addr.addEventListener('keydown', function (e) {
    if (box.style.display === 'none') return;
    if (e.key === 'ArrowDown') { e.preventDefault(); active = Math.min(active + 1, items.length - 1); render(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); active = Math.max(active - 1, 0); render(); }
    else if (e.key === 'Enter') { if (active >= 0) { e.preventDefault(); choose(active); } }
    else if (e.key === 'Escape') { hideBox(); }
  });
  addr.addEventListener('blur', function () { setTimeout(hideBox, 150); });
  window.addEventListener('resize', function () { if (box.style.display === 'block') positionBox(); });
  window.addEventListener('scroll', function () { if (box.style.display === 'block') positionBox(); }, true);
})();
