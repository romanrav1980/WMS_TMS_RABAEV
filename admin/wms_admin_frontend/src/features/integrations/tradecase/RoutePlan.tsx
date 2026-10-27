import { useRead } from "./useRead";
import { sourceZone, stamp, minutesBetween } from "./routeZone";
import { Tech } from "./ui";
import { RAW_ADMIN_BASE } from "../../../api";

export type RouteMember = { id: number; st_number: string; address: string | null; route_ordinal: number | null; delivery_window_from: string | null; delivery_window_to: string | null };
type Point = { point_id: number; link_status: "LINKED" | "UNLINKED" | "AMBIGUOUS" | "HIDDEN" | "OTHER_WAREHOUSE"; reason?: string; recipient_id?: string;
  recipient_title?: string | null; order_ids?: string[]; customer_consistent?: boolean | null; address_status?: string | null; address_type?: string | null };
export type Points = { native_task_id: number | null; points: Point[]; blocked_reason: string | null };
type Stop = { address: string; arrival_at: string | null; service_start_at: string | null; service_finish_at: string | null; wait_min: string | null; late_min: string | null;
  window_from: string | null; window_to: string | null; issues: string[]; store_time_zone?: string | null };
type Segment = { code: string; start_at: string; finish_at: string };
type Windows = { status: string; departure_at: string | null; return_at: string | null; stops: Stop[]; issues: { code: string; address: string | null }[];
  warnings: { code: string; address: string | null }[]; segments?: Segment[]; destination_time_zones_verified?: boolean };
type TimeContext = Parameters<typeof sourceZone>[0];

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
export const routeIssue = issue;
// Где сотрудник задаёт недостающее: только существующие действия этого экрана (C-0154).
const FIX: Record<string, string> = { WAREHOUSE_DEPOT_NOT_CONFIGURED: "«Настроить исходные данные маршрута» → адрес склада выезда",
  ROUTE_DEPARTURE_STAGE_UNKNOWN: "«Настроить исходные данные маршрута» → оценка длительности рейса (создаёт плановые операции и время выезда)",
  ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED: "«Обновить дорожные плечи»", DESTINATION_RULE_INVALID: "«Настроить окна и разгрузку магазина» у точки",
  DELIVERY_WINDOW_UNCONFIGURED: "«Настроить окна и разгрузку магазина» у точки",
  ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE: "«Настроить исходные данные маршрута» → увеличить «Возврат на склад, мин» (оценка должна включать разгрузку и отдых водителя)" };
const clock = (iso: string) => iso.slice(11, 16);
const BASIS = { APPROVAL: "основание — утверждение времени рейса" };
const minutes = (v: string | null) => (v === null ? "неизвестно" : `${Math.round(Number(v))} мин`);

/** План маршрута: точки текущего основания, их получатели по ключам и расчёт приезда/обслуживания/ожидания/возврата
 *  существующим расчётом окон. Отсутствующие данные называются; расчёт не означает выезд или доставку. */
export function RoutePlan({ nativeTask, members, points }: { nativeTask: number; members: RouteMember[]; points: Points }) {
  // Окна и операции рейса записаны местным временем; расчёт трактует их в поясе исходных данных, поэтому без подтверждённого пояса он не запрашивается.
  const context = useRead<TimeContext>(`/api/transport/preflight/trips/${nativeTask}/time-context`);
  const src = context.data ? sourceZone(context.data) : null;
  const windows = useRead<Windows>(src?.zone ? `/api/transport/preflight/trips/${nativeTask}/delivery-windows?time_zone=${encodeURIComponent(src.zone)}&depot_address=&max_age_hours=24` : null);
  const time = stamp;
  const byPoint = new Map(points.points.map(p => [p.point_id, p])), w = windows.data;
  const stop = (address: string | null) => w?.stops.find(s => s.address === address);
  const tripIssues = [...new Set((w?.issues ?? []).filter(i => !i.address).map(i => i.code))];
  const blocked = points.blocked_reason || (w && w.status !== "NO_EARLIEST_WINDOW_VIOLATION");
  const rests = (w?.segments ?? []).filter(x => x.code === "REST");
  const handover = w?.segments?.find(x => x.code === "RETURN_HANDOVER");
  const short = w?.return_at && handover && w.issues.some(i => i.code === "ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE") ? minutesBetween(handover.start_at, w.return_at) : 0;
  return <div aria-label="План маршрута">
    {context.error && <p className="tc-err" role="alert">Пояс исходных данных рейса не прочитан: {context.error}</p>}
    {src && !src.zone && <p className="tc-msg warn" role="status" data-help-id="tradecase.route.zone">{src.reason === "MIXED_ZONES"
      ? `В маршруте магазины в другом поясе (${src.zones.join(", ")}), чем утверждённое время рейса; текущий расчёт считает рейс в одном поясе и такой маршрут пока не показывает.`
      : "Пояс местного времени рейса не подтверждён: утвердите время рейса с явным часовым поясом в транспортном экране."} Расчёт окон не выполняется, чтобы не сдвинуть время.</p>}
    {src?.zone && <p className="tc-note" data-help-id="tradecase.route.zone">Местное время рейса записано в поясе {src.zone} ({src.basis ? BASIS[src.basis] : ""}); время показано со смещением от UTC.</p>}
    {windows.error && <p className="tc-err" role="alert">{windows.error.includes("Нет права") ? "Нет права расчёта окон доставки." : `Расчёт окон не получен: ${windows.error}`}</p>}
    {windows.loading && !w && <p className="tc-note">Читаем расчёт окон…</p>}
    {w && <p className={"tc-msg " + (blocked ? "warn" : "ok")} role="status">
      Выезд: {time(w.departure_at)} · возврат: {time(w.return_at)}.{" "}
      {w.status === "NO_EARLIEST_WINDOW_VIOLATION" ? "Нарушений окон по расчёту нет." : "Окна не подтверждены"}
      {tripIssues.length ? `: ${tripIssues.map(issue).join("; ")}` : ""}.
      {points.blocked_reason && " Не у всех точек подтверждён получатель."} Расчёт — план; выезд и доставку он не подтверждает.</p>}
    {w && (() => { const fixes = [...new Set(w.issues.map(i => FIX[i.code]).filter(Boolean))];
      return fixes.length > 0 && <p className="tc-note" title="Что задать, чтобы расчёт стал полным" data-help-id="tradecase.route.fix">Что сделать: {fixes.join("; ")}.</p>; })()}
    {short > 0 && handover && <p className="tc-msg warn" role="status">Возврат по расчёту {time(w!.return_at)}, а план машины рассчитан до {time(handover.start_at)}: не хватает {short} мин.</p>}
    {w && <p className="tc-note">{rests.length ? `Отдых водителя по правилу 120/15: ${rests.map(x => `${clock(x.start_at)}–${clock(x.finish_at)}`).join(", ")}.` : "Отдых водителя в расчёте не потребовался."}</p>}
    {members.map(m => {
      const p = byPoint.get(m.id), s = stop(m.address);
      return <article key={m.id} className="tc-panel" aria-label={`Точка ${m.route_ordinal ?? "без номера"}`}>
        <h5>{m.route_ordinal ?? "—"}. {p?.link_status === "OTHER_WAREHOUSE" ? "точка другого склада" : m.address ?? "адрес отсутствует"}</h5>
        {m.address && <p><a href={`${RAW_ADMIN_BASE}/store-directory.html?addr=${encodeURIComponent(m.address)}`} target="_blank" rel="noopener"
          title="Открыть карточку адреса: настроить окна приёма, норму разгрузки и строгость окна доставки" data-help-id="tradecase.route.store-settings">Настроить окна и разгрузку магазина</a></p>}
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
