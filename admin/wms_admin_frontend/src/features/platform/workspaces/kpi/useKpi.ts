import { useMemo } from "react";
import { useApiRead } from "../../access-admin";
import type { ReadState } from "../../access-admin/useApiRead";

export function useKpi<T>(path: string | null, warehouse: number, parse: (value: unknown, warehouse: number) => T, reload: number): ReadState<T> {
 const read = useApiRead<unknown>(path, reload);
 return useMemo(() => {
  if (read.data === null) return { ...read, data: null };
  try { return { ...read, data: parse(read.data, warehouse) }; }
  catch (error) { return { ...read, data: null, error: "Данные не подтверждены: " + String(error) }; }
 }, [read.data, read.error, read.loading, read.at, warehouse, parse]);
}

export function number(value: string | number | null): string {
 if (value === null) return "Нет данных";
 const parsed = Number(value);
 return Number.isFinite(parsed) ? parsed.toLocaleString("ru-RU", { maximumFractionDigits: 3 }) : String(value);
}

export function hours(value: string | null): string {
 if (value === null) return "Нет подтверждённого времени";
 return Number(value) > 0 && Number(value) < 0.001 ? "<0,001 ч" : number(value) + " ч";
}

export function moment(value: string | null, zone: string): string {
 if (!value) return "Нет данных";
 const shifted = new Date(Date.parse(value) + (zone === "+03:00" ? 3 : 0) * 3600000);
 return shifted.toLocaleString("ru-RU", { timeZone: "UTC", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" }) + " " + zone;
}
