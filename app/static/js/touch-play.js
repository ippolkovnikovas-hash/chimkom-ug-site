// «Включение касанием» для интерактивных анимаций на телефоне.
// По умолчанию зона прокручивается вместе со страницей. Короткое касание
// включает режим: прокрутка в зоне блокируется, палец управляет анимацией.
// Режим выключается через 3 с без касаний или при касании вне зоны.
// Использование: touchPlay(element, onMove(clientX, clientY), onEnd()).
(function () {
  "use strict";

  var IDLE_MS = 3000;   // через сколько без касаний режим выключается
  var TAP_MS = 400;     // касание короче — это «тап»
  var TAP_MOVE = 10;    // сдвиг пальца больше (px) — это прокрутка, а не тап

  window.touchPlay = function (el, onMove, onEnd) {
    var active = false, timer = null, start = null;

    var hint = document.createElement("div");
    hint.className = "touch-play-hint";
    hint.setAttribute("aria-hidden", "true");
    el.appendChild(hint);

    function setActive(on) {
      active = on;
      el.classList.toggle("touch-play-active", on);
      hint.textContent = on ? "Водите пальцем" : "Коснитесь, чтобы поиграть";
      if (!on) { clearTimeout(timer); onEnd(); }
    }
    function armTimer() {
      clearTimeout(timer);
      timer = setTimeout(function () { setActive(false); }, IDLE_MS);
    }

    el.addEventListener("touchstart", function (e) {
      var t = e.touches[0];
      start = { x: t.clientX, y: t.clientY, time: Date.now() };
      if (active) { clearTimeout(timer); onMove(t.clientX, t.clientY); }
    }, { passive: true });

    // Не passive: в активном режиме отменяем прокрутку страницы
    el.addEventListener("touchmove", function (e) {
      var t = e.touches[0];
      if (active) {
        e.preventDefault();
        onMove(t.clientX, t.clientY);
      } else if (start && Math.hypot(t.clientX - start.x, t.clientY - start.y) > TAP_MOVE) {
        start = null; // человек листает страницу
      }
    }, { passive: false });

    el.addEventListener("touchend", function () {
      if (active) {
        onEnd();
        armTimer();
      } else if (start && Date.now() - start.time < TAP_MS) {
        setActive(true);
        armTimer();
      }
      start = null;
    }, { passive: true });

    // Касание вне зоны — сразу выключаем
    document.addEventListener("touchstart", function (e) {
      if (active && !el.contains(e.target)) setActive(false);
    }, { passive: true });

    setActive(false);
  };
})();
