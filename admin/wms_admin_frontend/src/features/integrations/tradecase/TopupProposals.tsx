import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech } from "./ui";

type Proposal = { proposal_id: number; trip_id: string; need_id: string; priority: number; recipient_id: string; sku_id: string; source_owner_id: string; mrc: string;
  min_expiry_date: string; units_per_box: number; need_boxes: string; proposed_boxes: number; approved_boxes: number; status: string; version: number;
  need_snapshot_at: string; max_age_minutes: number; sap_order_id: string | null; sap_reason: string | null; sap_order_received: boolean;
  holds: { reservation_id: number; base_quantity: string; status: string }[];
  calculation: { limited_by: string | null; uncovered_boxes: string; sender_stock_boxes: number; already_confirmed_boxes: string } };
type List = { items: Proposal[]; approval_available: boolean };
type Action = "SAVE" | "ADJUST" | "REJECT" | "CONFIRM" | "RELEASE";
export type TopupBody = { operation_id: string; action: Action; trip: string; proposal_id?: number; expected_version?: number; boxes?: number;
  need_ids?: string[]; max_age_minutes?: number };

const ACTIONS: Action[] = ["SAVE", "ADJUST", "REJECT", "CONFIRM", "RELEASE"];
export const topupJournal = journal<TopupBody>("topup", "TC.TOPUP.UI", b => ACTIONS.includes(b.action) && Boolean(b.trip)
  && (b.action === "SAVE" ? Array.isArray(b.need_ids) && b.need_ids.length > 0 : Number.isSafeInteger(b.proposal_id) && Number.isSafeInteger(b.expected_version)), "решение по добивке");
const help = (id: string, text: string) => ({ id: "tradecase.topup." + id, text, anchor: "topup.decide" });
const STATUS: Record<string, string> = { PROPOSED: "предложено", ADJUSTED: "количество изменено", REJECTED: "отклонено — складских заданий нет",
  CONFIRMED: "подтверждено, короба удержаны; ждём ответ SAP", SAP_ACCEPTED: "SAP создал заказ", SAP_REJECTED: "SAP отказал, удержание снято", CANCELLED: "отменено, удержание снято" };
const LIMIT: Record<string, string> = { CAPACITY: "ограничено свободным местом в машине", SENDER_STOCK: "ограничено пригодным запасом сверх основных заказов" };
const REASONS: Record<string, string> = {
  TRADE_TOPUP_CAPACITY_BASIS_CHANGED: "место в машине изменилось после расчёта (другое подтверждение, рейс или машина) — сохраните расчёт заново",
  TRADE_TOPUP_NEED_EXPIRED: "данные потребности устарели — обновите снимок и пересчитайте", TRADE_TOPUP_NEED_VERSION_CHANGED: "пришла новая версия потребности — пересчитайте",
  TRADE_TOPUP_NEED_ALREADY_COVERED: "потребность уже покрыта другим подтверждением", TRADE_TOPUP_SENDER_STOCK_INSUFFICIENT: "не хватает пригодных целых коробов",
  TRADE_TOPUP_MAIN_ORDER_STOCK_PROTECTED: "запас нужен основным заказам — уменьшите количество", TRADE_TOPUP_STOCK_CHANGED: "выбранный запас изменился — повторите подтверждение",
  TOPUP_LOADING_ALREADY_STARTED: "погрузка рейса уже началась", VERSION_CONFLICT: "предложение изменилось — обновите список", TRADE_TOPUP_STATE_CONFLICT: "предложение уже в другом состоянии",
  TRADE_TOPUP_ACCESS_DENIED: "нет права согласовывать добивку на этом складе", TRADE_OWNER_ACCESS_DENIED: "нет права на собственника товара",
  TRADE_TOPUP_ADJUST_OUT_OF_RANGE: "количество должно быть от 1 до предложенного", TOPUP_STOCK_TERMS_REQUIRED: "нет основного заказа этого получателя и товара — условия запаса неизвестны",
  TOPUP_STOCK_TERMS_AMBIGUOUS: "в основных заказах разные условия товара", TRADE_TOPUP_ADOPTED_RETURN_REQUIRED: "товар уже передан в сборку — нужен возврат, а не отмена",
  TRADE_TOPUP_OPERATION_CONFLICT: "номер операции уже использован с другими данными" };

function route(wh: string, b: TopupBody) {
  const base = `/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(b.trip)}/topup-proposals`;
  return b.action === "SAVE" ? base : `${base}/${b.proposal_id}/${b.action === "CONFIRM" ? "confirm" : b.action === "RELEASE" ? "release" : "decision"}`;
}
function payload(b: TopupBody) {
  if (b.action === "SAVE") return { operation_id: b.operation_id, need_ids: b.need_ids, max_age_minutes: b.max_age_minutes };
  if (b.action === "ADJUST" || b.action === "REJECT") return { operation_id: b.operation_id, expected_version: b.expected_version, action: b.action, ...(b.action === "ADJUST" ? { boxes: b.boxes } : {}) };
  return { operation_id: b.operation_id, expected_version: b.expected_version };
}
const DONE: Record<Action, string> = { SAVE: "Предложения сохранены.", ADJUST: "Количество изменено.", REJECT: "Предложение отклонено; складские задания не созданы.",
  CONFIRM: "Подтверждено: короба удержаны, запрос в SAP поставлен в очередь. Заказ SAP ещё не создан.", RELEASE: "Отменено: удержание этого предложения снято." };

/** Согласование добивки: сохранённые предложения, изменение/отклонение, подтверждение с удержанием и отмена.
 *  Все решения — долговечные команды: неизвестный исход повторяется тем же телом; сборка до заказа SAP не начинается. */
export function useTopup(wh: string, user: string) {
  const [reload, setReload] = useState(0);
  const cmd = useCommand<TopupBody, { replayed?: boolean }>(topupJournal, "", user, wh, REASONS, (_r, b) => DONE[b.action],
    { path: b => route(wh, b), payload });
  return { cmd, reload, refresh: () => setReload(n => n + 1) };
}

export function TopupProposals({ wh, trip, topup }: { wh: string; trip: string; topup: ReturnType<typeof useTopup> }) {
  const list = useRead<List>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(trip)}/topup-proposals`, topup.reload);
  const { cmd } = topup, s = cmd.stored, after = () => topup.refresh();
  const note = cmd.msg && <p className={"tc-msg " + cmd.msg.tone} role="status">{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>;
  return <section className="tc-bind" aria-label="Предложения добивки">
    <h4>Предложения добивки <HelpLink anchor="topup.decide" /></h4>
    {s.kind === "damaged" && <div className="tc-msg bad">Сохранённое решение по добивке повреждено; новое не создаётся.<Tech value={s.raw} /></div>}
    {s.kind === "ok" && <div className="tc-bind warn"><p>Сохранённое решение по добивке ({s.intent.body.action}, рейс {s.intent.body.trip}). {s.intent.sent ? "Результат не подтверждён." : "Ещё не отправлено."} Другие решения заблокированы.</p>
      <Act help={help("retry", "Повторить ту же команду с тем же номером операции. Повтор не создаст второе удержание или второй запрос в SAP.")} disabled={cmd.busy} onClick={() => cmd.send(s.intent, after)}>Повторить ту же команду</Act></div>}
    {note}
    {list.loading && !list.data && <p className="tc-note">Читаем предложения…</p>}
    {list.error && <p className="tc-err" role="alert">{list.error}</p>}
    {list.data && list.data.items.length === 0 && <p className="tc-note">Сохранённых предложений по этому рейсу нет. Распределите место и сохраните расчёт.</p>}
    {list.data && !list.data.approval_available && list.data.items.length > 0 && <p className="tc-note">Подтверждение пока недоступно: сервер ещё не разрешил удержание запаса под добивку.</p>}
    {list.data?.items.map(p => <ProposalCard key={p.proposal_id} p={p} approval={list.data!.approval_available} locked={s.kind !== "none" || cmd.busy}
      act={(action, extra) => cmd.start({ action, trip, proposal_id: p.proposal_id, expected_version: p.version, ...extra }, after)} />)}
  </section>;
}

function ProposalCard({ p, approval, locked, act }: { p: Proposal; approval: boolean; locked: boolean; act: (a: Action, extra?: { boxes: number }) => void }) {
  const [boxes, setBoxes] = useState(""), open = p.status === "PROPOSED" || p.status === "ADJUSTED", held = p.holds.filter(h => h.status === "ACTIVE");
  const n = Number(boxes), valid = /^\d+$/.test(boxes) && n >= 1 && n <= p.proposed_boxes;
  return <article className="tc-panel" aria-label={"Предложение " + p.proposal_id}>
    <h5>{p.priority}. {p.recipient_id} · {p.sku_id} — {STATUS[p.status] ?? "состояние не распознано"}</h5>
    <dl className="tc-fields">
      <dt>Потребность</dt><dd>{p.need_boxes} кор.{p.calculation.already_confirmed_boxes !== "0" ? `, уже подтверждено другими рейсами ${p.calculation.already_confirmed_boxes}` : ""}</dd>
      <dt>Предложено / к отправке</dt><dd>{p.proposed_boxes} / {p.approved_boxes} кор. ({p.units_per_box} шт. в коробе)</dd>
      <dt>Почему столько</dt><dd>{p.calculation.limited_by ? LIMIT[p.calculation.limited_by] ?? p.calculation.limited_by : "покрывает потребность"}; осталось покрыть {p.calculation.uncovered_boxes} кор.; пригодно сверх основных заказов {p.calculation.sender_stock_boxes} кор.</dd>
      <dt>Товар</dt><dd>собственник {p.source_owner_id}, МРЦ {p.mrc}, годен не раньше {p.min_expiry_date}</dd>
      {held.length > 0 && <><dt>Удержано</dt><dd>{held.reduce((a, h) => a + Number(h.base_quantity), 0)} шт., мест хранения: {held.length}</dd></>}
      {p.sap_order_id && <><dt>Заказ SAP</dt><dd>{p.sap_order_id} · {p.sap_order_received ? "заказ получен" : "документ заказа ещё не получен"}</dd></>}
      {p.sap_reason && <><dt>Причина отказа SAP</dt><dd>{p.sap_reason}</dd></>}
    </dl>
    {open && <div className="tc-actions">
      <label>Коробов к отправке<input value={boxes} inputMode="numeric" onChange={e => setBoxes(e.target.value.replace(/\D/g, ""))} title="Новое количество: от 1 до предложенного расчётом" data-help-id="tradecase.topup.boxes" /></label>
      <Act help={help("adjust", "Уменьшить количество в пределах расчёта. Запас не удерживается, заказ не создаётся.")} disabled={locked || !valid} onClick={() => act("ADJUST", { boxes: n })}>Изменить</Act>
      <Act help={help("reject", "Отклонить предложение. Складские задания и запрос в SAP не создаются.")} disabled={locked} onClick={() => act("REJECT")}>Отклонить</Act>
      <Act help={help("confirm", "Подтвердить: сервер заново сверит место, потребность и запас, удержит целые короба и поставит один запрос заказа в SAP. Сборка начнётся только после заказа SAP.")}
        disabled={locked || !approval || p.approved_boxes < 1} onClick={() => act("CONFIRM")}>Подтвердить</Act></div>}
    {(p.status === "CONFIRMED" || p.status === "SAP_ACCEPTED") && <Act help={help("release", "Отменить добивку и снять удержание только этого предложения. Если запрос уже ушёл в SAP, туда отправится отмена.")}
      disabled={locked} onClick={() => act("RELEASE")}>Отменить добивку</Act>}
    <Tech value={p} label="Версии и данные предложения" />
  </article>;
}
