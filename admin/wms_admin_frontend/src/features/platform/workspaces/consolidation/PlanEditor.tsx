import { useState } from "react";
import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { useApiRead } from "../../access-admin";
import { planHelpUrl } from "./planModel";
import type { PlanDetail } from "./planModel";

const h = (id: string, text: string): HelpEntry => ({ id: "consolidation.edit." + id, text, article: "consolidation-plan" });
const help = {
  root: h("root", "Идентификатор будущего или существующего корня паллеты (SSCC/код места), куда собираются сборки."),
  cell: h("cell", "Ячейка, где должен стоять собранный корень."),
  order: h("order", "Найти заказ по номеру, чтобы выбрать его сборки (СТ). Технические номера вводить не нужно."),
  search: h("search", "Найти заказы по номеру. Список читается с вашими правами; закрытые заказы не показываются."),
  pick: h("pick", "Добавить или убрать эту сборку из ожидаемого состава."),
  remove: h("remove", "Убрать сборку из ожидаемого состава. Физическое дерево не меняется."),
  reason: h("reason", "Причина изменения — сохраняется в истории плана."),
  save: h("save", "Сохранить ожидаемый состав с текущей версией плана. При потере ответа повторяется та же команда."),
  cancel: h("cancel", "Отменить план. История сохраняется; физическое дерево не разбирается."),
  close: h("close", "Закрыть редактор без изменений."),
};
type Order = { customer_order_id: number; order_no: string; status: string; ware_id: number; customer_name: string | null; shipment_date: string | null };
type Fulfillment = { fulfillment_id: number; legacy_sborka_pallet_id: number | null; pallet_uid: string | null; status: string; customer_order_id: number };
export type MemberPick = { fulfillment_id: number; label: string };
export type EditorValue = { root_identifier: string; cell: string; members: MemberPick[]; reason: string };

function OrderPicker({ picked, onToggle, warehouseId }: { picked: Set<number>; onToggle: (m: MemberPick) => void; warehouseId: string }) {
  const [text, setText] = useState(""), [query, setQuery] = useState(""), [orderId, setOrderId] = useState<number | null>(null);
  const orders = useApiRead<Order[]>(query ? `/api/customer-orders?order_no=${encodeURIComponent(query)}&limit=10` : null);
  const ful = useApiRead<Fulfillment[]>(orderId ? `/api/customer-orders/${orderId}/fulfillment` : null);
  return <div className="cp-picker">
    <label>Заказ <input value={text} onChange={e => setText(e.target.value)} placeholder="номер заказа" title={help.order.text} data-help-id={help.order.id} /></label>
    <HelpButton help={help.search} unavailable={!text.trim() && "введите номер заказа"} onClick={() => { setQuery(text.trim()); setOrderId(null); }}>Найти</HelpButton>
    {orders.error && <p className="ops-err">{orders.error.includes("права") ? orders.error + " Заказы этого склада недоступны вашей учётной записи." : orders.error}</p>}
    {orders.data && (orders.data.length === 0 ? <p className="ops-note">Заказы не найдены.</p> : <ul className="ops-list">{orders.data.map(o => <li key={o.customer_order_id}>
      <span><b>{o.order_no}</b><br /><small>{o.customer_name ?? "клиент не указан"} · склад {o.ware_id}{String(o.ware_id) !== warehouseId ? " (другой склад)" : ""} · {o.status}</small></span>
      <HelpButton help={help.order} onClick={() => setOrderId(o.customer_order_id)}>Сборки</HelpButton></li>)}</ul>)}
    {ful.error && <p className="ops-err">{ful.error}</p>}
    {ful.data && (ful.data.length === 0 ? <p className="ops-note">У заказа нет сборок.</p> : <ul className="ops-list">{ful.data.map(f => {
      const label = `${f.pallet_uid ?? "без идентификатора"} · СТ ${f.legacy_sborka_pallet_id ?? "—"}`;
      return <li key={f.fulfillment_id}><label className="cp-check"><input type="checkbox" checked={picked.has(f.fulfillment_id)} onChange={() => onToggle({ fulfillment_id: f.fulfillment_id, label })}
        title={help.pick.text} data-help-id={help.pick.id} /> <span><b>{f.pallet_uid ?? "без идентификатора"}</b><br /><small>СТ {f.legacy_sborka_pallet_id ?? "—"} · {f.status}</small></span></label></li>; })}</ul>)}
  </div>;
}

/** Редактор ожидаемого состава. Значения уходят серверу как есть; сортировку и уникальность ID проверит и сервер. */
export function PlanEditor({ plan, warehouseId, planId, busy, onSave, onCancelPlan, onClose }: {
  plan: PlanDetail | null; warehouseId: string; planId: string; busy: boolean;
  onSave: (v: EditorValue) => void; onCancelPlan: (reason: string) => void; onClose: () => void;
}) {
  const [root, setRoot] = useState(plan?.root_identifier ?? ""), [cell, setCell] = useState(plan?.cell ?? ""), [reason, setReason] = useState("");
  const [members, setMembers] = useState<MemberPick[]>(() => (plan?.readiness.members ?? []).map(m => ({ fulfillment_id: m.fulfillment_id, label: `${m.pallet_identifier ?? "без идентификатора"} · СТ ${m.shipment_id ?? "—"}` })));
  const picked = new Set(members.map(m => m.fulfillment_id));
  const toggle = (m: MemberPick) => setMembers(old => old.some(x => x.fulfillment_id === m.fulfillment_id) ? old.filter(x => x.fulfillment_id !== m.fulfillment_id) : [...old, m]);
  const bytes = (s: string) => new TextEncoder().encode(s).length;
  const problem = !root.trim() || root !== root.trim() || bytes(root) > 200 ? "корень: 1–200 байт, без пробелов по краям"
    : !cell.trim() || cell !== cell.trim() || bytes(cell) > 60 ? "ячейка: 1–60 байт, без пробелов по краям"
    : members.length < 1 || members.length > 200 ? "выберите от 1 до 200 сборок" : !reason.trim() ? "укажите причину" : null;
  return <section className="ops-card cp-editor" aria-label="Изменение плана">
    <h3>{plan ? `Изменить план ${planId}` : `Новый план ${planId}`} <small>{plan ? `версия ${plan.version}` : "версия 0"}</small></h3>
    <label>Корень паллеты <input value={root} onChange={e => setRoot(e.target.value)} title={help.root.text} data-help-id={help.root.id} maxLength={200} /></label>
    <label>Ячейка <input value={cell} onChange={e => setCell(e.target.value)} title={help.cell.text} data-help-id={help.cell.id} maxLength={60} /></label>
    <h3>Сборки в плане <small>{members.length}</small></h3>
    <ul className="ops-list">{members.map(m => <li key={m.fulfillment_id}><span><b>{m.label}</b><br /><small>сборка {m.fulfillment_id}</small></span>
      <HelpButton help={help.remove} disabled={busy} onClick={() => toggle(m)}>Убрать</HelpButton></li>)}</ul>
    <OrderPicker picked={picked} onToggle={toggle} warehouseId={warehouseId} />
    <label>Причина <textarea rows={2} value={reason} maxLength={1000} onChange={e => setReason(e.target.value)} title={help.reason.text} data-help-id={help.reason.id} /></label>
    <div className="cp-actions">
      <HelpButton help={help.save} unavailable={problem} disabled={busy} onClick={() => onSave({ root_identifier: root, cell, members, reason: reason.trim() })}>Сохранить план</HelpButton>
      {plan && plan.status === "ACTIVE" && <HelpButton help={help.cancel} unavailable={!reason.trim() && "укажите причину отмены"} disabled={busy} onClick={() => onCancelPlan(reason.trim())}>Отменить план</HelpButton>}
      <HelpButton help={help.close} disabled={busy} onClick={onClose}>Закрыть</HelpButton>
      <a href={planHelpUrl(plan ? "save" : "save")} target="_blank" rel="noopener" title="Справка: как сохранить и отменить план. Откроется в новой вкладке, черновик сохранится" data-help-id="consolidation.edit.help">Справка</a>
    </div>
  </section>;
}
