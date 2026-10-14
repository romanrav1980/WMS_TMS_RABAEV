(() => {
 "use strict";
 const terminal = new Set(["DONE", "CANCELLED", "SHORT_PICKED"]);
 const unfinished = line => !terminal.has(line.status);
 let lastState = "";
 const originalRender = cpTsdRender;
 cpTsdRender = function () {
  const lines = cpTsd.task?.lines || [];
  const next = lines.findIndex(unfinished);
  const state = JSON.stringify([cpTsd.task?.case_pick_task_id, lines.map(line => [line.case_pick_line_id, line.status, line.picked_qty])]);
  if (next >= 0 && state !== lastState) {
   cpTsd.lineIndex = next;
  }
  lastState = state;
  originalRender();
  let hint = document.getElementById("cpTsdIssuedRoute");
  if (!hint) {
   hint = document.createElement("p");hint.id = "cpTsdIssuedRoute";
   cpTsdEl("cpTsdCounter").parentElement.appendChild(hint);
  }
  const point = next >= 0 ? lines[next] : null;
  const routed = lines.some(line => line.pick_sequence != null);
  hint.textContent = !routed ? "" : point
   ? "Следующая незавершённая точка: " + point.cell_code + ", порядок " + point.pick_sequence + ", слой: " + ({BASE:"основание",MAIN:"основная часть",TOP:"верхний"}[point.stack_stage] || "основная часть") + ". При недостаче дождитесь решения или пополнения."
   : "Все точки выданного маршрута завершены.";
 };
 const originalMove = cpTsdMove;
 cpTsdMove = function (delta) {
  const lines = cpTsd.task?.lines || [];
  if (lines.some(line => line.pick_sequence != null)) {
   cpTsd.lineIndex = Math.max(0, Math.min(lines.length - 1, cpTsd.lineIndex + delta));
   cpTsdRender();return;
  }
  originalMove(delta);
 };
 window.addEventListener("DOMContentLoaded", () => {
  cpTsdEl("cpTsdPrev").title = "Посмотреть предыдущую строку; ядро запрещает возвращаться за товаром.";
  cpTsdEl("cpTsdNext").title = "Посмотреть следующую строку; незавершённая предыдущая точка блокирует отбор.";
 });
})();
