import { useState } from "react";
import { useRead } from "./useRead";
import { RoutePlan } from "./RoutePlan";
import { RouteSettings } from "./RouteSettings";
import type { Points, RouteMember } from "./RoutePlan";
import { HelpLink, Tech } from "./ui";

type Member = RouteMember;
type Leg = { from_address: string | null; to_address: string | null; duration_min: number | null; fresh: boolean };
type RouteContext = { version: number; source_hash: string; route_status: string; route_duration_verified: boolean; source: { members: Member[];
  warehouse_origins: { status: string; depot_address: string | null }[]; route_material: { legs: Leg[]; order_valid: boolean } } };
type Line = { order_id: string; line_id: string; order_kind: string; recipient_id: string; order_cancelled: boolean; native_error: string | null; sku_id: string;
  source_owner_id: string; uom: string; units_per_box: number; ordered_base: string; native_row_id: number | null; binding_current: boolean | null;
  reserved_base: string | null; picked_base: string | null; unallocated_base: string | null; loaded_base: string | null; departed_base: string | null; released_base: string | null };
type Coverage = { trip_version: number; native_task_id: number | null; lines: Line[]; owner_scope_filtered: boolean; unattributed_loads: number | null; load_coverage_complete?: boolean };

const ROUTE: Record<string, string> = { NO_INPUT: "время в пути не рассчитано", VERIFIED: "время в пути подтверждено" };
const q = (v: string | null) => v ?? "нет данных";
const orderLink = (wh: string, id: string) => `?page=tradecase&tc_wh=${encodeURIComponent(wh)}&tc_tab=ORDER&tc_open=${encodeURIComponent(id)}`;

/** Маршрут рейса из текущего транспортного основания склада и обеспеченность его настоящих строк заказов.
 *  Порядок точек — план, не исполненный маршрут; отсутствующий источник показывается как «нет данных», не ноль. */
export function TripRoute({ wh, user, trip, nativeTask, bindingState }: { wh: string; user: string; trip: string; nativeTask: number | null; bindingState: "LOADING" | "UNAVAILABLE" | "KNOWN" }) {
  const [reload, setReload] = useState(0);
  const cover = useRead<Coverage>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(trip)}/coverage`);
  const points = useRead<Points>(nativeTask ? `/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(trip)}/route-points` : null);
  const routeAllowed = points.data && points.data.blocked_reason !== "ROUTE_POINTS_NOT_VISIBLE";
  const route = useRead<RouteContext>(nativeTask && routeAllowed ? `/api/transport/preflight/trips/${nativeTask}/route-context` : null, reload);
  const r = route.data, members = [...(r?.source.members ?? [])].sort((a, b) => (a.route_ordinal ?? 1e9) - (b.route_ordinal ?? 1e9));
  return <section className="tc-bind" aria-label="Маршрут и обеспеченность рейса">
    <h4>Маршрут рейса <HelpLink anchor="route" /></h4>
    {bindingState === "LOADING" ? <p className="tc-note">Читаем привязку рейса…</p> : bindingState === "UNAVAILABLE" ? <p className="tc-note">Привязка рейса не прочитана — маршрут неизвестен.</p> : !nativeTask ? <p className="tc-note">Рейс не привязан к рейсу склада — точки и порядок маршрута неизвестны.</p>
      : points.error ? <p className="tc-err" role="alert">Связь точек с получателями не прочитана: {points.error}</p>
      : points.data?.blocked_reason === "ROUTE_POINTS_NOT_VISIBLE" ? <p className="tc-err" role="alert">Нет доступа к точкам маршрута. Проверьте склад и доступ к собственникам.</p>
      : !points.data ? <p className="tc-note">Проверяем доступ к точкам маршрута…</p>
      : route.loading && !r ? <p className="tc-note">Читаем транспортное основание…</p>
      : route.error ? <p className="tc-err" role="alert">{route.error.includes("Нет права") ? "Нет права просмотра транспортного маршрута." : route.error}</p>
      : r && <>
        <p className="tc-note">Порядок точек — из текущего транспортного основания рейса склада № {nativeTask}. Это план, а не подтверждённое прохождение маршрута.
          Склад отправления: {r.source.warehouse_origins[0]?.status === "NOT_CONFIGURED" || !r.source.warehouse_origins.length ? "адрес не настроен" : q(r.source.warehouse_origins[0].depot_address)};
          {" "}{ROUTE[r.route_status] ?? "время в пути не подтверждено"}.</p>
        {members.length === 0 ? <p className="tc-note">В транспортном основании нет точек доставки.</p>
          : nativeTask && points.data && <RoutePlan key={reload} nativeTask={nativeTask} members={members} points={points.data} />}
        {nativeTask && <RouteSettings key={`${user}:${wh}:${nativeTask}`} wh={wh} user={user} trip={nativeTask}
          version={r.version} sourceHash={r.source_hash} refreshing={route.loading} onSaved={() => setReload(n => n + 1)} />}
        <p className="tc-note">Карта не строится: координат точек в источнике нет.</p>
        <Tech value={r} label="Транспортное основание" /></>}
    <h4>Обеспеченность заказов рейса <HelpLink anchor="coverage" /></h4>
    {cover.loading && !cover.data && <p className="tc-note">Читаем заказы и факты…</p>}
    {cover.error && <p className="tc-err" role="alert">{cover.error}</p>}
    {cover.data && <>
      {cover.data.owner_scope_filtered && <p className="tc-msg warn">Часть строк скрыта правами собственника и в таблицу не входит.</p>}
      {cover.data.load_coverage_complete === false && cover.data.native_task_id !== null && <p className="tc-msg warn">Часть состава погрузки не сопоставлена со строками заказов. Количества погрузки и выезда пока неизвестны.</p>}
      {cover.data.lines.length === 0 && <p className="tc-note">Видимых строк заказов в рейсе нет.</p>}
      {cover.data.lines.map(l => <article key={l.order_id + ":" + l.line_id} className="tc-panel" aria-label={`Строка ${l.order_id}/${l.line_id}`}>
        <h5><a href={orderLink(wh, l.order_id)} target="_blank" rel="noopener" title="Открыть основание этой строки в новой вкладке" data-help-id="tradecase.coverage.order">{l.order_id}</a> / {l.line_id}
          {" "}· {l.recipient_id} · {l.sku_id} <small>({l.source_owner_id})</small></h5>
        {l.order_cancelled && <p className="tc-msg warn">Заказ отменён.</p>}
        {l.native_row_id !== null && l.binding_current === false && <p className="tc-msg warn">Склад работает по прежней версии заказа.</p>}
        <dl className="tc-fields"><dt>Заказано</dt><dd>{l.ordered_base}</dd>
          {l.native_row_id === null ? <><dt>Обеспечение</dt><dd>заказ ещё не передан на склад — неизвестно</dd></>
            : l.native_error ? <><dt>Обеспечение</dt><dd>данные склада по строке недоступны</dd></>
            : <><dt title="Действующий резерв склада; после сборки и отгрузки он расходуется">Резерв сейчас</dt><dd>{q(l.reserved_base)}</dd><dt>Собрано</dt><dd>{q(l.picked_base)}</dd><dt>Не обеспечено</dt><dd>{q(l.unallocated_base)}</dd>
              <dt>Погружено, не выехало</dt><dd>{q(l.loaded_base)}</dd>
              <dt>Выехало</dt><dd>{q(l.departed_base)}{l.released_base && l.released_base !== "0" ? `, из них передано получателю ${l.released_base}` : ""}</dd></>}</dl>
      </article>)}
      <p className="tc-note">Количества — в базовых единицах (шт.). Погрузка относится к строке через задание сборки или целую паллету; {cover.data.native_task_id === null ? "рейс не привязан — погрузка неизвестна" :
        cover.data.unattributed_loads === null ? "погрузки вне видимых строк не показываются" : cover.data.unattributed_loads ? `погрузок без привязки к строке: ${cover.data.unattributed_loads}` : "все погрузки отнесены к строкам"}.</p>
      <Tech value={cover.data} label="Источники обеспеченности" /></>}
  </section>;
}
