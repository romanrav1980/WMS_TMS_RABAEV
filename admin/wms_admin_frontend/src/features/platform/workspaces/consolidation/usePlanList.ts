import { useCallback, useEffect, useRef, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../../api";
import { readError } from "../../access-admin";
import { parsePage, PlanShapeError } from "./planModel";
import type { PlanRow } from "./planModel";

export type PlanFilter = "ACTIVE" | "CANCELLED" | "ALL";
export const PLAN_PAGE = 30;
type State = { key: string; items: PlanRow[]; next: string | null; hasMore: boolean; loading: boolean; error: string; at: Date | null };

/** Постраничный список планов склада. Смена склада/фильтра/пользователя сбрасывает курсор и данные; ответ другого ключа отбрасывается.
 *  401/403/404 очищают закрытые данные. Итога по складу API не даёт — показываем «загружено N, есть ещё». */
export function usePlanList(warehouseId: string, filter: PlanFilter, scope: string, reload: number) {
  const key = warehouseId ? `${scope}|${warehouseId}|${filter}` : "";
  const [s, setS] = useState<State>({ key: "", items: [], next: null, hasMore: false, loading: false, error: "", at: null });
  const active = useRef<AbortController | null>(null);
  const load = useCallback(async (after: string | null) => {
    if (!key) return;
    active.current?.abort(); const ctrl = new AbortController(); active.current = ctrl;
    setS(old => ({ ...(old.key === key ? old : { key, items: [], next: null, hasMore: false, at: null }), key, loading: true, error: "" }));
    const q = new URLSearchParams({ warehouse_id: warehouseId, status: filter, limit: String(PLAN_PAGE) });
    if (after) q.set("after", after);
    try {
      const page = parsePage(await apiFetch<unknown>(`/api/consolidation-plans?${q}`, { signal: ctrl.signal }), Number(warehouseId));
      if (ctrl.signal.aborted) return;
      setS(old => old.key !== key ? old : { key, items: after ? [...old.items, ...page.items.filter(i => !old.items.some(o => o.plan_id === i.plan_id))] : page.items,
        next: page.next_after, hasMore: page.has_more, loading: false, error: "", at: new Date() });
    } catch (e) {
      if (ctrl.signal.aborted) return;
      const denied = e instanceof ApiRequestError && [401, 403, 404].includes(e.status);
      const error = e instanceof PlanShapeError ? e.message : readError(e);
      setS(old => old.key !== key ? old : denied ? { key, items: [], next: null, hasMore: false, loading: false, error, at: null } : { ...old, loading: false, error });
    }
  }, [key, warehouseId, filter]);
  useEffect(() => { void load(null); return () => active.current?.abort(); }, [load, reload]);
  const own = s.key === key;
  return { items: own ? s.items : [], hasMore: own && s.hasMore, loading: !own || s.loading, error: own ? s.error : "", at: own ? s.at : null,
    more: () => { if (own && s.next) void load(s.next); } };
}
