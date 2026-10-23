import { useEffect, useState } from "react";
import { ApiRequestError, RAW_ADMIN_BASE, apiFetch } from "../../api";
import { INTENT_EVENT, compare, fieldsOf, readIntent, send, settle, type TripFields, type TripRow } from "./vehicleEditIntent";

// Смена машины у собранного рейса (C-0167). Переходы уже обеспечивает native: до погрузки машину можно сменить с проверкой
// вместимости; при погруженных местах сначала нужна выгрузка отдельной командой сотрудника; после выезда — нельзя.
// Блок читает фактическую погрузку рейса и объясняет, что делать; незавершённое изменение рейса сверяет с текущим рейсом.
type Place = { load_operation_id: string; root_uid: string | null; vehicle_number: string | null; dock: string | null; status: string };
type Status = { trip: { id: number; transport: string | null; dock: string | null; condition: string | null }; physical_places: Place[] };

const HELP = "/help/transport-vehicle-change.html";
const CODES: [string, string][] = [
  ["TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT", "Машину сменить нельзя: в рейсе есть погруженные или выехавшие места. Сначала выгрузите их на экране «Погрузка и выезд», затем повторите смену."],
  ["TRANSPORT_PLAN_FROZEN", "Рейс уже отгружен или оплачен: смена машины недоступна."],
  ["TRANSPORT_VEHICLE_CHANGED_RETRY", "Машину рейса только что изменил другой сотрудник. Обновите карточку и проверьте выбор."],
];
const NAMES: Record<keyof TripFields, string> = { transport: "машина", voditel_id: "водитель", dock: "докстанция", transtype: "тип ТС",
  shipment_date: "дата", shipment_time: "время", primechanie: "примечание" };

/** Plain words for a refused trip edit; the raw text stays visible when the reason is unknown. */
export function vehicleChangeError(text: string): string {
  const hit = CODES.find(([code]) => text.includes(code));
  return hit ? hit[1] + " (" + text + ")" : text;
}

type Check = { state: "loading" | "saved" | "unsaved" | "other" | "denied" | "error"; text: string };

function PendingEdit<T extends TripRow>({ taskId, onTask }: { taskId: number; onTask: (trip: T) => void }) {
  const [, setVersion] = useState(0), [tick, setTick] = useState(0), [check, setCheck] = useState<Check | null>(null), [busy, setBusy] = useState(false);
  useEffect(() => {
    const again = () => setVersion(n => n + 1);
    window.addEventListener(INTENT_EVENT, again); window.addEventListener("storage", again);
    return () => { window.removeEventListener(INTENT_EVENT, again); window.removeEventListener("storage", again); };
  }, []);
  const pending = readIntent(taskId);
  const raw = pending?.raw ?? null;
  useEffect(() => {
    if (!raw) { setCheck(c => c?.state === "saved" ? c : null); return; }  // keep the confirmation visible after settling
    const controller = new AbortController(), stored = readIntent(taskId);
    if (!stored) return;
    setCheck({ state: "loading", text: "Сверяем изменение с текущим рейсом…" });
    apiFetch<T>(`/api/admin/transport/tasks/${taskId}`, { signal: controller.signal }).then(trip => {
      if (controller.signal.aborted || trip.ID !== taskId) return;
      const now = fieldsOf(trip), result = compare(stored.intent.body, now);
      if (result.saved) { settle(taskId, stored.raw); onTask(trip); setCheck({ state: "saved", text: "Изменение рейса сохранено сервером." }); return; }
      const untouched = result.differ.every(k => (now[k] ?? null) === (stored.intent.before[k] ?? null));
      const list = result.differ.map(k => `${NAMES[k]}: сейчас «${now[k] ?? "—"}», нужно «${stored.intent.body[k] ?? "—"}»`).join("; ");
      setCheck(untouched ? { state: "unsaved", text: "Изменение не сохранено: " + list + "." }
        : { state: "other", text: "Рейс изменил другой сотрудник: " + list + ". Проверьте, нужно ли ещё ваше изменение." });
    }).catch(e => {
      if (controller.signal.aborted) return;
      setCheck(e instanceof ApiRequestError && (e.status === 401 || e.status === 403)
        ? { state: "denied", text: "Нет доступа к рейсу: сверить нельзя. Изменение сохранено до восстановления прав." }
        : { state: "error", text: "Рейс не прочитан: исход изменения пока неизвестен. " + String(e) });
    });
    return () => controller.abort();
  }, [raw, taskId, tick, onTask]);
  if (!pending && check?.state !== "saved") return null;
  const retry = async () => {
    const stored = readIntent(taskId); if (!stored) return;
    setBusy(true);
    try {
      await send(stored.intent, stored.raw);
      setCheck({ state: "saved", text: "Изменение рейса сохранено сервером." });
      onTask(await apiFetch<T>(`/api/admin/transport/tasks/${taskId}`));
    } catch (e) { setCheck({ state: "error", text: vehicleChangeError(String(e)) }); }  // keep the reason; "Проверить снова" reads the trip
    finally { setBusy(false); }
  };
  const readOk = check?.state === "unsaved" || check?.state === "other";
  return <div className="dispatch-vehicle-pending" role="status">
    <p><b>Незавершённое изменение рейса</b>{pending ? ` от ${new Date(pending.intent.saved_at).toLocaleString("ru-RU")}: ` +
      Object.entries(pending.intent.body).map(([k, v]) => `${NAMES[k as keyof TripFields]} «${v}»`).join(", ") : ""}</p>
    {check && <p>{check.text}</p>}
    {pending && <>
      <button type="button" title="Отправить то же самое исходное изменение ещё раз, без правок" data-help-id="transport.vehicle.retry"
        disabled={busy || !readOk} onClick={() => void retry()}>Повторить исходное изменение</button>{" "}
      <button type="button" title="Отказаться от изменения: доступно только после чтения рейса, показавшего, что оно не сохранено" data-help-id="transport.vehicle.discard"
        disabled={busy || !readOk} onClick={() => { const s = readIntent(taskId); if (s) settle(taskId, s.raw); setCheck(null); }}>Отказаться от изменения</button>{" "}
      <button type="button" title="Прочитать текущий рейс ещё раз и сверить с изменением" data-help-id="transport.vehicle.recheck"
        disabled={busy} onClick={() => setTick(n => n + 1)}>Проверить снова</button>
    </>}
  </div>;
}

export function VehicleChange<T extends TripRow>({ taskId, editing, onTask }: { taskId: number; editing: boolean; onTask: (trip: T) => void }) {
  const [data, setData] = useState<Status | null>(null), [error, setError] = useState(""), [tick, setTick] = useState(0);
  useEffect(() => {
    if (!editing) { setData(null); setError(""); return; }
    const controller = new AbortController();
    setData(null); setError("");
    apiFetch<Status>(`/api/transport/loading/${taskId}/status`, { signal: controller.signal })
      .then(value => { if (!controller.signal.aborted && value.trip.id === taskId) setData(value); })
      .catch(e => {
        if (controller.signal.aborted) return;
        setData(null);  // 401/403/404 and any failure: no stale places of another trip or user
        setError(e instanceof ApiRequestError && (e.status === 401 || e.status === 403) ? "Нет доступа к погрузке этого рейса." : "Погрузка рейса не прочитана: " + String(e));
      });
    return () => controller.abort();
  }, [taskId, editing, tick]);
  const loaded = data?.physical_places.filter(p => p.status === "LOADED") ?? [];
  const departed = data?.physical_places.filter(p => p.status === "DEPARTED") ?? [];
  const screen = `${RAW_ADMIN_BASE}/transport-loading.html?trip_id=${taskId}`;
  return <section className="dispatch-vehicle-change" aria-label="Смена машины">
    <PendingEdit taskId={taskId} onTask={onTask} />
    {editing && <>
      <b>Смена машины</b>{" "}
      <a href={HELP} target="_blank" rel="noopener" title="Открыть инструкцию по смене машины в новой вкладке" data-help-id="transport.vehicle.help">Справка</a>{" "}
      <button type="button" title="Перечитать фактическую погрузку рейса" data-help-id="transport.vehicle.refresh" onClick={() => setTick(n => n + 1)}>Обновить</button>
      {error && <p role="alert">{error}</p>}
      {data && <>
        <p>Текущая машина: <b>{data.trip.transport ?? "не выбрана"}</b>{data.trip.dock ? `, рампа ${data.trip.dock}` : ""}.
          {" "}Погружено мест: {loaded.length}, выехало: {departed.length}.</p>
        {departed.length > 0 || data.trip.condition === "Отгружен"
          ? <p role="status">Рейс выехал: смена машины недоступна. Груз остаётся за прежней машиной.</p>
          : loaded.length > 0
            ? <>
                <p role="status">Сначала выгрузите погруженные места — это отдельное действие сотрудника со сканом места, машины, рампы и исходной ячейки. После выгрузки смените машину и погрузите места в новую: погрузку подтверждает только скан новой машины.</p>
                <ul>{loaded.slice(0, 20).map(p => <li key={p.load_operation_id}>{p.root_uid ?? p.load_operation_id} — машина {p.vehicle_number ?? "—"}, рампа {p.dock ?? "—"}</li>)}</ul>
                {loaded.length > 20 && <p>И ещё {loaded.length - 20} мест — полный список на экране погрузки.</p>}
                <a href={screen} target="_blank" rel="noopener" title="Открыть экран «Погрузка и выезд» этого рейса: там выполняется выгрузка" data-help-id="transport.vehicle.unload">Открыть выгрузку рейса</a>
              </>
            : <p role="status">Груз ещё не погружен: машину можно сменить, назначенные СТ сохранятся. Вместимость новой машины проверит сервер при сохранении.</p>}
      </>}
    </>}
  </section>;
}
