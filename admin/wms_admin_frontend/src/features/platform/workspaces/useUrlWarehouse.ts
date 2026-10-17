import { useState } from "react";

/** Выбранный склад рабочего места хранится в адресе (warehouse_id): переключение вкладок рабочих мест, переходы между столами
 *  и перезагрузка открывают тот же склад (C0118). Это только навигация: права и данные проверяет сервер. */
export function readUrlWarehouse(): string {
  return new URLSearchParams(location.search).get("warehouse_id")?.replace(/\D/g, "") ?? "";
}

export function writeUrlWarehouse(id: string): void {
  const url = new URL(location.href);
  if (id) url.searchParams.set("warehouse_id", id); else url.searchParams.delete("warehouse_id");
  history.replaceState(history.state, "", url);
}

export function useUrlWarehouse() {
  const [warehouse, setWarehouse] = useState(readUrlWarehouse);
  const select = (id: string) => { setWarehouse(id); writeUrlWarehouse(id); };
  return [warehouse, select] as const;
}
