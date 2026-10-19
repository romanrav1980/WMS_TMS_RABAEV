
/** TRADECASE T02 (API_READY_C0130): только GET. Сервер проверяет право в области склада на каждом чтении. */
export type Kind = "ORDER" | "TRIP" | "RECIPIENT" | "SKU" | "OWNER" | "SUPPLY";
export type Tab = Kind | "MESSAGES" | "STOCK" | "BUYOUTS" | "SORT";
export type Site = { warehouse_id: number; source_id: string; active_skm: string; planning_source: string; enabled: boolean; version: number };
export type Payload = Record<string, unknown>;
export type DocRow = { document_id: string; version: number; status: "ACCEPTED" | "CANCELLED"; payload: Payload };
export type Result = { status: "ACCEPTED" | "REJECTED"; code?: string; replayed?: boolean; stock_changed?: boolean; physical_execution?: string;
  external_delivery?: string; external_business?: string; outbox_id?: number; occurred_at?: string; [key: string]: unknown };
export type MsgRow = { event_id: string; entity_type: Kind; document_id: string; version: number; result: Result };
export type Page<T> = Site & { owner_scope_filtered?: boolean; items: T[]; has_more: boolean; next_after: string | null };
export type DocCard = Site & { document_id: string; entity_type: Kind; document_version: number; payload: Payload };
export type MsgCard = Site & { request: unknown; result: Result };
/** Группа запаса (C-0133): количества — десятичные строки, счётчики кодов — числа. Один идентификатор может иметь несколько групп. */
export type StockGroup = { pallet_identifier: string; cell: string | null; sku_id: string; owner_id: string; mrc: string | null; expiry_date: string | null;
  base_uom: string; base_quantity: string; hard_reserved_base: string; unit_count: number; pending_units: number; valid_units: number; rejected_units: number };
export type StockPage = { warehouse_id: number; items: StockGroup[]; has_more: boolean; next_after: string | null };
/** Выкуп (C-0136): финансовая инструкция; физическое количество не меняется. LIST: composition_checked=false — риск смотреть в DETAIL. */
export type Buyout = { buyout_id: string; basis_order_id: string; basis_line_id: string; basis_version: number; sku_id: string; mrc: string | null;
  source_owner_id: string; target_owner_id: string; buyout_mode: string; skm_id: string; external_document_id: string | null; status: string; version: number;
  requested_units: number; confirmed_units: number; rejected_units: number; pending_units: number; requires_sorting: boolean | null;
  requires_transit_reconciliation: boolean | null; composition_checked: boolean; created_at: string; [key: string]: unknown };
export type BuyoutPage = { warehouse_id: number; items: Buyout[]; has_more: boolean; next_after: string | null };
export type BuyoutUnit = { physical_unit_key: string; outcome: "CONFIRMED" | "REJECTED" | "PENDING"; reason: string | null; owner_id: string; pallet_identifier: string; cell: string | null; buyout_hold: boolean };
export type StockUnit = { physical_unit_key: string; sku_id: string; owner_id: string; mrc: string | null; expiry_date: string | null; pallet_identifier: string;
  cell: string | null; mark_state: string; base_quantity: string; base_uom: string; allocation_enabled: boolean; buyout_hold: boolean; hard_reserved: boolean;
  location_kind?: string; last_warehouse_cell?: string | null };
export type UnitPage<T> = { owner_scope_filtered?: boolean; warehouse_id: number; items: T[]; has_more: boolean; next_after: string | null };
export type BuyoutBody = { operation_id: string; buyout_id: string; basis_order_id: string; basis_line_id: string; expected_basis_version: number; unit_keys: string[];
  demand_order_id?: string; demand_line_id?: string; load_operation_id?: string };
export type Scan = { system_code: string; profile_code: string; code: string };
export type SortBody = { operation_id: string; source_pallet: string; source_cell: string; target_cell: string; scans: Scan[] };
export type SortResult = { operation_id: string; status: string; source_uid: string; uid: string; from_cell: string; cell: string; base_quantity: string; base_uom: string; regulatory_composition_status?: string; outbox_id?: number };
export type BindBody = { operation_id: string; supply_id: string; expected_supply_version: number; scanned_pallet: string };
export type BindResult = { warehouse_id: number; operation_id: string; stock_changed: boolean; replayed: boolean; supply_id: string; owner_id: string;
  bound_units: number; pallet_identifier: string; mark_state: string; attributes_bound: boolean; outbox_id?: number };

export const TABS: { id: Tab; label: string }[] = [
  { id: "ORDER", label: "Заказы" }, { id: "TRIP", label: "Рейсы" }, { id: "RECIPIENT", label: "Получатели" },
  { id: "SKU", label: "Товары" }, { id: "OWNER", label: "Собственники" }, { id: "SUPPLY", label: "Поставки" }, { id: "STOCK", label: "Запас" },
  { id: "BUYOUTS", label: "Выкупы" }, { id: "SORT", label: "Разделение" }, { id: "MESSAGES", label: "Обмен" },
];

const base = (wh: string) => "/api/tradecase/warehouses/" + encodeURIComponent(wh);
export const sitePath = (wh: string) => base(wh) + "/site";
export function listPath(wh: string, tab: Tab, after: string | null, pending = false): string {
  if (tab === "BUYOUTS") return base(wh) + "/buyouts?" + new URLSearchParams({ after: after ?? "0", limit: "50", pending_only: String(pending) });
  const q = new URLSearchParams({ limit: "50" }); if (after) q.set("after", after);
  return base(wh) + (tab === "MESSAGES" ? "/messages" : tab === "STOCK" ? "/stock/pallets" : "/documents/" + encodeURIComponent(tab)) + "?" + q;
}
export const cardPath = (wh: string, tab: Tab, id: string) =>
  base(wh) + (tab === "MESSAGES" ? "/messages/" : tab === "BUYOUTS" ? "/buyouts/" : "/documents/" + encodeURIComponent(tab) + "/") + encodeURIComponent(id);
export const buyoutUnitsPath = (wh: string, id: string, after: string | null) => base(wh) + "/buyouts/" + encodeURIComponent(id) + "/units?" + new URLSearchParams({ after: after ?? "", limit: "100" });
export const stockUnitsPath = (wh: string, pallet: string, after: string | null) => { const q = new URLSearchParams({ pallet_identifier: pallet, limit: "100" }); if (after) q.set("after", after); return base(wh) + "/stock?" + q; };
export const buyoutsPostPath = (wh: string) => base(wh) + "/buyouts";
export const sortPath = (wh: string) => base(wh) + "/stock/sort";
/** Исполнение внешнего рейса (C-0139): 404 — привязки к фактическому рейсу ещё нет, а не пустой рейс. */
export type TripLoad = { load_operation_id: string; status: string; identifier: string; content_version: number; departed_at: string | null; custody_released: boolean };
export type TripExec = { basis_current: boolean; trip_id: string; native_task_id: number | null; trip_version: number; binding_version: number; manifest_signature: string | null;
  loads: TripLoad[]; document_version: number | null; document_status: "READY" | "ERROR" | "REVOKED" | "MISSING" | string; external_document_id: string | null;
  error_reason: string | null; manifest_matched: boolean; document_ready: boolean };
export type NativeTrip = { ID: number; TRANSPORT: string | null; CONDITION: string | null; DOCK: string | null; SHIPMENT_DATE: string | null; VODITEL_NAME: string | null };
export type BindingBody = { operation_id: string; native_task_id: number; expected_trip_version: number; expected_binding_version: number };
export const executionPath = (wh: string, trip: string) => base(wh) + "/trips/" + encodeURIComponent(trip) + "/execution";
export const tripBindingPath = (wh: string, trip: string) => base(wh) + "/trips/" + encodeURIComponent(trip) + "/binding";
export const nativeTripPath = (id: number) => "/api/admin/transport/tasks/" + id;
export const transitUnitsPath = (wh: string, load: string, after: string | null) => { const q = new URLSearchParams({ load_operation_id: load, limit: "100" }); if (after) q.set("after", after); return base(wh) + "/stock/transit?" + q; };
/** МРЦ сравнивается точной нормализацией десятичной строки: «200.00» равно «200». */
export function normMrc(v: unknown): string {
  const s = String(v ?? "").trim(); if (!/^\d+(\.\d+)?$/.test(s)) return s;
  const [i, f = ""] = s.split("."), frac = f.replace(/0+$/, ""); return BigInt(i).toString() + (frac ? "." + frac : "");
}

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
  pending: h("pending", "Показать выкупы, где хотя бы один код ожидает ответа СКМ.", "buyout"),
  openBuyout: h("open.buyout", "Открыть выкуп: свежий состав, ответы СКМ по кодам и необходимость разделения паллеты.", "buyout"),
  moreUnits: h("more.units", "Следующие 100 кодов выкупа (по курсору).", "buyout"),
  createBuyout: h("buyout.create", "Начать выкуп по этой строке финансового основания: отсканировать паллету и выбрать коды из текущего запаса.", "buyout.create"),
  loadUnits: h("buyout.load", "Прочитать все коды этой паллеты на складе (все страницы) и выбрать подходящие строке.", "buyout.create"),
  sendBuyout: h("buyout.send", "Отправить запрос выкупа с показанным набором кодов. Собственник меняется только после ответа СКМ.", "buyout.create"),
  addScan: h("sort.scan", "Добавить отсканированный код маркировки (сканер вводит текст и Enter).", "sort"),
  removeScan: h("sort.remove", "Убрать последний отсканированный код.", "sort"),
  sendSort: h("sort.send", "Перенести отсканированные коды с исходной паллеты в целевую ячейку. Новая этикетка и агрегация этим не подтверждаются.", "sort"),
  checkTrip: h("trip.check", "Прочитать фактический рейс по номеру и сверить машину с внешним рейсом. Ничего не записывает.", "trip"),
  bindTrip: h("trip.bind", "Привязать внешний рейс к показанному фактическому рейсу склада. Транспортный документ эта кнопка не создаёт.", "trip"),
  rebindTrip: h("trip.rebind", "Открыть форму смены привязки к другому фактическому рейсу.", "trip"),
  loadTransit: h("transit.load", "Прочитать весь груз этой погрузки в машине (все страницы) и выбрать подходящие строке коды.", "buyout.create"),
  flowTrip: h("flow.trip", "Открыть рейсы, их транспортные документы и фактические погрузки.", "flow"),
};

/** Компактное время с часовым поясом в подсказке; неверное значение показывается как есть. */
export function when(value: unknown): { text: string; title: string } {
  const s = typeof value === "string" ? value : "", t = Date.parse(s);
  if (!s || !Number.isFinite(t)) return { text: s || "—", title: s };
  return { text: new Date(t).toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }), title: s };
}
