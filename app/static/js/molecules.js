// «Молекулярная сетка» в тёмных шапках внутренних страниц (.page-heading).
// Точки медленно дрейфуют и соединяются тонкими линиями; к курсору (или пальцу
// на телефоне) тянутся зелёные связи. На устройствах без мыши, пока шапку
// не трогают, по ней медленно скользит невидимая точка с бледными связями.
// Без зависимостей, только <canvas>.
(function () {
  "use strict";

  var hero = document.querySelector(".page-heading");
  var canvas = document.createElement("canvas");
  if (!hero || !canvas.getContext) return;

  var ctx = canvas.getContext("2d");
  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var noHover = window.matchMedia && window.matchMedia("(hover: none)").matches;
  var GREEN = "95, 201, 53"; // #5fc935 — фирменный зелёный

  canvas.className = "molecules-canvas";
  canvas.setAttribute("aria-hidden", "true");
  hero.insertBefore(canvas, hero.firstChild);

  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function rnd(a, b) { return a + Math.random() * (b - a); }

  var W = 0, H = 0, LINK = 130, nodes = [];
  function resize() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = hero.clientWidth;
    H = hero.clientHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    LINK = clamp(W / 10, 90, 140);
    var n = clamp(Math.round(W * H / 16000), 18, 70);
    nodes = [];
    for (var i = 0; i < n; i++) {
      nodes.push({ x: rnd(0, W), y: rnd(0, H), vx: rnd(-0.2, 0.2), vy: rnd(-0.2, 0.2) });
    }
  }

  // Указатель: мышь, палец или «призрак» на тач-устройствах.
  // strength плавно растёт при касании/наведении и гаснет после.
  var pointer = { x: 0, y: 0, on: false, strength: 0, lastTouch: -1e9 };
  function setPointer(clientX, clientY) {
    var r = hero.getBoundingClientRect();
    pointer.x = clientX - r.left;
    pointer.y = clientY - r.top;
    pointer.on = pointer.x >= 0 && pointer.y >= 0 && pointer.x <= r.width && pointer.y <= r.height;
  }
  // Слушаем документ: меню сайта лежит поверх шапки
  document.addEventListener("mousemove", function (e) {
    // После касания браузер телефона присылает «мышиное» событие — не даём связям залипнуть
    if (performance.now() - pointer.lastTouch < 1000) return;
    setPointer(e.clientX, e.clientY);
  });
  hero.addEventListener("mouseleave", function () { pointer.on = false; });
  function onTouch(e) {
    var t = e.touches[0];
    if (t) { setPointer(t.clientX, t.clientY); pointer.lastTouch = performance.now(); }
  }
  // passive — касание не мешает прокрутке страницы
  document.addEventListener("touchstart", onTouch, { passive: true });
  document.addEventListener("touchmove", onTouch, { passive: true });
  document.addEventListener("touchend", function () { pointer.on = false; }, { passive: true });

  function draw(time) {
    ctx.clearRect(0, 0, W, H);
    ctx.lineWidth = 1;

    // Куда тянутся зелёные связи: реальный указатель или «призрак»
    var px = pointer.x, py = pointer.y, target = pointer.on ? 1 : 0;
    var idle = noHover && !pointer.on && time - pointer.lastTouch > 3000;
    if (idle) {
      px = W * (0.5 + 0.35 * Math.sin(time / 7000));
      py = H * (0.5 + 0.3 * Math.sin(time / 4300));
      target = 0.45;
    }
    pointer.strength += (target - pointer.strength) * 0.06;
    var reach = LINK * 1.4;

    for (var i = 0; i < nodes.length; i++) {
      var p = nodes[i];
      if (!reduceMotion) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
      }
      for (var j = i + 1; j < nodes.length; j++) {
        var q = nodes[j], d = Math.hypot(p.x - q.x, p.y - q.y);
        if (d < LINK) {
          ctx.strokeStyle = "rgba(255, 255, 255, " + (0.14 * (1 - d / LINK)) + ")";
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
        }
      }
      if (pointer.strength > 0.01) {
        var md = Math.hypot(p.x - px, p.y - py);
        if (md < reach) {
          ctx.strokeStyle = "rgba(" + GREEN + ", " + (0.5 * (1 - md / reach) * pointer.strength) + ")";
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(px, py); ctx.stroke();
        }
      }
      ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
      ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, Math.PI * 2); ctx.fill();
    }
  }

  resize();
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { resize(); if (reduceMotion) draw(0); }, 150);
  });

  // При «уменьшить движение» — одна статичная картинка
  if (reduceMotion || !("IntersectionObserver" in window)) {
    draw(0);
    if (reduceMotion) return;
  }

  // Анимация работает только пока шапка видна
  var visible = true, rafId = null;
  function frame(time) {
    rafId = null;
    draw(time);
    if (visible) rafId = requestAnimationFrame(frame);
  }
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible && !rafId) rafId = requestAnimationFrame(frame);
    }).observe(hero);
  } else {
    rafId = requestAnimationFrame(frame);
  }
})();
