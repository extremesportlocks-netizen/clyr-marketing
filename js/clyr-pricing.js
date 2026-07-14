/* CLYR price hydrator — fills [data-clyr-price="product:plan"] from /api/prices.
   Static markup stays as fallback if the fetch fails; this only ever overwrites
   with engine truth, so pages can never drift from Stripe.
   Optional data-clyr-fmt:
     (none)      -> engine display string ("$129")
     "permo:N"   -> "$" + round(amount / N)          (per-month equivalent)
     "save:N"    -> "$" + (monthly*N - amount)        (savings vs N months of monthly)
     "amount"    -> "$" + amount (no suffix)
*/
(function () {
  var els = document.querySelectorAll('[data-clyr-price]');
  if (!els.length) return;
  fetch('https://clyr-backend.onrender.com/api/prices')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (d) {
      if (!d || !d.products) return;
      els.forEach(function (el) {
        var ref = (el.getAttribute('data-clyr-price') || '').split(':');
        var prod = d.products[ref[0]] || {};
        var p = prod[ref[1]];
        if (!p) return;
        var fmt = el.getAttribute('data-clyr-fmt');
        if (!fmt) { if (p.display) el.textContent = p.display; return; }
        var parts = fmt.split(':');
        if (parts[0] === 'amount') { el.textContent = '$' + p.amount; return; }
        var n = parseInt(parts[1] || '1', 10) || 1;
        if (parts[0] === 'permo') { el.textContent = '$' + Math.round(p.amount / n); return; }
        if (parts[0] === 'permo2') { el.textContent = '$' + (p.amount / n).toFixed(2); return; }
        if (parts[0] === 'save') {
          var m = prod.monthly; if (!m) return;
          var s = m.amount * n - p.amount;
          if (s > 0) el.textContent = '$' + s;
        }
      });
    })
    .catch(function () { /* keep static fallback */ });
})();
