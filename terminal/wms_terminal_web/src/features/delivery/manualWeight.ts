import { storeAppApiBase } from "./api";

// Ручной вес приёмки магазина (C0116): строка GROSS KG, как требует сервер — `^[0-9]{1,18}(\.[0-9]{1,9})?$`, строго > 0.
// Источник MANUAL_CONFIRMED; одновременно с scale_capture_key не отправляется.

export type WeightSource = "MANUAL" | "SCALE";
export const MANUAL_PATTERN = /^[0-9]{1,18}(\.[0-9]{1,9})?$/;

/** Ввод оператора → строка для сервера: запятая как десятичный разделитель, без пробелов и ведущих нулей. null — ввод неполный или неверный. */
export function normalizeManualKg(input: string): string | null {
  const text = input.trim().replace(/\s+/g, "").replace(",", ".");
  if (!MANUAL_PATTERN.test(text)) return null;
  const [whole, fraction] = text.split(".");
  const value = (whole.replace(/^0+(?=\d)/, "")) + (fraction !== undefined ? "." + fraction : "");
  return /[1-9]/.test(value) ? value : null; // ноль и 0.000 сервер отклоняет: вес должен быть положительным
}

/** Разница с отгрузкой — только подсказка; итог (в допуске или нет) считает сервер. Числа в десятичной записи без float. */
export function previewDelta(manual: string, shipping: string): string | null {
  const scale = (value: string, digits: number) => { const [w, f = ""] = value.split("."); return BigInt(w + f.padEnd(digits, "0").slice(0, digits)); };
  if (!MANUAL_PATTERN.test(shipping)) return null;
  const digits = Math.max(manual.split(".")[1]?.length ?? 0, shipping.split(".")[1]?.length ?? 0, 0);
  const delta = scale(manual, digits) - scale(shipping, digits), sign = delta < 0n ? "−" : delta > 0n ? "+" : "";
  const abs = (delta < 0n ? -delta : delta).toString().padStart(digits + 1, "0");
  return sign + (digits ? abs.slice(0, -digits) + "," + abs.slice(-digits) : abs);
}

/** Обычная страница справки на API origin; открывается в новой вкладке, черновик приёмки не теряется. */
export const manualWeightHelp = (anchor: "enter" | "confirm" | "store" | "integrated" | "retry") => `${storeAppApiBase()}/help/manual-weight.html#${anchor}`;
