import { storeAppRequest, isAuthError } from "./api";
import { readReceiptDraft, draftMatchesSaved, writeReceiptDraft, clearReceiptDraft } from "./receiptDraft";
import { parseReceiptResult } from "./receiptResult";
import type { StoreCredentials, StorePreview, PendingReceipt, ReceiptResult, ReceiptStatusLookup } from "./contracts";

function deliveryPath(storeId: string, loadOperationId: string): string {
 return "/api/store-app/deliveries/" + encodeURIComponent(loadOperationId) + "?store_id=" + encodeURIComponent(storeId);
}

export interface OpenResult { preview?: StorePreview; result?: ReceiptResult; pending?: PendingReceipt | null; corrupt?: boolean; message: string; authError?: boolean }

export async function runOpen(scope: string, storeId: string, id: string, credentials: StoreCredentials): Promise<OpenResult> {
 try {
  const data = await storeAppRequest<StorePreview>(deliveryPath(storeId, id), credentials);
  if (data.load_operation_id !== id) throw new Error("Ответ состава относится к другой поставке.");
  if (data.already_received && data.receipt?.state === "APPLIED" && data.receipt.result) {
   const result = parseReceiptResult(data.receipt.result, {
    operation_id: data.receipt.operation_id, load_operation_id: id, store_address: data.store_address,
   } as PendingReceipt["body"]);
   return { preview: data, result, pending: null, message: "Сохранённый результат приёмки." };
  }
  try {
   return { preview: data, pending: readReceiptDraft(scope, data.store_address), message: "" };
  } catch {
   return { preview: data, pending: null, corrupt: true,
    message: "Сохранённая операция повреждена. Новая отправка заблокирована; сохраните архив и перечитайте поставку." };
  }
 } catch (error) {
  return { message: String(error), authError: isAuthError(error) };
 }
}

export interface SendResult { ok: boolean; corrupt?: boolean; result?: ReceiptResult; pendingToSave?: PendingReceipt; message: string; authError?: boolean }

export async function runSend(scope: string, intent: PendingReceipt, credentials: StoreCredentials): Promise<SendResult> {
 const { matches, raw } = draftMatchesSaved(scope, intent.body.store_address, intent);
 if (!matches || !raw) {
  return { ok: false, corrupt: true, message: "Сохранённая команда повреждена или изменена. Отправка заблокирована; перечитайте поставку." };
 }
 if (typeof navigator !== "undefined" && navigator.onLine === false) {
  return { ok: false, message: "Нет соединения. Команда сохранена как ожидающая отправку; нажмите «Повторить», когда появится связь." };
 }
 try {
  const raw2 = await storeAppRequest<unknown>("/api/delivery/store-receipts/confirm", credentials, intent.body);
  const result = parseReceiptResult(raw2, intent.body);
  clearReceiptDraft(scope, raw);
  return { ok: true, result, message: "Приёмка подтверждена. " + result.operation_id };
 } catch (error) {
  const confirmed = (error as { confirmed?: boolean })?.confirmed === true;
  const pendingToSave: PendingReceipt = { ...intent, confirmedRejection: confirmed };
  if (localStorage.getItem(scope) === raw) writeReceiptDraft(scope, pendingToSave);
  return { ok: false, pendingToSave, authError: isAuthError(error),
   message: String(error) + (confirmed ? " Отказ подтверждён: можно исправить данные." : " Повторите сохранённую операцию.") };
 }
}

export interface StatusResult { ok: boolean; result?: ReceiptResult; message: string; authError?: boolean }

export async function runCheckStatus(storeId: string, scope: string, pending: PendingReceipt, credentials: StoreCredentials): Promise<StatusResult> {
 try {
  const path = "/api/store-app/receipts/" + encodeURIComponent(pending.body.operation_id) + "?store_id=" + encodeURIComponent(storeId);
  const status = await storeAppRequest<ReceiptStatusLookup>(path, credentials);
  if (status.operation_id !== pending.body.operation_id) throw new Error("Ответ квитанции относится к другой операции.");
  if (status.state === "APPLIED" && status.outcome_confirmed === true && status.result) {
   const result = parseReceiptResult(status.result, pending.body);
   clearReceiptDraft(scope, JSON.stringify(pending));
   return { ok: true, result, message: "Приёмка подтверждена по квитанции. " + result.operation_id };
  }
  return { ok: false, message: status.state === "NOT_VISIBLE"
   ? "Квитанция не видна с этой учётной записи. Это не подтверждение отмены — повторите сохранённую операцию или уточните у диспетчера."
   : "Результат пока не подтверждён. Повторите сохранённую операцию." };
 } catch (error) {
  return { ok: false, message: String(error), authError: isAuthError(error) };
 }
}

export interface RestartResult { ok: boolean; preview?: StorePreview; changed?: boolean; message: string; authError?: boolean }

export async function runRestart(storeId: string, scope: string, previous: StorePreview, pending: PendingReceipt, credentials: StoreCredentials): Promise<RestartResult> {
 try {
  const data = await storeAppRequest<StorePreview>(deliveryPath(storeId, previous.load_operation_id), credentials);
  const { matches, raw } = draftMatchesSaved(scope, data.store_address, pending);
  if (!matches || !raw) throw new Error("Команда изменена другой вкладкой. Ввод сохранён.");
  clearReceiptDraft(scope, raw);
  const changed = data.composition_signature !== previous.composition_signature || data.mode !== previous.mode
   || JSON.stringify(data.marked_unit_control) !== JSON.stringify(previous.marked_unit_control);
  return {
   ok: true, preview: changed ? undefined : data, changed,
   message: changed
    ? "Состав или правила изменились. Прежний ввод оставлен для сверки. Откройте поставку заново для новой формы; автоматического переноса нет."
    : "Отказ подтверждён. Исправьте данные: количества, фото и сканы сохранены. Состав перечитан с сервера.",
  };
 } catch (error) {
  return { ok: false, message: String(error), authError: isAuthError(error) };
 }
}
