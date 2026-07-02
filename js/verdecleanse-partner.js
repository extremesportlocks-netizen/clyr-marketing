/**
 * Verde Cleanse partner funnel on antiparasitic hub.
 * When utm_source=verdecleanse (or plan=onetime from cleanse campaign),
 * show partner banner, $99/$139 pricing, and route CTAs to intake with onetime plan.
 */
(function () {
  'use strict';

  var params = new URLSearchParams(window.location.search);
  var isVerde = params.get('utm_source') === 'verdecleanse'
    || params.get('utm_campaign') === '30day-cleanse'
    || params.get('plan') === 'onetime';

  if (!isVerde) return;

  var product = (params.get('product') || '').toLowerCase().replace(/-/g, '_');
  var plan = params.get('plan') || 'onetime';

  function intakeUrl(prod) {
    var q = new URLSearchParams();
    q.set('product', prod);
    q.set('plan', plan);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'].forEach(function (k) {
      if (params.get(k)) q.set(k, params.get(k));
    });
    if (!q.get('utm_source')) q.set('utm_source', 'verdecleanse');
    if (!q.get('utm_medium')) q.set('utm_medium', 'referral');
    if (!q.get('utm_campaign')) q.set('utm_campaign', '30day-cleanse');
    return '/intake-wellness.html?' + q.toString();
  }

  // Inject partner banner after breadcrumb
  var banner = document.createElement('div');
  banner.className = 'verde-partner-banner';
  banner.innerHTML =
    '<div class="verde-partner-inner">' +
      '<div class="verde-partner-mark">🌿</div>' +
      '<div class="verde-partner-copy">' +
        '<div class="verde-partner-eyebrow">From Verde Cleanse</div>' +
        '<h2>30-day cleanse tiers — <span class="serif">one-time, no subscription</span></h2>' +
        '<p>You came from our plant-forward education partner. Choose your protocol below — provider review and pharmacy fulfillment through CLYR Health.</p>' +
      '</div>' +
      '<div class="verde-partner-prices">' +
        '<div class="verde-price-chip"><strong>$99</strong><span>Ivermectin · 30-day</span></div>' +
        '<div class="verde-price-chip lead"><strong>$139</strong><span>IVM + Mebendazole</span></div>' +
      '</div>' +
    '</div>';

  var breadcrumb = document.querySelector('.breadcrumb');
  if (breadcrumb && breadcrumb.parentNode) {
    breadcrumb.parentNode.insertBefore(banner, breadcrumb.nextSibling);
  } else {
    document.body.insertBefore(banner, document.body.firstChild);
  }

  // Update compare cards to cleanse pricing
  var cards = document.querySelectorAll('.cmp-card');
  if (cards[0]) {
    var p0 = cards[0].querySelector('.cmp-price');
    if (p0) p0.innerHTML = '<span class="amt">$99</span><span class="per">one-time</span>';
    var prep0 = cards[0].querySelector('.cmp-prepay');
    if (prep0) prep0.innerHTML = '30-day cleanse · <strong>no auto-refill</strong>';
    var cta0 = cards[0].querySelector('.cmp-cta');
    if (cta0) {
      cta0.href = intakeUrl('ivermectin');
      cta0.textContent = 'Start 30-day cleanse ';
      cta0.insertAdjacentHTML('beforeend', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>');
    }
    if (product === 'ivermectin') cards[0].classList.add('verde-highlight');
  }
  if (cards[1]) {
    var p1 = cards[1].querySelector('.cmp-price');
    if (p1) p1.innerHTML = '<span class="amt">$139</span><span class="per">one-time</span>';
    var prep1 = cards[1].querySelector('.cmp-prepay');
    if (prep1) prep1.innerHTML = 'Broader coverage · <strong>30-day supply</strong>';
    var cta1 = cards[1].querySelector('.cmp-cta');
    if (cta1) {
      cta1.href = intakeUrl('ivermectin_mebendazole');
      cta1.textContent = 'Start dual cleanse ';
      cta1.insertAdjacentHTML('beforeend', '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>');
    }
    if (product === 'ivermectin_mebendazole') cards[1].classList.add('verde-highlight');
  }

  // Bottom CTA section if present
  document.querySelectorAll('a[href*="intake-wellness"]').forEach(function (a) {
    var href = a.getAttribute('href') || '';
    if (href.indexOf('ivermectin-mebendazole') !== -1 || href.indexOf('ivermectin_mebendazole') !== -1) {
      a.href = intakeUrl('ivermectin_mebendazole');
    } else if (href.indexOf('product=ivermectin') !== -1) {
      a.href = intakeUrl('ivermectin');
    }
  });

  if (window.clyrTrack) {
    window.clyrTrack('verdecleanse_hub_view', {
      product: product || null,
      plan: plan,
      utm_content: params.get('utm_content') || null,
    });
  }
})();