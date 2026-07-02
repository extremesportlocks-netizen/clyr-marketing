(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var mouse = { x: 0.5, y: 0.5, active: false };

  /* ── Page load entrance ── */
  function initLoad() {
    requestAnimationFrame(function () {
      document.body.classList.add('is-loaded');
    });
  }

  /* ── Copper particle canvas (mouse-reactive) ── */
  function initParticles() {
    var canvas = document.getElementById('ghk-particles');
    if (!canvas || reduced) return;
    var ctx = canvas.getContext('2d');
    var particles = [];
    var count = Math.min(110, Math.floor((window.innerWidth * window.innerHeight) / 12000));

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    document.addEventListener('mousemove', function (e) {
      mouse.x = e.clientX / window.innerWidth;
      mouse.y = e.clientY / window.innerHeight;
      mouse.active = true;
    }, { passive: true });

    for (var i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2.4 + 0.4,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        hue: Math.random() > 0.5 ? 24 : 186,
        alpha: Math.random() * 0.5 + 0.12,
        phase: Math.random() * Math.PI * 2,
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var mx = mouse.x * canvas.width;
      var my = mouse.y * canvas.height;

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.phase += 0.012;

        if (mouse.active) {
          var dx = mx - p.x;
          var dy = my - p.y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 220 && dist > 0) {
            var force = (220 - dist) / 220 * 0.018;
            p.vx += (dx / dist) * force;
            p.vy += (dy / dist) * force;
          }
        }

        p.vx *= 0.98;
        p.vy *= 0.98;
        p.x += p.vx + Math.sin(p.phase) * 0.15;
        p.y += p.vy + Math.cos(p.phase) * 0.12;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        var grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 3.5);
        grad.addColorStop(0, 'hsla(' + p.hue + ', 72%, 62%, ' + p.alpha + ')');
        grad.addColorStop(1, 'hsla(' + p.hue + ', 72%, 50%, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r * 3.5, 0, Math.PI * 2);
        ctx.fill();
      }

      for (var a = 0; a < particles.length; a++) {
        for (var b = a + 1; b < particles.length; b++) {
          var ddx = particles[a].x - particles[b].x;
          var ddy = particles[a].y - particles[b].y;
          var ddist = Math.sqrt(ddx * ddx + ddy * ddy);
          if (ddist < 110) {
            ctx.strokeStyle = 'rgba(201, 120, 74, ' + (0.1 * (1 - ddist / 110)) + ')';
            ctx.lineWidth = 0.7;
            ctx.beginPath();
            ctx.moveTo(particles[a].x, particles[a].y);
            ctx.lineTo(particles[b].x, particles[b].y);
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    }
    draw();
  }

  /* ── Hero panel: drifting copper ball-and-stick molecules ── */
  function initHeroMolecules() {
    if (reduced) return;
    var panel = document.getElementById('ghk-hero-panel');
    var canvas = document.getElementById('ghk-hero-molecules');
    var stage = document.getElementById('ghk-product-stage');
    if (!panel || !canvas || !stage) return;

    var ctx = canvas.getContext('2d');
    if (!ctx) return;

    var templates = [
      { atoms: [[0, 0, 5.5], [26, 4, 4.5], [-20, 16, 4], [18, -18, 4]], bonds: [[0, 1], [0, 2], [1, 3]] },
      { atoms: [[0, 0, 5], [0, 28, 4], [24, 14, 4], [-24, 14, 4], [0, -22, 3.5]], bonds: [[0, 1], [0, 2], [0, 3], [0, 4], [2, 3]] },
      { atoms: [[18, 0, 4], [9, 16, 4], [-9, 16, 4], [-18, 0, 4], [-9, -16, 4], [9, -16, 4]], bonds: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]] },
      { atoms: [[-30, 0, 4], [-10, 0, 4.5], [10, 0, 4.5], [30, 0, 4], [0, 18, 3.5]], bonds: [[0, 1], [1, 2], [2, 3], [1, 4], [2, 4]] },
      { atoms: [[0, 0, 6], [22, 12, 4], [-16, 20, 3.5], [-18, -10, 4]], bonds: [[0, 1], [0, 2], [0, 3], [2, 3]] },
    ];

    var molecules = [];
    var running = true;
    var count = 16;
    var avoid = { x: 0, y: 0, r: 120 };

    function resize() {
      var rect = panel.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      molecules = [];
      for (var i = 0; i < count; i++) {
        molecules.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          rot: Math.random() * Math.PI * 2,
          rotSpeed: (Math.random() - 0.5) * 0.009,
          scale: 0.7 + Math.random() * 0.9,
          depth: 0.4 + Math.random() * 0.6,
          tpl: templates[i % templates.length],
        });
      }
    }

    function updateAvoidZone() {
      var panelRect = panel.getBoundingClientRect();
      var stageRect = stage.getBoundingClientRect();
      avoid.x = stageRect.left - panelRect.left + stageRect.width * 0.5;
      avoid.y = stageRect.top - panelRect.top + stageRect.height * 0.46;
      avoid.r = Math.min(stageRect.width, stageRect.height) * 0.34;
    }

    function drawAtom(x, y, r, depth) {
      var g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.4);
      g.addColorStop(0, 'rgba(244, 201, 168, ' + (0.6 * depth) + ')');
      g.addColorStop(0.45, 'rgba(201, 120, 74, ' + (0.8 * depth) + ')');
      g.addColorStop(1, 'rgba(139, 79, 42, 0)');
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(x, y, r * 2, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(0, 180, 197, ' + (0.4 * depth) + ')';
      ctx.beginPath();
      ctx.arc(x, y, r * 0.5, 0, Math.PI * 2);
      ctx.fill();
    }

    function draw() {
      if (!running) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      updateAvoidZone();

      molecules.forEach(function (mol) {
        mol.x += mol.vx;
        mol.y += mol.vy;
        mol.rot += mol.rotSpeed;

        if (mol.x < -70) mol.x = canvas.width + 70;
        if (mol.x > canvas.width + 70) mol.x = -70;
        if (mol.y < -70) mol.y = canvas.height + 70;
        if (mol.y > canvas.height + 70) mol.y = -70;

        var dx = mol.x - avoid.x;
        var dy = mol.y - avoid.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < avoid.r + 40) {
          var push = (avoid.r + 40 - dist) * 0.03;
          mol.vx += (dx / (dist || 1)) * push;
          mol.vy += (dy / (dist || 1)) * push;
        }
        mol.vx *= 0.992;
        mol.vy *= 0.992;

        var cos = Math.cos(mol.rot);
        var sin = Math.sin(mol.rot);
        var pts = mol.tpl.atoms.map(function (a) {
          var sx = a[0] * mol.scale;
          var sy = a[1] * mol.scale;
          return {
            x: mol.x + sx * cos - sy * sin,
            y: mol.y + sx * sin + sy * cos,
            r: a[2] * mol.scale,
          };
        });

        ctx.lineWidth = 1.3 * mol.scale;
        mol.tpl.bonds.forEach(function (b) {
          var p1 = pts[b[0]];
          var p2 = pts[b[1]];
          ctx.strokeStyle = 'rgba(201, 120, 74, ' + (0.28 * mol.depth) + ')';
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        });

        pts.forEach(function (p) {
          drawAtom(p.x, p.y, p.r, mol.depth);
        });
      });

      requestAnimationFrame(draw);
    }

    resize();
    draw();
    window.addEventListener('resize', resize);

    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        running = entry.isIntersecting;
        if (running) draw();
      });
    }, { threshold: 0.05 });
    obs.observe(panel);
  }

  /* ── 3D product tilt ── */
  function initProductTilt() {
    if (reduced) return;
    var stage = document.getElementById('ghk-product-stage');
    var wrap = stage && stage.querySelector('.ghk-hero-photo-wrap');
    if (!stage || !wrap) return;

    var bounds = null;
    var currentX = 0;
    var currentY = 0;
    var targetX = 0;
    var targetY = 0;

    function updateBounds() {
      bounds = stage.getBoundingClientRect();
    }
    updateBounds();
    window.addEventListener('resize', updateBounds);

    stage.addEventListener('mousemove', function (e) {
      if (!bounds) return;
      var x = (e.clientX - bounds.left) / bounds.width - 0.5;
      var y = (e.clientY - bounds.top) / bounds.height - 0.5;
      targetX = y * -10;
      targetY = x * 12;
    });

    stage.addEventListener('mouseleave', function () {
      targetX = 0;
      targetY = 0;
    });

    function animateTilt() {
      currentX += (targetX - currentX) * 0.08;
      currentY += (targetY - currentY) * 0.08;
      wrap.style.transform = 'rotateX(' + currentX + 'deg) rotateY(' + currentY + 'deg) translateZ(12px)';
      requestAnimationFrame(animateTilt);
    }
    animateTilt();
  }

  /* ── Magnetic CTA ── */
  function initMagnetic() {
    if (reduced) return;
    document.querySelectorAll('[data-magnetic]').forEach(function (btn) {
      btn.addEventListener('mousemove', function (e) {
        var rect = btn.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = 'translate(' + (x * 0.18) + 'px, ' + (y * 0.18) + 'px)';
      });
      btn.addEventListener('mouseleave', function () {
        btn.style.transform = '';
      });
    });
  }

  /* ── Scroll reveal + bar animation ── */
  function initScroll() {
    var reveals = document.querySelectorAll('.reveal');
    var routine = document.querySelector('.ghk-routine-steps');

    if (!('IntersectionObserver' in window)) {
      reveals.forEach(function (el) { el.classList.add('visible'); });
      document.querySelectorAll('.ghk-bar-fill').forEach(function (b) {
        b.style.width = b.dataset.width || '0';
      });
      if (routine) routine.classList.add('in-view');
      return;
    }

    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('visible');
        if (entry.target.classList.contains('ghk-bars')) {
          entry.target.querySelectorAll('.ghk-bar-fill').forEach(function (bar) {
            bar.style.width = bar.dataset.width || '0';
          });
        }
        if (entry.target.classList.contains('ghk-routine-steps')) {
          entry.target.classList.add('in-view');
        }
        if (entry.target.classList.contains('ghk-stats')) {
          initCounters(entry.target);
        }
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (el) { obs.observe(el); });
    var barSection = document.querySelector('.ghk-bars');
    if (barSection) obs.observe(barSection);
    if (routine) obs.observe(routine);
    var stats = document.querySelector('.ghk-stats');
    if (stats) obs.observe(stats);
  }

  /* ── Animated counters ── */
  var countersStarted = false;
  function initCounters(root) {
    if (countersStarted || reduced) {
      root.querySelectorAll('[data-count]').forEach(function (el) {
        var suffix = el.dataset.suffix || '';
        var prefix = el.dataset.prefix || '';
        el.textContent = prefix + el.dataset.count + suffix;
      });
      return;
    }
    countersStarted = true;
    root.querySelectorAll('[data-count]').forEach(function (el) {
      var target = parseFloat(el.dataset.count);
      var suffix = el.dataset.suffix || '';
      var prefix = el.dataset.prefix || '';
      var duration = 1400;
      var start = performance.now();

      function tick(now) {
        var t = Math.min(1, (now - start) / duration);
        var eased = 1 - Math.pow(1 - t, 3);
        var val = Math.round(target * eased);
        el.textContent = prefix + val + suffix;
        if (t < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  /* ── Skin scroll cinema ── */
  function initSkinCinema() {
    var section = document.getElementById('ghk-skin-cinema');
    if (!section || reduced) return;

    var scrollEl = section.querySelector('.ghk-skin-scroll');
    var frames = section.querySelectorAll('.ghk-skin-frame');
    var progressFill = section.querySelector('.ghk-skin-progress-fill');
    var dollop = section.querySelector('.ghk-cream-dollop');
    var peptides = section.querySelectorAll('.ghk-pep');
    var signal = section.querySelector('.ghk-signal-pulse');
    var glow = section.querySelector('.ghk-appearance-glow');
    if (!scrollEl || !frames.length) return;

    var frameCount = frames.length;

    function setProgress(p) {
      var clamped = Math.max(0, Math.min(1, p));
      var idx = Math.min(frameCount - 1, Math.floor(clamped * frameCount));

      frames.forEach(function (f, i) {
        f.classList.toggle('is-active', i === idx);
      });
      if (progressFill) progressFill.style.width = (clamped * 100) + '%';

      if (dollop) dollop.setAttribute('opacity', clamped < 0.15 ? clamped / 0.15 : Math.max(0, 1 - (clamped - 0.1) * 2));

      peptides.forEach(function (pep, i) {
        var threshold = 0.15 + i * 0.18;
        var op = clamped >= threshold ? Math.min(1, (clamped - threshold) * 4) : 0;
        pep.setAttribute('opacity', op);
      });

      if (signal) signal.setAttribute('opacity', clamped > 0.45 && clamped < 0.85 ? Math.min(1, (clamped - 0.45) * 2.5) : clamped >= 0.85 ? Math.max(0, 1 - (clamped - 0.85) * 5) : 0);
      if (glow) glow.setAttribute('opacity', clamped > 0.7 ? Math.min(1, (clamped - 0.7) * 3.3) : 0);
    }

    function onScroll() {
      var rect = scrollEl.getBoundingClientRect();
      var total = scrollEl.offsetHeight - window.innerHeight;
      if (total <= 0) return;
      var scrolled = -rect.top;
      setProgress(scrolled / total);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Molecular Matrix dashboard ── */
  function initMatrixDashboard() {
    var section = document.getElementById('ghk-matrix');
    var canvas = document.getElementById('ghk-matrix-canvas');
    var concValue = document.getElementById('ghk-conc-value');
    var concCaption = document.getElementById('ghk-conc-caption');
    var btnAnalyze = document.getElementById('ghk-btn-analyze');
    var btnCompare = document.getElementById('ghk-btn-compare');
    if (!section) return;

    var analyzing = false;
    var comparing = false;
    var concAnim = null;

    function setConcentration(val) {
      if (!concValue) return;
      concValue.textContent = val.toFixed(2) + '%';
    }

    function runConcentrationAnim(toHigh) {
      if (concAnim) cancelAnimationFrame(concAnim);
      var startVal = toHigh ? 0.05 : 3.0;
      var endVal = toHigh ? 3.0 : 0.05;
      var duration = 2000;
      var t0 = performance.now();

      function tick(now) {
        var t = Math.min(1, (now - t0) / duration);
        var eased = 1 - Math.pow(1 - t, 3);
        setConcentration(startVal + (endVal - startVal) * eased);
        if (t < 1) {
          concAnim = requestAnimationFrame(tick);
        } else {
          concAnim = null;
        }
      }
      concAnim = requestAnimationFrame(tick);
    }

    function updateAnalyzeUI() {
      section.classList.toggle('is-analyzing', analyzing);
      if (btnAnalyze) {
        btnAnalyze.setAttribute('aria-pressed', analyzing ? 'true' : 'false');
        btnAnalyze.querySelector('span').textContent = analyzing ? 'Reset bio-metrics' : 'Analyze concentration';
      }
      if (concCaption) {
        concCaption.textContent = analyzing
          ? 'Prescription strength · 30 mg/g GHK-Cu (3%)'
          : 'Typical OTC cosmetic baseline (~0.05–0.1% actual GHK-Cu)';
      }
      runConcentrationAnim(analyzing);
      if (window.clyrTrack) {
        clyrTrack('ghk_matrix_analyze', { active: analyzing, product: 'ghk-cu-cream' });
      }
    }

    function updateCompareUI() {
      section.classList.toggle('is-comparing', comparing);
      if (btnCompare) {
        btnCompare.setAttribute('aria-pressed', comparing ? 'true' : 'false');
        btnCompare.querySelector('span').textContent = comparing ? 'Reset market data' : 'Compare pricing';
      }
      if (window.clyrTrack) {
        clyrTrack('ghk_matrix_compare', { active: comparing, product: 'ghk-cu-cream' });
      }
    }

    if (btnAnalyze) {
      btnAnalyze.addEventListener('click', function () {
        analyzing = !analyzing;
        updateAnalyzeUI();
      });
    }
    if (btnCompare) {
      btnCompare.addEventListener('click', function () {
        comparing = !comparing;
        updateCompareUI();
      });
    }

    setConcentration(0.05);

    // Default to the activated comparison state — no click required
    analyzing = true;
    comparing = true;
    updateAnalyzeUI();
    updateCompareUI();

    if (!canvas || reduced) return;
    var ctx = canvas.getContext('2d');
    var particles = [];
    var running = true;

    function resizeCanvas() {
      var rect = section.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      particles = [];
      for (var i = 0; i < 60; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          r: Math.random() * 2 + 1,
          hue: Math.random() > 0.45 ? 186 : 24,
        });
      }
    }

    function drawMatrix() {
      if (!running) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        var speed = analyzing ? 1.35 : 1;
        p.x += p.vx * speed;
        p.y += p.vy * speed;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.hue === 186
          ? 'rgba(0, 180, 197, 0.55)'
          : 'rgba(201, 120, 74, 0.5)';
        ctx.fill();

        for (var j = i + 1; j < particles.length; j++) {
          var p2 = particles[j];
          var dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = 'rgba(0, 180, 197, ' + (0.12 * (1 - dist / 120)) + ')';
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(drawMatrix);
    }

    resizeCanvas();
    drawMatrix();
    window.addEventListener('resize', resizeCanvas);

    var matrixObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        running = entry.isIntersecting;
        if (running) drawMatrix();
      });
    }, { threshold: 0.05 });
    matrixObs.observe(section);
  }

  /* ── Parallax hero on scroll ── */
  function initParallax() {
    if (reduced) return;
    var visual = document.querySelector('.ghk-hero-panel') || document.querySelector('.ghk-hero-visual');
    var mesh = document.querySelector('.ghk-mesh');
    if (!visual) return;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      if (y > 800) return;
      visual.style.transform = 'translateY(' + (y * 0.05) + 'px)';
      if (mesh) mesh.style.transform = 'translateY(' + (y * 0.03) + 'px)';
    }, { passive: true });
  }

  /* ── Sticky mobile CTA ── */
  function initStickyCta() {
    var bar = document.getElementById('ghk-sticky-cta');
    var hero = document.querySelector('.ghk-hero');
    if (!bar || !hero) return;

    function update() {
      var heroBottom = hero.getBoundingClientRect().bottom;
      var show = heroBottom < 0 && window.innerWidth <= 640;
      bar.classList.toggle('is-visible', show);
      bar.setAttribute('aria-hidden', show ? 'false' : 'true');
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  /* ── Nav solid on scroll past hero ── */
  function initNav() {
    var nav = document.getElementById('nav');
    if (!nav) return;
    window.addEventListener('scroll', function () {
      if (window.scrollY > 80) {
        nav.classList.add('nav-scrolled');
      } else {
        nav.classList.remove('nav-scrolled');
      }
    }, { passive: true });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initLoad();
    initHeroMolecules();
    initParticles();
    initProductTilt();
    initMagnetic();
    initScroll();
    initSkinCinema();
    initMatrixDashboard();
    initParallax();
    initStickyCta();
    initNav();

    if (window._pvFired) return;
    window._pvFired = true;
    if (window.clyrTrack) {
      clyrTrack('product_viewed', { product: 'ghk-cu-cream', source: 'product_page', version: 'v3-matrix' });
    }
  });
})();