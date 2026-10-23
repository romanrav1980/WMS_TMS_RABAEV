import { useEffect, useState } from "react";
import { ApiRequestError, RAW_ADMIN_BASE, apiFetch } from "../../api";

// Смена машины у собранного рейса (C-0167). Переходы уже обеспечивает native: до погрузки машину можно сменить с проверкой
// вместимости; при погруженных местах сначала нужна выгрузка отдельной командой сотрудника; после выезда — нельзя.
// Блок только читает фактическую погрузку рейса и объясняет, что делать; никаких действий с грузом сам не выполняет.
type Place = { load_operation_id: string; root_uid: string | null; vehicle_number: string | null; dock: string | null; status: string };
type Status = { trip: { id: number; transport: string | null; dock: string | null; condition: string | null }; physical_places: Place[] };

const HELP = "/help/transport-vehicle-change.html";
const CODES: [string, string][] = [
  ["TRIP_CONFIRMED_UNLOADING_REQUIRED_BEFORE_REASSIGNMENT", "Машину сменить нельзя: в рейсе есть погруженные или выехавшие места. Сначала выгрузите их на экране «Погрузка и выезд», затем повторите смену."],
  ["TRANSPORT_PLAN_FROZEN", "Рейс уже отгружен или оплачен: смена машины недоступна."],
  ["TRANSPORT_VEHICLE_CHANGED_RETRY", "Машину рейса только что изменил другой сотрудник. Обновите карточку и проверьте выбор."],
];

/** Plain words for a refused trip edit; the raw text stays visible when the reason is unknown. */
export function vehicleChangeError(text: string): string {
  const hit = CODES.find(([code]) => text.includes(code));
  return hit ? hit[1] + " (" + text + ")" : text;
}

export function VehicleChange({ taskId, reload }: { taskId: number; reload: number }) {
  const [data, setData] = useState<Status | null>(null), [error, setError] = useState(""), [tick, setTick] = useState(0);
  useEffect(() => {
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
  }, [taskId, reload, tick]);
  const loaded = data?.physical_places.filter(p => p.status === "LOADED") ?? [];
  const departed = data?.physical_places.filter(p => p.status === "DEPARTED") ?? [];
  const screen = `${RAW_ADMIN_BASE}/transport-loading.html?trip_id=${taskId}`;
  return <section className="dispatch-vehicle-change" aria-label="Смена машины">
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
  </section>;
}
