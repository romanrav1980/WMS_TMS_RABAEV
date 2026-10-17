/* Передача CASE другому комплектовщику (C0121/C0122): долговечный журнал на wmsCommandIntent, точный повтор
   тем же offline_event_id и телом. Неизвестный исход снимается только ответом 200 или неизменной серверной
   квитанцией этого же запроса (transfer-receipt). Текущий исполнитель карточки квитанцией не является.
   Серверной отмены передачи нет: архив или копия в браузере не отменяют поздний запрос и не разблокируют новый. */
(() => {
  const NEW_PREFIX = "retailcase.caseHandoff:";
  const LEGACY_PREFIX = "case.handoff:";
  const FIELDS = ["to_resource_id", "to_resource_session_id", "to_equipment_id", "reason", "offline_event_id", "scan_container",
    "expected_content_version", "expected_assigned_to", "expected_from_session_id", "expected_assignment_version"];
  const REFUSED = [400, 403, 404, 409, 422];
  const pos = v => Number.isSafeInteger(v) && v > 0;
  const user = () => window.wmsAdminAuth?.state?.user?.username || "";
  const text = (v, min, max) => typeof v === "string" && v.trim().length >= min && v.length <= max;

  function validBody(b) {
    return Boolean(b && typeof b === "object" && !Array.isArray(b) && pos(b.to_resource_id) && pos(b.to_resource_session_id)
      && (b.to_equipment_id == null || pos(b.to_equipment_id)) && text(b.reason, 1, 1000)
      && typeof b.offline_event_id === "string" && /^HANDOFF:[A-Za-z0-9-]{8,90}$/.test(b.offline_event_id)
      && (b.scan_container == null || text(b.scan_container, 1, 150))
      && Number.isSafeInteger(b.expected_content_version) && b.expected_content_version >= 0
      && (b.expected_assignment_version == null || Number.isSafeInteger(b.expected_assignment_version) && b.expected_assignment_version >= 0)
      && (b.expected_assigned_to == null || text(b.expected_assigned_to, 1, 100))
      && (b.expected_from_session_id == null || pos(b.expected_from_session_id)));
  }
  const validNew = v => Boolean(v && pos(v.task) && validBody(v.body));

  function key(prefix, task) {
    if (!user()) throw new Error("Войдите в систему.");
    return prefix + caseApiBase() + ":" + user() + ":" + task;
  }
  function journals(task) {
    const make = (prefix, valid) => window.wmsCommandIntent.create(prefix, valid,
      { storageKey: () => key(prefix, task), invalid: "Некорректный запрос передачи." });
    return { legacy: make(LEGACY_PREFIX, validBody), fresh: make(NEW_PREFIX, validNew) };
  }

  /** Сохранённый запрос задания. Прежний (legacy) разбирается первым: его исход всегда считается неизвестным. */
  function entry(task) {
    const j = journals(task), legacy = j.legacy.read();
    if (legacy.raw !== null) return { kind: "legacy", task, journal: j.legacy, record: legacy, body: legacy.value };
    const fresh = j.fresh.read();
    if (fresh.raw !== null) return { kind: "new", task, journal: j.fresh, record: fresh, body: fresh.value?.body ?? null };
    return { kind: null, task, journal: j.fresh, record: fresh, body: null };
  }

  /** Новое намерение: тело сохраняется до отправки и потом не меняется. */
  function create(task, current, form) {
    const body = {
      to_resource_id: form.resource, to_resource_session_id: form.session, to_equipment_id: form.equipment ?? null,
      reason: form.reason.trim(), offline_event_id: "HANDOFF:" + crypto.randomUUID(), scan_container: form.scan || null,
      expected_content_version: current.content_version, expected_assigned_to: current.assigned_to ?? null,
      expected_from_session_id: current.resource_session_id ?? null, expected_assignment_version: current.assignment_version ?? null,
    };
    journals(task).fresh.save({ task, body });
    return entry(task);
  }

  /** Снять запрос можно только после доказанного исхода. Повреждённая запись удаляется напрямую (journal.settle её не примет). */
  function finish(e) {
    const r = e.record;
    if (r.damaged) {
      if (localStorage.getItem(r.storageKey) !== r.raw) throw new Error("Сохранённый запрос изменился. Перечитайте карточку.");
      localStorage.removeItem(r.storageKey);
    } else e.journal.settle(r);
    localStorage.removeItem(r.storageKey + ":delivery");
  }

  const eventId = e => e.body?.offline_event_id ?? e.record.raw?.match(/HANDOFF:[A-Za-z0-9-]{8,90}/)?.[0] ?? null;

  /** Квитанция совпадает, только если это тот же запрос: задание, ключ, автор, источник и каждое поле тела.
      Отсутствующее поле приравнивается к null только для nullable-полей DTO (все, кроме to_resource_id). */
  function sameRequest(request, body) {
    if (!request || typeof request !== "object") return false;
    return FIELDS.every(f => f === "to_resource_id" ? request[f] === body[f] : (request[f] ?? null) === (body[f] ?? null));
  }
  function receiptMatches(r, e, id) {
    return Boolean(r && r.case_pick_task_id === e.task && r.status === "TRANSFERRED" && r.offline_event_id === id
      && r.actor === user() && r.outcome_confirmed === true && r.source === "IMMUTABLE_TRANSFERRED_EVENT"
      && (e.body ? sameRequest(r.request, e.body) : r.request?.offline_event_id === id));
  }

  /** Проверить серверную квитанцию. confirmed — доказанный исход; всё остальное — исход не подтверждён. */
  async function receipt(e) {
    const id = eventId(e);
    if (!id) return { state: "no-id", message: "В записи нет ключа запроса: квитанцию проверить нельзя." };
    try {
      const r = await caseFetch("/api/case-pick/tasks/" + e.task + "/transfer-receipt?offline_event_id=" + encodeURIComponent(id));
      if (receiptMatches(r, e, id)) { finish(e); return { state: "confirmed", message: "Квитанция сервера подтверждает этот запрос: передача выполнена." }; }
      return { state: "mismatch", message: "Квитанция сервера не совпадает с сохранённым запросом. Исход не подтверждён." };
    } catch (error) {
      const s = error.status;
      if (s === 404) return { state: "absent", message: "Квитанции этого запроса на сервере пока нет. Это не подтверждает отмену: запрос может выполниться позже." };
      if (s === 403) return { state: "denied", message: "Квитанцию этого запроса может прочитать только его автор в своей области (" + error.message + ")." };
      return { state: "unavailable", message: "Квитанция недоступна (" + (error.message || "нет ответа") + "). Повторите проверку позже." };
    }
  }

  async function deliver(e) {
    if (!e.body || e.record.damaged) throw new Error("Сохранённый запрос повреждён: повтор невозможен, доступна только проверка квитанции.");
    const mark = e.record.storageKey + ":delivery";
    const priorUnknown = e.kind === "legacy" || localStorage.getItem(mark) !== null;
    localStorage.setItem(mark, "unknown");
    try {
      const res = await caseFetch("/api/case-pick/tasks/" + e.task + "/transfer", { method: "POST",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(e.body) });
      if (res.case_pick_task_id !== e.task || res.status !== "TRANSFERRED")
        return { outcome: "unknown", message: "Ответ сервера не подтверждает передачу. Запрос сохранён для точного повтора." };
      finish(e); return { outcome: "done" };
    } catch (error) {
      const s = error.status;
      if (REFUSED.includes(s) && !priorUnknown) { finish(e); return { outcome: "refused", status: s, message: refusal(s, error.message) + " Запрос снят: сервер его не выполнил." }; }
      if (REFUSED.includes(s)) {
        const check = await receipt(e);
        if (check.state === "confirmed") return { outcome: "done", proven: true };
        return { outcome: "pending", status: s, message: refusal(s, error.message) + " Прежняя отправка могла дойти до сервера, поэтому запрос остаётся. " + check.message };
      }
      if (s === 401) return { outcome: "auth", message: "Сессия истекла. Войдите снова — запрос сохранён." };
      return { outcome: "unknown", message: (error.message || "Нет ответа") + ". Результат неизвестен: запрос сохранён, повторите тот же запрос." };
    }
  }

  function refusal(status, message) {
    if (status === 403) return "Нет права на передачу в этой области или целевой исполнитель недоступен (" + message + ").";
    if (status === 404) return "Задание или ресурс не найдены (" + message + ").";
    if (status === 409) return "Конфликт: скан, версия, исполнитель или сессия не совпадают с текущими (" + message + ").";
    return "Запрос отклонён проверкой полей (" + message + ").";
  }

  /** Копия для разбора: сохраняется рядом, сохранённый запрос и блокировка новой передачи остаются. */
  function copy(e) {
    const r = e.record, target = r.storageKey + ":copy:" + crypto.randomUUID();
    const value = JSON.stringify({ raw: r.raw, kind: e.kind, damaged: Boolean(r.damaged), by: user(), at: new Date().toISOString() });
    localStorage.setItem(target, value);
    if (localStorage.getItem(target) !== value) throw new Error("Не удалось сохранить копию.");
    return target;
  }

  window.caseHandoff = { entry, create, deliver, receipt, copy, validBody, sameRequest };
})();
