import { useEffect, useState } from "react";
import { API_BASE, ApiRequestError, apiFetch, currentSessionCredentials } from "../../api";

// D001 (по отзыву Codex): обычное создание рейса — цепочка POST /tasks → PATCH /tasks/{id} → POST /tasks/{id}/sts.
// Модель восстановления:
//   - intent сохраняется ДО первого POST (защита от закрытия вкладки/падения между отправкой и ответом);
//   - pending/unknown НЕ удаляется при закрытии диалога — разрешение требует фактической сверки со списком рейсов;
//   - повтор использует СОХРАНЁННЫЕ params/st_numbers; изменённые параметры блокируются до завершения исходной операции;
//   - подтверждённый отказ первой попытки (4xx) снимает intent; 5xx/сеть/обрыв сохраняют неопределённый исход.

export type TripCreateParams = {
  transtype: string;
  shipment_date: string;
  shipment_time: string;
  vehicle: string;
  driver_id: number | null;
  dock: string;
};

export type TripCreateResult = {
  task_id: number;
  st_count: number;
  warnings: string[];
};

export type PendingTripCreate = {
  operation_id: string;
  params: TripCreateParams;
  st_numbers: string[];
  /** intent — сохранено до POST; created — task_id известен; unknown — исход POST не подтверждён. */
  kind: "intent" | "created" | "unknown";
  task_id: number | null;
  step: "requisites" | "assign" | null;
};

const pendingKey = () =>
  "retailcase.trip.create.pending:" + JSON.stringify([API_BASE, currentSessionCredentials().username]);

function readPending(): PendingTripCreate | null {
  try {
    const raw = localStorage.getItem(pendingKey());
    if (raw === null) return null;
    const v = JSON.parse(raw) as PendingTripCreate;
    return v && v.operation_id && v.params && typeof v.params === "object" ? v : null;
  } catch {
    return null;
  }
}

export function readTripCreatePending(): PendingTripCreate | null {
  return readPending();
}

/** Видимость незавершённого (intent/unknown) создания и его явное разрешение после сверки. */
export function usePendingTripCreate(createDialog: boolean, createLoading: boolean): {
  kind: null | "intent" | "unknown";
  resolve: () => void;
} {
  const [kind, setKind] = useState<null | "intent" | "unknown">(null);
  useEffect(() => {
    if (!createDialog) { setKind(null); return; }
    const p = readPending();
    setKind(p && p.kind !== "created" ? p.kind : null);
  }, [createDialog, createLoading]);
  const resolve = () => { settlePending(); setKind(null); };
  return { kind, resolve };
}

// Записать до отправки: сбой/повреждение localStorage не должен выглядеть как отсутствие pending.
function savePending(pending: PendingTripCreate): void {
  const key = pendingKey();
  const raw = JSON.stringify(pending);
  try {
    localStorage.setItem(key, raw);
    if (localStorage.getItem(key) === raw) return;
  } catch { /* below */ }
  throw new Error("Не удалось надёжно сохранить состояние создания рейса — действие не выполнено.");
}

function settlePending(): void {
  try { localStorage.removeItem(pendingKey()); } catch { /* */ }
}

/** Явное разрешение неопределённого исхода после фактической сверки со списком рейсов. */
export function resolveTripCreatePending(): void {
  settlePending();
}

export class TripCreateConflict extends Error {
  constructor() {
    super("Есть незавершённое создание рейса с другими параметрами. Завершите или сверьте его прежде нового создания.");
    this.name = "TripCreateConflict";
  }
}

export class TripCreateUncertain extends Error {
  constructor() {
    super("Исход создания рейса не подтверждён. Список рейсов обновлён — проверьте, создан ли рейс, затем подтвердите сверку.");
    this.name = "TripCreateUncertain";
  }
}

function sameParams(a: TripCreateParams, b: TripCreateParams): boolean {
  return a.transtype === b.transtype
    && a.shipment_date === b.shipment_date
    && a.shipment_time === b.shipment_time
    && a.vehicle === b.vehicle
    && a.driver_id === b.driver_id
    && a.dock === b.dock;
}

function sameSts(a: string[], b: string[]): boolean {
  return a.length === b.length && [...a].sort().join("\u0000") === [...b].sort().join("\u0000");
}

function isConfirmedRefusal(e: unknown): boolean {
  // 4xx (400/401/403/404/409/422) — сервер подтвердил, что мутации не было.
  return e instanceof ApiRequestError && e.status >= 400 && e.status < 500;
}

async function patchRequisites(taskId: number, params: TripCreateParams): Promise<void> {
  await apiFetch(`/api/admin/transport/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify({
      transport: params.vehicle || null,
      voditel_id: params.driver_id,
      dock: params.dock || null,
      shipment_time: params.shipment_time,
    }),
  });
}

async function assignSts(taskId: number, stNumbers: string[]): Promise<{ assigned: number; warnings: string[] }> {
  return apiFetch<{ assigned: number; warnings: string[] }>(
    `/api/admin/transport/tasks/${taskId}/sts`,
    { method: "POST", body: JSON.stringify({ st_numbers: stNumbers }) },
  );
}

async function finishChain(pending: PendingTripCreate): Promise<TripCreateResult> {
  const taskId = pending.task_id!;
  try {
    if (pending.step === "requisites") {
      await patchRequisites(taskId, pending.params);
      savePending({ ...pending, step: "assign" });
    }
    let assigned = 0;
    let warnings: string[] = [];
    if (pending.st_numbers.length > 0) {
      const result = await assignSts(taskId, pending.st_numbers);
      assigned = result.assigned;
      warnings = result.warnings;
    }
    settlePending();
    return { task_id: taskId, st_count: assigned, warnings };
  } catch (e) {
    throw new Error(`Рейс #${taskId} создан, но действие не завершено. Обновите список и проверьте реквизиты и состав. (${String(e)})`);
  }
}

async function postCreate(pending: PendingTripCreate): Promise<TripCreateResult> {
  let taskId: number;
  try {
    const res = await apiFetch<{ task_id: number }>("/api/admin/transport/tasks", {
      method: "POST",
      body: JSON.stringify({
        transtype: pending.params.transtype,
        shipment_date: pending.params.shipment_date,
        operation_id: pending.operation_id, // forward-compatible: сервер примет после D001.5
      }),
    });
    taskId = res.task_id;
  } catch (e) {
    if (isConfirmedRefusal(e)) {
      settlePending(); // первая попытка подтверждённо не создала рейс
      throw e;
    }
    // 5xx/сеть/обрыв ответа: исход не подтверждён.
    savePending({ ...pending, kind: "unknown" });
    throw new TripCreateUncertain();
  }
  const created: PendingTripCreate = { ...pending, kind: "created", task_id: taskId, step: "requisites" };
  savePending(created);
  return finishChain(created);
}

export async function createTrip(params: TripCreateParams, stNumbers: string[]): Promise<TripCreateResult> {
  if (!params.transtype || !params.shipment_date || !/^\d{2}:\d{2}$/.test(params.shipment_time)) {
    throw new Error("Укажите тип транспорта, дату и время отгрузки (ЧЧ:ММ).");
  }

  const existing = readPending();
  if (existing) {
    // Повтор строго сохранённого запроса; изменённые параметры не подменяют незавершённую команду.
    if (!sameParams(existing.params, params) || !sameSts(existing.st_numbers, stNumbers)) {
      throw new TripCreateConflict();
    }
    if (existing.kind === "created") {
      return finishChain(existing);
    }
    // intent/unknown: исход POST не подтверждён; без серверного operation_id слепой повтор запрещён.
    throw new TripCreateUncertain();
  }

  // intent ДО первого POST.
  const pending: PendingTripCreate = {
    operation_id: "TRIP.UI:" + crypto.randomUUID(),
    params,
    st_numbers: stNumbers,
    kind: "intent",
    task_id: null,
    step: null,
  };
  savePending(pending);
  return postCreate(pending);
}
