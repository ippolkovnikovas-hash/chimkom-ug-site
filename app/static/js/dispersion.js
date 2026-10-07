// Анимация «Диспергирование» для главной страницы.
// Частицы цемента слиплись в комки; по мере прокрутки к блоку на них
// садятся частицы добавки (зелёные), и комки расходятся равномерно.
// Курсор расталкивает частицы. Без зависимостей, только <canvas>.
(function () {
  "use strict";

  var canvas = document.getElementById("dispersion-canvas");
  if (!canvas || !canvas.getContext) return;

  var ctx = canvas.getContext("2d");
  var box = canvas.parentElement;
  var reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var N = 240;             // частицы цемента
  var CLUSTERS = 12;       // комков в исходном состоянии
  var ADDITIVE_EVERY = 2;  // зелёная частица добавки на каждую N-ю частицу цемента
  var BG = "#1a1a1a";
  var GREEN = "95, 201, 53"; // #5fc935 — фирменный зелёный

  // Детерминированный генератор случайных чисел — картинка одинаковая при каждой загрузке
  var seed = 7;
  function rand() {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  }
  function gauss() {
    return Math.sqrt(-2 * Math.log(rand() + 1e-9)) * Math.cos(2 * Math.PI * rand());
  }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function smooth(a, b, v) { var x = clamp((v - a) / (b - a), 0, 1); return x * x * (3 - 2 * x); }

  // Центры комков — в круге вокруг центра (координаты 0..1)
  var centers = [];
  for (var c = 0; c < CLUSTERS; c++) {
    var ang = rand() * Math.PI * 2;
    var rad = 0.08 + Math.sqrt(rand()) * 0.30;
    centers.push({ x: 0.5 + Math.cos(ang) * rad, y: 0.5 + Math.sin(ang) * rad });
  }

  // Частицы: исходное положение в комке
  var particles = [];
  for (var i = 0; i < N; i++) {
    var cl = i % CLUSTERS;
    particles.push({
      cluster: cl,
      cx: centers[cl].x + gauss() * 0.028,
      cy: centers[cl].y + gauss() * 0.028,
      r: 0.0045 + rand() * 0.0045,
      shade: 120 + Math.floor(rand() * 70),
      phase: rand() * Math.PI * 2,
      speed: 0.6 + rand() * 0.8,
      x: 0, y: 0, vx: 0, vy: 0
    });
  }

  // Конечное положение — равномерно («подсолнух»), назначаем по углу,
  // чтобы частицы расходились из комков, а не пересекали весь квадрат
  var golden = Math.PI * (3 - Math.sqrt(5));
  var spots = [];
  for (var k = 0; k < N; k++) {
    var rr = 0.44 * Math.sqrt((k + 0.5) / N);
    spots.push({ x: 0.5 + Math.cos(k * golden) * rr, y: 0.5 + Math.sin(k * golden) * rr });
  }
  function angleKey(p) { return Math.atan2(p.y - 0.5, p.x - 0.5) * 10 + Math.hypot(p.x - 0.5, p.y - 0.5); }
  var byAngle = particles.slice().sort(function (a, b) {
    return angleKey({ x: a.cx, y: a.cy }) - angleKey({ x: b.cx, y: b.cy });
  });
  spots.sort(function (a, b) { return angleKey(a) - angleKey(b); });
  byAngle.forEach(function (p, idx) { p.dx = spots[idx].x; p.dy = spots[idx].y; });

  // Пары соседей внутри комка — рисуем между ними «связи»
  var bonds = [];
  for (var a = 0; a < N; a++) {
    for (var b = a + 1; b < N; b++) {
      var pa = particles[a], pb = particles[b];
      if (pa.cluster === pb.cluster && Math.hypot(pa.cx - pb.cx, pa.cy - pb.cy) < 0.04) {
        bonds.push([pa, pb]);
      }
    }
  }

  var W = 0, dpr = 1;
  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = box.clientWidth;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(W * dpr);
    canvas.style.width = W + "px";
    canvas.style.height = W + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // Прогресс диспергирования от положения блока на экране
  var progress = reduceMotion ? 1 : 0, target = progress;
  function scrollTarget() {
    var rect = box.getBoundingClientRect();
    var vh = window.innerHeight || 800;
    return clamp((vh * 0.85 - rect.top) / (rect.height * 0.9), 0, 1);
  }

  var mouse = { x: -1, y: -1, active: false }, lastTouch = -1e9;
  function setMouse(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    mouse.x = (clientX - rect.left) / W;
    mouse.y = (clientY - rect.top) / W;
    mouse.active = true;
  }
  box.addEventListener("mousemove", function (e) {
    // После касания браузер телефона присылает «мышиное» событие — пропускаем его
    if (Date.now() - lastTouch < 1000) return;
    setMouse(e.clientX, e.clientY);
  });
  box.addEventListener("mouseleave", function () { mouse.active = false; });
  // Телефон: палец расталкивает частицы после тапа по блоку (js/touch-play.js)
  box.addEventListener("touchstart", function () { lastTouch = Date.now(); }, { passive: true });
  if (window.touchPlay) {
    window.touchPlay(box, function (x, y) {
      lastTouch = Date.now();
      setMouse(x, y);
    }, function () { mouse.active = false; });
  }

  var placed = false;
  function step(time) {
    var t = smooth(0, 1, progress);
    // Постоянное «плавание» частиц: в комках — меньше, после диспергирования — свободнее
    var wobble = 0.006 * (1 - t) + 0.014 * t;
    var s = time * 0.001;

    for (var i = 0; i < N; i++) {
      var p = particles[i];
      // Комки целиком медленно дрейфуют
      var cd = centers[p.cluster];
      var driftX = Math.cos(s * 0.35 + cd.x * 9) * 0.012 * (1 - t);
      var driftY = Math.sin(s * 0.3 + cd.y * 9) * 0.012 * (1 - t);
      var wx = Math.cos(s * p.speed + p.phase) + 0.5 * Math.sin(s * p.speed * 1.7 + p.phase * 2);
      var wy = Math.sin(s * p.speed * 0.9 + p.phase) + 0.5 * Math.cos(s * p.speed * 1.3 + p.phase * 3);
      var tx = p.cx + driftX + (p.dx - p.cx) * t + wx * wobble;
      var ty = p.cy + driftY + (p.dy - p.cy) * t + wy * wobble;
      if (!placed) { p.x = tx; p.y = ty; }

      var fx = (tx - p.x) * 0.08, fy = (ty - p.y) * 0.08;
      if (mouse.active && !reduceMotion) {
        var mx = p.x - mouse.x, my = p.y - mouse.y, md = Math.hypot(mx, my);
        if (md < 0.12 && md > 1e-4) {
          var push = (0.12 - md) / 0.12 * 0.012;
          fx += mx / md * push; fy += my / md * push;
        }
      }
      p.vx = (p.vx + fx) * 0.78;
      p.vy = (p.vy + fy) * 0.78;
      p.x += p.vx; p.y += p.vy;
    }
    placed = true;
    return t;
  }

  function draw(t) {
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, W, W);

    // Связи между частицами в комках — исчезают по мере диспергирования
    var bondAlpha = 0.35 * (1 - smooth(0, 0.6, t));
    if (bondAlpha > 0.01) {
      ctx.strokeStyle = "rgba(200, 200, 200, " + bondAlpha + ")";
      ctx.lineWidth = 0.6;
      ctx.beginPath();
      for (var j = 0; j < bonds.length; j++) {
        var a = bonds[j][0], b = bonds[j][1];
        ctx.moveTo(a.x * W, a.y * W);
        ctx.lineTo(b.x * W, b.y * W);
      }
      ctx.stroke();
    }

    // Частицы цемента
    for (var i = 0; i < N; i++) {
      var p = particles[i];
      ctx.fillStyle = "rgb(" + p.shade + "," + p.shade + "," + p.shade + ")";
      ctx.beginPath();
      ctx.arc(p.x * W, p.y * W, p.r * W, 0, Math.PI * 2);
      ctx.fill();
    }

    // Частицы добавки — появляются и «садятся» на поверхность цемента
    var addAlpha = smooth(0.05, 0.5, t);
    if (addAlpha > 0.01) {
      ctx.fillStyle = "rgba(" + GREEN + ", " + addAlpha + ")";
      for (var m = 0; m < N; m += ADDITIVE_EVERY) {
        var q = particles[m];
        var dist = q.r * W + 2 + (1 - addAlpha) * 14;
        var ax = q.x * W + Math.cos(q.phase) * dist;
        var ay = q.y * W + Math.sin(q.phase) * dist;
        ctx.beginPath();
        ctx.arc(ax, ay, Math.max(1.2, W * 0.0028), 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  var visible = false, rafId = null;
  function frame(time) {
    rafId = null;
    target = scrollTarget();
    progress += (target - progress) * 0.06;
    draw(step(time));
    if (visible) rafId = requestAnimationFrame(frame);
  }
  function start() { if (!rafId) rafId = requestAnimationFrame(frame); }

  resize();
  window.addEventListener("resize", function () { resize(); if (reduceMotion) draw(step(0)); });

  if (reduceMotion || !("IntersectionObserver" in window)) {
    progress = 1;
    draw(step(0));
    if (!reduceMotion) { visible = true; start(); }
    return;
  }

  draw(step(0));
  new IntersectionObserver(function (entries) {
    visible = entries[0].isIntersecting;
    if (visible) start();
  }).observe(box);
})();
