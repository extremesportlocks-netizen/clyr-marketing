/**
 * CLYR Health — Unified Event Tracking
 * Loads PostHog JS SDK + fires events to PostHog, Meta Pixel, and internal DB.
 * Include on all customer-facing pages: <script src="/js/clyr-tracking.js"></script>
 */
(function() {
  'use strict';

  var API = 'https://clyr-backend.onrender.com';
  var vid = localStorage.getItem('clyr_vid');
  if (!vid) { vid = crypto.randomUUID(); localStorage.setItem('clyr_vid', vid); }

  // ── First-touch attribution capture ────────────────────────
  // Captures UTMs + referrer + gclid the FIRST time a visitor lands and
  // persists them so the intake form (often several pages/days later) can
  // attribute the customer to their true source. First-touch wins: once set,
  // it is never overwritten within the visitor's stored history.
  function captureAttribution() {
    var params = new URLSearchParams(window.location.search);
    var ref = document.referrer || '';
    var hasUtm = params.get('utm_source') || params.get('gclid') || params.get('fbclid') || params.get('twclid');
    var existing = null;
    try { existing = JSON.parse(localStorage.getItem('clyr_attribution')); } catch (e) {}

    // Derive a source from referrer when no explicit UTM is present.
    function deriveSource() {
      if (params.get('twclid')) return 'Twitter/X';
      if (params.get('gclid')) return 'Google';
      if (params.get('fbclid')) return 'Facebook';
      if (params.get('utm_source')) return params.get('utm_source');
      var r = ref.toLowerCase();
      if (!r) return 'Direct';
      if (r.indexOf('clyr.health') !== -1 || r.indexOf('getclyrtoday.com') !== -1) return null; // internal nav, ignore
      if (r.indexOf('instagram') !== -1) return 'Instagram';
      if (r.indexOf('google') !== -1) return 'Google';
      if (r.indexOf('tiktok') !== -1) return 'TikTok';
      if (r.indexOf('facebook') !== -1 || r.indexOf('fb.') !== -1) return 'Facebook';
      if (r.indexOf('twitter') !== -1 || r.indexOf('t.co') !== -1) return 'Twitter/X';
      if (r.indexOf('youtube') !== -1) return 'YouTube';
      if (r.indexOf('linkedin') !== -1) return 'LinkedIn';
      if (r.indexOf('mail') !== -1 || r.indexOf('email') !== -1) return 'Email';
      return 'Referral';
    }

    var derived = deriveSource();

    // Bound stored values so they never exceed backend VARCHAR limits
    // (utm_* are 255, referrer is 500) and keep the localStorage record small.
    function cap(v, n) { return (v == null) ? null : (String(v).length > n ? String(v).slice(0, n) : String(v)); }

    // Only set first-touch once. Internal-nav (derived === null) never sets it.
    if (!existing && derived !== null) {
      var attribution = {
        utm_source: cap(params.get('utm_source') || derived, 255),
        utm_medium: cap(params.get('utm_medium') || ((params.get('gclid') || params.get('twclid')) ? 'cpc' : (ref ? 'referral' : 'none')), 255),
        utm_campaign: cap(params.get('utm_campaign'), 255),
        referrer: cap(ref, 500),
        gclid: cap(params.get('gclid'), 255),
        fbclid: cap(params.get('fbclid'), 255),
        twclid: cap(params.get('twclid'), 255),
        landing_page: window.location.pathname,
        captured_at: new Date().toISOString()
      };
      try { localStorage.setItem('clyr_attribution', JSON.stringify(attribution)); } catch (e) {}
    } else if (hasUtm && existing) {
      // Last-touch: if a NEW explicit campaign click arrives, record it separately
      // without clobbering first-touch. Useful for retargeting / email re-clicks.
      try {
        existing.last_utm_source = params.get('utm_source') || existing.last_utm_source;
        existing.last_utm_campaign = params.get('utm_campaign') || existing.last_utm_campaign;
        existing.last_touch_at = new Date().toISOString();
        localStorage.setItem('clyr_attribution', JSON.stringify(existing));
      } catch (e) {}
    }
  }
  captureAttribution();

  // Helper the intake forms call to retrieve stored first-touch attribution.
  window.clyrAttribution = function() {
    try { return JSON.parse(localStorage.getItem('clyr_attribution')) || {}; }
    catch (e) { return {}; }
  };

  // ── Load PostHog SDK ───────────────────────────────────────
  var _phReady = false;
  var _phQueue = [];

  function initPostHog() {
    fetch(API + '/api/config/tracking')
      .then(function(r) { return r.json(); })
      .then(function(cfg) {
        if (!cfg.posthogKey) return;

        !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture captureException identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onFeatureFlags onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

        window.posthog.init(cfg.posthogKey, {
          api_host: cfg.posthogHost || 'https://us.i.posthog.com',
          person_profiles: 'identified_only',
          capture_pageview: true,
          capture_pageleave: true,
          autocapture: true
        });

        // Identify by visitor ID
        window.posthog.identify(vid);

        _phReady = true;
        // Flush queued events
        for (var i = 0; i < _phQueue.length; i++) {
          window.posthog.capture(_phQueue[i].event, _phQueue[i].props);
        }
        _phQueue = [];
      })
      .catch(function() {});
  }

  // ── Core tracking function ─────────────────────────────────
  // Fires to: PostHog + internal DB
  window.clyrTrack = function(eventName, properties) {
    var props = properties || {};
    props.visitor_id = vid;
    props.page = window.location.pathname;
    props.url = window.location.href;
    props.referrer = document.referrer || null;
    props.timestamp = new Date().toISOString();

    // PostHog
    if (_phReady && window.posthog) {
      window.posthog.capture(eventName, props);
    } else {
      _phQueue.push({ event: eventName, props: props });
    }

    // Internal DB (fire-and-forget)
    try {
      var _a = (window.clyrAttribution && window.clyrAttribution()) || {};
      fetch(API + '/api/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event: eventName,
          page: props.page,
          visitor_id: vid,
          referrer: props.referrer,
          utm_source: _a.utm_source || null,
          utm_medium: _a.utm_medium || null,
          utm_campaign: _a.utm_campaign || null,
          gclid: _a.gclid || null,
          fbclid: _a.fbclid || null,
          twclid: _a.twclid || null,
          metadata: props
        })
      }).catch(function() {});
    } catch(e) {}
  };

  // ── Identify user (call after collecting email) ────────────
  window.clyrIdentify = function(email, traits) {
    if (!email) return;
    var t = traits || {};
    t.email = email;
    if (_phReady && window.posthog) {
      window.posthog.identify(email, t);
    }
    localStorage.setItem('clyr_email', email);
  };

  // ── Auto page view to internal DB ──────────────────────────
  try {
    var _ap = (window.clyrAttribution && window.clyrAttribution()) || {};
    fetch(API + '/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: window.location.pathname,
        visitor_id: vid,
        referrer: document.referrer || null,
        utm_source: _ap.utm_source || null,
        utm_medium: _ap.utm_medium || null,
        utm_campaign: _ap.utm_campaign || null,
        gclid: _ap.gclid || null,
        fbclid: _ap.fbclid || null,
        twclid: _ap.twclid || null
      })
    }).catch(function() {});
  } catch(e) {}

  // ── Init ───────────────────────────────────────────────────
  initPostHog();

})();

// ── Promo offer card ──────────────────────────────────────────
// Data-driven from /api/promo/active. Clean bottom-right slide-in
// (bottom sheet on mobile) — deliberately NOT a full-screen blocker.
// Shows once per 24h per visitor, never on funnel/legal pages.
(function () {
  var API = 'https://clyr-backend.onrender.com';
  var path = (window.location.pathname || '').toLowerCase();

  // Don't interrupt people who are already converting or reading legal copy.
  var SKIP = ['/intake', '/checkout', '/portal', '/resume', '/thank', '/confirm',
              '/privacy', '/terms', '/telehealth-consent', '/sms-terms', '/hipaa', '/return', '/refund',
              '/ads/']; // dedicated ad landing pages — never let the popup compete with their CTA
  for (var i = 0; i < SKIP.length; i++) { if (path.indexOf(SKIP[i]) !== -1) return; }

  function seenKey(code) { return 'clyr_promo_card_' + code; }
  function recentlySeen(code) {
    try {
      var t = parseInt(localStorage.getItem(seenKey(code)) || '0', 10);
      return t && (Date.now() - t) < 24 * 60 * 60 * 1000; // 24h cap
    } catch (e) { return false; }
  }
  function markSeen(code) { try { localStorage.setItem(seenKey(code), String(Date.now())); } catch (e) {} }
  function track(ev, props) { try { if (window.clyrTrack) window.clyrTrack(ev, props || {}); } catch (e) {} }

  function discountLabel(p) {
    var v = parseFloat(p.discount_value);
    var n = (v % 1 === 0) ? String(v) : v.toFixed(2);
    return p.discount_type === 'percent' ? (n + '% off') : ('$' + n + ' off');
  }

  function build(promo) {
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var code = promo.code || '';
    var label = discountLabel(promo);

    var style = document.createElement('style');
    style.textContent =
      '#clyrPromo{position:fixed;z-index:99998;right:24px;bottom:24px;width:340px;max-width:calc(100vw - 32px);' +
        'background:#fff;border:1px solid rgba(0,180,197,0.18);border-radius:18px;' +
        'box-shadow:0 18px 50px rgba(16,28,44,0.18),0 2px 8px rgba(16,28,44,0.06);' +
        'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;' +
        'opacity:0;transform:translateY(16px);transition:opacity .45s cubic-bezier(.2,.7,.2,1),transform .45s cubic-bezier(.2,.7,.2,1);overflow:hidden}' +
      '#clyrPromo.in{opacity:1;transform:translateY(0)}' +
      '#clyrPromo .cp-bar{height:4px;background:linear-gradient(90deg,#00B4C5,#009BAA)}' +
      '#clyrPromo .cp-body{padding:20px 22px 22px}' +
      '#clyrPromo .cp-x{position:absolute;top:10px;right:12px;width:28px;height:28px;border:none;background:transparent;' +
        'color:#9aa6b2;font-size:18px;line-height:1;cursor:pointer;border-radius:8px}' +
      '#clyrPromo .cp-x:hover{background:#f1f5f7;color:#4b5563}' +
      '#clyrPromo .cp-eyebrow{font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:#00B4C5;margin:0 0 8px}' +
      '#clyrPromo .cp-title{font-size:20px;font-weight:700;color:#101c2c;margin:0 0 6px;line-height:1.25}' +
      '#clyrPromo .cp-sub{font-size:13.5px;color:#5b6776;margin:0 0 16px;line-height:1.5}' +
      '#clyrPromo .cp-code{display:flex;align-items:center;justify-content:space-between;gap:10px;' +
        'background:#F2FBFC;border:1px dashed rgba(0,180,197,0.45);border-radius:12px;padding:10px 12px;margin:0 0 16px}' +
      '#clyrPromo .cp-code b{font-size:16px;letter-spacing:.06em;color:#0a7a85;font-weight:800}' +
      '#clyrPromo .cp-copy{border:none;background:#fff;border:1px solid rgba(0,180,197,0.35);color:#0a7a85;' +
        'font-size:12px;font-weight:700;padding:6px 12px;border-radius:8px;cursor:pointer}' +
      '#clyrPromo .cp-copy:hover{background:#E0F7FA}' +
      '#clyrPromo .cp-cta{display:block;width:100%;box-sizing:border-box;text-align:center;text-decoration:none;' +
        'background:linear-gradient(135deg,#00B4C5,#009BAA);color:#fff;font-size:15px;font-weight:700;' +
        'padding:13px 16px;border-radius:12px;box-shadow:0 6px 16px rgba(0,180,197,0.28)}' +
      '#clyrPromo .cp-cta:hover{filter:brightness(1.04)}' +
      '#clyrPromo .cp-fine{text-align:center;font-size:11px;color:#9aa6b2;margin:10px 0 0}' +
      '#clyrPromo .cp-ok{width:48px;height:48px;border-radius:50%;background:#E0F7FA;display:flex;align-items:center;justify-content:center;margin:2px 0 14px}' +
      '#clyrPromo .cp-ok svg{width:26px;height:26px;stroke:#00B4C5;fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}' +
      '@media (max-width:520px){#clyrPromo{right:0;left:0;bottom:0;width:100%;max-width:100%;' +
        'border-radius:18px 18px 0 0;border-left:none;border-right:none;border-bottom:none}}' +
      (reduce ? '#clyrPromo{transition:opacity .25s ease}#clyrPromo.in{transform:none}#clyrPromo{transform:none}' : '');
    document.head.appendChild(style);

    var card = document.createElement('div');
    card.id = 'clyrPromo';
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-label', 'Limited-time offer');
    card.innerHTML =
      '<div class="cp-bar"></div>' +
      '<button class="cp-x" aria-label="Close">×</button>' +
      '<div class="cp-body">' +
        '<p class="cp-eyebrow">Weekend offer</p>' +
        '<h3 class="cp-title">' + label.replace(/ off$/,'') + ' off any plan</h3>' +
        '<p class="cp-sub">Cold-chain shipped, clinician-reviewed care — now ' + label + ' through Sunday.</p>' +
        '<div class="cp-code"><span>Code <b>' + code + '</b></span>' +
          '<button class="cp-copy" type="button">Copy</button></div>' +
        '<button class="cp-cta" type="button" id="cpClaim">Claim ' + label + '</button>' +
        '<p class="cp-fine">Applied at checkout · no account needed</p>' +
      '</div>';
    document.body.appendChild(card);
    requestAnimationFrame(function () { requestAnimationFrame(function () { card.classList.add('in'); }); });
    markSeen(code);
    track('promo_popup_shown', { code: code });

    function close(reason) {
      card.classList.remove('in');
      setTimeout(function () { if (card.parentNode) card.parentNode.removeChild(card); }, 450);
      document.removeEventListener('keydown', onKey);
      track('promo_popup_dismissed', { code: code, reason: reason || 'close' });
    }
    function onKey(e) { if (e.key === 'Escape') close('esc'); }

    card.querySelector('.cp-x').addEventListener('click', function () { close('x'); });
    document.addEventListener('keydown', onKey);
    card.querySelector('#cpClaim').addEventListener('click', function () {
      track('promo_popup_clicked', { code: code });
      var body = card.querySelector('.cp-body');
      body.innerHTML =
        '<div class="cp-ok"><svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg></div>' +
        '<p class="cp-eyebrow">Offer claimed</p>' +
        '<h3 class="cp-title">You’re all set</h3>' +
        '<p class="cp-sub">Your <strong>' + label + '</strong> is locked in — it’ll be applied automatically at checkout. No code to enter.</p>' +
        '<a class="cp-cta" href="/weight-loss.html">Browse treatments →</a>';
      try { localStorage.setItem('clyr_promo_claimed', code); } catch (e) {}
      setTimeout(function () { close('claimed_timeout'); }, 10000);
    });
    card.querySelector('.cp-copy').addEventListener('click', function () {
      var btn = this;
      var done = function () { btn.textContent = 'Copied ✓'; setTimeout(function () { btn.textContent = 'Copy'; }, 1800); };
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(code).then(done, done); }
        else { var ta = document.createElement('textarea'); ta.value = code; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); done(); }
      } catch (e) { done(); }
      track('promo_code_copied', { code: code });
    });
  }

  function arm(promo) {
    if (recentlySeen(promo.code)) return;
    var fired = false;
    function go() { if (fired) return; fired = true; cleanup(); build(promo); }
    function onLeave(e) { if (e.clientY <= 0) go(); } // exit-intent (desktop)
    function cleanup() { clearTimeout(t); document.removeEventListener('mouseleave', onLeave); }
    var t = setTimeout(go, 8000);                       // or 8s dwell, whichever first
    document.addEventListener('mouseleave', onLeave);
  }

  function init() {
    fetch(API + '/api/promo/active')
      .then(function (r) { return r.json(); })
      .then(function (d) { if (d && d.active && d.promo && d.promo.code) arm(d.promo); })
      .catch(function () {});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
