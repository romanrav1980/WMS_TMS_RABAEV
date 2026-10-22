import { useMemo } from "react";
import { isClosedWave } from "./executionState";
import { executionRisks, waveRisks } from "./risks";
import { SHIFT_LIMITS } from "./useShiftData";
import type { Coverage, ShiftData } from "./useShiftData";
import type { Wave } from "../types";
import type { Risk, WaveDetail } from "./types";

/** Риски смены, фактические статусы сборки по волнам и пробелы проверки. Пока есть пробел, «рисков нет» не утверждается:
 *  непрочитанный источник или волна без подробной проверки — неизвестность, а не отсутствие риска. */
export function useShiftRisks(waves: Wave[], details: Map<number, WaveDetail>, data: ShiftData, coverage: Coverage, loading: boolean) {
  return useMemo(() => {
    const risks: Risk[] = [...waves.flatMap(w => { const d = details.get(w.pick_wave_id); return d ? waveRisks(w, d) : []; }),
      ...executionRisks(data.caseTasks.data ?? [], data.shorts.data ?? [])];
    const risky = new Set(risks.filter(r => r.severity === "BLOCKER" && r.wave_id != null).map(r => r.wave_id!));
    // Статусы сборки по волне — только из необрезанной выборки: иначе невидимое открытое задание дало бы ложное «отгружено».
    const tasks = data.caseTasks.data, truncated = (tasks?.length ?? 0) >= SHIFT_LIMITS.caseTasks, cases = new Map<number, string[]>();
    if (tasks && !truncated) for (const t of tasks) (cases.get(t.pick_wave_id) ?? cases.set(t.pick_wave_id, []).get(t.pick_wave_id)!).push(t.status);
    const gaps: string[] = [];
    for (const [label, r] of [["будущие волны", data.future], ["волны в работе", data.launched], ["сборка", data.caseTasks], ["недостачи", data.shorts]] as const)
      if (r.error) gaps.push(`${label}: ${r.error}`); else if (r.data == null) gaps.push(`${label}: ещё читаются`);
    const unread = waves.filter(w => !isClosedWave(w.status) && !details.has(w.pick_wave_id)).length;
    if (unread) gaps.push(`подробно не проверено волн: ${unread}${loading ? " (идёт чтение)" : coverage.error ? " — " + coverage.error : ""}`);
    if (truncated) gaps.push(`сборка: показаны первые ${SHIFT_LIMITS.caseTasks} заданий, остальные не проверены`);
    return { risks, risky, cases, gaps };
  }, [waves, details, data.future, data.launched, data.caseTasks, data.shorts, coverage, loading]);
}
