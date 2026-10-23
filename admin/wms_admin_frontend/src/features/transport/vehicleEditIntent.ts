import { API_BASE, ApiRequestError, apiFetch, currentSessionCredentials } from "../../api";

// C-0167: the trip edit (vehicle, driver, dock, ...) is a SET of fields without operation id. An unknown outcome (5xx, broken
// connection, lost response, 401/403) keeps the exact original request until the current trip is read back; a confirmed refusal
// (409/422) or success settles it. While it is unresolved, no other edit of that trip is sent. Same storage discipline as
// TransportTimeApprovalIntent: write-then-verify before sending, remove only the unchanged record.
export type TripFields = { transport?: string | null; voditel_id?: number | null; dock?: string | null; transtype?: string | null;
  shipment_date?: string | null; shipment_time?: string | null; primechanie?: string | null };
export type VehicleEditIntent = { trip_id: number; body: TripFields; before: TripFields; saved_at: string; unknown?: boolean };
export type TripRow = { ID: number; TRANSPORT: string | null; VODITEL_ID: number | null; DOCK: string | null; TRANSTYPE: string | null;
  SHIPMENT_DATE: string | null; SHIPMENT_TIME: string | null; PRIMECHANIE: string | null };

export const INTENT_EVENT = "wms-vehicle-edit-intent";
export const intentKey = (trip: number) =>
  "retailcase.trip.edit.pending:" + JSON.stringify([API_BASE, currentSessionCredentials().username, trip]);

export function readIntent(trip: number): { intent: VehicleEditIntent; raw: string } | null {
  try {
    const raw = localStorage.getItem(intentKey(trip));
    if (raw === null) return null;
    const v = JSON.parse(raw) as VehicleEditIntent;
    return v && v.trip_id === trip && v.body && typeof v.body === "object" ? { intent: v, raw } : null;
  } catch { return null; }
}

function save(intent: VehicleEditIntent): string {
  const key = intentKey(intent.trip_id), raw = JSON.stringify(intent);
  try { localStorage.setItem(key, raw); if (localStorage.getItem(key) === raw) { notify(); return raw; } } catch { /* below */ }
  throw new Error("Не удалось надёжно сохранить изменение рейса — оно не отправлено.");
}

export function settle(trip: number, raw: string): boolean {
  try {
    const key = intentKey(trip);
    if (localStorage.getItem(key) !== raw) return false;
    localStorage.removeItem(key); notify(); return localStorage.getItem(key) === null;
  } catch { return false; }
}

const notify = () => window.dispatchEvent(new Event(INTENT_EVENT));

export const fieldsOf = (t: TripRow): TripFields => ({ transport: t.TRANSPORT, voditel_id: t.VODITEL_ID, dock: t.DOCK, transtype: t.TRANSTYPE,
  shipment_date: t.SHIPMENT_DATE, shipment_time: t.SHIPMENT_TIME, primechanie: t.PRIMECHANIE });

const norm = (k: keyof TripFields, v: unknown) => v === null || v === undefined ? null
  : k === "shipment_date" ? String(v).slice(0, 10) : k === "shipment_time" ? (String(v).match(/(\d{2}:\d{2})/) ?? [""])[0]
  : k === "transtype" ? String(v).trim().toUpperCase() : String(v);

/** Which requested fields the current trip already has. Only fields present in the request are compared. */
export function compare(body: TripFields, current: TripFields): { saved: boolean; differ: (keyof TripFields)[] } {
  const differ = (Object.keys(body) as (keyof TripFields)[]).filter(k => body[k] !== null && body[k] !== undefined && norm(k, body[k]) !== norm(k, current[k]));
  return { saved: differ.length === 0, differ };
}

/** Mark that an attempt of this request had an unknown outcome; from then on only a read of the trip may resolve it. */
function markUnknown(intent: VehicleEditIntent, raw: string): void {
  if (intent.unknown) return;
  try { if (localStorage.getItem(intentKey(intent.trip_id)) === raw) save({ ...intent, unknown: true }); } catch { /* the record stays as it was */ }
}

/** Send the exact stored request; settle it only on a confirmed outcome. A 409/422 confirms "nothing changed" only for a request
 *  that never had an unknown outcome: after a lost response the earlier attempt may have saved, and a later freeze (e.g. loading)
 *  makes the same request 409 — that does not disprove the earlier save, so the trip must be read back. */
export async function send(intent: VehicleEditIntent, raw: string): Promise<void> {
  try {
    await apiFetch(`/api/admin/transport/tasks/${intent.trip_id}`, { method: "PATCH", body: JSON.stringify(intent.body) });
  } catch (e) {
    if (e instanceof ApiRequestError && (e.status === 409 || e.status === 422)) {
      if (!intent.unknown) { settle(intent.trip_id, raw); throw e; }  // first attempt: confirmed refusal, nothing changed
      throw new Error("Сервер отклонил повтор, но прежняя попытка могла уже сохраниться. Изменение остаётся до сверки с рейсом. (" + String(e) + ")");
    }
    markUnknown(intent, raw);
    throw new Error((e instanceof ApiRequestError && (e.status === 401 || e.status === 403)
      ? "Нет прав на изменение рейса сейчас. " : "Исход изменения рейса не подтверждён. ")
      + "Изменение сохранено: проверьте рейс в блоке «Смена машины» и повторите или откажитесь. (" + String(e) + ")");
  }
  settle(intent.trip_id, raw);
}

/** A new edit: refused while an earlier one of this trip is unresolved; otherwise stored first, then sent. */
export async function saveTripEdit(trip: TripRow, body: TripFields): Promise<void> {
  if (readIntent(trip.ID)) throw new Error("У рейса есть неподтверждённое изменение. Сначала проверьте его в блоке «Смена машины».");
  const intent: VehicleEditIntent = { trip_id: trip.ID, body, before: fieldsOf(trip), saved_at: new Date().toISOString() };
  await send(intent, save(intent));
}
