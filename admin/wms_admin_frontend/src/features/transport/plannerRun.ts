import { API_BASE, ApiRequestError, adminAuthorization, apiFetch, currentSessionCredentials } from "../../api";

// D002: VRP solve/apply через прямые синхронные контракты транспорта.
// POST /planner/solve без async_response возвращает полный VrpPlan (routes включены) —
// это единственный существующий контракт, отдающий результат расчёта.
// Применение фиксирует payload (plan_id + дата) до отправки: повтор/перезагрузка/повторное
// нажатие повторяют исходный payload, а не создают новый intent поверх неизвестного исхода.

export type PlannerSolveRequest = {
  plan_date: string;
  transport_type: string | null;
  time_limit_s: number;
  source: string;
  solver: string;
};

export type PlannerSolveOutcome<T> = {
  plan: T;
  /** Дата отгрузки, с которой выполнялся расчёт; применять план нужно именно с ней. */
  shipment_date: string;
};

export type ApplyPending = {
  plan_id: number;
  shipment_date: string;
};

const applyKey = () =>
  "retailcase.planner.apply.pending:" + JSON.stringify([API_BASE, currentSessionCredentials().username]);

export function readApplyPending(): ApplyPending | null {
  try {
    const raw = localStorage.getItem(applyKey());
    if (raw === null) return null;
    const v = JSON.parse(raw) as ApplyPending;
    return v && typeof v.plan_id === "number" && typeof v.shipment_date === "string" ? v : null;
  } catch {
    return null;
  }
}

/** Явная сверка: снять сохранённый payload применения после проверки списка рейсов. */
export function resolveApplyPending(): void {
  try { localStorage.removeItem(applyKey()); } catch { /* */ }
}

function isConfirmedRefusal(e: unknown): boolean {
  return e instanceof ApiRequestError && e.status >= 400 && e.status < 500;
}

export async function runSolve<T extends { routes?: unknown }>(
  request: PlannerSolveRequest,
): Promise<PlannerSolveOutcome<T>> {
  const plan = await apiFetch<T>("/api/admin/transport/planner/solve", {
    method: "POST",
    body: JSON.stringify(request),
  });
  if (!plan || !Array.isArray(plan.routes)) {
    throw new Error(
      "Сервер не вернул маршруты расчёта. Повторите расчёт; если ошибка повторяется — сообщите о несоответствии контракта результата VRP.",
    );
  }
  return { plan, shipment_date: request.plan_date };
}

export async function applyPlan<T>(planId: number, shipmentDate: string): Promise<T> {
  const intent: ApplyPending = { plan_id: planId, shipment_date: shipmentDate };
  const raw = JSON.stringify(intent);
  try {
    localStorage.setItem(applyKey(), raw);
    if (localStorage.getItem(applyKey()) !== raw) throw new Error("verify");
  } catch {
    throw new Error("Не удалось надёжно сохранить payload применения плана — действие не выполнено.");
  }
  try {
    const result = await apiFetch<T>("/api/admin/transport/planner/apply", {
      method: "POST",
      body: JSON.stringify(intent),
    });
    resolveApplyPending();
    return result;
  } catch (e) {
    if (isConfirmedRefusal(e)) resolveApplyPending();
    else throw new Error(
      "Исход применения плана не подтверждён. Проверьте список рейсов и повторите тем же планом. (" + String(e) + ")",
    );
    throw e;
  }
}

// --- Sprint 101: асинхронный solve + отмена + полный результат задачи ---

export type SolveJob = { job_id: string; stream_url: string };
export type SolveJobResult<T> = { job_id: string; done: boolean; error: string | null; result: T | null };

export async function startSolveAsync(request: PlannerSolveRequest): Promise<SolveJob> {
  return apiFetch<SolveJob>("/api/admin/transport/planner/solve?async_response=true", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function cancelSolve(jobId: string): Promise<void> {
  await apiFetch(`/api/admin/transport/planner/solve/${jobId}`, { method: "DELETE" });
}

export async function getJobResult<T>(jobId: string): Promise<SolveJobResult<T>> {
  return apiFetch<SolveJobResult<T>>(`/api/admin/transport/planner/solve/${jobId}`);
}

/** Fetch-нативный SSE-поток с Basic-авторизацией (EventSource не передаёт заголовки). */
export async function streamJob(
  jobId: string,
  onEvent: (event: { type: string; [k: string]: unknown }) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/admin/transport/planner/solve/${jobId}/stream`, {
    headers: { Authorization: adminAuthorization() },
    signal,
  });
  if (!res.ok) throw new ApiRequestError(res.status, res.statusText);
  if (!res.body) throw new Error("Поток результата расчёта недоступен.");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      const line = frame.split("\n").find(l => l.startsWith("data: "));
      if (!line) continue;
      const data = line.slice(6).trim();
      if (!data || data === '{"type":"ping"}') continue;
      try { onEvent(JSON.parse(data) as { type: string }); } catch { /* ignore malformed frame */ }
    }
  }
}
