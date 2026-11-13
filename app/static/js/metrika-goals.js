/* Цели Яндекс.Метрики (reachGoal).
   Счётчик подключается в base.html, его id — в window.YM_COUNTER_ID.
   Одноразовая цель после успешной отправки формы — window.YM_GOAL_ON_LOAD. */
(function () {
  "use strict";

  function reachGoal(name) {
    if (window.YM_COUNTER_ID && typeof window.ym === "function") {
      window.ym(window.YM_COUNTER_ID, "reachGoal", name);
    }
  }

  // Клики по телефону и мессенджерам (шапка, футер, страницы)
  document.addEventListener("click", function (event) {
    var link = event.target.closest ? event.target.closest("a[href]") : null;
    if (!link) return;
    var href = link.getAttribute("href") || "";
    if (href.indexOf("tel:") === 0) reachGoal("phone_click");
    else if (href.indexOf("wa.me") !== -1) reachGoal("whatsapp_click");
    else if (href.indexOf("t.me") !== -1) reachGoal("telegram_click");
    else if (href.indexOf("max.ru") !== -1) reachGoal("max_click");
  });

  // Цель из формы: маршрут записал её в сессию, шаблон вывел на странице-ответе
  if (window.YM_GOAL_ON_LOAD) reachGoal(window.YM_GOAL_ON_LOAD);
})();
