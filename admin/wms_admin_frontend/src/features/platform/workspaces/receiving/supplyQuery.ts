// Запрос поставок SAP по контракту C-0093/C-0094: склад (warehouse_id) и календарь фильтрует сервер до limit.
// Даты — календарные поля источника (UNRESOLVED_SERVER_LOCAL), не UTC и не доказанная смена РЦ.

export type DateBasis = "PLANNED_ACCEPT" | "ACCEPTED" | "DOCUMENT";
export const BASIS: { id: DateBasis; label: string; field: "planning_accept_time" | "date_of_accept" | "date_of_naklad"; hint: string }[] = [
  { id: "PLANNED_ACCEPT", label: "плановая дата приёмки", field: "planning_accept_time", hint: "Поставки, которые по плану должны быть приняты в эти дни. Поставка без плановой даты в эти дни не попадает — её показывает отдельный список." },
  { id: "ACCEPTED", label: "дата приёмки", field: "date_of_accept", hint: "Поставки, фактически принятые в эти дни (календарная дата источника)." },
  { id: "DOCUMENT", label: "дата документа", field: "date_of_naklad", hint: "Поставки по дате накладной." },
];
export const MAX_DAYS = 31, SUPPLY_LIMIT = 100;
export type SupplyFilter = { warehouseId: string; from: string; to: string; basis: DateBasis; unplanned: boolean };

/** Число дней окна включительно; NaN — дата не задана. */
export const spanDays = (from: string, to: string) => (Date.parse(to + "T00:00:00Z") - Date.parse(from + "T00:00:00Z")) / 86400000 + 1;

/** Ошибка окна до запроса (сервер проверит то же самое) или null. */
export function filterError(f: SupplyFilter): string | null {
  const n = spanDays(f.from, f.to);
  if (!Number.isFinite(n)) return "Укажите обе даты.";
  if (n < 1) return "Дата «по» раньше даты «с».";
  if (n > MAX_DAYS) return `Окно больше ${MAX_DAYS} дней — сервер его не принимает.`;
  return null;
}

export function supplyPath(f: SupplyFilter): string | null {
  if (filterError(f)) return null;
  const q = new URLSearchParams({ date_from: f.from, date_to: f.to, date_basis: f.basis, limit: String(SUPPLY_LIMIT) });
  if (f.warehouseId) q.set("warehouse_id", f.warehouseId);
  if (f.unplanned && f.basis === "PLANNED_ACCEPT") q.set("include_unplanned", "true");
  return `/api/integrations/sap/supply-orders?${q.toString()}`;
}

/** Календарная дата источника для показа: без перевода поясом браузера. */
export const sourceDate = (v: string | null | undefined) => v ? v.replace("T", " ").slice(0, 16) : "—";
