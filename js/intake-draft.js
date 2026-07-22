// CLYR intake draft — Plan C / C2 (docs/PLAN-C-PERSISTENCE-BACK-NAV-EXECUTION.txt)
// NON-CLINICAL draft persistence so a reload/back-return doesn't wipe the form.
//
// HARD RULES (locked in the execution contract — do not relax here):
//   * NO clinical data: never mdiAnswers, flaggedConditions, or any screening
//     payload. PHI does not belong in unencrypted localStorage.
//   * NO clientSecret / Stripe session ids / anything payment-method-shaped.
//   * NO consents: the buyer must re-tick on review (never a "ready-looking"
//     state with a dead Continue).
//   * FAIL-OPEN: every storage touch is try/catch'd. A blocked/broken
//     localStorage must never stop a checkout — worst case is "no persistence".
//   * v-schema'd (v:1) + 24h TTL: mismatch or stale -> draft dropped on load.
(function () {
  var V = 1;
  var TTL_MS = 24 * 60 * 60 * 1000;
  var KEYS = { glp: 'clyr_intake_draft_glp', wellness: 'clyr_intake_draft_wellness' };
  var DETAIL_FIELDS = ['firstName', 'lastName', 'email', 'phone', 'sex', 'dobMonth', 'dobDay', 'dobYear'];
  var SHIP_FIELDS = ['address', 'apt', 'city', 'state', 'zip', 'currentMeds', 'drugAllergies'];

  function keyFor(flow) { return KEYS[flow] || null; }

  window.ClyrDraft = {
    // Save (merge) a draft. Guard: no identity (email) -> no save, so an empty
    // early save can never clobber a good draft (contract race guard).
    save: function (flow, data) {
      try {
        var key = keyFor(flow);
        if (!key || !data || !data.details || !String(data.details.email || '').trim()) return;
        var prev = this.load(flow) || {};
        var pd = prev.details || {}, ps = prev.shipping || {};
        var merged = {
          v: V,
          savedAt: Date.now(),
          flow: flow,
          product: data.product || prev.product || null,
          plan: data.plan || prev.plan || null,
          // deepest progress wins (restore precedence caps it later)
          step: Math.max(Number(data.step) || 1, Number(prev.step) || 1),
          paymentOpen: (data.paymentOpen != null) ? !!data.paymentOpen : !!prev.paymentOpen,
          details: {},
          shipping: {}
        };
        // merge, never overwrite a populated field with empty
        DETAIL_FIELDS.forEach(function (f) {
          merged.details[f] = String((data.details && data.details[f]) || pd[f] || '');
        });
        SHIP_FIELDS.forEach(function (f) {
          merged.shipping[f] = String((data.shipping && data.shipping[f]) || ps[f] || '');
        });
        localStorage.setItem(key, JSON.stringify(merged));
      } catch (e) { /* fail-open */ }
    },

    // Load a draft; drops it on schema mismatch or age > 24h.
    load: function (flow) {
      try {
        var key = keyFor(flow);
        if (!key) return null;
        var raw = localStorage.getItem(key);
        if (!raw) return null;
        var d = JSON.parse(raw);
        if (!d || d.v !== V || !d.savedAt || (Date.now() - d.savedAt) > TTL_MS) {
          localStorage.removeItem(key);
          return null;
        }
        return d;
      } catch (e) { return null; }
    },

    // Flag whether the embedded checkout was open when the draft was last live.
    // (Wellness payment is a panel swap on step 5 — the step number alone can't
    // tell the draft the embed was open; this flag is how it knows.)
    setPaymentOpen: function (flow, open) {
      try {
        var key = keyFor(flow);
        var d = this.load(flow);
        if (key && d) {
          d.paymentOpen = !!open;
          d.savedAt = Date.now();
          localStorage.setItem(key, JSON.stringify(d));
        }
      } catch (e) { /* fail-open */ }
    },

    clear: function (flow) {
      try { var key = keyFor(flow); if (key) localStorage.removeItem(key); } catch (e) {}
    },

    clearAll: function () {
      try { localStorage.removeItem(KEYS.glp); } catch (e) {}
      try { localStorage.removeItem(KEYS.wellness); } catch (e) {}
      try { localStorage.removeItem('clyr_intake_pos'); } catch (e) {}
    }
  };
})();
