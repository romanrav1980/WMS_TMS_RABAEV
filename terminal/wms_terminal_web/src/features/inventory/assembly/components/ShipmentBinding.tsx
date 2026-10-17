import { useState } from "react";
import type { AssemblyContext } from "../contracts";
import type { ShipmentBindState } from "../useShipmentBind";
export function BindingRecovery({ workflow }: { workflow: ShipmentBindState }) {
  if (!workflow.entry && !workflow.error) return null;
  return <section className="asm-weigh-card" aria-label="Сверка привязки отгрузки"><h3>Привязка к отгрузке</h3><p>Исходная привязка сохранена. Сначала прочитайте результат или повторите её без изменений.</p>
    {workflow.error && <p className="asm-err" role="alert">{workflow.error}</p>}
    <button type="button" disabled={workflow.busy || workflow.denied} onClick={workflow.read} title="Прочитать текущую привязку этого задания. Неподтверждённый запрос сохраняется." data-help-id="assembly.bind-read">Прочитать привязку</button>
    <button type="button" disabled={workflow.busy || workflow.denied} onClick={workflow.retry} title="Повторить исходный адрес и тело привязки; другой СТ этот запрос не подменит." data-help-id="assembly.bind-retry">Повторить ту же привязку</button></section>;
}
export function ShipmentBinding({ context, container, workflow, disabled }: { context: AssemblyContext; container: string; workflow: ShipmentBindState; disabled: boolean }) {
  const [selected, select] = useState("");
  if (context.shipment_binding_state === "BOUND") return <p className="asm-note">Отгрузка привязана: {context.bound_pallet_identifier}.</p>;
  const candidates = context.prepared_shipments ?? [];
  const valid = candidates.some(c => c.pallet_identifier === selected);
  return <section className="asm-weigh-card"><h3>Отгрузка для этой сборки</h3>
    <p className="asm-note">Выберите подготовленную СТ своего заказа. Сервер повторно проверит физический состав.</p>
    {!candidates.length && <p className="asm-note">Нет подготовленной СТ этого заказа. Ответственный за планирование должен подготовить её в существующем процессе.</p>}
    <select aria-label="Подготовленная отгрузка" title="Выберите существующую подготовленную СТ текущего заказа. Новая СТ не создаётся." value={selected} onChange={e => select(e.target.value)} disabled={disabled || workflow.blocked} data-help-id="assembly.bind-select">
      <option value="">Выберите СТ</option>{candidates.map(c => <option key={c.fulfillment_id} value={c.pallet_identifier}>{c.pallet_identifier}</option>)}
    </select>
    <button type="button" disabled={disabled || workflow.blocked || !valid || container !== context.scan_container} onClick={() => workflow.start({ pallet_identifier: selected, scan_container: container, expected_content_version: context.content_version })}
      title="Сохранить и отправить привязку этой физической тары к выбранной существующей СТ. Остатки не изменяются." data-help-id="assembly.bind-submit">Привязать отгрузку</button>
  </section>;
}
