import type { HelpEntry } from "../../help/catalog";
import { HelpButton } from "../../help/HelpButton";
import { RAW_ADMIN_BASE } from "../../../../api";
import { planHelpUrl, stateText } from "./planModel";
import type { PlanDetail } from "./planModel";

const h = (id: string, text: string): HelpEntry => ({ id: "consolidation.plan." + id, text, article: "consolidation-plan" });
export const planViewHelp = {
  tree: h("tree", "Показать фактическое физическое дерево корня ниже. План и физика читаются раздельно; планового корня может ещё не быть."),
  edit: h("edit", "Изменить состав или ячейку плана. Изменение отправляется с текущей версией и причиной."),
  refresh: h("refresh", "Перечитать план и готовность с сервера. Ничего не меняет."),
  member: h("member", "Сборка (СТ) в плане и её состояние относительно фактического корня."),
};

/** Ожидаемый состав: корень, плитки сборок по состоянию, итог готовности. ready — «Состав полон», а не «можно отгружать». */
export function PlanView({ plan, onTree, onEdit, onRefresh, busy }: { plan: PlanDetail; onTree: () => void; onEdit: () => void; onRefresh: () => void; busy: boolean }) {
  const r = plan.readiness, cancelled = plan.status === "CANCELLED";
  return <section className="ops-card cp-view" aria-label={"План " + plan.plan_id}>
    <div className="cp-root">
      <span className="cp-root-icon" aria-hidden="true">▣</span>
      <div><span className="cp-eyebrow">ОЖИДАЕМЫЙ СОСТАВ · план v{plan.version}{cancelled ? " · отменён" : ""}</span>
        <h3 className="cp-uid" title={plan.root_identifier}>{plan.root_identifier}</h3>
        <small>ячейка {plan.cell} · склад {plan.warehouse_id}</small></div>
      <span className={"ops-chip " + (cancelled ? "closed" : r.ready ? "ship" : "other")}>{cancelled ? "План отменён" : r.ready ? "Состав полон" : "Состав не полон"}</span>
    </div>
    <dl className="cp-counts">
      <div><dt>Ожидается</dt><dd>{r.expected_count}</dd></div><div><dt>Нет в составе</dt><dd>{r.missing_count}</dd></div>
      <div><dt>Лишние</dt><dd>{r.extra_count}</dd></div><div><dt>Изменены</dt><dd>{r.changed_count}</dd></div>
      <div><dt>Неизвестные листья</dt><dd>{r.unknown_leaf_count}</dd></div><div><dt>Место</dt><dd>{r.location_ready ? "в ячейке плана" : "не подтверждено"}</dd></div>
    </dl>
    {!cancelled && r.ready && <p className="ops-note">«Состав полон» не разрешает отгрузку: качество, вес и погрузку подтверждают их владельцы{r.quality_release_approved === false ? " (выпуск качества не подтверждён)" : ""}.</p>}
    <ul className="cp-members" aria-label="Сборки плана">{r.members.map(m => { const st = stateText(m.state); return <li key={m.fulfillment_id} className={"cp-member " + st.tone} title={planViewHelp.member.text} data-help-id={planViewHelp.member.id}>
      <b title={m.pallet_identifier ?? ""}>{m.pallet_identifier ?? `сборка ${m.fulfillment_id}`}</b>
      <small>СТ {m.shipment_id ?? "—"} · сборка {m.fulfillment_id}</small><span className="cp-state">{st.label}</span></li>; })}</ul>
    <div className="cp-actions">
      <HelpButton help={planViewHelp.tree} onClick={onTree}>Физическое дерево корня</HelpButton>
      <HelpButton help={planViewHelp.edit} unavailable={cancelled && "отменённый план не изменяется"} disabled={busy} onClick={onEdit}>Изменить план</HelpButton>
      <HelpButton help={planViewHelp.refresh} disabled={busy} onClick={onRefresh}>Обновить</HelpButton>
      <a href={`${RAW_ADMIN_BASE}/warehouse-hus.html?identifier=${encodeURIComponent(plan.root_identifier)}`} target="_blank" rel="noopener"
        title="Открыть контроль этого грузового места (состав, вес, качество) в новой вкладке по идентификатору корня" data-help-id="consolidation.plan.control">Контроль места</a>
      <a href={planHelpUrl("refresh")} target="_blank" rel="noopener" title="Справка: состояния сборок и готовность состава. Откроется в новой вкладке" data-help-id="consolidation.plan.help">Справка</a>
    </div>
  </section>;
}
