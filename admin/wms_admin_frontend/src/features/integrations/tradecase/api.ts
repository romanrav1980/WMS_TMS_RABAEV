
/** TRADECASE T02 (API_READY_C0130): только GET. Сервер проверяет право в области склада на каждом чтении. */
export type Kind = "ORDER" | "TRIP" | "RECIPIENT" | "SKU" | "OWNER" | "SUPPLY";
export type Tab = Kind | "MESSAGES" | "STOCK";
export type Site = { warehouse_id: number; source_id: string; active_skm: string; planning_source: string; enabled: boolean; version: number };
export type Payload = Record<string, unknown>;
export type DocRow = { document_id: string; version: number; status: "ACCEPTED" | "CANCELLED"; payload: Payload };
export type Result = { status: "ACCEPTED" | "REJECTED"; code?: string; replayed?: boolean; stock_changed?: boolean; physical_execution?: string;
  external_delivery?: string; external_business?: string; outbox_id?: number; occurred_at?: string; [key: string]: unknown };
export type MsgRow = { event_id: string; entity_type: Kind; document_id: string; version: number; result: Result };
export type Page<T> = Site & { items: T[]; has_more: boolean; next_after: string | null };
export type DocCard = Site & { document_id: string; entity_type: Kind; document_version: number; payload: Payload };
export type MsgCard = Site & { request: unknown; result: Result };
/** Группа запаса (C-0133): количества — десятичные строки, счётчики кодов — числа. Один идентификатор может иметь несколько групп. */
export type StockGroup = { pallet_identifier: string; cell: string | null; sku_id: string; owner_id: string; mrc: string | null; expiry_date: string | null;
  base_uom: string; base_quantity: string; hard_reserved_base: string; unit_count: number; pending_units: number; valid_units: number; rejected_units: number };
export type StockPage = { warehouse_id: number; items: StockGroup[]; has_more: boolean; next_after: string | null };
export type BindBody = { operation_id: string; supply_id: string; expected_supply_version: number; scanned_pallet: string };
export type BindResult = { warehouse_id: number; operation_id: string; stock_changed: boolean; replayed: boolean; supply_id: string; owner_id: string;
  bound_units: number; pallet_identifier: string; mark_state: string; attributes_bound: boolean; outbox_id?: number };

export const TABS: { id: Tab; label: string }[] = [
  { id: "ORDER", label: "Заказы" }, { id: "TRIP", label: "Рейсы" }, { id: "RECIPIENT", label: "Получатели" },
  { id: "SKU", label: "Товары" }, { id: "OWNER", label: "Собственники" }, { id: "SUPPLY", label: "Поставки" }, { id: "STOCK", label: "Запас" },
  { id: "MESSAGES", label: "Обмен" },
];

const base = (wh: string) => "/api/tradecase/warehouses/" + encodeURIComponent(wh);
export const sitePath = (wh: string) => base(wh) + "/site";
export function listPath(wh: string, tab: Tab, after: string | null): string {
  const q = new URLSearchParams({ limit: "50" }); if (after) q.set("after", after);
  return base(wh) + (tab === "MESSAGES" ? "/messages" : tab === "STOCK" ? "/stock/pallets" : "/documents/" + encodeURIComponent(tab)) + "?" + q;
}
export const cardPath = (wh: string, tab: Tab, id: string) =>
  base(wh) + (tab === "MESSAGES" ? "/messages/" : "/documents/" + encodeURIComponent(tab) + "/") + encodeURIComponent(id);

export const bindPath = (wh: string) => base(wh) + "/stock/bind";
export const helpUrl = (anchor: string) => "/help/tradecase-documents.html#" + anchor;
export type Help = { id: string; text: string; anchor: string };
const h = (id: string, text: string, anchor = "screen"): Help => ({ id: "tradecase." + id, text, anchor });
export const tcHelp = {
  back: h("back", "Вернуться к предыдущему разделу. Выбор склада и вкладки сохраняется в адресе.", "screen"),
  warehouse: h("warehouse", "Выбрать склад. Список берётся из ваших текущих доступов; право на СНС/BLC проверит сервер.", "warehouse"),
  refresh: h("refresh", "Перечитать площадку и текущую страницу с сервера. Ничего не отправляет."),
  tab: h("tab", "Показать документы этого вида. Курсор страниц сбрасывается."),
  next: h("next", "Следующие 50 записей с сервера (по курсору, без загрузки архива)."),
  first: h("first", "Вернуться к первой странице этого вида."),
  open: h("open", "Открыть документ: версия, состав, получатель и технические сведения.", "order"),
  openMessage: h("open.message", "Открыть сообщение обмена: результат приёма и причина отказа.", "exchange"),
  close: h("close", "Закрыть карточку и вернуться к списку на той же странице."),
  related: h("related", "Открыть связанный документ на этом складе."),
  flowBasis: h("flow.basis", "Открыть принятые основания — заказы этого склада.", "flow"),
  flowStock: h("flow.stock", "Открыть фактический запас склада по паллетам и адресам.", "stock"),
  scan: h("scan", "Отсканируйте идентификатор паллеты (сканер вводит текст и Enter) или введите его вручную.", "bind"),
  review: h("review", "Показать, что именно будет привязано, до записи. Ничего не отправляет.", "bind"),
  bind: h("bind", "Привязать собственника, МРЦ и срок поставки к уже принятому товару этой паллеты. Товар физически не принимается и не выкупается.", "bind"),
  retry: h("retry", "Повторить ту же команду с тем же номером операции — повтор не создаёт новую операцию.", "unknown"),
  cancelReview: h("cancel.review", "Вернуться к сканированию без записи.", "bind"),
  flowTrip: h("flow.trip", "Открыть рейсы — основания перевозки. Фактическая погрузка здесь не показывается.", "flow"),
};

/** Компактное время с часовым поясом в подсказке; неверное значение показывается как есть. */
export function when(value: unknown): { text: string; title: string } {
  const s = typeof value === "string" ? value : "", t = Date.parse(s);
  if (!s || !Number.isFinite(t)) return { text: s || "—", title: s };
  return { text: new Date(t).toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }), title: s };
}
