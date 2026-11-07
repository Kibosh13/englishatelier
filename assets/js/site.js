/* English Atelier — site.js (без зависимостей) */
(function () {
  'use strict';
  var d = document, w = window, root = d.documentElement;
  var EA = w.EA || {};
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var reduce = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function sstore(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- Яндекс Метрика: только после согласия ---------- */
  var ymReady = false;
  function loadMetrika() {
    if (ymReady || !EA.metrika) return;
    ymReady = true;
    (function (m, e, t, r, i, k, a) { m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); }; m[i].l = 1 * new Date();
      k = e.createElement(t), a = e.getElementsByTagName(t)[0]; k.async = 1; k.src = r; a.parentNode.insertBefore(k, a); })
      (w, d, 'script', 'https://mc.yandex.ru/metrika/tag.js', 'ym');
    w.ym(+EA.metrika, 'init', { clickmap: true, trackLinks: true, accurateTrackBounce: true, webvisor: false });
  }
  function goal(name) { if (ymReady && w.ym && name) { try { w.ym(+EA.metrika, 'reachGoal', name); } catch (e) {} } }
  w.eaGoal = goal;

  var cookie = $('#cookie'), choice = store('ea-cookies');
  if (choice === 'all') loadMetrika();
  else if (!choice && cookie) cookie.hidden = false;
  if (cookie) {
    $('#cookie-ok').addEventListener('click', function () { store('ea-cookies', 'all'); cookie.hidden = true; loadMetrika(); });
    $('#cookie-no').addEventListener('click', function () { store('ea-cookies', 'necessary'); cookie.hidden = true; });
  }
  d.addEventListener('click', function (e) { var a = e.target.closest('[data-goal]'); if (a) goal(a.getAttribute('data-goal')); });

  /* UTM для заявок */
  if (location.search.indexOf('utm_') > -1 || location.search.indexOf('yclid') > -1) sstore('ea-utm', location.search.slice(1));

  /* ---------- шапка, меню ---------- */
  var top = $('.top'), menuBtn = $('#menu-btn'), nav = $('#site-nav');
  var narrow = w.matchMedia('(max-width: 1100px)');
  function menuOpen() { return top && top.classList.contains('menu-open'); }
  function setMenu(open) {
    if (!menuBtn) return;
    top.classList.toggle('menu-open', open);
    top.classList.remove('is-condensed');
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    d.body.style.overflow = open ? 'hidden' : '';
    if (open) { var f = $('a', nav); if (f) f.focus({ preventScroll: true }); }
    updateFloat();
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(!menuOpen()); });
    $$('a', nav).forEach(function (a) { a.addEventListener('click', function () { if (menuOpen()) setMenu(false); }); });
    d.addEventListener('click', function (e) { if (menuOpen() && !top.contains(e.target)) setMenu(false); });
    var onMq = function () { if (!narrow.matches && menuOpen()) setMenu(false); };
    narrow.addEventListener ? narrow.addEventListener('change', onMq) : narrow.addListener(onMq);
    // удерживаем фокус внутри открытого меню
    top.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab' || !menuOpen()) return;
      var items = [menuBtn].concat($$('a', nav)), first = items[0], last = items[items.length - 1];
      if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* прячем строку с логотипом при прокрутке вниз (полоса разделов остаётся) */
  var lastY = w.scrollY, ticking = false;
  function onScroll() {
    var y = w.scrollY;
    if (top && narrow.matches && !menuOpen()) {
      if (y > 240 && y > lastY + 4) top.classList.add('is-condensed');
      else if (y < lastY - 4 || y < 120) top.classList.remove('is-condensed');
    } else if (top) top.classList.remove('is-condensed');
    lastY = y; ticking = false;
  }
  w.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });

  /* ---------- активный раздел ---------- */
  var chips = $('.chips ul');
  var links = $$('.chips a, .nav a.l');
  var ids = []; links.forEach(function (a) { var id = (a.getAttribute('href') || '').split('#')[1]; if (id && ids.indexOf(id) < 0 && d.getElementById(id)) ids.push(id); });
  ids.sort(function (a, b) { return d.getElementById(a).compareDocumentPosition(d.getElementById(b)) & 4 ? -1 : 1; });
  var current = null;
  function setActive(id) {
    if (id === current) return; current = id;
    links.forEach(function (a) { var on = a.getAttribute('href').split('#')[1] === id; if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
    var chip = chips && $('a[aria-current="true"]', chips);
    if (chip) {
      var li = chip.parentNode, left = li.offsetLeft - 20;
      chips.scrollTo ? chips.scrollTo({ left: left, behavior: reduce ? 'auto' : 'smooth' }) : (chips.scrollLeft = left);
    }
  }
  function spy() {
    var line = (top ? top.getBoundingClientRect().bottom : 0) + w.innerHeight * 0.25, found = null;
    ids.forEach(function (id) { var r = d.getElementById(id).getBoundingClientRect(); if (r.top <= line) found = id; });
    if (w.innerHeight + w.scrollY >= d.documentElement.scrollHeight - 4) found = ids[ids.length - 1];
    setActive(found);
  }
  if (ids.length) { w.addEventListener('scroll', function () { requestAnimationFrame(spy); }, { passive: true }); spy(); }

  /* ---------- плавающая кнопка записи ---------- */
  var fl = $('#float'), consult = $('#consult'), hero = $('.hero'), mini = $('#mini');
  var vis = { hero: true, consult: false, mini: false }, focusField = false;
  function updateFloat() {
    if (!fl) return;
    var lb = $('#lb');
    var hide = vis.hero || vis.consult || vis.mini || focusField || menuOpen() || (lb && !lb.hidden);
    fl.classList.toggle('is-hidden', hide);
    fl.setAttribute('aria-hidden', hide ? 'true' : 'false');
    fl.tabIndex = hide ? -1 : 0;
  }
  if (fl && 'IntersectionObserver' in w) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.target === hero) vis.hero = e.isIntersecting; if (e.target === consult) vis.consult = e.isIntersecting; if (e.target === mini) vis.mini = e.isIntersecting; });
      updateFloat();
    }, { threshold: 0, rootMargin: '0px 0px -15% 0px' });
    [hero, consult, mini].forEach(function (el) { if (el) io.observe(el); });
  } else if (fl) { vis.hero = false; updateFloat(); }
  d.addEventListener('focusin', function (e) { if (e.target.matches('input,textarea,select')) { focusField = true; updateFloat(); } });
  d.addEventListener('focusout', function (e) { if (e.target.matches('input,textarea,select')) { focusField = false; setTimeout(updateFloat, 50); } });

  /* ---------- выбор тарифа подставляет цель ---------- */
  var goalSel = $('#goal');
  $$('[data-pick]').forEach(function (a) { a.addEventListener('click', function () { if (goalSel) goalSel.value = a.getAttribute('data-pick'); }); });

  /* ---------- дополнительные документы ---------- */
  var tg = $('#extra-toggle'), panel = $('#extra-panel');
  if (tg) tg.addEventListener('click', function () {
    var open = tg.getAttribute('aria-expanded') === 'true';
    tg.setAttribute('aria-expanded', String(!open)); panel.hidden = open; $('.extra-icon', tg).textContent = open ? '+' : '−';
  });

  /* ---------- лента документов: бесшовные клоны вне Tab, пауза касанием ---------- */
  var gallery = $('#gallery'), marquee = $('#marquee');
  if (gallery) {
    $$('.mat', gallery).forEach(function (b) {
      var c = b.cloneNode(true); c.setAttribute('aria-hidden', 'true'); c.tabIndex = -1; c.removeAttribute('data-i');
      c.addEventListener('click', function () { b.click(); });
      gallery.appendChild(c);
    });
    var resume = null;
    marquee.addEventListener('touchstart', function () { clearTimeout(resume); marquee.classList.add('paused'); }, { passive: true });
    marquee.addEventListener('touchend', function () { clearTimeout(resume); resume = setTimeout(function () { marquee.classList.remove('paused'); }, 5000); }, { passive: true });
  }

  /* ---------- просмотрщик ---------- */
  var lb = $('#lb');
  if (lb) {
    var img = $('#lb-img'), cap = $('#lb-cap'), cnt = $('#lb-count'), set = [], cur = 0, opener = null, sx = null, sy = null;
    var webp = (function () { try { return d.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp') === 0; } catch (e) { return false; } })();
    var groups = { docs: $$('[data-group="docs"][data-i]'), samples: $$('[data-group="samples"]') };
    groups.docs.sort(function (a, b) { return a.getAttribute('data-i') - b.getAttribute('data-i'); });
    function show(i) {
      cur = (i + set.length) % set.length;
      var b = set[cur], t = $('img', b);
      img.src = b.getAttribute('data-full') + (webp ? '.webp' : '.jpg');
      img.alt = t.alt; cap.textContent = t.alt; cnt.textContent = (cur + 1) + ' / ' + set.length;
    }
    function open(group, el) {
      if (menuOpen()) setMenu(false);
      set = groups[group]; opener = el; show(set.indexOf(el));
      lb.hidden = false; d.body.style.overflow = 'hidden'; $('#lb-close').focus(); updateFloat();
      goal(group === 'docs' ? 'doc_open' : 'sample_open');
    }
    function close() { lb.hidden = true; d.body.style.overflow = ''; img.removeAttribute('src'); if (opener) opener.focus({ preventScroll: true }); updateFloat(); }
    Object.keys(groups).forEach(function (g) { groups[g].forEach(function (b) { b.addEventListener('click', function () { open(g, b); }); }); });
    $('#lb-prev').addEventListener('click', function () { show(cur - 1); });
    $('#lb-next').addEventListener('click', function () { show(cur + 1); });
    $('#lb-close').addEventListener('click', close);
    lb.addEventListener('click', function (e) { if (e.target === lb || e.target.id === 'lb-stage') close(); });
    lb.addEventListener('touchstart', function (e) { if (e.touches.length !== 1) { sx = null; return; } sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (sx === null || !e.changedTouches.length) return;
      var dx = e.changedTouches[0].clientX - sx, dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) show(cur + (dx < 0 ? 1 : -1));
      else if (dy > 110 && Math.abs(dy) > Math.abs(dx) * 1.5) close();
      sx = null;
    }, { passive: true });
    d.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'ArrowRight') show(cur + 1);
      else if (e.key === 'Tab') {
        var c = $$('button', lb), f = c[0], l = c[c.length - 1];
        if (e.shiftKey && d.activeElement === f) { e.preventDefault(); l.focus(); }
        else if (!e.shiftKey && d.activeElement === l) { e.preventDefault(); f.focus(); }
      }
    });
  }
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menuOpen() && (!lb || lb.hidden)) { setMenu(false); menuBtn.focus(); } });

  /* ---------- анимация: появление, счётчики, параллакс, лента прогресса ---------- */
  var bar = $('#progress-bar');
  function progress() { if (!bar) return; var h = d.documentElement.scrollHeight - w.innerHeight; bar.style.setProperty('--p', h > 0 ? Math.min(1, w.scrollY / h).toFixed(4) : 0); }
  w.addEventListener('scroll', function () { requestAnimationFrame(progress); }, { passive: true }); progress();

  if (!reduce && 'IntersectionObserver' in w) {
    // что проявляется при прокрутке; data-группы получают задержку «лесенкой»
    var groups = [
      ['.sec-head > *', 1], ['.stats .stat', 1], ['.about-text > *', 1], ['.school', 1],
      ['.method-step', 1], ['.method-note, .inline-cta', 0], ['.track-label', 0], ['.cards .card', 1],
      ['.wide-card .card', 0], ['.sample', 1], ['.consult-copy > *', 1], ['.lead-box', 0],
      ['.extra-docs', 0], ['.q', 1], ['.faq-list details', 1], ['.faq-contact', 0], ['.foot-grid > *', 1], ['.legal', 0],
      ['.doc h2, .doc p, .doc .tbl, .doc ul', 0]
    ];
    var seen = [];
    groups.forEach(function (g) {
      var parents = new Map();
      $$(g[0]).forEach(function (el) {
        if (seen.indexOf(el) > -1 || el.closest('.hero')) return; seen.push(el);
        el.classList.add('rv'); if (el.matches('.consult-copy > *, .about-text > *')) el.classList.add('rv-l');
        if (g[1]) { var p = el.parentNode, n = parents.get(p) || 0; el.style.setProperty('--i', Math.min(n, 6)); parents.set(p, n + 1); }
      });
    });
    var rio = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); rio.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    $$('.rv').forEach(function (el) {
      // то, что уже на экране при загрузке, показываем сразу
      if (el.getBoundingClientRect().top < w.innerHeight * 0.92) el.classList.add('in'); else rio.observe(el);
    });

    // счётчики цифр «5» и «7+»
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; cio.unobserve(e.target);
        var node = e.target.firstChild, to = parseInt(node.nodeValue, 10), t0 = null;
        function step(t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 1200); node.nodeValue = String(Math.round(to * (1 - Math.pow(1 - k, 3)))); if (k < 1) requestAnimationFrame(step); }
        node.nodeValue = '0'; requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    $$('.stat .n').forEach(function (n) { if (n.firstChild && /^\d+$/.test((n.firstChild.nodeValue || '').trim())) cio.observe(n); });

    // лёгкий параллакс фото на первом экране
    var ph = $('.portrait'), heroEl = $('.hero');
    if (ph && heroEl) w.addEventListener('scroll', function () {
      requestAnimationFrame(function () { var y = w.scrollY; if (y < heroEl.offsetHeight) ph.style.setProperty('--py', Math.min(y * 0.04, 16).toFixed(1) + 'px'); });
    }, { passive: true });
  }

  /* ---------- формы заявки ---------- */
  var t0 = Date.now();
  function validContact(v) {
    v = v.trim();
    if (/^(https?:\/\/)?(t\.me|telegram\.me)\/[A-Za-z0-9_]{4,32}$/i.test(v)) return true;
    if (/^@?[A-Za-z][A-Za-z0-9_]{3,31}$/.test(v)) return true;               // @username
    var digits = v.replace(/\D/g, '');
    return /^[+\d\s()\-.]+$/.test(v) && digits.length >= 10 && digits.length <= 15; // телефон
  }
  function fieldErr(wrap, on, errEl, input) {
    if (wrap) wrap.classList.toggle('err', on);
    if (errEl) errEl.hidden = !on;
    if (input) input.setAttribute('aria-invalid', on ? 'true' : 'false');
  }
  $$('.lead-form').forEach(function (form) {
    var src = form.getAttribute('data-source'), msg = $('.form-msg', form), btn = $('button[type=submit]', form);
    var name = $('[name=name]', form), contact = $('[name=contact]', form), agree = $('[name=agree]', form);
    var row = $('.mini-row', form);
    function check() {
      var bad = null;
      if (name) { var e1 = !name.value.trim(); fieldErr($('#f-name'), e1, $('#name-err'), name); if (e1) bad = bad || name; }
      var e2 = !validContact(contact.value);
      if (row) { row.classList.toggle('err', e2); contact.setAttribute('aria-invalid', e2 ? 'true' : 'false'); }
      else fieldErr($('#f-contact'), e2, $('#contact-err'), contact);
      if (e2) bad = bad || contact;
      var e3 = !agree.checked; agree.closest('.check').classList.toggle('err', e3); if (e3) bad = bad || agree;
      if (bad) {
        msg.textContent = (name && !name.value.trim()) ? 'Укажите имя и телефон или Telegram.'
          : e2 ? 'Проверьте контакт: нужен номер телефона или @username в Telegram.'
          : 'Отметьте согласие на обработку персональных данных.';
        bad.focus();
        return false;
      }
      msg.textContent = ''; return true;
    }
    [name, contact, agree].forEach(function (el) { if (el) el.addEventListener(el.type === 'checkbox' ? 'change' : 'input', function () { if (msg.textContent) check(); }); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!check()) return;
      var fd = new FormData(form);
      fd.append('source', src); fd.append('page', location.pathname); fd.append('t', String(Math.round((Date.now() - t0) / 1000)));
      fd.append('utm', sstore('ea-utm') || '');
      if (!fd.get('agree')) fd.set('agree', 'on');
      btn.disabled = true; var label = btn.innerHTML; btn.innerHTML = src === 'footer' ? '…' : 'Отправляем…';
      // Превью на GitHub Pages: PHP там не работает, показываем успешную отправку без реальной заявки
      var demo = /\.github\.io$/.test(location.hostname);
      (demo ? new Promise(function (res) { setTimeout(function () { res({ ok: true, demo: true }); }, 600); })
        : fetch(form.getAttribute('action'), { method: 'POST', body: fd, headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return { ok: false }; }).then(function (j) { j.status = r.status; return j; }); }))
        .then(function (j) {
          if (!j.ok) throw j;
          goal('lead_sent'); goal('lead_sent_' + src);
          var demoNote = j.demo ? '<p class="small" style="color:var(--err)">Демо-превью: заявка никуда не отправлена.</p>' : '';
          if (src === 'main') {
            form.hidden = true; var done = $('#lead-done'); if (demoNote) done.insertAdjacentHTML('beforeend', demoNote); done.hidden = false; done.focus({ preventScroll: true });
            done.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' });
          } else {
            form.innerHTML = '<div class="mini-done" tabindex="-1"><span class="tick" aria-hidden="true">✓</span><span>Заявка отправлена. Анна свяжется с вами по указанному контакту.</span></div>' + demoNote;
            $('.mini-done', form).focus({ preventScroll: true });
          }
        })
        .catch(function (j) {
          btn.disabled = false; btn.innerHTML = label;
          msg.innerHTML = (j && j.error === 'rate') ? 'Слишком много попыток. Подождите пару минут и попробуйте снова.'
            : 'Не удалось отправить заявку. Попробуйте ещё раз или <a href="' + EA.tg + '" target="_blank" rel="noopener noreferrer">напишите в Telegram</a>.';
        });
    });
  });
})();
