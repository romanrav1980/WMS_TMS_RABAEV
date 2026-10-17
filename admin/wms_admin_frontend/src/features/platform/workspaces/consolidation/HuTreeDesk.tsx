import { apiFetch, apiOperationScope, ApiRequestError } from "../../../../api";
import { HelpHint } from "../../help/HelpHint";
import { HuTreeWorkspace } from "../../../inventory";

async function loadComposition(identifier: string, signal: AbortSignal): Promise<unknown> {
 try {
  return await apiFetch<unknown>("/api/warehouse-hus/composition?identifier=" + encodeURIComponent(identifier), { signal });
 } catch (error) {
  if (error instanceof ApiRequestError && error.status === 403) {
   throw new Error("Нет допуска к составу грузового места. Текущий HU API требует warehouse_task_view и серверного допуска к фактическому складу. Выбор рабочего места не выдаёт права.");
  }
  throw error;
 }
}
/** Read-only host. No invented links to resource/Gantt identities absent from snapshot. */
export function HuTreeDesk({ identifier = "" }: { identifier?: string }) {
 return <div className="ops-panel" style={{ gridColumn: "1 / -1", minWidth: 0 }}>
  <HuTreeWorkspace loadComposition={loadComposition} accessKey={apiOperationScope()} initialIdentifier={identifier} helpSlot={<HelpHint help={{ id: "hu.tree", article: "warehouse-hu-tree", title: "Дерево грузового места", text: "Сканируйте место любого уровня. Выберите узел для фактов; родитель открывается отдельным чтением.", details: ["Показан серверный состав, а не план ожидаемых детей.", "Учётная масса, scale_qc и запись размещения имеют разные основания. Неизвестные факты остаются неизвестными."] }} />} />
 </div>;
}
