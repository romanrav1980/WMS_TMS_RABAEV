import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type TransportTask = {
  ID: number;
  TRANSPORT: string | null;
  TRANSTYPE: string | null;
  CONDITION: string | null;
  SHIPMENT_DATE: string | null;
  VODITEL_ID: number | null;
  VODITEL_NAME: string | null;
  VODITEL_TEL: string | null;
  TK_NAME: string | null;
  IS_OWN_DRIVER: number | null;
  PRIMECHANIE: string | null;
  DOCK: string | null;
  SHIPMENT_TIME: string | null;
  TEMP_REGION: string | null;
  PRICE: number | null;
  PALLET_COUNT: number;
  ST_COUNT: number;
  DELETED: number | null;
  READY_PERC: number | null;
  UNREADY_COUNT: number | null;
};

type TaskSt = {
  ST_NUMBER: string;
  ADDR: string | null;
  REGION: string | null;
  RAION: string | null;
  ORD: number | null;
  PALLETS_COUNT: number;
  WEIGHT_KG: number;
  STDATE: string | null;
  ZONE: string | null;
  TIME_FROM: string | null;
  TIME_TO: string | null;
  LOAD_TYPE: string | null;
};

type AvailableSt = {
  ST_NUMBER: string;
  ADDR: string | null;
  REGION: string | null;
  RAION: string | null;
  PALLETS_COUNT: number;
  WEIGHT_KG: number;
  VOLUME_M3: number | null;
  STDATE: string | null;
  TRANSTASK_ID: number | null;
  TRANSPORT_TYPE: string | null;
  NEEDS_HYDRO_BOARD: number;
  NAPR: string | null;
  VERIFY_PERC: number | null;
};

type Vehicle = {
  ID: number;
  NUM: string;
  TR_TYPE: string | null;
  MARKA: string | null;
  PALLETS: number | null;
  GIDROBORT: number;
};

type Driver = {
  ID: number;
  FULL_NAME: string | null;
  TEL: string | null;
  SOBSTVENNYY: number | null;
  DOVERENNOST_OT: string | null;
};

type TransportType = {
  TRANSPORTTYPE: string;
  NAME: string | null;
};

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8088";
const API_BASIC_AUTH = import.meta.env.VITE_ADMIN_BASIC_AUTH || "admin:admin123";

function apiHeaders(): HeadersInit {
  return { Authorization: `Basic ${btoa(API_BASIC_AUTH)}`, "Content-Type": "application/json" };
}

async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers: apiHeaders() });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body?.detail || detail;
    } catch { /* ignore */ }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function fmtDate(s: string | null): string {
  if (!s) return "—";
  return s.slice(0, 10);
}

function fmtTime(s: string | null): string {
  if (!s) return "";
  // ISO datetime: "2026-05-22T09:00:00" → "09:00"
  const t = s.includes("T") ? s.slice(11, 16) : s.slice(0, 5);
  return t || "";
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function TransportDispatchPage({ onBack }: { onBack: () => void }) {
  const [tasks, setTasks] = useState<TransportTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<TransportTask | null>(null);
  const [taskSts, setTaskSts] = useState<TaskSt[]>([]);
  const [availableSts, setAvailableSts] = useState<AvailableSt[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [transportTypes, setTransportTypes] = useState<TransportType[]>([]);

  const [filterDate, setFilterDate] = useState(todayIso());
  const [stDate, setStDate] = useState(todayIso());
  const [selectedStNums, setSelectedStNums] = useState<Set<string>>(new Set());

  // Фильтры панели доступных СТ
  const [addrMask, setAddrMask] = useState("");
  const [stMask, setStMask] = useState("");
  const [assembledOnly, setAssembledOnly] = useState(false);
  const debouncedAddrMask = useDebounce(addrMask, 300);
  const debouncedStMask = useDebounce(stMask, 300);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editDraft, setEditDraft] = useState<Partial<TransportTask>>({});

  const editRef = useRef(editDraft);
  editRef.current = editDraft;

  // ------------------------------------------------------------------
  // Load reference data once
  // ------------------------------------------------------------------
  useEffect(() => {
    Promise.all([
      apiFetch<Vehicle[]>("/api/admin/transport/vehicles"),
      apiFetch<Driver[]>("/api/admin/transport/drivers"),
      apiFetch<TransportType[]>("/api/admin/transport/types"),
    ]).then(([v, d, t]) => {
      setVehicles(v);
      setDrivers(d);
      setTransportTypes(t);
    }).catch(() => {
      setVehicles([
        { ID: 61, NUM: "Т368ХН", TR_TYPE: "10", MARKA: "MAN", PALLETS: 11, GIDROBORT: 0 },
        { ID: 62, NUM: "Е152НХ", TR_TYPE: "10", MARKA: "КАМАЗ", PALLETS: 12, GIDROBORT: 0 },
        { ID: 66, NUM: "Р234УХ", TR_TYPE: "15", MARKA: "КАМАЗ", PALLETS: 11, GIDROBORT: 1 },
      ]);
      setDrivers([
        { ID: 6, FULL_NAME: "Сташков Иван Викторович", TEL: "8-952-74-109-09", SOBSTVENNYY: 1, DOVERENNOST_OT: null },
        { ID: 7, FULL_NAME: "Петров Алексей", TEL: "", SOBSTVENNYY: 0, DOVERENNOST_OT: "ООО Транс-Авто" },
      ]);
      setTransportTypes([
        { TRANSPORTTYPE: "10", NAME: "Тент 10т" },
        { TRANSPORTTYPE: "15", NAME: "Тент 15т" },
        { TRANSPORTTYPE: "20реф", NAME: "Рефрижератор 20т" },
      ]);
    });
  }, []);

  // ------------------------------------------------------------------
  // Load tasks for date
  // ------------------------------------------------------------------
  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<TransportTask[]>(
        `/api/admin/transport/tasks?shipment_date=${filterDate}&include_readiness=true`
      );
      setTasks(data);
    } catch (e) {
      setError(String(e));
      setTasks(demoTasks(filterDate));
    } finally {
      setLoading(false);
    }
  }, [filterDate]);

  useEffect(() => { loadTasks(); }, [loadTasks]);

  // ------------------------------------------------------------------
  // Load available STs (перезагружается при любом изменении фильтров)
  // ------------------------------------------------------------------
  const loadAvailableSts = useCallback(async () => {
    try {
      const params = new URLSearchParams({ stdate: stDate, unassigned_only: "true" });
      if (debouncedAddrMask) params.set("addr_mask", debouncedAddrMask);
      if (debouncedStMask) params.set("st_mask", debouncedStMask);
      if (assembledOnly) params.set("assembled_only", "true");
      const data = await apiFetch<AvailableSt[]>(`/api/admin/transport/available-sts?${params}`);
      setAvailableSts(data);
    } catch {
      setAvailableSts(demoAvailableSts(stDate));
    }
  }, [stDate, debouncedAddrMask, debouncedStMask, assembledOnly]);

  useEffect(() => { loadAvailableSts(); }, [loadAvailableSts]);

  // ------------------------------------------------------------------
  // Select task → load its STs
  // ------------------------------------------------------------------
  async function selectTask(task: TransportTask) {
    setSelectedTask(task);
    setEditMode(false);
    setSelectedStNums(new Set());
    try {
      const data = await apiFetch<TaskSt[]>(`/api/admin/transport/tasks/${task.ID}/sts`);
      setTaskSts(data);
    } catch {
      setTaskSts([]);
    }
  }

  // ------------------------------------------------------------------
  // Assign selected STs to task
  // ------------------------------------------------------------------
  async function handleAssign() {
    if (!selectedTask || selectedStNums.size === 0) return;
    setLoading(true);
    try {
      const result = await apiFetch<{ assigned: number; warnings: string[] }>(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts`,
        { method: "POST", body: JSON.stringify({ st_numbers: Array.from(selectedStNums) }) }
      );
      if (result.warnings.length > 0) {
        setError(result.warnings.join("; "));
      }
      setSelectedStNums(new Set());
      await Promise.all([selectTask(selectedTask), loadTasks(), loadAvailableSts()]);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  // ------------------------------------------------------------------
  // Unassign ST from task
  // ------------------------------------------------------------------
  async function handleUnassign(stNumber: string) {
    if (!selectedTask) return;
    setLoading(true);
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}`,
        { method: "DELETE" }
      );
      await Promise.all([selectTask(selectedTask), loadTasks(), loadAvailableSts()]);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  // ------------------------------------------------------------------
  // Set load_type for ST in task
  // ------------------------------------------------------------------
  async function handleSetLoadType(stNumber: string, loadType: string) {
    if (!selectedTask) return;
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}/load-type`,
        { method: "PATCH", body: JSON.stringify({ load_type: loadType }) }
      );
      setTaskSts(prev => prev.map(s =>
        s.ST_NUMBER === stNumber ? { ...s, LOAD_TYPE: loadType || null } : s
      ));
    } catch (e) {
      setError(String(e));
    }
  }

  // ------------------------------------------------------------------
  // Set ORD for ST in task
  // ------------------------------------------------------------------
  async function handleSetOrder(stNumber: string, ord: number) {
    if (!selectedTask) return;
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}/order`,
        { method: "PATCH", body: JSON.stringify({ ord }) }
      );
      setTaskSts(prev => prev.map(s =>
        s.ST_NUMBER === stNumber ? { ...s, ORD: ord } : s
      ));
    } catch (e) {
      setError(String(e));
    }
  }

  // ------------------------------------------------------------------
  // Create task
  // ------------------------------------------------------------------
  async function handleCreate(transtype: string, shipment_date: string) {
    setLoading(true);
    try {
      const res = await apiFetch<{ task_id: number }>(
        "/api/admin/transport/tasks",
        { method: "POST", body: JSON.stringify({ transtype, shipment_date }) }
      );
      setCreateDialog(false);
      await loadTasks();
      const newTask = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${res.task_id}`);
      selectTask(newTask);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  // ------------------------------------------------------------------
  // Save task edits
  // ------------------------------------------------------------------
  async function handleSaveEdit() {
    if (!selectedTask) return;
    setLoading(true);
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}`,
        { method: "PATCH", body: JSON.stringify(editRef.current) }
      );
      setEditMode(false);
      const updated = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${selectedTask.ID}`);
      setSelectedTask(updated);
      setTasks(prev => prev.map(t => t.ID === updated.ID ? updated : t));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  // ------------------------------------------------------------------
  // Close / Cancel task
  // ------------------------------------------------------------------
  async function handleClose() {
    if (!selectedTask) return;
    if (!confirm(`Закрыть рейс #${selectedTask.ID} как отгруженный?`)) return;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/close`, { method: "POST" });
      setSelectedTask(null);
      setTaskSts([]);
      await loadTasks();
    } catch (e) {
      // Показываем полное сообщение от can_print (422)
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel() {
    if (!selectedTask) return;
    if (!confirm(`Отменить рейс #${selectedTask.ID}? Это действие необратимо.`)) return;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/cancel`, { method: "POST" });
      setSelectedTask(null);
      setTaskSts([]);
      await loadTasks();
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  const totalWeight = taskSts.reduce((s, st) => s + (st.WEIGHT_KG || 0), 0);
  const totalPallets = taskSts.reduce((s, st) => s + (st.PALLETS_COUNT || 0), 0);
  const selectedVehicle = vehicles.find(v => v.NUM === selectedTask?.TRANSPORT);

  return (
    <div className="dispatch-shell">
      {/* ---- Topbar ---- */}
      <header className="dispatch-topbar">
        <button className="dispatch-back" onClick={onBack} title="Назад">◄</button>
        <div className="dispatch-title">
          <h1>Диспетчер отгрузки</h1>
          <span className="dispatch-subtitle">Ручное планирование рейсов</span>
        </div>
        <label className="dispatch-date-pick">
          <span>Дата отгрузки</span>
          <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
        </label>
        <button className="dispatch-new-btn" onClick={() => setCreateDialog(true)}>
          + Создать рейс
        </button>
        {loading && <span className="dispatch-spinner">●</span>}
        {error && (
          <span
            className="dispatch-error"
            title={error}
            onClick={() => setError(null)}
            style={{ cursor: "pointer" }}
          >
            ⚠ {error.slice(0, 80)}
          </span>
        )}
      </header>

      <div className="dispatch-body">
        {/* ---- Left: task list + available STs ---- */}
        <aside className="dispatch-left">
          {/* Task list */}
          <section className="dispatch-panel">
            <div className="dispatch-panel-header">
              <b>Рейсы на {filterDate}</b>
              <span className="dispatch-count">{tasks.length}</span>
            </div>
            <div className="dispatch-task-list">
              {tasks.length === 0 && (
                <div className="dispatch-empty">Рейсов нет. Создайте первый.</div>
              )}
              {tasks.map(task => (
                <div
                  key={task.ID}
                  className={`dispatch-task-card ${selectedTask?.ID === task.ID ? "selected" : ""} ${task.CONDITION === "Отгружен" ? "closed" : ""}`}
                  onClick={() => selectTask(task)}
                >
                  <div className="dispatch-task-card-top">
                    <b>#{task.ID}</b>
                    {task.TRANSPORT && <span className="dispatch-vehicle-badge">{task.TRANSPORT}</span>}
                    <span className={`dispatch-cond ${condClass(task.CONDITION)}`}>
                      {task.CONDITION || "Новый"}
                    </span>
                  </div>
                  <div className="dispatch-task-card-mid">
                    {task.TRANSTYPE && <span className="dispatch-type-chip">{task.TRANSTYPE}</span>}
                    <span>{task.ST_COUNT} СТ · {task.PALLET_COUNT} пал</span>
                    {task.DOCK && <span>· Д{task.DOCK}</span>}
                  </div>
                  {task.VODITEL_NAME && (
                    <div className="dispatch-task-card-bot">
                      {task.VODITEL_NAME}
                      {task.IS_OWN_DRIVER === 0 && task.TK_NAME && (
                        <span className="dispatch-tk-badge">{task.TK_NAME}</span>
                      )}
                    </div>
                  )}
                  {task.READY_PERC !== null && task.READY_PERC !== undefined && (
                    <ReadinessBar perc={task.READY_PERC} unready={task.UNREADY_COUNT} />
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Available STs */}
          <section className="dispatch-panel dispatch-available-panel">
            <div className="dispatch-panel-header">
              <b>Свободные СТ</b>
              <label className="dispatch-st-date">
                <input
                  type="date"
                  value={stDate}
                  onChange={e => { setStDate(e.target.value); setSelectedStNums(new Set()); }}
                />
              </label>
              <span className="dispatch-count">{availableSts.length}</span>
            </div>

            {/* Фильтры */}
            <div className="dispatch-st-filters">
              <input
                className="dispatch-filter-input"
                type="text"
                placeholder="Адрес / регион"
                value={addrMask}
                onChange={e => setAddrMask(e.target.value)}
              />
              <input
                className="dispatch-filter-input"
                type="text"
                placeholder="Номер СТ"
                value={stMask}
                onChange={e => setStMask(e.target.value)}
              />
              <label className="dispatch-filter-check">
                <input
                  type="checkbox"
                  checked={assembledOnly}
                  onChange={e => setAssembledOnly(e.target.checked)}
                />
                Только собранные
              </label>
            </div>

            <div className="dispatch-st-list">
              {availableSts.length === 0 && (
                <div className="dispatch-empty">Нет свободных СТ по фильтрам.</div>
              )}
              {availableSts.map(st => {
                const checked = selectedStNums.has(st.ST_NUMBER);
                return (
                  <label key={st.ST_NUMBER} className={`dispatch-st-row ${checked ? "selected" : ""}`}>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => {
                        setSelectedStNums(prev => {
                          const next = new Set(prev);
                          if (next.has(st.ST_NUMBER)) next.delete(st.ST_NUMBER);
                          else next.add(st.ST_NUMBER);
                          return next;
                        });
                      }}
                    />
                    <span className="dispatch-st-num">{st.ST_NUMBER}</span>
                    <span className="dispatch-st-addr">{st.REGION || st.ADDR || "—"}</span>
                    {st.RAION && <span className="dispatch-st-raion-sm">{st.RAION}</span>}
                    <span className="dispatch-st-meta">
                      {st.PALLETS_COUNT} пал
                      {st.WEIGHT_KG ? ` · ${st.WEIGHT_KG} кг` : ""}
                    </span>
                    {st.NEEDS_HYDRO_BOARD === 1 && <span className="dispatch-hydro" title="Гидроборт">Г</span>}
                    {st.VERIFY_PERC !== null && st.VERIFY_PERC !== undefined && (
                      <VerifyPill perc={st.VERIFY_PERC} />
                    )}
                  </label>
                );
              })}
            </div>
            {selectedStNums.size > 0 && selectedTask && (
              <div className="dispatch-assign-bar">
                <span>{selectedStNums.size} СТ выбрано</span>
                <button className="dispatch-assign-btn" onClick={handleAssign} disabled={loading}>
                  → Назначить в рейс #{selectedTask.ID}
                </button>
              </div>
            )}
          </section>
        </aside>

        {/* ---- Right: task detail ---- */}
        <main className="dispatch-detail">
          {!selectedTask ? (
            <div className="dispatch-no-selection">
              <span>Выберите рейс слева или создайте новый</span>
            </div>
          ) : (
            <>
              {/* Detail header */}
              <div className="dispatch-detail-header">
                <div>
                  <h2>Рейс #{selectedTask.ID}</h2>
                  <span className={`dispatch-cond-big ${condClass(selectedTask.CONDITION)}`}>
                    {selectedTask.CONDITION || "Новый"}
                  </span>
                  {selectedTask.READY_PERC !== null && selectedTask.READY_PERC !== undefined && (
                    <ReadinessBar perc={selectedTask.READY_PERC} unready={selectedTask.UNREADY_COUNT} />
                  )}
                </div>
                <div className="dispatch-detail-actions">
                  {!editMode ? (
                    <button className="dispatch-edit-btn" onClick={() => { setEditMode(true); setEditDraft({}); }}>
                      Редактировать
                    </button>
                  ) : (
                    <>
                      <button className="dispatch-save-btn" onClick={handleSaveEdit} disabled={loading}>Сохранить</button>
                      <button className="dispatch-cancel-edit-btn" onClick={() => setEditMode(false)}>Отмена</button>
                    </>
                  )}
                </div>
              </div>

              {/* Реквизиты */}
              <div className="dispatch-meta-grid">
                <MetaField label="Машина">
                  {editMode ? (
                    <select
                      value={editDraft.TRANSPORT ?? selectedTask.TRANSPORT ?? ""}
                      onChange={e => setEditDraft(d => ({ ...d, TRANSPORT: e.target.value || null }))}
                    >
                      <option value="">— не выбрана —</option>
                      {vehicles.map(v => (
                        <option key={v.ID} value={v.NUM}>
                          {v.NUM} · {v.MARKA} · {v.TR_TYPE} · {v.PALLETS} пал
                          {v.GIDROBORT ? " · Гидроборт" : ""}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span>{selectedTask.TRANSPORT || "—"}{selectedVehicle ? ` · ${selectedVehicle.MARKA}` : ""}</span>
                  )}
                </MetaField>

                <MetaField label="Тип">
                  <span>{selectedTask.TRANSTYPE || "—"}</span>
                </MetaField>

                <MetaField label="Водитель">
                  {editMode ? (
                    <select
                      value={editDraft.VODITEL_ID ?? selectedTask.VODITEL_ID ?? ""}
                      onChange={e => setEditDraft(d => ({ ...d, VODITEL_ID: e.target.value ? Number(e.target.value) : null }))}
                    >
                      <option value="">— не выбран —</option>
                      {drivers.map(d => (
                        <option key={d.ID} value={d.ID}>
                          {d.FULL_NAME || `#${d.ID}`}
                          {d.SOBSTVENNYY === 0 && d.DOVERENNOST_OT ? ` (${d.DOVERENNOST_OT})` : ""}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span>
                      {selectedTask.VODITEL_NAME || "—"}
                      {selectedTask.VODITEL_TEL ? ` · ${selectedTask.VODITEL_TEL}` : ""}
                      {selectedTask.IS_OWN_DRIVER === 0 && selectedTask.TK_NAME && (
                        <span className="dispatch-tk-inline"> · {selectedTask.TK_NAME}</span>
                      )}
                    </span>
                  )}
                </MetaField>

                <MetaField label="Докстанция">
                  {editMode ? (
                    <input
                      type="text"
                      value={editDraft.DOCK ?? selectedTask.DOCK ?? ""}
                      onChange={e => setEditDraft(d => ({ ...d, DOCK: e.target.value || null }))}
                      placeholder="Д1"
                    />
                  ) : (
                    <span>{selectedTask.DOCK || "—"}</span>
                  )}
                </MetaField>

                <MetaField label="Время отгрузки">
                  {editMode ? (
                    <input
                      type="time"
                      value={editDraft.SHIPMENT_TIME ?? fmtTime(selectedTask.SHIPMENT_TIME)}
                      onChange={e => setEditDraft(d => ({ ...d, SHIPMENT_TIME: e.target.value || null }))}
                    />
                  ) : (
                    <span>{fmtTime(selectedTask.SHIPMENT_TIME) || "—"}</span>
                  )}
                </MetaField>

                <MetaField label="Примечание">
                  {editMode ? (
                    <input
                      type="text"
                      value={editDraft.PRIMECHANIE ?? selectedTask.PRIMECHANIE ?? ""}
                      onChange={e => setEditDraft(d => ({ ...d, PRIMECHANIE: e.target.value || null }))}
                      placeholder="Комментарий диспетчера"
                    />
                  ) : (
                    <span>{selectedTask.PRIMECHANIE || "—"}</span>
                  )}
                </MetaField>
              </div>

              {/* СТ в рейсе */}
              <div className="dispatch-sts-header">
                <b>Заказы в рейсе</b>
                <span className="dispatch-count">{taskSts.length} СТ · {totalPallets} пал · {totalWeight.toFixed(0)} кг</span>
              </div>
              <div className="dispatch-sts-table">
                {/* Заголовок таблицы */}
                {taskSts.length > 0 && (
                  <div className="dispatch-st-task-row dispatch-st-task-header">
                    <span className="dispatch-st-ord">#</span>
                    <span className="dispatch-st-num">СТ</span>
                    <span className="dispatch-st-region">Адрес</span>
                    <span className="dispatch-st-zone">Зона</span>
                    <span className="dispatch-st-window">Окно</span>
                    <span className="dispatch-st-pall">Пал</span>
                    <span className="dispatch-st-wt">Кг</span>
                    <span className="dispatch-st-loadtype">Погр.</span>
                    <span></span>
                  </div>
                )}
                {taskSts.length === 0 && (
                  <div className="dispatch-empty">Рейс пуст. Назначьте СТ из левой панели.</div>
                )}
                {taskSts.map(st => (
                  <TaskStRow
                    key={st.ST_NUMBER}
                    st={st}
                    disabled={loading || selectedTask.CONDITION === "Отгружен"}
                    onUnassign={() => handleUnassign(st.ST_NUMBER)}
                    onSetLoadType={lt => handleSetLoadType(st.ST_NUMBER, lt)}
                    onSetOrder={ord => handleSetOrder(st.ST_NUMBER, ord)}
                  />
                ))}
              </div>

              {/* Footer actions */}
              <div className="dispatch-detail-footer">
                {selectedTask.CONDITION !== "Отгружен" && (
                  <button
                    className="dispatch-close-btn"
                    onClick={handleClose}
                    disabled={loading || taskSts.length === 0}
                  >
                    Закрыть рейс (Отгружен)
                  </button>
                )}
                {selectedTask.CONDITION !== "Отгружен" && (
                  <button className="dispatch-cancel-task-btn" onClick={handleCancel} disabled={loading}>
                    Отменить рейс
                  </button>
                )}
                {selectedTask.CONDITION === "Отгружен" && (
                  <span className="dispatch-closed-label">Рейс отгружен · только чтение</span>
                )}
                {selectedTask.PRICE != null && (
                  <span className="dispatch-price">
                    {selectedTask.PRICE.toLocaleString("ru-RU")} ₽
                  </span>
                )}
              </div>
            </>
          )}
        </main>
      </div>

      {/* ---- Create task dialog ---- */}
      {createDialog && (
        <CreateTaskDialog
          filterDate={filterDate}
          transportTypes={transportTypes}
          onConfirm={handleCreate}
          onClose={() => setCreateDialog(false)}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// TaskStRow — строка состава рейса с inline-редактированием
// ---------------------------------------------------------------------------

function TaskStRow({
  st,
  disabled,
  onUnassign,
  onSetLoadType,
  onSetOrder,
}: {
  st: TaskSt;
  disabled: boolean;
  onUnassign: () => void;
  onSetLoadType: (lt: string) => void;
  onSetOrder: (ord: number) => void;
}) {
  const [ordEdit, setOrdEdit] = useState(false);
  const [ordVal, setOrdVal] = useState(String(st.ORD ?? ""));

  const timeWindow = (() => {
    const f = fmtTime(st.TIME_FROM);
    const t = fmtTime(st.TIME_TO);
    if (f && t) return `${f}–${t}`;
    if (f) return `от ${f}`;
    return "—";
  })();

  function commitOrder() {
    setOrdEdit(false);
    const n = parseInt(ordVal, 10);
    if (!isNaN(n) && n !== st.ORD) onSetOrder(n);
    else setOrdVal(String(st.ORD ?? ""));
  }

  return (
    <div className="dispatch-st-task-row">
      {/* Порядок — кликабельный для редактирования */}
      <span className="dispatch-st-ord" title="Изменить порядок">
        {ordEdit ? (
          <input
            className="dispatch-ord-input"
            type="number"
            min={0}
            value={ordVal}
            autoFocus
            onChange={e => setOrdVal(e.target.value)}
            onBlur={commitOrder}
            onKeyDown={e => { if (e.key === "Enter") commitOrder(); if (e.key === "Escape") { setOrdEdit(false); setOrdVal(String(st.ORD ?? "")); } }}
            onClick={e => e.stopPropagation()}
          />
        ) : (
          <span
            className="dispatch-ord-val"
            onClick={() => { if (!disabled) setOrdEdit(true); }}
            title={disabled ? "" : "Нажмите для изменения порядка"}
          >
            {st.ORD ?? "—"}
          </span>
        )}
      </span>

      <span className="dispatch-st-num">{st.ST_NUMBER}</span>
      <span className="dispatch-st-region">
        {st.REGION || st.ADDR || "—"}
        {st.RAION && <span className="dispatch-st-raion-sm"> · {st.RAION}</span>}
      </span>
      <span className="dispatch-st-zone">{st.ZONE || "—"}</span>
      <span className="dispatch-st-window" title="Временное окно доставки">{timeWindow}</span>
      <span className="dispatch-st-pall">{st.PALLETS_COUNT} пал</span>
      <span className="dispatch-st-wt">{st.WEIGHT_KG.toFixed(0)} кг</span>

      {/* Тип погрузки */}
      <span className="dispatch-st-loadtype">
        {disabled ? (
          <LoadTypeBadge value={st.LOAD_TYPE} />
        ) : (
          <select
            className="dispatch-loadtype-select"
            value={st.LOAD_TYPE ?? ""}
            onChange={e => onSetLoadType(e.target.value)}
            title="Способ погрузки"
          >
            <option value="">—</option>
            <option value="Г">Г</option>
            <option value="П">П</option>
          </select>
        )}
      </span>

      <button
        className="dispatch-unassign-btn"
        title="Снять СТ с рейса"
        disabled={disabled}
        onClick={onUnassign}
      >
        ✕
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function MetaField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="dispatch-meta-field">
      <span className="dispatch-meta-label">{label}</span>
      <div className="dispatch-meta-value">{children}</div>
    </div>
  );
}

function LoadTypeBadge({ value }: { value: string | null }) {
  if (!value) return <span className="dispatch-lt-empty">—</span>;
  return (
    <span className={`dispatch-lt-badge dispatch-lt-${value.toLowerCase()}`}>{value}</span>
  );
}

function VerifyPill({ perc }: { perc: number }) {
  const cls = perc >= 100 ? "done" : perc >= 50 ? "partial" : "low";
  return (
    <span className={`dispatch-verify-pill dispatch-verify-${cls}`} title={`Сборка: ${perc}%`}>
      {perc}%
    </span>
  );
}

function ReadinessBar({ perc, unready }: { perc: number; unready: number | null | undefined }) {
  if (perc === null || perc === undefined) return null;
  const cls = perc >= 100 ? "done" : perc > 0 ? "partial" : "zero";
  return (
    <div className="dispatch-readiness">
      <div className="dispatch-readiness-track">
        <div className={`dispatch-readiness-fill dispatch-readiness-${cls}`} style={{ width: `${Math.min(perc, 100)}%` }} />
      </div>
      <span className="dispatch-readiness-label">
        {perc >= 100 ? "Собран" : `${perc}%${unready ? ` (−${unready})` : ""}`}
      </span>
    </div>
  );
}

function CreateTaskDialog({
  filterDate,
  transportTypes,
  onConfirm,
  onClose,
}: {
  filterDate: string;
  transportTypes: TransportType[];
  onConfirm: (transtype: string, date: string) => void;
  onClose: () => void;
}) {
  const [transtype, setTranstype] = useState(transportTypes[0]?.TRANSPORTTYPE || "10");
  const [shipDate, setShipDate] = useState(filterDate);

  return (
    <div className="dispatch-dialog-overlay" onClick={onClose}>
      <div className="dispatch-dialog" onClick={e => e.stopPropagation()}>
        <h3>Создать рейс</h3>
        <label className="dispatch-dialog-field">
          <span>Тип транспорта</span>
          <select value={transtype} onChange={e => setTranstype(e.target.value)}>
            {transportTypes.map(t => (
              <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>
                {t.TRANSPORTTYPE}{t.NAME ? ` — ${t.NAME}` : ""}
              </option>
            ))}
            {transportTypes.length === 0 && <option value="10">10</option>}
          </select>
        </label>
        <label className="dispatch-dialog-field">
          <span>Дата отгрузки</span>
          <input type="date" value={shipDate} onChange={e => setShipDate(e.target.value)} />
        </label>
        <div className="dispatch-dialog-actions">
          <button className="dispatch-new-btn" onClick={() => onConfirm(transtype, shipDate)}>
            Создать
          </button>
          <button className="dispatch-cancel-edit-btn" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function condClass(cond: string | null): string {
  if (!cond) return "new";
  if (cond === "Отгружен") return "closed";
  if (cond === "Отменён") return "cancelled";
  return "planned";
}

// ---------------------------------------------------------------------------
// Demo data (when API is unavailable)
// ---------------------------------------------------------------------------

function demoTasks(date: string): TransportTask[] {
  return [
    {
      ID: 1247, TRANSPORT: "Т368ХН", TRANSTYPE: "10", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: 6, VODITEL_NAME: "Сташков Иван Викторович",
      VODITEL_TEL: "8-952-74-109-09", TK_NAME: null, IS_OWN_DRIVER: 1,
      PRIMECHANIE: null, DOCK: "Д1", SHIPMENT_TIME: null,
      TEMP_REGION: "Москва, Химки, Лобня", PRICE: null,
      PALLET_COUNT: 12, ST_COUNT: 3, DELETED: 0,
      READY_PERC: 67, UNREADY_COUNT: 4,
    },
    {
      ID: 1248, TRANSPORT: "В703РО", TRANSTYPE: "15", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: 7, VODITEL_NAME: "Петров Алексей",
      VODITEL_TEL: null, TK_NAME: "ООО Транс-Авто", IS_OWN_DRIVER: 0,
      PRIMECHANIE: null, DOCK: "Д2", SHIPMENT_TIME: null,
      TEMP_REGION: "Красногорск", PRICE: null,
      PALLET_COUNT: 8, ST_COUNT: 2, DELETED: 0,
      READY_PERC: 100, UNREADY_COUNT: 0,
    },
    {
      ID: 1249, TRANSPORT: null, TRANSTYPE: "10", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: null, VODITEL_NAME: null,
      VODITEL_TEL: null, TK_NAME: null, IS_OWN_DRIVER: null,
      PRIMECHANIE: null, DOCK: null, SHIPMENT_TIME: null,
      TEMP_REGION: null, PRICE: null,
      PALLET_COUNT: 0, ST_COUNT: 0, DELETED: 0,
      READY_PERC: 0, UNREADY_COUNT: 0,
    },
  ];
}

function demoAvailableSts(date: string): AvailableSt[] {
  return [
    { ST_NUMBER: "0441", ADDR: "Москва, ул. Ленина 5", REGION: "Москва", RAION: "ЦАО", PALLETS_COUNT: 3, WEIGHT_KG: 450, VOLUME_M3: 2.1, STDATE: date, TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, NAPR: null, VERIFY_PERC: 100 },
    { ST_NUMBER: "0442", ADDR: "Красногорск, пр. Мира 12", REGION: "Красногорск", RAION: null, PALLETS_COUNT: 5, WEIGHT_KG: 780, VOLUME_M3: 3.8, STDATE: date, TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, NAPR: null, VERIFY_PERC: 75 },
    { ST_NUMBER: "0443", ADDR: "Химки, ул. Победы 3", REGION: "Химки", RAION: null, PALLETS_COUNT: 6, WEIGHT_KG: 890, VOLUME_M3: 4.2, STDATE: date, TRANSTASK_ID: null, TRANSPORT_TYPE: "15", NEEDS_HYDRO_BOARD: 1, NAPR: null, VERIFY_PERC: 0 },
    { ST_NUMBER: "0445", ADDR: "Лобня, ул. Свободы 8", REGION: "Лобня", RAION: null, PALLETS_COUNT: 4, WEIGHT_KG: 620, VOLUME_M3: 3.0, STDATE: date, TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, NAPR: null, VERIFY_PERC: 50 },
  ];
}
