import type { ReceiptBody, ReceiptResult, ReceiptResultLine } from "./contracts";

const isObject = (value: unknown): value is Record<string, unknown> => Boolean(value && typeof value === "object");
const isQuantity = (value: unknown): value is string => typeof value === "string" && /^(?:\d+(?:\.\d+)?|\.\d+)$/.test(value);

export function parseReceiptResult(value: unknown, body: ReceiptBody): ReceiptResult {
 if (!isObject(value) || value.operation_id !== body.operation_id || value.load_operation_id !== body.load_operation_id
  || value.store_address !== body.store_address || !["ACCEPTED", "DISCREPANCY"].includes(String(value.status))
  || typeof value.root !== "string" || !Array.isArray(value.accepted_lines) || !value.accepted_lines.length || value.accepted_lines.length > 200
  || (value.status === "DISCREPANCY" && (typeof value.discrepancy_case_id !== "string" || !value.discrepancy_case_id))) {
  throw new Error("Ответ сервера не подтверждает исходную приёмку. Сохранённый запрос оставлен для повтора.");
 }
 const lines = value.accepted_lines.map((row: unknown) => {
  if (!isObject(row) || !Number.isSafeInteger(row.line_no) || typeof row.lot_uid !== "string" || typeof row.article !== "string" || typeof row.base_uom !== "string"
   || !isQuantity(row.accepted ?? row.accepted_quantity)
   || ["shipped", "missing", "refused", "damaged", "extra"].some((key) => row[key] !== undefined && !isQuantity(row[key]))) {
   throw new Error("Сервер вернул неподтверждённые количества акта. Повторите сохранённую операцию.");
  }
  if (value.status === "DISCREPANCY" && ["shipped", "missing", "refused", "damaged", "extra"].some((key) => !isQuantity(row[key]))) {
   throw new Error("В акте расхождения отсутствуют количества. Повторите исходный запрос.");
  }
  return { ...row, accepted: row.accepted ?? row.accepted_quantity } as unknown as ReceiptResultLine;
 });
 return { ...value, accepted_lines: lines } as unknown as ReceiptResult;
}
