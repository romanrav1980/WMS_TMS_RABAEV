import { useEffect, useRef, useState } from "react";
import { storeAppRequest, isAuthError } from "./api";
import type { StoreCredentials, DeliveryListItem, DeliveryListResponse } from "./contracts";

const TIME_STATUSES = ["UNRESOLVED_SERVER_LOCAL", "AWARE"];

function isValidItem(value: unknown): value is DeliveryListItem {
 const item = value as DeliveryListItem;
 return !!item && typeof item.load_operation_id === "string" && !!item.load_operation_id
  && typeof item.trip_id === "number" && typeof item.root_key === "string"
  && (item.gross_weight_kg === null || typeof item.gross_weight_kg === "number")
  && (item.departed_at === null || typeof item.departed_at === "string")
  && TIME_STATUSES.includes(item.time_status);
}

function validateResponse(data: unknown, storeId: string): DeliveryListResponse {
 const response = data as DeliveryListResponse;
 if (!response || response.store_id !== storeId || !Array.isArray(response.items) || !response.items.every(isValidItem)
  || (response.next_after !== null && typeof response.next_after !== "string")) {
  throw new Error("Сервер вернул непригодный список поставок.");
 }
 return response;
}

export function useStoreDeliveries(storeId: string, credentials: StoreCredentials, onAuthError: () => void) {
 const [items, setItems] = useState<DeliveryListItem[]>([]);
 const [nextAfter, setNextAfter] = useState<string | null>(null);
 const [busy, setBusy] = useState(false);
 const [message, setMessage] = useState("");
 const scopeKey = credentials.username + ":" + storeId;
 const current = useRef(scopeKey);

 useEffect(() => {
  current.current = scopeKey;
  setItems([]); setNextAfter(null); setMessage("");
  return () => { current.current = ""; };
 }, [scopeKey]);

 async function load(append: boolean) {
  if (busy || current.current !== scopeKey) return;
  if (append && nextAfter === null) return;
  setBusy(true);
  try {
   const params = new URLSearchParams({ store_id: storeId, limit: "50" });
   if (append && nextAfter) params.set("after", nextAfter);
   const raw = await storeAppRequest<unknown>("/api/store-app/deliveries?" + params.toString(), credentials);
   const data = validateResponse(raw, storeId);
   if (current.current !== scopeKey) return;
   setItems((rows) => append ? [...rows, ...data.items.filter((item) => !rows.some((row) => row.load_operation_id === item.load_operation_id))] : data.items);
   setNextAfter(data.next_after);
   setMessage(data.items.length || append ? "" : "Нет поставок для этого магазина.");
  } catch (error) {
   if (current.current === scopeKey) {
    setMessage(String(error));
    if (isAuthError(error)) onAuthError();
   }
  } finally {
   setBusy(false);
  }
 }

 return {
  items, busy, message, hasMore: nextAfter !== null,
  load: () => load(false),
  loadMore: () => load(true),
 };
}
