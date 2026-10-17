import { canonical, hash, record, validateAbandoned, validateOriginal, validateResolution } from "./contracts";
import type { ControlBody, OriginalIntent, RecoveryProof } from "./contracts";
export class ControlJournalError extends Error {}
export interface SavedControl { schema: 1; body: ControlBody; wire: string; sha256: string; original: OriginalIntent; proof: RecoveryProof | null }
function key(original: OriginalIntent): string { return "wms.metadata-intent-control.v1:" + encodeURIComponent(original.server) + ":" + encodeURIComponent(original.actor) + ":" + original.domain + ":" + original.task_id + ":" + original.request_sha256; }
async function loadControl(original: OriginalIntent): Promise<SavedControl | null> {
 await validateOriginal(original);
 const raw = localStorage.getItem(key(original)); if (raw === null) return null;
 const value: unknown = JSON.parse(raw);
 if (!record(value) || value.schema !== 1 || !record(value.body) || !record(value.original)
  || canonical(value.original) !== canonical(original) || typeof value.wire !== "string"
  || value.wire !== canonical(value.body) || value.sha256 !== await hash(value.wire)
  || Object.keys(value).sort().join() !== "body,original,proof,schema,sha256,wire"
  || Object.keys(value.body).sort().join() !== "domain,operation_id,original_wire,reason,task_id"
  || value.body.domain !== original.domain || value.body.task_id !== original.task_id || value.body.original_wire !== original.wire
  || typeof value.body.operation_id !== "string" || !/^[A-Za-z0-9_.:-]{1,100}$/.test(value.body.operation_id) || value.body.operation_id === original.operation_id
  || typeof value.body.reason !== "string" || Array.from(value.body.reason.trim()).length < 8 || Array.from(value.body.reason).length > 500)
  throw new Error("Журнал прекращения повреждён. Исходные данные сохранены; нужен разбор старшим смены.");
 const saved = value as unknown as SavedControl;
 if (saved.proof?.status === "ABANDONED") validateAbandoned(saved.proof.abandonment, original);
 else if (saved.proof !== null) validateResolution({ ...original, original_operation_id: original.operation_id, original_request_sha256: original.request_sha256,
  status: saved.proof.status, original_receipt: saved.proof.original_receipt, abandonment: null }, original);
 return saved;
}
async function createControl(original: OriginalIntent, reason: string): Promise<SavedControl> {
 const previous = await readControl(original); if (previous) return previous;
 if (Array.from(reason.trim()).length < 8 || Array.from(reason).length > 500) throw new Error("Нужна явная причина от 8 до 500 символов.");
 const body: ControlBody = { operation_id: "META.ABANDON:" + crypto.randomUUID(), domain: original.domain, task_id: original.task_id, reason, original_wire: original.wire };
 const wire = canonical(body), saved: SavedControl = { schema: 1, body, wire, sha256: await hash(wire), original, proof: null };
 if (localStorage.getItem(key(original)) !== null) throw new Error("Запрос прекращения изменён в другой вкладке.");
 const raw = JSON.stringify(saved); localStorage.setItem(key(original), raw);
 if (localStorage.getItem(key(original)) !== raw) throw new Error("Запрос прекращения не сохранён. Отправка запрещена.");
 return (await readControl(original))!;
}
async function recordProof(original: OriginalIntent, proof: RecoveryProof): Promise<void> {
 const saved = await readControl(original);
 if (!saved) return; // A read-only resolution can find a tombstone created on another device.
 const raw = JSON.stringify(saved), actual = localStorage.getItem(key(original));
 if (actual !== raw) throw new Error("Журнал прекращения изменён. Прочитайте результат повторно.");
 if (proof.status === "ABANDONED") validateAbandoned(proof.abandonment, original);
 if (saved.proof && JSON.stringify(saved.proof) !== JSON.stringify(proof)) throw new Error("Серверные доказательства противоречат друг другу. Нужен разбор владельцем.");
 const next = JSON.stringify({ ...saved, proof }); localStorage.setItem(key(original), next);
 if (localStorage.getItem(key(original)) !== next) throw new Error("Квитанция прекращения не сохранена; исходный запрос остаётся заблокирован.");
}

export async function readControl(original: OriginalIntent): Promise<SavedControl | null> {
 try { return await loadControl(original); }
 catch { throw new ControlJournalError("Журнал прекращения недоступен или повреждён. Исходные записи сохранены; действия заблокированы до разбора владельцем."); }
}
export async function saveControl(original: OriginalIntent, reason: string): Promise<SavedControl> {
 try { return await createControl(original, reason); }
 catch (error) { throw new ControlJournalError(error instanceof Error ? error.message : "Запрос прекращения не сохранён. Отправка запрещена."); }
}
export async function saveProof(original: OriginalIntent, proof: RecoveryProof): Promise<void> {
 try { return await recordProof(original, proof); }
 catch (error) { throw new ControlJournalError(error instanceof Error ? error.message : "Серверная квитанция не сохранена. Исходный запрос остаётся заблокирован."); }
}
