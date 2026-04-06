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
      fetch(API + '/api/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event: eventName,
          page: props.page,
          visitor_id: vid,
          referrer: props.referrer,
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
    fetch(API + '/api/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: window.location.pathname,
        visitor_id: vid,
        referrer: document.referrer || null
      })
    }).catch(function() {});
  } catch(e) {}

  // ── Init ───────────────────────────────────────────────────
  initPostHog();

})();
