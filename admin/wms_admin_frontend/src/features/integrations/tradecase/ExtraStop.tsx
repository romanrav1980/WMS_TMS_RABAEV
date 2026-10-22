import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, Tech } from "./ui";
import { routeIssue } from "./RoutePlan";

// Дополнительный заезд вне основного маршрута (программа, раздел 12). Сервер пересчитывает рейс штатным расчётом окон с новой точкой:
// заезд предлагается, только если укладывается в остаток до предельного времени основной доставки. Неизвестные данные — не обещание.
type StopRow = { address: string; arrival_at: string | null; service_finish_at: string | null; wait_min: string | null; late_min: string | null };
type Brief = { status: string; return_at: string | null; drive_min: string | null; stops: StopRow[]; issues: { code: string; address: string | null }[] };
type Evaluation = { decision: "PROPOSE" | "REJECT" | "UNKNOWN" | "FORBIDDEN" | "ALREADY_ON_ROUTE"; reason?: string; address: string; position?: number;
  before?: Brief; after?: Brief; before_slack_min?: number | null; after_slack_min?: number | null; added_min?: number | null;
  distance_km_before?: number | null; distance_km_after?: number | null; added_km?: number | null; source_hash: string; time_version: number;
  variants?: { position: number; verdict: string; issues: { code: string }[] }[] };
type Decisions = { new_stops_forbidden: boolean; policy_version: number; decisions: { operation_id: string; address: string; decision_state: string;
  decided_by: string; decided_at: string; validity: "CURRENT" | "STALE_ROUTE_CHANGED" }[] };
type Body = { operation_id: string; trip_id: number; action: "APPROVE" | "DECLINE" | "SET_POLICY"; reason: string; address?: string; zone?: string;
  expected_version?: number; source_hash?: string; position?: number; new_stops_forbidden?: boolean; expected_policy_version?: number };
type Receipt = { operation_id: string; action: string };

const pending = journal<Body>("extra-stop", "TC.STOP.UI", b => Number.isSafeInteger(b.trip_id) && b.trip_id > 0 && typeof b.reason === "string"
  && ["APPROVE", "DECLINE", "SET_POLICY"].includes(b.action), "решение о заезде");
const help = (id: string, text: string) => ({ id: "tradecase.route.extra." + id, text, anchor: "route" });
const reasons = { EXTRA_STOP_SOURCE_CHANGED: "Маршрут или его данные изменились после проверки. Проверьте заезд заново.",
  EXTRA_STOP_NOT_PROPOSED: "На текущих данных заезд уже не укладывается или точка вставки другая. Проверьте заново.",
  EXTRA_STOP_ACCESS_DENIED: "Согласование заездов вам недоступно для складов этого рейса.", VERSION_CONFLICT: "Настройку уже изменил другой сотрудник. Перечитайте.",
  EXTRA_STOP_OPERATION_CONFLICT: "Этот номер операции уже связан с другим запросом.", EXTRA_STOP_REASON_REQUIRED: "Укажите основание решения." };
const time = (iso: string | null | undefined) => (iso ? iso.slice(11, 16) : "—");
const mins = (v: number | string | null | undefined) => (v === null || v === undefined ? "нет данных" : `${Math.round(Number(v))} мин`);
const WHY: Record<string, string> = { BASE_ROUTE_NOT_CONFIRMED: "сам основной маршрут ещё не рассчитан полностью — обещать заезд нельзя",
  EXTRA_STOP_INPUTS_MISSING: "для новой точки не хватает данных (время в пути до неё, норма разгрузки или окно приёма)",
  EXTRA_ADDRESS_NOT_UNIQUE: "адрес не найден в справочнике или найден несколько раз", EXTRA_STOP_BREAKS_DEADLINE: "заезд не укладывается в остаток до предельного времени",
  NEW_STOPS_FORBIDDEN: "для рейса включён запрет новых точек" };

export function ExtraStop({ wh, user, trip }: { wh: string; user: string; trip: number }) {
  const [address, setAddress] = useState(""), [asked, setAsked] = useState(""), [reload, setReload] = useState(0), [reason, setReason] = useState("");
  const ev = useRead<Evaluation>(asked ? `/api/transport/preflight/trips/${trip}/extra-stops?address=${encodeURIComponent(asked)}&zone=UTC` : null, reload);
  const hist = useRead<Decisions>(`/api/transport/preflight/trips/${trip}/extra-stops/decisions`, reload);
  const cmd = useCommand<Body, Receipt>(pending, `/api/transport/preflight/trips/${trip}/extra-stops`, user, wh, reasons,
    (r, b) => r.operation_id !== b.operation_id ? null : b.action === "APPROVE" ? "Заезд согласован. Новая точка появится после заказа SAP; SAP сейчас недоступен — заказ не создан."
      : b.action === "DECLINE" ? "Решение «отклонить» записано." : "Настройка запрета новых точек сохранена.", {
    path: () => `/api/transport/preflight/trips/${trip}/extra-stops`, payload: ({ trip_id: _t, ...b }) => b });
  const after = () => setReload(n => n + 1), locked = cmd.busy || cmd.stored.kind !== "none", e = ev.data;
  const decide = (action: "APPROVE" | "DECLINE") => e && cmd.start({ trip_id: trip, action, reason: reason.trim(), address: e.address, zone: "UTC",
    expected_version: e.time_version, source_hash: e.source_hash, ...(action === "APPROVE" ? { position: e.position } : {}) }, after);
  const policy = hist.data;
  return <section className="tc-panel" aria-label="Дополнительный заезд">
    <h5>Дополнительный заезд вне маршрута</h5>
    <p className="tc-note">Система пересчитывает рейс с новой точкой тем же расчётом окон. Заезд предлагается, только если укладывается в остаток времени до предельного срока основной доставки и возврата машины.</p>
    {cmd.stored.kind === "damaged" && <p role="alert" className="tc-err">Сохранённая команда повреждена; новые решения заблокированы.<Tech value={cmd.stored.raw} /></p>}
    {cmd.stored.kind === "ok" && <div className="tc-msg warn"><p>Решение по рейсу № {cmd.stored.intent.body.trip_id} не подтверждено.</p>
      <Act help={help("retry", "Повторить сохранённое решение с тем же номером операции и полями.")} disabled={cmd.busy || cmd.stored.intent.body.trip_id !== trip}
        onClick={() => { if (cmd.stored.kind === "ok") void cmd.send(cmd.stored.intent, after); }}>Повторить ту же команду</Act></div>}
    {cmd.msg && <p role="status" className={"tc-msg " + cmd.msg.tone}>{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>}
    {policy && <p>Запрет новых точек: <b>{policy.new_stops_forbidden ? "включён" : "выключен"}</b>{" "}
      <Act help={help("policy", "Включить или выключить запрет добавления новых точек в этот рейс. При включённом запрете дополнительный заезд не предлагается.")}
        disabled={locked || reason.trim().length < 3} onClick={() => cmd.start({ trip_id: trip, action: "SET_POLICY", reason: reason.trim(),
          new_stops_forbidden: !policy.new_stops_forbidden, expected_policy_version: policy.policy_version }, after)}>{policy.new_stops_forbidden ? "Снять запрет" : "Запретить новые точки"}</Act></p>}
    <label>Адрес получателя для заезда <input value={address} maxLength={255} disabled={locked} onChange={x => setAddress(x.target.value)} /></label>
    <Act help={help("check", "Пересчитать рейс с этим адресом в каждой возможной точке вставки и показать, укладывается ли заезд.")} disabled={!address.trim()}
      onClick={() => { setAsked(address.trim()); setReload(n => n + 1); }}>Проверить заезд</Act>
    {ev.error && <p role="alert" className="tc-err">Проверка не выполнена: {ev.error}</p>}
    {ev.loading && asked && <p className="tc-note">Пересчитываем маршрут…</p>}
    {e && e.address === asked && <Verdict e={e} />}
    {e && e.address === asked && ["PROPOSE", "REJECT", "UNKNOWN"].includes(e.decision) && <>
      <label>Основание решения <input value={reason} maxLength={500} disabled={locked} onChange={x => setReason(x.target.value)} /></label>
      {e.decision === "PROPOSE" && <Act help={help("approve", "Согласовать заезд на текущем маршруте. Сервер повторно пересчитает рейс и откажет, если данные изменились. После согласования нужен заказ SAP.")}
        disabled={locked || reason.trim().length < 3} onClick={() => decide("APPROVE")}>Согласовать заезд</Act>}{" "}
      <Act help={help("decline", "Записать отказ от заезда с основанием. Маршрут не меняется.")} disabled={locked || reason.trim().length < 3} onClick={() => decide("DECLINE")}>Отклонить заезд</Act></>}
    {policy && policy.decisions.length > 0 && <><h6>Решения по рейсу</h6><ul>{policy.decisions.map(d => <li key={d.operation_id}>
      {d.decision_state === "APPROVED" ? "Согласован" : "Отклонён"} заезд «{d.address}» — {d.decided_by}, {time(d.decided_at)} UTC
      {d.validity === "STALE_ROUTE_CHANGED" ? " · маршрут изменился после решения — нужно новое решение" : ""}{d.decision_state === "APPROVED" && d.validity === "CURRENT" ? " · ждёт заказ SAP" : ""}</li>)}</ul></>}
  </section>;
}

function Verdict({ e }: { e: Evaluation }) {
  const tone = e.decision === "PROPOSE" ? "ok" : e.decision === "REJECT" || e.decision === "FORBIDDEN" ? "bad" : "warn";
  const head = { PROPOSE: "Заезд укладывается — предлагается на согласование.", REJECT: "Заезд не укладывается — предложение отклоняется.",
    UNKNOWN: "Нельзя обещать выполнимость.", FORBIDDEN: "Заезд не предлагается.", ALREADY_ON_ROUTE: "Этот адрес уже есть в маршруте." }[e.decision];
  const issues = [...new Set((e.before?.issues ?? []).map(i => i.code))];
  return <div className={"tc-msg " + tone} role="status">
    <p><b>{head}</b>{e.reason ? ` Причина: ${WHY[e.reason] ?? "см. технические сведения"}.` : ""}</p>
    {e.decision === "UNKNOWN" && issues.length > 0 && <p>Чего не хватает основному маршруту: {issues.map(routeIssue).join("; ")}. Задайте это в настройках маршрута, обновите дорожные плечи или карточку адреса и проверьте снова.</p>}
    {e.before_slack_min != null && <p>Остаток до предельного времени: {mins(e.before_slack_min)}{e.decision === "PROPOSE" ? ` → после заезда ${mins(e.after_slack_min)}` : ""}.</p>}
    {e.decision === "PROPOSE" && e.after && e.before && <>
      <p>Заезд добавляет {mins(e.added_min)} к возврату ({time(e.before.return_at)} → {time(e.after.return_at)} UTC); пробег:{" "}
        {e.added_km != null ? `+${e.added_km} км (${e.distance_km_before} → ${e.distance_km_after})` : "нет данных о расстояниях"}.</p>
      <div style={{ overflowX: "auto", maxWidth: "100%" }}><table className="tc-table"><thead><tr><th>Точка</th><th>Приезд до → после</th><th>Ожидание</th><th>Опоздание</th></tr></thead><tbody>
        {e.after.stops.map(s => { const b = e.before!.stops.find(x => x.address === s.address);
          return <tr key={s.address}><td>{s.address === e.address ? <b>{s.address} (новая)</b> : s.address}</td>
            <td>{b ? time(b.arrival_at) : "—"} → {time(s.arrival_at)}</td><td>{mins(s.wait_min)}</td><td>{mins(s.late_min)}</td></tr>; })}
      </tbody></table></div></>}
    <Tech value={e} label="Расчёт до и после заезда" />
  </div>;
}
