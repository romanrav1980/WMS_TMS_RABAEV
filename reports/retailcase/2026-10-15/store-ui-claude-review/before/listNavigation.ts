import type { DeliveryListItem } from "./contracts";

export type DeliveryFilter = "waiting" | "accepted" | "all";

export function isReceived(item: DeliveryListItem): boolean {
 return Boolean(item.receipt_operation_id || item.receipt_state);
}

export function deliveryStateLabel(item: DeliveryListItem): string {
 if (item.receipt_state === "DISCREPANCY") return "С расхождением";
 return isReceived(item) ? "Принято" : "К приёмке";
}

// Preserve the source wall clock: a missing zone must never become browser-local time.
export function shortDeparture(item: DeliveryListItem): string {
 const match = item.departed_at?.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/);
 return match ? `${match[3]}.${match[2]} ${match[4]}:${match[5]}` : "Дата не указана";
}

export function departureHint(item: DeliveryListItem): string {
 return item.time_status === "AWARE"
  ? "Время выезда в часовом поясе источника"
  : "Время выезда как указано в источнике; часовой пояс не подтверждён";
}

export function filterDeliveries(items: DeliveryListItem[], filter: DeliveryFilter, query: string): DeliveryListItem[] {
 const needle = query.trim().toLocaleLowerCase("ru");
 return items.filter((item) => {
  const matchesState = filter === "all" || (filter === "accepted" ? isReceived(item) : !isReceived(item));
  const searchText = `${item.trip_id} ${item.root_key} ${item.load_operation_id}`.toLocaleLowerCase("ru");
  return matchesState && (!needle || searchText.includes(needle));
 });
}
