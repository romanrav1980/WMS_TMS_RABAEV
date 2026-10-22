import { useRead } from "./useRead";
import { Tech } from "./ui";

export type RouteMember = { id: number; st_number: string; address: string | null; route_ordinal: number | null; delivery_window_from: string | null; delivery_window_to: string | null };
type Point = { point_id: number; link_status: "LINKED" | "UNLINKED" | "AMBIGUOUS" | "HIDDEN" | "OTHER_WAREHOUSE"; reason?: string; recipient_id?: string;
  recipient_title?: string | null; order_ids?: string[]; customer_consistent?: boolean | null; address_status?: string | null; address_type?: string | null };
export type Points = { native_task_id: number | null; points: Point[]; blocked_reason: string | null };
type Stop = { address: string; arrival_at: string | null; service_start_at: string | null; service_finish_at: string | null; wait_min: string | null; late_min: string | null;
  window_from: string | null; window_to: string | null; issues: string[] };
type Windows = { status: string; departure_at: string | null; return_at: string | null; stops: Stop[]; issues: { code: string; address: string | null }[];
  warnings: { code: string; address: string | null }[] };

const ISSUE: Record<string, string> = {
  WAREHOUSE_DEPOT_NOT_CONFIGURED: "адрес склада выезда не настроен", ROUTE_DEPARTURE_STAGE_UNKNOWN: "время выезда не определено",
  ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED: "нет актуального времени в пути", DESTINATION_RULE_INVALID: "не настроены норма разгрузки и строгость окна точки",
  ROUTE_ARRIVAL_UNKNOWN: "время приезда неизвестно", ROUTE_RETURN_TIME_UNKNOWN: "время возврата неизвестно", DELIVERY_HARD_WINDOW_MISSED: "строгое окно доставки нарушено",
  DELIVERY_SOFT_WINDOW_MISSED: "нестрогое окно доставки нарушено", ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE: "возврат позже запланированного времени машины",
  ROUTE_ORDER_INVALID: "порядок точек недействителен", ROUTE_OPERATION_MAPPING_REQUIRED: "операции рейса не сопоставлены с маршрутом",
  DRIVER_TRIP_DRIVE_LIMIT: "превышен лимит вождения водителя", DELIVERY_WINDOW_UNCONFIGURED: "окно доставки точки не настроено",
  DELIVERY_WINDOW_PARTIAL: "окно доставки задано не полностью", DELIVERY_WINDOW_REVERSED_OR_EMPTY: "окно доставки задано неверно",
  DELIVERY_WINDOW_DISJOINT: "окна отгрузок точки не пересекаются", DELIVERY_MEMBERS_MISSING: "у точки нет отгрузок" };
const LINK: Record<string, string> = { UNLINKED: "получатель не связан", AMBIGUOUS: "связь неоднозначна", HIDDEN: "скрыто правами собственника", OTHER_WAREHOUSE: "точка другого склада" };
const REASON: Record<string, string> = { NO_ORDER_FOR_POINT: "у точки нет задания сборки или целой паллеты с заказом", NOT_A_TRADECASE_ORDER: "заказ точки не из СНС/BLC",
  SEVERAL_RECIPIENTS: "у точки заказы разных получателей", RECIPIENT_DOCUMENT_MISSING: "нет действующего документа получателя" };
const ADDRESS: Record<string, string> = { CONFIRMED: "адрес совпадает с адресом клиента", NOT_IN_CUSTOMER_ADDRESSES: "адреса точки нет среди адресов клиента",
  AMBIGUOUS: "адрес совпадает с несколькими адресами клиента", ADDRESS_MISSING: "у точки нет адреса", UNKNOWN: "адрес не проверен" };
const issue = (code: string) => ISSUE[code] ?? "другая причина источника (подробно — в технических сведениях)";
const time = (iso: string | null) => (iso ? `${iso.slice(8, 10)}.${iso.slice(5, 7)} ${iso.slice(11, 16)} UTC` : "неизвестно");
const minutes = (v: string | null) => (v === null ? "неизвестно" : `${Math.round(Number(v))} мин`);

/** План маршрута: точки текущего основания, их получатели по ключам и расчёт приезда/обслуживания/ожидания/возврата
 *  существующим расчётом окон. Отсутствующие данные называются; расчёт не означает выезд или доставку. */
export function RoutePlan({ nativeTask, members, points }: { nativeTask: number; members: RouteMember[]; points: Points }) {
  const windows = useRead<Windows>(`/api/transport/preflight/trips/${nativeTask}/delivery-windows?time_zone=UTC&depot_address=&max_age_hours=24`);
  const byPoint = new Map(points.points.map(p => [p.point_id, p])), w = windows.data;
  const stop = (address: string | null) => w?.stops.find(s => s.address === address);
  const tripIssues = [...new Set((w?.issues ?? []).filter(i => !i.address).map(i => i.code))];
  const blocked = points.blocked_reason || (w && w.status !== "NO_EARLIEST_WINDOW_VIOLATION");
  return <div aria-label="План маршрута">
    {windows.error && <p className="tc-err" role="alert">{windows.error.includes("Нет права") ? "Нет права расчёта окон доставки." : `Расчёт окон не получен: ${windows.error}`}</p>}
    {windows.loading && !w && <p className="tc-note">Читаем расчёт окон…</p>}
    {w && <p className={"tc-msg " + (blocked ? "warn" : "ok")} role="status">
      Выезд: {time(w.departure_at)} · возврат: {time(w.return_at)}.{" "}
      {w.status === "NO_EARLIEST_WINDOW_VIOLATION" ? "Нарушений окон по расчёту нет." : "Окна не подтверждены"}
      {tripIssues.length ? `: ${tripIssues.map(issue).join("; ")}` : ""}.
      {points.blocked_reason && " Не у всех точек подтверждён получатель."} Расчёт — план; выезд и доставку он не подтверждает.</p>}
    {members.map(m => {
      const p = byPoint.get(m.id), s = stop(m.address);
      return <article key={m.id} className="tc-panel" aria-label={`Точка ${m.route_ordinal ?? "без номера"}`}>
        <h5>{m.route_ordinal ?? "—"}. {p?.link_status === "OTHER_WAREHOUSE" ? "точка другого склада" : m.address ?? "адрес отсутствует"}</h5>
        <dl className="tc-fields">
          <dt>Получатель</dt><dd>{!p ? "нет данных" : p.link_status === "LINKED"
            ? <>{p.recipient_title ?? p.recipient_id} ({p.recipient_id}) · заказ {p.order_ids?.join(", ")}</>
            : `${LINK[p.link_status]}${p.reason ? ` — ${REASON[p.reason] ?? "причина в технических сведениях"}` : ""}`}</dd>
          {p?.link_status === "LINKED" && <><dt>Проверки</dt><dd>{p.customer_consistent === false ? "клиент получателя не совпадает с клиентом заказа" : p.customer_consistent ? "клиент совпадает" : "клиент получателя не задан"}
            {"; "}{ADDRESS[p.address_status ?? "UNKNOWN"] ?? "адрес не проверен"}{p.address_type ? ` (тип: ${p.address_type})` : ""}</dd></>}
          <dt>Окно</dt><dd>{s?.window_from || s?.window_to ? `${time(s.window_from)} — ${time(s.window_to)}` : m.delivery_window_from || m.delivery_window_to ? `${m.delivery_window_from ?? "?"} — ${m.delivery_window_to ?? "?"}` : "не задано"}</dd>
          <dt>Приезд / начало разгрузки</dt><dd>{s ? `${time(s.arrival_at)} / ${time(s.service_start_at)}` : "нет данных расчёта"}</dd>
          <dt>Ожидание / опоздание</dt><dd>{s ? `${minutes(s.wait_min)} / ${minutes(s.late_min)}` : "нет данных расчёта"}</dd>
          {s && s.issues.length > 0 && <><dt>Причины</dt><dd>{s.issues.map(issue).join("; ")}</dd></>}
        </dl>
      </article>;
    })}
    {w && <Tech value={{ windows: w, points }} label="Расчёт окон и связи точек" />}
  </div>;
}
