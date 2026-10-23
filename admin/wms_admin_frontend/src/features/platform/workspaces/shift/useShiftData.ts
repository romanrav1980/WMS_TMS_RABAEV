import { useEffect, useState } from "react";
import { apiFetch } from "../../../../api";
import { readError, useApiRead } from "../../access-admin";
import type { ReadState } from "../../access-admin/useApiRead";
import type { CaseTask, Session, Wave } from "../types";
import type { CaseShort, PickReadiness, ReplenishmentRow, TimeContext, WaveDetail, WaveReadiness } from "./types";

export const SHIFT_LIMITS = { future: 50, launched: 100, caseTasks: 200, sessions: 100 } as const;  // sessions: limit API по умолчанию

export type ShiftData = { future: ReadState<Wave[]>; launched: ReadState<Wave[]>; caseTasks: ReadState<CaseTask[]>; sessions: ReadState<Session[]>;
  shorts: ReadState<CaseShort[]> };
// Восстановление недостач читается отдельно (recovery/useRecovery): типизировано и привязано к складу (C0117).

/** Списки старшего смены по выбранному складу: фильтр ware_id и native-права применяет сервер до limit (C-0085…C-0091).
 *  Волны — с ware_id (при нескольких складах сервер требует его, первый не угадываем); сборка — scope=all (сменный обзор, не «мои»).
 *  Без склада ничего не читается. */
export function useShiftData(reload: number, warehouseId: string): ShiftData {
  const wh = warehouseId ? `&ware_id=${warehouseId}` : null;
  return {
    future: useApiRead<Wave[]>(wh && `/api/picking/waves?status=PREVIEW&limit=${SHIFT_LIMITS.future}${wh}`, reload),
    launched: useApiRead<Wave[]>(wh && `/api/picking/waves?status=LAUNCHED&limit=${SHIFT_LIMITS.launched}${wh}`, reload),
    caseTasks: useApiRead<CaseTask[]>(wh && `/api/case-pick/tasks?scope=all&include_closed=true&limit=${SHIFT_LIMITS.caseTasks}${wh}`, reload),
    sessions: useApiRead<Session[]>(wh && `/api/resources/sessions?${wh.slice(1)}`, reload),
    shorts: useApiRead<CaseShort[]>(wh && `/api/case-pick/shorts?${wh.slice(1)}`, reload),
  };
}

/** Selected wave reads its own bounded queue, including completed carriers. */
export function useSelectedWaveCases(warehouse: string, wave: number | null, reload: number, overview: Map<number, string[]>) {
  const read = useApiRead<CaseTask[]>(warehouse && wave != null
    ? `/api/case-pick/tasks?scope=all&include_closed=true&limit=500&ware_id=${warehouse}&pick_wave_id=${wave}` : null, reload);
  const cases = new Map(overview);
  if (wave != null) {
    cases.delete(wave);
    if (!read.loading && !read.error && read.data && read.data.length < 500 && read.data.every(t => t.pick_wave_id === wave))
      cases.set(wave, read.data.map(t => t.status));
  }
  return { cases, tasks: !read.loading && !read.error ? read.data ?? [] : [] };
}

type Part<T> = { status: string; data: T | null; error: string };
type Overview = { warehouse_id: number; wave_ids: number[]; observed_at: string; all_sources_available: boolean;
  waves: { wave_id: number; readiness: Part<WaveReadiness>; pick: Part<PickReadiness>; time: Part<TimeContext>; replenishment: Part<ReplenishmentRow[]> }[] };
export const OVERVIEW_BATCH = 50, OVERVIEW_CONCURRENCY = 2;

/** Ошибка источника внутри батча — его статус и код; это не готовность волны и не «пусто». */
const part = <T,>(p: Part<T> | undefined): { data: T | null; error: string } =>
  !p ? { data: null, error: "нет в ответе" } : p.status === "READY" ? { data: p.data, error: "" } : { data: null, error: `${p.status === "FORBIDDEN" ? "нет права" : "ошибка источника"}${p.error ? " (" + p.error + ")" : ""}` };

export type Coverage = { requested: number; read: number; batches: number; failed: number; observed: string[]; error: string };

/** Детали всех видимых волн склада через read-only POST /api/picking/shift-overview (C-0088): батчи до 50, не больше 2 одновременно.
 *  Несколько батчей — не единый снимок смены: возвращается coverage с observed_at каждого. Смена склада/списка/пользователя
 *  (ремоунт стола) отменяет прежние запросы; ответ другого набора не выдаётся за текущий. Команд нет, автоповтора нет. */
export function useWaveDetails(ids: number[], warehouseId: string, reload: number): { details: Map<number, WaveDetail>; loading: boolean; coverage: Coverage } {
  const key = warehouseId && ids.length ? `${warehouseId}:${[...new Set(ids)].join(",")}` : "";
  const empty: Coverage = { requested: 0, read: 0, batches: 0, failed: 0, observed: [], error: "" };
  const [state, setState] = useState<{ key: string; details: Map<number, WaveDetail>; loading: boolean; coverage: Coverage }>({ key: "", details: new Map(), loading: false, coverage: empty });
  useEffect(() => {
    if (!key) { setState({ key, details: new Map(), loading: false, coverage: empty }); return; }
    const controller = new AbortController(), list = key.split(":")[1].split(",").map(Number);
    const batches: number[][] = []; for (let i = 0; i < list.length; i += OVERVIEW_BATCH) batches.push(list.slice(i, i + OVERVIEW_BATCH));
    setState(old => ({ ...old, loading: true }));
    const details = new Map<number, WaveDetail>(), cov: Coverage = { ...empty, requested: list.length, batches: batches.length };
    let next = 0;
    const worker = async () => { while (next < batches.length && !controller.signal.aborted) {
      const batch = batches[next++];
      try {
        const r = await apiFetch<Overview>("/api/picking/shift-overview", { method: "POST", signal: controller.signal,
          headers: { "Content-Type": "application/json" }, body: JSON.stringify({ warehouse_id: Number(warehouseId), wave_ids: batch }) });
        for (const w of r.waves) details.set(w.wave_id, { wave_id: w.wave_id, observed_at: r.observed_at, readiness: part(w.readiness), pick: part(w.pick), time: part(w.time), replenishment: part(w.replenishment) });
        cov.read += r.waves.length; cov.observed.push(r.observed_at);
      } catch (reason) { cov.failed++; cov.error = readError(reason); }
    } };
    Promise.all(Array.from({ length: Math.min(OVERVIEW_CONCURRENCY, batches.length) }, worker)).then(() => {
      if (!controller.signal.aborted) setState({ key, details, loading: false, coverage: cov });
    });
    return () => controller.abort();
  }, [key, reload]);
  const own = state.key === key;
  return { details: own ? state.details : new Map(), loading: state.loading || !own, coverage: own ? state.coverage : empty };
}
