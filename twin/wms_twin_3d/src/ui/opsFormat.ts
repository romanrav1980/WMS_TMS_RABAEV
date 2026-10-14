import type { ConnectionState, OpPhase, PositionBasis } from "../contracts/twin";
import type { Tone } from "./format";

export const PHASE_LABEL: Record<OpPhase, string> = {
  PLANNED: "План",
  ASSIGNED: "Назначено",
  STARTED: "Начато",
  SOURCE_CONFIRMED: "Источник подтверждён",
  CARRYING: "Перевозка",
  TARGET_CONFIRMED: "Назначение подтверждено",
  PARTIAL: "Частично",
  BLOCKED: "Заблокировано",
  COMPLETED: "Завершено",
  CANCELLED: "Отменено",
  FAILED: "Ошибка",
  UNKNOWN: "Неизвестно"
};

export function phaseTone(p: OpPhase): Tone {
  if (p === "BLOCKED" || p === "FAILED") return "crit";
  if (p === "PARTIAL" || p === "UNKNOWN") return "warn";
  if (p === "COMPLETED" || p === "TARGET_CONFIRMED") return "ok";
  if (p === "CANCELLED" || p === "PLANNED") return "idle";
  return "info";
}

export const POSITION_LABEL: Record<PositionBasis, string> = {
  OBSERVED_CELL: "по последней ячейке (наблюдение)",
  UNBOUND_CELL: "ячейка не найдена в топологии",
  UNKNOWN: "позиция неизвестна",
  SIMULATED: "симуляция"
};

export const CONNECTION_LABEL: Record<ConnectionState, string> = {
  SIM: "SIM · мок-данные",
  LOADING: "LIVE · загрузка",
  LIVE: "LIVE",
  STALE: "STALE · данные устарели",
  DISCONNECTED: "НЕТ СВЯЗИ"
};

export const KIND_LABEL: Record<string, string> = {
  PUTAWAY: "Размещение",
  REPLENISHMENT: "Пополнение",
  PICKING_MOVE: "Перемещение под отбор",
  RAW_TO_PRODUCTION: "Сырьё в производство",
  FG_TO_STORAGE: "Выпуск на хранение",
  OTHER: "Прочее",
  CASE_PICK: "Сборка CASE",
  ST_PICK: "Отбор СТ",
  SIM_LOAD: "Погрузка (SIM)",
  SIM_UNLOAD: "Выгрузка (SIM)"
};

export const kindLabel = (s: string) => KIND_LABEL[s] ?? s;

export function snapshotAge(at?: number) {
  if (!at) return "—";
  const sec = Math.round((Date.now() - at) / 1000);
  return sec < 60 ? `${sec} с` : `${Math.round(sec / 60)} мин`;
}
