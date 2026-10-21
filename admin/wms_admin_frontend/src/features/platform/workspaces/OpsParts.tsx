import type { ReactNode } from "react";
import { RAW_ADMIN_BASE } from "../../../api";
import { HelpButton } from "../help/HelpButton";
import { formatMoment } from "../access-admin";
import type { ReadState } from "../access-admin/useApiRead";
import { wsHelp } from "./help";
import { tripTone } from "./types";
import type { GanttVehicle, Session, Trip } from "./types";

/** Плитка факта: значение из API с источником; ошибка/нет данных — текстом, не нулём. */
export function KpiTile({ icon, label, read, value, sub, source }: { icon: string; label: string; read: ReadState<unknown>; value: (data: never) => ReactNode; sub?: (data: never) => ReactNode; source: string }) {
  const shown = read.data ? value(read.data as never) : null;
  // Нет данных или текстовое пояснение вместо числа — мелким шрифтом, чтобы не выглядело показателем.
  const nodata = !read.data || (typeof shown === "string" && /[а-яё]/i.test(shown));
  return <div className={"ops-panel ops-kpi" + (nodata ? " nodata" : "")} title={"Источник: " + source} data-help-id={"workspace.kpi." + label}>
    <span className="ops-kpi-icon" aria-hidden="true">{icon}</span>
    <div><div className="ops-kpi-label">{label}</div>
      <div className="ops-kpi-value">{read.data ? shown : read.loading ? "…" : read.error || "нет данных"}</div>
      {read.data != null && sub && <div className="ops-kpi-sub">{sub(read.data as never)}</div>}</div>
  </div>;
}

/** Статус каждого источника: момент последнего УСПЕШНОГО чтения, ошибка (и возраст показанных старых данных), загрузка.
 *  Историческая дата отмечается отдельно — это не живые данные текущего дня. */
export function SourceStrip({ sources, isToday, day }: { sources: [string, ReadState<unknown>][]; isToday: boolean; day: string }) {
  const used = sources.filter(([, r]) => r.loading || r.data !== null || r.error);
  return <div className="ops-sources" role="status" aria-label="Состояние источников данных">
    <span className={"ops-chip " + (isToday ? "ship" : "other")}>{isToday ? "текущая дата" : `архивная дата ${day}`}</span>
    {used.map(([label, r]) => {
      const age = r.at ? Math.floor((Date.now() - r.at.getTime()) / 60000) : null;
      const at = r.at ? r.at.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }) : "";
      const tone = r.error ? "bad" : r.loading && !r.data ? "plan" : age !== null && age >= 5 ? "other" : "ship";
      const text = r.error ? `${label}: ${r.error}${r.data ? ` · показаны данные от ${at}` : ""}` : r.loading && !r.data ? `${label}: загрузка` : `${label}: ${at}${age !== null && age >= 5 ? ` (${age} мин назад)` : ""}`;
      return <span key={label} className={"ops-chip " + tone} title={"Момент последнего успешного чтения источника «" + label + "»."}>{text}</span>;
    })}
  </div>;
}

export const rawLink = (page: string) => `${RAW_ADMIN_BASE}/${page}`;
export const appLink = (page: string, extra = "") => `${location.pathname.includes("/preview/") ? "/" : location.pathname}?page=${page}${extra}`;
export function shiftLink(wave?: number): string {
  const url = new URL(location.href);
  url.searchParams.set("page", "workspace"); url.searchParams.set("workspace", "shift");
  if (wave != null && Number.isSafeInteger(wave) && wave > 0) url.searchParams.set("wave_id", String(wave));
  else url.searchParams.delete("wave_id");
  return (url.pathname.includes("/preview/") ? "/" : url.pathname) + url.search;
}
export function openShift(wave?: number): void {
  history.pushState(history.state, "", shiftLink(wave));
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export function TripCard({ trip, vehicle, onClose, day }: { trip: Trip; vehicle?: GanttVehicle; onClose: () => void; day: string }) {
  const ops = vehicle?.operations.filter(o => o.tt_id === trip.ID) ?? [];
  const done = ops.filter(o => o.fact_end).length;
  return <section className="ops-card" aria-label={`Рейс ${trip.ID}`}>
    <h3>Рейс {trip.ID} <span className={"ops-chip " + tripTone(trip.CONDITION)}>{trip.CONDITION ?? "состояние неизвестно"}</span></h3>
    <dl>
      <dt>Машина</dt><dd>{trip.TRANSPORT ?? "не назначена"}{trip.TRANSTYPE ? ` · тип ${trip.TRANSTYPE}` : ""}</dd>
      <dt>Перевозчик</dt><dd>{trip.TK_NAME ?? "—"}</dd>
      <dt>Водитель</dt><dd>{trip.VODITEL_NAME ?? "не назначен"}{trip.VODITEL_TEL ? ` · ${trip.VODITEL_TEL}` : ""}</dd>
      <dt>Ворота</dt><dd>{trip.DOCK ?? "не назначены"}</dd>
      <dt>Груз</dt><dd>СТ {trip.ST_COUNT ?? "—"} · мест {trip.PALLET_COUNT ?? "—"} · {trip.VOLUME_M3 ?? "—"} м³</dd>
      <dt>Готовность склада</dt><dd>{trip.READY_PERC == null ? "нет данных" : `${trip.READY_PERC}%`}{trip.UNREADY_COUNT ? ` · не готово ${trip.UNREADY_COUNT}` : ""}</dd>
      <dt>Операции</dt><dd>{ops.length ? `завершено по факту ${done} из ${ops.length}` : "нет операций на эту дату"}</dd>
    </dl>
    {trip.READY_PERC != null && <div className="ops-bar" aria-label="Готовность склада"><span style={{ width: `${Math.min(100, Math.max(0, trip.READY_PERC))}%` }} /></div>}
    {ops.length > 0 && <ul className="ops-list" style={{ marginTop: 8 }}>{ops.map(o => <li key={o.op_id}>
      <span>{o.operation_code}<br /><small>план {o.plan_start?.slice(11, 16) ?? "—"}–{o.plan_end?.slice(11, 16) ?? "—"}</small></span>
      <small>{o.fact_end ? "завершено " + o.fact_end.slice(11, 16) : o.fact_start ? "идёт с " + o.fact_start.slice(11, 16) : "нет отметки"}</small></li>)}</ul>}
    <div className="aa-actions" style={{ marginTop: 10 }}>
      <HelpButton help={wsHelp.openDispatch} onClick={() => { location.href = appLink("transport", "&task_id=" + trip.ID); }}>Открыть рейс {trip.ID}</HelpButton>
      <HelpButton help={wsHelp.openGantt} onClick={() => { location.href = appLink("gantt"); }}>Ганта (без выбора рейса)</HelpButton>
      <HelpButton help={wsHelp.openLoading} onClick={() => window.open(rawLink("transport-loading.html"), "_blank")}>Погрузка и выезд</HelpButton>
      <HelpButton help={wsHelp.closeCard} onClick={onClose}>Закрыть</HelpButton>
    </div>
    <p className="ops-note">Дата {day}. Изменения рейса выполняются в экранах-владельцах с проверкой сервера.</p>
  </section>;
}

/** resourceKeyBySession/onOpenResource — необязательный переход к ресурсу в общем Ганте по тому же session_id, что вернул
 *  /api/resources/timeline (resource_session_view); без совпадения в карте кнопки нет — ключ не придумывается. */
export function ResourceList({ read, resourceKeyBySession, onOpenResource }: { read: ReadState<Session[]>; resourceKeyBySession?: Map<number, string>; onOpenResource?: (key: string) => void }) {
  const active = (read.data ?? []).filter(s => s.status === "ACTIVE" && !s.logout_at);
  return <section className="ops-panel" aria-label="Ресурсы на смене">
    <h3>Ресурсы на смене <small>{read.data ? `${active.length} сессий` : ""}</small></h3>
    {read.error && <p className="ops-err">{read.error}</p>}{read.loading && !read.data && <p className="ops-note">Загрузка…</p>}
    {read.data && (active.length === 0 ? <p className="ops-note">Открытых сессий нет.</p> :
      <ul className="ops-list">{active.slice(0, 30).map(s => { const key = resourceKeyBySession?.get(s.session_id);
        return <li key={s.session_id} title={wsHelp.session.text} data-help-id={wsHelp.session.id}>
        <span><b>{s.resource_name || s.resource_code}</b> <small>{s.resource_type}{s.equipment_code ? " · " + s.equipment_code : ""}{s.zone_code ? " · зона " + s.zone_code : ""}</small><br />
          <small>{s.current_task_id ? "задание " + s.current_task_id : "без задания"} · сигнал {formatMoment(s.last_heartbeat_at)}</small></span>
        <span style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
          <span className={"ops-chip " + (s.current_task_id ? "ship" : "plan")}>{s.current_task_id ? "в работе" : "без задания"}</span>
          {key && onOpenResource && <HelpButton help={wsHelp.openResourceGantt} onClick={() => onOpenResource(key)}>В Ганте</HelpButton>}
        </span></li>; })}</ul>)}
    {/* «Без задания» — не «свободен»: давность сигнала без пояса не рассчитывается, присутствие не подтверждено (C0074). */}
    {active.length > 30 && <p className="ops-note">Показаны 30 из {active.length}.</p>}
  </section>;
}
