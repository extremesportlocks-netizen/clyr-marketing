/* CLYR price hydrator — fills [data-clyr-price="product:plan"] from /api/prices.
   Static markup stays as fallback if the fetch fails; this only ever overwrites
   with engine truth, so pages can never drift from Stripe. */
(function () {
  var els = document.querySelectorAll('[data-clyr-price]');
  if (!els.length) return;
  fetch('https://clyr-backend.onrender.com/api/prices')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d || !d.products) return;
      els.forEach(function (el) {
        var ref = (el.getAttribute('data-clyr-price') || '').split(':');
        var p = d.products[ref[0]] && d.products[ref[0]][ref[1]];
        if (p && p.display) el.textContent = p.display;
      });
    })
    .catch(function () { /* keep static fallback */ });
})();
