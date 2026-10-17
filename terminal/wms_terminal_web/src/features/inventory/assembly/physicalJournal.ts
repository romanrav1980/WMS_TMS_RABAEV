import { readIntent, saveIntent, clearIntent } from "./journal";
import type { JournalMeta } from "./journal";
import { pendingCommands } from "./savedCommands";
import { readAbandonment } from "./abandonment";
import { bindPath, WEIGH_PATH, keyPattern } from "./physicalContracts";
import type { BindBody, WeighBody } from "./physicalContracts";
export type PhysicalKind = "warehouse_weigh" | "shipment_bind";
export interface PhysicalIntent<T> { version: 1; url: string; body: T }
export function readPhysical<T extends WeighBody | BindBody>(kind: PhysicalKind, meta: JournalMeta): PhysicalIntent<T> | null {
  const entry = readIntent<PhysicalIntent<T>>(kind, meta);
  if (!entry) return null;
  const value = entry.body;
  if (!value || typeof value !== "object" || !value.body || typeof value.body !== "object") throw new Error("Сохранённый запрос повреждён. Исходная запись сохранена, новые действия заблокированы.");
  const b = value.body as Partial<WeighBody & BindBody>;
  const allowed = kind === "shipment_bind" ? ["pallet_identifier","scan_container","expected_content_version"] : ["request_id","device_id","purpose","case_task_id","expected_content_version","scan_container","zero_progress_required", ...(b.purpose === "FINAL_GROSS" ? ["tare_capture_key","expected_composition_signature"] : ["resource_session_id"])];
  if (Object.keys(value).some(key => !["version","url","body"].includes(key)) || Object.keys(b).some(key => !allowed.includes(key))) throw new Error("Сохранённый запрос содержит неизвестные поля. Нужна сверка исходной записи.");
  const common = value.version === 1 && !!b && typeof b.scan_container === "string" && b.scan_container.length > 0 && b.scan_container.length <= 150 && Number.isInteger(b.expected_content_version) && Number(b.expected_content_version) >= 0;
  const correct = kind === "shipment_bind" ? value.url === bindPath(meta.task_id) && typeof b.pallet_identifier === "string" && !!b.pallet_identifier
    : value.url === WEIGH_PATH && b.case_task_id === meta.task_id && typeof b.request_id === "string" && b.request_id.length > 0 && b.request_id.length <= 100 && typeof b.device_id === "string" && b.device_id.length > 0 && b.device_id.length <= 100 && b.zero_progress_required === true
      && (b.purpose === "EMPTY_TARE" ? !b.tare_capture_key && !b.expected_composition_signature && (b.resource_session_id === undefined || Number.isInteger(b.resource_session_id) && Number(b.resource_session_id) > 0) : b.purpose === "FINAL_GROSS" && !!b.tare_capture_key && keyPattern.test(b.tare_capture_key) && !!b.expected_composition_signature && keyPattern.test(b.expected_composition_signature));
  if (!common || !correct) throw new Error("Сохранённый запрос весов/привязки повреждён или потерял исходный адрес. Новые действия заблокированы.");
  return value;
}
export function assertPhysicalClear(meta: JournalMeta): void {
  if (readPhysical("warehouse_weigh", meta) || readPhysical("shipment_bind", meta)) throw new Error("Сначала сверьте сохранённый запрос весов или привязку отгрузки.");
}
export async function physicalLock<T>(kind: PhysicalKind, meta: JournalMeta, work: () => Promise<T>, readOnly = false): Promise<T> {
  if (!navigator.locks) throw new Error("Браузер не поддерживает безопасный журнал между вкладками.");
  return navigator.locks.request(`assembly-command:${meta.server}:${meta.actor}:${meta.task_id}`, async () => {
    if (!readOnly && (pendingCommands(meta).length || readAbandonment(meta))) throw new Error("Сначала восстановите исходную команду сборки.");
    const other = kind === "warehouse_weigh" ? "shipment_bind" : "warehouse_weigh";
    if (!readOnly && readPhysical(other, meta)) throw new Error("Есть другой незавершённый запрос этого задания.");
    return work();
  });
}
export function persistPhysical<T>(kind: PhysicalKind, meta: JournalMeta, value: PhysicalIntent<T>): void { saveIntent(kind, meta, value); }
export function clearPhysical(kind: PhysicalKind, meta: JournalMeta): void { clearIntent(kind, meta); }


