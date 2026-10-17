import { useCallback, useEffect, useRef, useState } from "react";
import { rawApiGet, rawApiPost, isAuthError } from "./api";
import type { AssemblyCredentials, AssemblyContext } from "./contracts";
import type { JournalMeta } from "./journal";
import { bindPath, boundContext } from "./physicalContracts";
import type { BindBody } from "./physicalContracts";
import { readPhysical, physicalLock, persistPhysical, clearPhysical } from "./physicalJournal";
import type { PhysicalIntent } from "./physicalJournal";
export function useShipmentBind(credentials: AssemblyCredentials, meta: JournalMeta, refreshContext: () => void) {
  const [entry, setEntry] = useState<PhysicalIntent<BindBody> | null>(null), [error, setError] = useState(""), [busy, setBusy] = useState(false), [denied, setDenied] = useState(false);
  const life = useRef(true), refresh = useRef(refreshContext); refresh.current = refreshContext;
  const restore = useCallback(() => { try { setEntry(readPhysical<BindBody>("shipment_bind", meta)); setError(""); } catch (err) { setError(err instanceof Error ? err.message : String(err)); } }, [meta]);
  useEffect(() => { life.current = true; restore(); window.addEventListener("storage", restore); return () => { life.current = false; window.removeEventListener("storage", restore); }; }, [restore]);
  const resolve = useCallback(async (original: PhysicalIntent<BindBody>, retry: boolean) => {
    await physicalLock("shipment_bind", meta, async () => {
      if (JSON.stringify(readPhysical("shipment_bind", meta)) !== JSON.stringify(original)) throw new Error("Сохранённая привязка изменилась. Перечитайте журнал.");
      if (retry) {
        const ack = await rawApiPost<{case_pick_task_id: number; pallet_identifier: string; status: string; fulfillment_status: string; idempotent: boolean}>(original.url, credentials, original.body);
        if (ack.case_pick_task_id !== meta.task_id || ack.pallet_identifier !== original.body.pallet_identifier || ack.status !== "BOUND" || ack.fulfillment_status !== "PICKED" || typeof ack.idempotent !== "boolean") throw new Error("Ответ не подтверждает исходную привязку. Журнал сохранён.");
      }
      const context = await rawApiGet<AssemblyContext>(`/api/inventory/assembly-scale/context?task_id=${meta.task_id}`, credentials);
      if (!boundContext(context, meta.task_id, original.body)) throw new Error("Текущая привязка ещё не подтверждена. Исходный запрос сохранён; новый не создаётся.");
      clearPhysical("shipment_bind", meta);
      if (life.current) { setEntry(null); setError(""); setDenied(false); refresh.current(); }
    }, !retry);
  }, [credentials, meta]);
  const run = useCallback(async (retry: boolean, body?: BindBody) => {
    if (busy || denied) return; setBusy(true);
    try {
      let original = readPhysical<BindBody>("shipment_bind", meta);
      if (!original && body) await physicalLock("shipment_bind", meta, async () => {
        if (readPhysical("shipment_bind", meta)) throw new Error("Есть сохранённая привязка другой вкладки.");
        original = { version: 1, url: bindPath(meta.task_id), body }; persistPhysical("shipment_bind", meta, original);
        if (life.current) setEntry(original);
      });
      if (!original) throw new Error("Нет сохранённой привязки.");
      await resolve(original, retry);
    } catch (err) { if (life.current) { setError((err as {status?: number}).status === 404 ? "Результат пока не виден. Привязка сохранена для точного повтора." : err instanceof Error ? err.message : String(err)); setDenied(isAuthError(err)); } }
    finally { if (life.current) setBusy(false); }
  }, [busy, denied, credentials, meta, resolve]);
  // Reload performs only GET, never an automatic binding mutation.
  useEffect(() => { if (entry) void run(false); }, [entry]);
  return { entry, error, busy, denied, blocked: !!entry || !!error || busy || denied, start: (body: BindBody) => void run(true, body), read: () => void run(false), retry: () => void run(true) };
}
export type ShipmentBindState = ReturnType<typeof useShipmentBind>;
