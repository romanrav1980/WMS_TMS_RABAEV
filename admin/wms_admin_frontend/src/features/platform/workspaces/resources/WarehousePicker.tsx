import { useEffect } from "react";
import { useApiRead } from "../../access-admin";
import { ganttHelp } from "./ganttHelp";

export type WorkspaceWarehouse = { warehouse_id: number; title: string; capabilities: Record<string, boolean> };
type Workspaces = { warehouses: WorkspaceWarehouse[]; limit: number; has_more: boolean; navigation_only: boolean };

/** Выбор склада из GET /api/access/workspaces (C-0083): только склады с нужной native-возможностью. Это навигация,
 *  не разрешение: данные API всё равно проверяют доступ. Если список не прочитан — ручной ввод кода с пометкой. */
export function WarehousePicker({ value, onChange, capability }: { value: string; onChange: (id: string) => void; capability: string }) {
  const read = useApiRead<Workspaces>("/api/access/workspaces");
  const list = (read.data?.warehouses ?? []).filter(w => w.capabilities?.[capability]);
  // Единственный доступный склад выбирается сам; при нескольких — не угадываем (C-0085).
  useEffect(() => { if (!value && list.length === 1) onChange(String(list[0].warehouse_id)); }, [value, list.length === 1 ? list[0].warehouse_id : null]);
  const id = "rg-wh-" + capability;
  return <label>Склад/РЦ
    <input list={id} inputMode="numeric" value={value} placeholder={read.data ? `${list.length} доступно` : "код склада"} style={{ width: 150 }}
      onChange={e => onChange(e.target.value.replace(/\D/g, ""))} title={ganttHelp.warehouse.text} data-help-id={ganttHelp.warehouse.id} />
    <datalist id={id}>{list.map(w => <option key={w.warehouse_id} value={String(w.warehouse_id)}>{w.title}</option>)}</datalist>
    {read.error && <small className="ops-err"> список складов не прочитан: {read.error}</small>}
    {read.data && list.length === 0 && <small className="ops-err"> нет складов с этой возможностью</small>}
    {read.data?.has_more && <small className="ops-note"> показаны первые {read.data.limit}</small>}
    {value && read.data && !list.some(w => String(w.warehouse_id) === value) && <small className="ops-note"> склад не в списке доступных — сервер проверит доступ</small>}
  </label>;
}
