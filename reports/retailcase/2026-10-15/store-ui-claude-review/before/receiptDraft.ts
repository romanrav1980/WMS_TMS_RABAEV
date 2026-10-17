import { storeAppApiBase } from "./api";
import { parseReceiptIntent } from "./receiptIntentValidation";
import type { PendingReceipt } from "./contracts";

export function receiptScopeKey(storeId: string, username: string, loadOperationId: string): string {
 return "store-app-receipt:" + storeAppApiBase() + ":" + username + ":" + storeId + ":" + loadOperationId;
}

export function readReceiptDraft(scope: string, storeAddress: string): PendingReceipt | null {
 return parseReceiptIntent(localStorage.getItem(scope), storeAddress);
}

export function draftMatchesSaved(scope: string, storeAddress: string, intent: PendingReceipt): { matches: boolean; raw: string | null } {
 const raw = localStorage.getItem(scope);
 if (!raw) return { matches: false, raw };
 try {
  const saved = parseReceiptIntent(raw, storeAddress);
  return { matches: JSON.stringify(saved?.body) === JSON.stringify(intent.body), raw };
 } catch {
  return { matches: false, raw };
 }
}

export function writeReceiptDraft(scope: string, intent: PendingReceipt): void {
 const wire = JSON.stringify(intent);
 localStorage.setItem(scope, wire);
 if (localStorage.getItem(scope) !== wire) throw new Error("Не удалось надёжно сохранить команду. Отправка не выполнена.");
}

export function clearReceiptDraft(scope: string, expectedRaw: string): void {
 if (localStorage.getItem(scope) !== expectedRaw) throw new Error("Черновик изменился во время запроса. Сервер ответил; перечитайте поставку.");
 localStorage.removeItem(scope);
 if (localStorage.getItem(scope) !== null) throw new Error("Сервер подтвердил приёмку, но сохранённая команда не очищена. Повторите её с прежним номером.");
}
