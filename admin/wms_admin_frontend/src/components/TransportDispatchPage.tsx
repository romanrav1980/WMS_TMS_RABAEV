import { Fragment, useCallback, useEffect, useRef, useState } from "react";

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
  REGIONS: string | null;
  TEMP_WEIGHT: number | null;
  PRICE: number | null;
  VOLUME_M3: number | null;
  LOGIST: string | null;
  PAY_ORDER_ID: number | null;
  PALLET_COUNT: number;
  ST_COUNT: number;
  DELETED: number | null;
  READY_PERC: number | null;
  UNREADY_COUNT: number | null;
};

type TaskUpdateDraft = {
  transport?: string | null;
  voditel_id?: number | null;
  dock?: string | null;
  shipment_time?: string | null;
  shipment_date?: string | null;
  transtype?: string | null;
  primechanie?: string | null;
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
  WARE_ID: number | null;
  VERIFY_PERC: number | null;
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
  DATE_LOAD: string | null;
  TRANSTASK_ID: number | null;
  TRANSPORT_TYPE: string | null;
  NEEDS_HYDRO_BOARD: number;
  STOL: number;
  PRIM1: string | null;
  NAPR: string | null;
  WARE_ID: number;
  VERIFY_PERC: number | null;
  SUGAR: number;
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

type TransportCluster = {
  RAION: string;
  ST_COUNT: number;
  PALLET_COUNT: number;
  WEIGHT_KG: number;
  VOLUME_M3: number;
  STS: AvailableSt[];
};

type StPalletRow = {
  PALLET_UID: string;
  ZONE: string | null;
  LOAD_TYPE: string | null;
  ORD: number | null;
  ARTICUL: string | null;
  ORDER_WEIGHT: number;
  PACK_COUNT: number;
  ROW_VOLUME_M3: number;
};

type BillingOrder = {
  order_id: number;
  num: string | null;
  company: string | null;
  date_of_order: string | null;
  date_from: string | null;
  date_to: string | null;
  closed: number;
  payed: number;
  task_count?: number | null;
  total_price?: number | null;
  num_plat?: string | null;
};

type BillingOrderTask = {
  tt_id: number;
  transport: string | null;
  status: string | null;
  price: number;
  shipment_date: string | null;
};

// ---------------------------------------------------------------------------
// Config / API
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
    try { const b = await res.json(); detail = b?.detail || detail; } catch { /* */ }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

function todayIso(): string { return new Date().toISOString().slice(0, 10); }
function fmtDate(s: string | null): string { return s ? s.slice(0, 10) : "—"; }
function fmtTime(s: string | null): string {
  if (!s) return "";
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

  const [viewMode, setViewMode] = useState<"flat" | "clusters">("flat");
  const [clusters, setClusters] = useState<TransportCluster[]>([]);
  const [expandedRaions, setExpandedRaions] = useState<Set<string>>(new Set());

  // Filters
  const [addrMask, setAddrMask] = useState("");
  const [stMask, setStMask] = useState("");
  const [stMaskExclude, setStMaskExclude] = useState(false);
  const [assembledOnly, setAssembledOnly] = useState(false);
  const [notAssembledOnly, setNotAssembledOnly] = useState(false);
  const [unassignedOnly, setUnassignedOnly] = useState(true);
  const [dateTo, setDateTo] = useState<string>("");
  const [maxWeightKg, setMaxWeightKg] = useState<number | null>(null);
  const [maxVolM3, setMaxVolM3] = useState<number | null>(null);
  const [trTypeFilter, setTrTypeFilter] = useState("");
  const [articulFilter, setArticulFilter] = useState("");

  const debouncedAddrMask = useDebounce(addrMask, 300);
  const debouncedStMask = useDebounce(stMask, 300);
  const debouncedMaxWeight = useDebounce(maxWeightKg, 500);
  const debouncedMaxVol = useDebounce(maxVolM3, 500);
  const debouncedArticul = useDebounce(articulFilter, 400);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editDraft, setEditDraft] = useState<TaskUpdateDraft>({});
  const editRef = useRef(editDraft);
  editRef.current = editDraft;
  const lastClickedIdxRef = useRef<number | null>(null);

  const [editingTranstypeId, setEditingTranstypeId] = useState<number | null>(null);
  const [palletStNum, setPalletStNum] = useState<string | null>(null);
  const [stPallets, setStPallets] = useState<StPalletRow[]>([]);
  const [palletLoading, setPalletLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"tasks" | "routes" | "billing">("tasks");
  const [routeShipDate, setRouteShipDate] = useState(todayIso());
  const [routeTaskId, setRouteTaskId] = useState("");
  const [routeCarMask, setRouteCarMask] = useState("");
  const [routeCompanyMask, setRouteCompanyMask] = useState("");
  const [routeDateTo, setRouteDateTo] = useState("");
  const [routeNoPayments, setRouteNoPayments] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [billingDialog, setBillingDialog] = useState(false);
  const [openingBilling, setOpeningBilling] = useState(false);
  const [billingOrder, setBillingOrder] = useState<BillingOrder | null>(null);
  const [billingActionLoading, setBillingActionLoading] = useState(false);

  // Price management (Sprint 18)
  const [priceRecalcLoading, setPriceRecalcLoading] = useState(false);
  const [priceLoading, setPriceLoading] = useState(false);
  const [manualPrice, setManualPrice] = useState("");

  // Billing registry (Sprint 17)
  const [billingOrders, setBillingOrders] = useState<BillingOrder[]>([]);
  const [billingLoading, setBillingLoading] = useState(false);
  const [billingDateFrom, setBillingDateFrom] = useState(() => {
    const d = new Date(); d.setDate(1); return d.toISOString().slice(0, 10);
  });
  const [billingDateTo, setBillingDateTo] = useState(todayIso());
  const [billingCompany, setBillingCompany] = useState("");
  const [billingStatus, setBillingStatus] = useState<"all" | "open" | "closed" | "paid">("all");

  // Billing order detail panel (Sprint 23)
  const [selectedBillingOrder, setSelectedBillingOrder] = useState<BillingOrder | null>(null);
  const [billingOrderTasks, setBillingOrderTasks] = useState<BillingOrderTask[]>([]);
  const [billingOrderTasksLoading, setBillingOrderTasksLoading] = useState(false);
  const debouncedRouteTaskId = useDebounce(routeTaskId, 300);
  const debouncedRouteCarMask = useDebounce(routeCarMask, 300);
  const debouncedRouteCompany = useDebounce(routeCompanyMask, 300);

  // ------------------------------------------------------------------
  // Load reference data once
  // ------------------------------------------------------------------
  useEffect(() => {
    Promise.all([
      apiFetch<Vehicle[]>("/api/admin/transport/vehicles"),
      apiFetch<Driver[]>("/api/admin/transport/drivers"),
      apiFetch<TransportType[]>("/api/admin/transport/types"),
    ]).then(([v, d, t]) => { setVehicles(v); setDrivers(d); setTransportTypes(t); })
      .catch(() => {
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
  // Load tasks
  // ------------------------------------------------------------------
  const loadTasks = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      let url: string;
      if (activeTab === "routes") {
        const p = new URLSearchParams({ include_readiness: "true" });
        if (routeShipDate) p.set("shipment_date", routeShipDate);
        if (debouncedRouteTaskId) p.set("task_id", debouncedRouteTaskId);
        if (debouncedRouteCarMask) p.set("transport_mask", debouncedRouteCarMask);
        if (debouncedRouteCompany) p.set("company_mask", debouncedRouteCompany);
        if (routeDateTo) p.set("date_to", routeDateTo);
        if (routeNoPayments) p.set("no_payments_only", "true");
        url = `/api/admin/transport/tasks?${p}`;
      } else {
        url = `/api/admin/transport/tasks?shipment_date=${filterDate}&include_readiness=true`;
      }
      const data = await apiFetch<TransportTask[]>(url);
      setTasks(data);
    } catch (e) {
      setError(String(e));
      setTasks(demoTasks(filterDate));
    } finally { setLoading(false); }
  }, [activeTab, filterDate, routeShipDate, debouncedRouteTaskId, debouncedRouteCarMask,
      debouncedRouteCompany, routeDateTo, routeNoPayments]);

  useEffect(() => { loadTasks(); }, [loadTasks]);

  // ------------------------------------------------------------------
  // Load billing orders (Sprint 17)
  // ------------------------------------------------------------------
  const loadBillingOrders = useCallback(async () => {
    setBillingLoading(true);
    try {
      const p = new URLSearchParams();
      if (billingDateFrom) p.set("date_from", billingDateFrom);
      if (billingDateTo)   p.set("date_to", billingDateTo);
      if (billingCompany)  p.set("company", billingCompany);
      if (billingStatus === "open")   { p.set("closed", "0"); p.set("payed", "0"); }
      if (billingStatus === "closed") { p.set("closed", "1"); p.set("payed", "0"); }
      if (billingStatus === "paid")   { p.set("payed", "1"); }
      const data = await apiFetch<BillingOrder[]>(`/api/admin/transport/billing/orders?${p}`);
      setBillingOrders(data);
    } catch { setBillingOrders([]); } finally { setBillingLoading(false); }
  }, [billingDateFrom, billingDateTo, billingCompany, billingStatus]);

  useEffect(() => {
    if (activeTab === "billing") loadBillingOrders();
  }, [activeTab, loadBillingOrders]);

  // ------------------------------------------------------------------
  // Load billing order detail tasks (Sprint 23)
  // ------------------------------------------------------------------
  async function handleBillingOrderSelect(order: BillingOrder) {
    if (selectedBillingOrder?.order_id === order.order_id) {
      setSelectedBillingOrder(null);
      setBillingOrderTasks([]);
      return;
    }
    setSelectedBillingOrder(order);
    setBillingOrderTasksLoading(true);
    try {
      const data = await apiFetch<BillingOrderTask[]>(
        `/api/admin/transport/billing/orders/${order.order_id}/tasks`
      );
      setBillingOrderTasks(data);
    } catch { setBillingOrderTasks([]); } finally { setBillingOrderTasksLoading(false); }
  }

  // ------------------------------------------------------------------
  // Load available STs
  // ------------------------------------------------------------------
  const loadAvailableSts = useCallback(async () => {
    try {
      const params = new URLSearchParams({ stdate: stDate });
      if (!unassignedOnly) params.set("unassigned_only", "false");
      if (dateTo) params.set("date_to", dateTo);
      if (debouncedAddrMask) params.set("addr_mask", debouncedAddrMask);
      if (debouncedStMask) {
        params.set("st_mask", debouncedStMask);
        if (stMaskExclude) params.set("st_mask_exclude", "true");
      }
      if (trTypeFilter) params.set("transport_type", trTypeFilter);
      if (assembledOnly) params.set("assembled_only", "true");
      if (notAssembledOnly) params.set("not_assembled_only", "true");
      if (debouncedMaxWeight != null) params.set("max_weight_kg", String(debouncedMaxWeight));
      if (debouncedMaxVol != null) params.set("max_volume_m3", String(debouncedMaxVol));
      if (debouncedArticul) params.set("articul", debouncedArticul);
      const data = await apiFetch<AvailableSt[]>(`/api/admin/transport/available-sts?${params}`);
      setAvailableSts(data);
    } catch {
      setAvailableSts(demoAvailableSts(stDate));
    }
  }, [stDate, dateTo, debouncedAddrMask, debouncedStMask, stMaskExclude, trTypeFilter,
      assembledOnly, notAssembledOnly, unassignedOnly, debouncedMaxWeight, debouncedMaxVol, debouncedArticul]);

  useEffect(() => { loadAvailableSts(); }, [loadAvailableSts]);

  // ------------------------------------------------------------------
  // Load clusters
  // ------------------------------------------------------------------
  const loadClusters = useCallback(async () => {
    try {
      const params = new URLSearchParams({ stdate: stDate });
      const data = await apiFetch<TransportCluster[]>(`/api/admin/transport/clusters?${params}`);
      setClusters(data);
    } catch {
      setClusters(demoClusters(stDate));
    }
  }, [stDate]);

  useEffect(() => {
    if (viewMode === "clusters") loadClusters();
  }, [viewMode, loadClusters]);

  // ------------------------------------------------------------------
  // Select task
  // ------------------------------------------------------------------
  async function selectTask(task: TransportTask) {
    setSelectedTask(task);
    setEditMode(false);
    setNoteText(task.PRIMECHANIE ?? "");
    setPalletStNum(null);
    setStPallets([]);
    setBillingOrder(null);
    try {
      const data = await apiFetch<TaskSt[]>(`/api/admin/transport/tasks/${task.ID}/sts`);
      setTaskSts(data);
    } catch { setTaskSts([]); }
    if (task.PAY_ORDER_ID) {
      try {
        const bo = await apiFetch<BillingOrder>(
          `/api/admin/transport/billing/orders/${task.PAY_ORDER_ID}`
        );
        setBillingOrder(bo);
      } catch { setBillingOrder(null); }
    }
  }

  async function handleRecalculatePrice() {
    if (!selectedTask) return;
    setPriceRecalcLoading(true);
    try {
      const res = await apiFetch<{ task_id: number; price: number }>(
        `/api/admin/transport/tasks/${selectedTask.ID}/recalculate-price`,
        { method: "POST" }
      );
      setSelectedTask(prev => prev ? { ...prev, PRICE: res.price } : prev);
      setTasks(prev => prev.map(t => t.ID === selectedTask.ID ? { ...t, PRICE: res.price } : t));
    } catch { /* ignore */ } finally { setPriceRecalcLoading(false); }
  }

  async function handleSetPrice(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedTask || !manualPrice) return;
    const price = parseFloat(manualPrice);
    if (isNaN(price) || price < 0) return;
    setPriceLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/price`, {
        method: "PATCH",
        body: JSON.stringify({ price }),
      });
      setSelectedTask(prev => prev ? { ...prev, PRICE: price } : prev);
      setTasks(prev => prev.map(t => t.ID === selectedTask.ID ? { ...t, PRICE: price } : t));
      setManualPrice("");
    } catch { /* ignore */ } finally { setPriceLoading(false); }
  }

  async function handleShowPallets(stNum: string) {
    if (palletStNum === stNum) { setPalletStNum(null); return; }
    setPalletStNum(stNum);
    setPalletLoading(true);
    try {
      const data = await apiFetch<StPalletRow[]>(
        `/api/admin/transport/sts/${encodeURIComponent(stNum)}/pallets`
      );
      setStPallets(data);
    } catch { setStPallets([]); } finally { setPalletLoading(false); }
  }

  // ------------------------------------------------------------------
  // Assign STs
  // ------------------------------------------------------------------
  async function handleAssign() {
    if (!selectedTask || selectedStNums.size === 0) return;
    setLoading(true);
    try {
      const result = await apiFetch<{ assigned: number; warnings: string[] }>(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts`,
        { method: "POST", body: JSON.stringify({ st_numbers: Array.from(selectedStNums) }) }
      );
      if (result.warnings.length > 0) setError(result.warnings.join("; "));
      setSelectedStNums(new Set());
      const reloads: Promise<void>[] = [selectTask(selectedTask), loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  // ------------------------------------------------------------------
  // Unassign ST
  // ------------------------------------------------------------------
  async function handleUnassign(stNumber: string) {
    if (!selectedTask) return;
    setLoading(true);
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}`,
        { method: "DELETE" }
      );
      const reloads: Promise<void>[] = [selectTask(selectedTask), loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleSetLoadType(stNumber: string, loadType: string) {
    if (!selectedTask) return;
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}/load-type`,
        { method: "PATCH", body: JSON.stringify({ load_type: loadType }) }
      );
      setTaskSts(prev => prev.map(s => s.ST_NUMBER === stNumber ? { ...s, LOAD_TYPE: loadType || null } : s));
    } catch (e) { setError(String(e)); }
  }

  async function handleSetOrder(stNumber: string, ord: number) {
    if (!selectedTask) return;
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(stNumber)}/order`,
        { method: "PATCH", body: JSON.stringify({ ord }) }
      );
      setTaskSts(prev => prev.map(s => s.ST_NUMBER === stNumber ? { ...s, ORD: ord } : s));
    } catch (e) { setError(String(e)); }
  }

  async function handleCreate(params: {
    transtype: string; shipment_date: string;
    vehicle: string; driver_id: number | null; dock: string;
  }) {
    setLoading(true);
    try {
      const res = await apiFetch<{ task_id: number }>(
        "/api/admin/transport/tasks",
        { method: "POST", body: JSON.stringify({ transtype: params.transtype, shipment_date: params.shipment_date }) }
      );
      const taskId = res.task_id;
      if (params.vehicle || params.driver_id || params.dock) {
        await apiFetch(`/api/admin/transport/tasks/${taskId}`, {
          method: "PATCH",
          body: JSON.stringify({ transport: params.vehicle || null, voditel_id: params.driver_id, dock: params.dock || null }),
        });
      }
      if (selectedStNums.size > 0) {
        const result = await apiFetch<{ assigned: number; warnings: string[] }>(
          `/api/admin/transport/tasks/${taskId}/sts`,
          { method: "POST", body: JSON.stringify({ st_numbers: Array.from(selectedStNums) }) }
        );
        if (result.warnings.length > 0) setError(result.warnings.join("; "));
        setSelectedStNums(new Set());
      }
      setCreateDialog(false);
      const reloads: Promise<unknown>[] = [loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
      const newTask = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${taskId}`);
      selectTask(newTask);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

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
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleClose() {
    if (!selectedTask) return;
    if (!confirm(`Закрыть рейс #${selectedTask.ID} как отгруженный?`)) return;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/close`, { method: "POST" });
      setSelectedTask(null); setTaskSts([]);
      await loadTasks();
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleCancel() {
    if (!selectedTask) return;
    if (!confirm(`Отменить рейс #${selectedTask.ID}? Это действие необратимо.`)) return;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/cancel`, { method: "POST" });
      setSelectedTask(null); setTaskSts([]);
      await loadTasks();
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleUpdateTranstype(taskId: number, transtype: string) {
    setEditingTranstypeId(null);
    try {
      await apiFetch(`/api/admin/transport/tasks/${taskId}`, {
        method: "PATCH",
        body: JSON.stringify({ transtype: transtype || null }),
      });
      setTasks(prev => prev.map(t => t.ID === taskId ? { ...t, TRANSTYPE: transtype || null } : t));
      if (selectedTask?.ID === taskId) setSelectedTask(prev => prev ? { ...prev, TRANSTYPE: transtype || null } : prev);
    } catch (e) { setError(String(e)); }
  }

  async function handleSaveNote() {
    if (!selectedTask) return;
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}`, {
        method: "PATCH",
        body: JSON.stringify({ primechanie: noteText }),
      });
      setSelectedTask(prev => prev ? { ...prev, PRIMECHANIE: noteText } : prev);
      setTasks(prev => prev.map(t => t.ID === selectedTask.ID ? { ...t, PRIMECHANIE: noteText } : t));
    } catch (e) { setError(String(e)); }
  }

  async function handleOpenBilling(existingOrderId: number | null) {
    if (!selectedTask) return;
    setOpeningBilling(true);
    try {
      let order: BillingOrder;
      if (existingOrderId) {
        await apiFetch(`/api/admin/transport/billing/orders/${existingOrderId}/tasks`, {
          method: "POST",
          body: JSON.stringify({ tt_ids: [selectedTask.ID] }),
        });
        order = await apiFetch<BillingOrder>(
          `/api/admin/transport/billing/orders/${existingOrderId}`
        );
      } else {
        order = await apiFetch<BillingOrder>(
          `/api/admin/transport/tasks/${selectedTask.ID}/billing/open`,
          { method: "POST" }
        );
      }
      const updated = { ...selectedTask, PAY_ORDER_ID: order.order_id };
      setSelectedTask(updated);
      setTasks(prev => prev.map(t => t.ID === updated.ID ? updated : t));
      setBillingOrder(order);
      setBillingDialog(false);
    } catch (e) { setError(String(e)); } finally { setOpeningBilling(false); }
  }

  async function handleBillingClose() {
    if (!billingOrder) return;
    if (!confirm(`Закрыть счёт ${billingOrder.num ?? `#${billingOrder.order_id}`}?`)) return;
    setBillingActionLoading(true);
    try {
      const updated = await apiFetch<BillingOrder>(
        `/api/admin/transport/billing/orders/${billingOrder.order_id}/close`,
        { method: "PATCH" }
      );
      setBillingOrder(updated);
    } catch (e) { setError(String(e)); } finally { setBillingActionLoading(false); }
  }

  async function handleBillingPay() {
    if (!billingOrder) return;
    if (!confirm(`Отметить счёт ${billingOrder.num ?? `#${billingOrder.order_id}`} как оплаченный?`)) return;
    setBillingActionLoading(true);
    try {
      const updated = await apiFetch<BillingOrder>(
        `/api/admin/transport/billing/orders/${billingOrder.order_id}/pay`,
        { method: "PATCH" }
      );
      setBillingOrder(updated);
    } catch (e) { setError(String(e)); } finally { setBillingActionLoading(false); }
  }

  // ------------------------------------------------------------------
  // Toggle helpers
  // ------------------------------------------------------------------
  function toggleSt(stNum: string) {
    setSelectedStNums(prev => {
      const next = new Set(prev);
      next.has(stNum) ? next.delete(stNum) : next.add(stNum);
      return next;
    });
  }

  function handleStToggle(stNum: string, idx: number) {
    lastClickedIdxRef.current = idx;
    toggleSt(stNum);
  }

  function handleShiftClick(idx: number) {
    const last = lastClickedIdxRef.current;
    if (last === null) { handleStToggle(availableSts[idx].ST_NUMBER, idx); return; }
    const [a, b] = [Math.min(last, idx), Math.max(last, idx)];
    const range = availableSts.slice(a, b + 1).map(s => s.ST_NUMBER);
    setSelectedStNums(prev => {
      const next = new Set(prev);
      const allSel = range.every(n => next.has(n));
      range.forEach(n => allSel ? next.delete(n) : next.add(n));
      return next;
    });
    lastClickedIdxRef.current = idx;
  }

  function handleSelectByField(field: "RAION" | "REGION", value: string | null) {
    if (!value) return;
    setSelectedStNums(prev => {
      const next = new Set(prev);
      availableSts.filter(s => s[field] === value).forEach(s => next.add(s.ST_NUMBER));
      return next;
    });
  }

  function toggleRaion(raion: string) {
    setExpandedRaions(prev => {
      const next = new Set(prev);
      next.has(raion) ? next.delete(raion) : next.add(raion);
      return next;
    });
  }

  // ------------------------------------------------------------------
  // PMV counters
  // ------------------------------------------------------------------
  const selSts = availableSts.filter(s => selectedStNums.has(s.ST_NUMBER));
  const selP = selSts.reduce((s, x) => s + (x.PALLETS_COUNT || 0), 0);
  const selM = selSts.reduce((s, x) => s + (x.WEIGHT_KG || 0), 0);
  const selV = selSts.reduce((s, x) => s + (x.VOLUME_M3 || 0), 0);
  const tripP = taskSts.reduce((s, x) => s + (x.PALLETS_COUNT || 0), 0);
  const tripM = taskSts.reduce((s, x) => s + (x.WEIGHT_KG || 0), 0);

  const selectedVehicle = vehicles.find(v => v.NUM === selectedTask?.TRANSPORT);

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  return (
    <div className="dispatch-shell">
      {/* Topbar */}
      <header className="dispatch-topbar">
        <button className="dispatch-back" onClick={onBack}>◄</button>
        <div className="dispatch-title">
          <h1>Диспетчер отгрузки</h1>
          <span className="dispatch-subtitle">Ручное планирование рейсов</span>
        </div>
        {loading && <span className="dispatch-spinner">●</span>}
        {error && (
          <span className="dispatch-error" title={error} onClick={() => setError(null)} style={{ cursor: "pointer" }}>
            ⚠ {error.slice(0, 120)}
          </span>
        )}
      </header>

      <div className="dispatch-workspace">
        {/* ============================================================
            CENTER
            ============================================================ */}
        <div className="dispatch-center">

          {/* ---- Tab bar ---- */}
          <div className="dispatch-tabs">
            <button
              className={`dispatch-tab${activeTab === "tasks" ? " active" : ""}`}
              onClick={() => { setActiveTab("tasks"); setSelectedTask(null); setTaskSts([]); }}>
              Заявки
            </button>
            <button
              className={`dispatch-tab${activeTab === "routes" ? " active" : ""}`}
              onClick={() => { setActiveTab("routes"); setSelectedTask(null); setTaskSts([]); }}>
              Маршруты
            </button>
            <button
              className={`dispatch-tab${activeTab === "billing" ? " active" : ""}`}
              onClick={() => { setActiveTab("billing"); setSelectedTask(null); setTaskSts([]); }}>
              Биллинг
            </button>
          </div>

          {activeTab === "tasks" && <>

          {/* ---- ST toolbar ---- */}
          <div className="dispatch-st-toolbar">
            <label className="dispatch-tbl-label">
              Дата СТ:
              <input type="date" value={stDate}
                onChange={e => { setStDate(e.target.value); setSelectedStNums(new Set()); }} />
            </label>
            <div className="dispatch-vmtoggle">
              <button className={viewMode === "flat" ? "active" : ""} onClick={() => setViewMode("flat")}>По СТ</button>
              <button className={viewMode === "clusters" ? "active" : ""} onClick={() => setViewMode("clusters")}>По районам</button>
            </div>
            <span className="dispatch-pmv">
              P={selP}&nbsp; M={selM.toFixed(0)}&nbsp; V={selV.toFixed(2)}
              {selectedStNums.size > 0 && <b>&nbsp;({selectedStNums.size} выбр.)</b>}
            </span>
            {selectedStNums.size > 0 && selectedTask && (
              <button className="dispatch-add-btn" onClick={handleAssign} disabled={loading}>
                Добавить в рейс #{selectedTask.ID}
              </button>
            )}
            {selectedStNums.size > 0 && !selectedTask && (
              <span className="dispatch-hint">↓ Выберите рейс</span>
            )}
            <button className="dispatch-refresh-btn"
              onClick={() => { loadAvailableSts(); if (viewMode === "clusters") loadClusters(); }}
              title="Обновить список СТ">⟳</button>
            <span className="dispatch-tcount">{availableSts.length} СТ</span>
          </div>

          {/* ---- Available STs table ---- */}
          <div className="dispatch-st-section">
            <table className="dispatch-grid">
              <thead>
                <tr>
                  <th style={{ width: 22 }}></th>
                  <th title="Склад">Скл</th>
                  <th>Пал.</th>
                  <th>Вес</th>
                  <th>Объём</th>
                  <th>Регион</th>
                  <th>Адрес</th>
                  <th>СТ №</th>
                  <th>В рейсе</th>
                  <th>Дата СТ</th>
                  <th>%</th>
                  <th>Район</th>
                  <th>Тип ТС</th>
                  <th title="Стол-лифт">Стол</th>
                  <th title="Примечание">Прим.</th>
                  <th title="Сахар">Сах</th>
                </tr>
              </thead>
              <tbody>
                {viewMode === "flat" && (
                  availableSts.length === 0
                    ? <tr><td colSpan={16} className="dispatch-grid-empty">Нет свободных СТ по текущим фильтрам</td></tr>
                    : availableSts.map((st, idx) => (
                        <AvailableStRow key={st.ST_NUMBER} st={st} idx={idx}
                          checked={selectedStNums.has(st.ST_NUMBER)}
                          onToggle={() => handleStToggle(st.ST_NUMBER, idx)}
                          onShiftClick={handleShiftClick}
                          onSelectByField={handleSelectByField} />
                      ))
                )}
                {viewMode === "clusters" && (
                  clusters.length === 0
                    ? <tr><td colSpan={16} className="dispatch-grid-empty">Нет свободных СТ</td></tr>
                    : clusters.map(cluster => (
                        <ClusterGroup
                          key={cluster.RAION}
                          cluster={cluster}
                          expanded={expandedRaions.has(cluster.RAION)}
                          onToggle={() => toggleRaion(cluster.RAION)}
                          selectedNums={selectedStNums}
                          onToggleSt={toggleSt}
                        />
                      ))
                )}
              </tbody>
            </table>
          </div>

          {/* ---- Trips table ---- */}
          <div className="dispatch-trips-section">
            <div className="dispatch-trips-toolbar">
              <b>Рейсы на</b>
              <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
              <button className="dispatch-new-btn" onClick={() => setCreateDialog(true)}>
                {selectedStNums.size > 0 ? `+ Создать маршрут (${selectedStNums.size})` : "+ Создать маршрут"}
              </button>
              <button className="dispatch-refresh-btn" onClick={loadTasks} title="Обновить рейсы">⟳</button>
              <span className="dispatch-tcount">{tasks.length} рейс(ов)</span>
            </div>
            <div className="dispatch-trips-table-wrap">
              <table className="dispatch-grid">
                <thead>
                  <tr>
                    <th>Время</th><th>ID</th><th>СТ</th><th>Пал.</th>
                    <th>Тип</th><th>Машина</th><th>Дата</th><th>Водитель</th>
                    <th>Докст.</th><th>Районы</th><th>Цена</th><th>Статус</th><th>%</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.length === 0
                    ? <tr><td colSpan={13} className="dispatch-grid-empty">Нет рейсов на {filterDate}. Нажмите «+ Создать рейс».</td></tr>
                    : tasks.map(task => (
                        <tr key={task.ID}
                          className={["dispatch-gr",
                            selectedTask?.ID === task.ID ? "selected" : "",
                            task.CONDITION === "Отгружен" ? "grid-closed" : "",
                          ].filter(Boolean).join(" ")}
                          onClick={() => selectTask(task)}>
                          <td>{fmtTime(task.SHIPMENT_TIME) || "—"}</td>
                          <td><b>#{task.ID}</b></td>
                          <td className="num-r">{task.ST_COUNT}</td>
                          <td className="num-r">{task.PALLET_COUNT}</td>
                          <td>{task.TRANSTYPE ?? "—"}</td>
                          <td>{task.TRANSPORT ?? "—"}</td>
                          <td>{fmtDate(task.SHIPMENT_DATE)}</td>
                          <td>
                            {task.VODITEL_NAME ?? "—"}
                            <DriverOwnerBadge isOwn={task.IS_OWN_DRIVER} tkName={task.TK_NAME} />
                          </td>
                          <td>{task.DOCK ?? "—"}</td>
                          <td className="col-flex">{task.TEMP_REGION ?? "—"}</td>
                          <td>{task.PRICE != null ? task.PRICE.toLocaleString("ru-RU") + " ₽" : "—"}</td>
                          <td><span className={`dispatch-cond ${condClass(task.CONDITION)}`}>{task.CONDITION ?? "Новый"}</span></td>
                          <td>{task.READY_PERC != null
                            ? <ReadinessBar perc={task.READY_PERC} unready={task.UNREADY_COUNT} />
                            : "—"}</td>
                        </tr>
                      ))
                  }
                </tbody>
              </table>
            </div>
          </div>

          {/* ---- Trip detail (tasks tab) ---- */}
          {selectedTask ? (
            <div className="dispatch-trip-detail-section">
              <div className="dispatch-trip-detail-hdr">
                <div className="dispatch-trip-title-row">
                  <b>Рейс #{selectedTask.ID}</b>
                  <span className={`dispatch-cond-big ${condClass(selectedTask.CONDITION)}`}>
                    {selectedTask.CONDITION ?? "Новый"}
                  </span>
                  {selectedTask.READY_PERC != null && (
                    <ReadinessBar perc={selectedTask.READY_PERC} unready={selectedTask.UNREADY_COUNT} />
                  )}
                  <span className="dispatch-pmv" style={{ marginLeft: "auto" }}>
                    P={tripP}&nbsp; M={tripM.toFixed(0)}
                  </span>
                  {!editMode
                    ? <button className="dispatch-edit-btn" onClick={() => { setEditMode(true); setEditDraft({}); }}>Редактировать</button>
                    : <>
                        <button className="dispatch-save-btn" onClick={handleSaveEdit} disabled={loading}>Сохранить</button>
                        <button className="dispatch-cancel-edit-btn" onClick={() => setEditMode(false)}>Отмена</button>
                      </>
                  }
                  {selectedTask.CONDITION !== "Отгружен" && <>
                    <button className="dispatch-close-btn"
                      onClick={handleClose} disabled={loading || taskSts.length === 0}>
                      Закрыть рейс
                    </button>
                    <button className="dispatch-cancel-task-btn"
                      onClick={handleCancel}
                      disabled={loading || !!selectedTask.PAY_ORDER_ID}>
                      Отменить
                    </button>
                  </>}
                  {selectedTask.CONDITION === "Отгружен" && (
                    <span className="dispatch-closed-label">Рейс отгружен · только чтение</span>
                  )}
                  {selectedTask.PAY_ORDER_ID
                    ? <span className="billing-badge">💰 Счёт #{selectedTask.PAY_ORDER_ID}</span>
                    : selectedTask.CONDITION === "Отгружен" && selectedTask.IS_OWN_DRIVER === 0 && (
                        <button className="billing-open-btn" onClick={() => setBillingDialog(true)}>
                          Выставить счёт
                        </button>
                      )
                  }
                  {selectedTask.PRICE != null && (
                    <span className="dispatch-price">{selectedTask.PRICE.toLocaleString("ru-RU")} ₽</span>
                  )}
                </div>

                <div className="dispatch-trip-meta-row">
                  <span className="dispatch-trip-ml">Машина:</span>
                  {editMode
                    ? <select className="dispatch-trip-ms"
                        value={editDraft.transport ?? selectedTask.TRANSPORT ?? ""}
                        onChange={e => setEditDraft(d => ({ ...d, transport: e.target.value || null }))}>
                        <option value="">— не выбрана —</option>
                        {vehicles.map(v => (
                          <option key={v.ID} value={v.NUM}>
                            {v.NUM} · {v.MARKA} · {v.TR_TYPE} · {v.PALLETS} пал{v.GIDROBORT ? " · Г" : ""}
                          </option>
                        ))}
                      </select>
                    : <span>{selectedTask.TRANSPORT ?? "—"}{selectedVehicle?.MARKA ? ` · ${selectedVehicle.MARKA}` : ""}</span>
                  }

                  <span className="dispatch-trip-ml">Водитель:</span>
                  {editMode
                    ? <select className="dispatch-trip-ms"
                        value={editDraft.voditel_id ?? selectedTask.VODITEL_ID ?? ""}
                        onChange={e => setEditDraft(d => ({ ...d, voditel_id: e.target.value ? Number(e.target.value) : null }))}>
                        <option value="">— не выбран —</option>
                        {drivers.map(d => (
                          <option key={d.ID} value={d.ID}>
                            {d.FULL_NAME ?? `#${d.ID}`}
                            {d.SOBSTVENNYY === 0 && d.DOVERENNOST_OT ? ` (${d.DOVERENNOST_OT})` : ""}
                          </option>
                        ))}
                      </select>
                    : <span>
                        {selectedTask.VODITEL_NAME ?? "—"}
                        {selectedTask.VODITEL_TEL ? ` · ${selectedTask.VODITEL_TEL}` : ""}
                        <DriverOwnerBadge isOwn={selectedTask.IS_OWN_DRIVER} tkName={selectedTask.TK_NAME} />
                      </span>
                  }

                  <span className="dispatch-trip-ml">Докст.:</span>
                  {editMode
                    ? <input type="text" className="dispatch-trip-mi"
                        value={editDraft.dock ?? selectedTask.DOCK ?? ""}
                        onChange={e => setEditDraft(d => ({ ...d, dock: e.target.value || null }))}
                        placeholder="Д1" />
                    : <span>{selectedTask.DOCK ?? "—"}</span>
                  }

                  <span className="dispatch-trip-ml">Время:</span>
                  {editMode
                    ? <input type="time" className="dispatch-trip-mi"
                        value={editDraft.shipment_time ?? fmtTime(selectedTask.SHIPMENT_TIME)}
                        onChange={e => setEditDraft(d => ({ ...d, shipment_time: e.target.value || null }))} />
                    : <span>{fmtTime(selectedTask.SHIPMENT_TIME) || "—"}</span>
                  }

                  <span className="dispatch-trip-ml">Дата:</span>
                  {editMode
                    ? <input type="date" className="dispatch-trip-mi"
                        value={editDraft.shipment_date ?? fmtDate(selectedTask.SHIPMENT_DATE)}
                        onChange={e => setEditDraft(d => ({ ...d, shipment_date: e.target.value || null }))} />
                    : <span>{fmtDate(selectedTask.SHIPMENT_DATE)}</span>
                  }

                  <span className="dispatch-trip-ml">Тип ТС:</span>
                  {editMode
                    ? <select className="dispatch-trip-ms"
                        value={editDraft.transtype ?? selectedTask.TRANSTYPE ?? ""}
                        onChange={e => setEditDraft(d => ({ ...d, transtype: e.target.value || null }))}>
                        <option value="">— тип —</option>
                        {transportTypes.map(t => (
                          <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>
                            {t.TRANSPORTTYPE}{t.NAME ? ` — ${t.NAME}` : ""}
                          </option>
                        ))}
                      </select>
                    : <span>{selectedTask.TRANSTYPE ?? "—"}</span>
                  }

                  <span className="dispatch-trip-ml">Прим.:</span>
                  {editMode
                    ? <input type="text" className="dispatch-trip-mi dispatch-trip-mi-w"
                        value={editDraft.primechanie ?? selectedTask.PRIMECHANIE ?? ""}
                        onChange={e => setEditDraft(d => ({ ...d, primechanie: e.target.value || null }))}
                        placeholder="Примечание диспетчера" />
                    : <span>{selectedTask.PRIMECHANIE ?? "—"}</span>
                  }
                </div>
              </div>

              <div className="dispatch-trip-sts-wrap">
                <table className="dispatch-grid">
                  <thead>
                    <tr>
                      <th style={{ width: 34 }}>#</th>
                      <th style={{ width: 80 }}>СТ №</th>
                      <th>Адрес</th>
                      <th>Пал.</th>
                      <th>Вес</th>
                      <th>Зона</th>
                      <th>Окно</th>
                      <th>Погр.</th>
                      <th style={{ width: 26 }} title="Паллеты">📦</th>
                      <th style={{ width: 26 }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {taskSts.length === 0
                      ? <tr><td colSpan={10} className="dispatch-grid-empty">Рейс пуст. Выберите СТ выше и нажмите «Добавить в рейс».</td></tr>
                      : taskSts.map(st => (
                          <TaskStTableRow
                            key={st.ST_NUMBER}
                            st={st}
                            disabled={loading || selectedTask.CONDITION === "Отгружен" || !!selectedTask.PAY_ORDER_ID}
                            isPalletOpen={palletStNum === st.ST_NUMBER}
                            onUnassign={() => handleUnassign(st.ST_NUMBER)}
                            onSetLoadType={lt => handleSetLoadType(st.ST_NUMBER, lt)}
                            onSetOrder={ord => handleSetOrder(st.ST_NUMBER, ord)}
                            onShowPallets={() => handleShowPallets(st.ST_NUMBER)}
                          />
                        ))
                    }
                  </tbody>
                </table>
              </div>
              {palletStNum && (
                <PalletPanel
                  stNum={palletStNum}
                  rows={stPallets}
                  loading={palletLoading}
                  onClose={() => setPalletStNum(null)}
                />
              )}
            </div>
          ) : (
            <div className="dispatch-no-task">
              {tasks.length > 0 && "← Выберите рейс в таблице выше"}
            </div>
          )}

          </> /* end activeTab === "tasks" */}

          {/* ============================================================
              ROUTES TAB
              ============================================================ */}
          {activeTab === "routes" && <>

          {/* ---- Routes toolbar ---- */}
          <div className="dispatch-trips-toolbar">
            <b>Маршруты за</b>
            <input type="date" value={routeShipDate} onChange={e => setRouteShipDate(e.target.value)} />
            <button className="dispatch-refresh-btn" onClick={loadTasks} title="Обновить рейсы">⟳</button>
            <span className="dispatch-tcount">{tasks.length} рейс(ов)</span>
          </div>

          {/* ---- Routes table ---- */}
          <div className="dispatch-trips-table-wrap dispatch-routes-table-wrap">
            <table className="dispatch-grid">
              <thead>
                <tr>
                  <th>Отгрузка</th><th>#</th><th>Пал.</th><th>Вес</th><th>Объём</th>
                  <th>Тип</th><th>Машина</th><th>Водитель</th><th>ДОК</th>
                  <th>Регионы</th><th>Цена</th><th>ТК</th><th>Логист</th><th>Статус</th><th title="Биллинг">💰</th>
                </tr>
              </thead>
              <tbody>
                {tasks.length === 0
                  ? <tr><td colSpan={14} className="dispatch-grid-empty">Нет рейсов по фильтрам</td></tr>
                  : tasks.map(task => (
                      <tr key={task.ID}
                        className={["dispatch-gr",
                          selectedTask?.ID === task.ID ? "selected" : "",
                          task.CONDITION === "Отгружен" ? "grid-closed" : "",
                        ].filter(Boolean).join(" ")}
                        onClick={() => selectTask(task)}>
                        <td>{fmtDate(task.SHIPMENT_DATE)}</td>
                        <td><b>#{task.ID}</b></td>
                        <td className="num-r">{task.PALLET_COUNT}</td>
                        <td className="num-r">{task.TEMP_WEIGHT != null ? task.TEMP_WEIGHT.toFixed(0) : "—"}</td>
                        <td className="num-r">{task.VOLUME_M3 != null ? task.VOLUME_M3.toFixed(2) : "—"}</td>
                        <td onClick={e => { e.stopPropagation(); if (task.CONDITION !== "Отгружен") setEditingTranstypeId(task.ID); }}
                            title={task.CONDITION !== "Отгружен" ? "Изменить тип ТС" : ""}>
                          {editingTranstypeId === task.ID
                            ? <select className="dispatch-loadtype-select" autoFocus
                                value={task.TRANSTYPE ?? ""}
                                onClick={e => e.stopPropagation()}
                                onChange={e => handleUpdateTranstype(task.ID, e.target.value)}
                                onBlur={() => setEditingTranstypeId(null)}>
                                <option value="">—</option>
                                {transportTypes.map(t => (
                                  <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>{t.TRANSPORTTYPE}</option>
                                ))}
                              </select>
                            : <span className="dispatch-inline-edit">{task.TRANSTYPE ?? "—"}</span>
                          }
                        </td>
                        <td>{task.TRANSPORT ?? "—"}</td>
                        <td>
                          {task.VODITEL_NAME ?? "—"}
                          <DriverOwnerBadge isOwn={task.IS_OWN_DRIVER} tkName={task.TK_NAME} />
                        </td>
                        <td>{task.DOCK ?? "—"}</td>
                        <td className="col-flex">{task.REGIONS ?? task.TEMP_REGION ?? "—"}</td>
                        <td>{task.PRICE != null ? task.PRICE.toLocaleString("ru-RU") + " ₽" : "—"}</td>
                        <td>{task.TK_NAME ?? "—"}</td>
                        <td>{task.LOGIST ?? "—"}</td>
                        <td><span className={`dispatch-cond ${condClass(task.CONDITION)}`}>{task.CONDITION ?? "Новый"}</span></td>
                        <td>{task.PAY_ORDER_ID ? <span className="billing-badge-sm">💰</span> : "—"}</td>
                      </tr>
                    ))
                }
              </tbody>
            </table>
          </div>

          {/* ---- Route detail ---- */}
          {selectedTask ? (
            <div className="dispatch-trip-detail-section">
              <div className="dispatch-trip-detail-hdr">
                <div className="dispatch-trip-title-row">
                  <b>Рейс #{selectedTask.ID}</b>
                  <span className={`dispatch-cond-big ${condClass(selectedTask.CONDITION)}`}>
                    {selectedTask.CONDITION ?? "Новый"}
                  </span>
                  {selectedTask.READY_PERC != null && (
                    <ReadinessBar perc={selectedTask.READY_PERC} unready={selectedTask.UNREADY_COUNT} />
                  )}
                  <span className="dispatch-pmv" style={{ marginLeft: "auto" }}>
                    P={tripP}&nbsp; M={tripM.toFixed(0)}
                  </span>
                  {selectedTask.CONDITION !== "Отгружен" && <>
                    <button className="dispatch-close-btn"
                      onClick={handleClose} disabled={loading || taskSts.length === 0}>
                      Закрыть рейс
                    </button>
                    <button className="dispatch-cancel-task-btn"
                      onClick={handleCancel}
                      disabled={loading || !!selectedTask.PAY_ORDER_ID}>
                      Отменить
                    </button>
                  </>}
                  {selectedTask.CONDITION === "Отгружен" && (
                    <span className="dispatch-closed-label">Рейс отгружен · только чтение</span>
                  )}
                  {selectedTask.PAY_ORDER_ID
                    ? <span className="billing-badge">💰 Счёт #{selectedTask.PAY_ORDER_ID}</span>
                    : selectedTask.CONDITION === "Отгружен" && selectedTask.IS_OWN_DRIVER === 0 && (
                        <button className="billing-open-btn" onClick={() => setBillingDialog(true)}>
                          Выставить счёт
                        </button>
                      )
                  }
                </div>
                <div className="dispatch-note-row">
                  <span className="dispatch-trip-ml">Примечание:</span>
                  <textarea className="dispatch-note-textarea" value={noteText}
                    onChange={e => setNoteText(e.target.value)} rows={2}
                    placeholder="Примечание диспетчера" />
                  <button className="dispatch-save-note-btn" onClick={handleSaveNote} disabled={loading}>
                    Сохранить примечание
                  </button>
                </div>
                {billingOrder && (
                  <BillingOrderCard
                    order={billingOrder}
                    loading={billingActionLoading}
                    onClose={handleBillingClose}
                    onPay={handleBillingPay}
                  />
                )}
                <div className="price-section">
                  <span className="price-label">Цена рейса:</span>
                  <span className="price-value">
                    {(selectedTask.PRICE ?? 0) > 0
                      ? (selectedTask.PRICE ?? 0).toLocaleString("ru-RU") + " ₽"
                      : "—"}
                  </span>
                  <button className="price-recalc-btn" onClick={handleRecalculatePrice}
                    disabled={priceRecalcLoading} title="Пересчитать цену через Oracle stoim_tt">
                    {priceRecalcLoading ? "…" : "⟳ Пересчитать"}
                  </button>
                  <form className="price-manual-form" onSubmit={handleSetPrice}>
                    <input type="number" className="price-input" value={manualPrice}
                      onChange={e => setManualPrice(e.target.value)}
                      min={0} step={0.01} placeholder="Сумма ₽" />
                    <button type="submit" className="price-save-btn"
                      disabled={priceLoading || !manualPrice}>
                      Сохранить
                    </button>
                  </form>
                </div>
              </div>
              <div className="dispatch-trip-sts-wrap">
                <table className="dispatch-grid">
                  <thead>
                    <tr>
                      <th title="Склад">Скл</th>
                      <th>Пал.</th>
                      <th style={{ width: 40 }}>ПОР</th>
                      <th>Адрес</th>
                      <th style={{ width: 80 }}>СТ №</th>
                      <th title="Проверка %">ПРОВ</th>
                      <th>Зона</th>
                      <th>Вр.От</th>
                      <th>Вр.До</th>
                      <th>Погр.</th>
                      <th style={{ width: 26 }} title="Паллеты">📦</th>
                      <th style={{ width: 26 }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {taskSts.length === 0
                      ? <tr><td colSpan={12} className="dispatch-grid-empty">Рейс пуст.</td></tr>
                      : taskSts.map(st => (
                          <RouteTaskStRow
                            key={st.ST_NUMBER}
                            st={st}
                            disabled={loading || selectedTask.CONDITION === "Отгружен" || !!selectedTask.PAY_ORDER_ID}
                            isPalletOpen={palletStNum === st.ST_NUMBER}
                            onUnassign={() => handleUnassign(st.ST_NUMBER)}
                            onSetLoadType={lt => handleSetLoadType(st.ST_NUMBER, lt)}
                            onSetOrder={ord => handleSetOrder(st.ST_NUMBER, ord)}
                            onShowPallets={() => handleShowPallets(st.ST_NUMBER)}
                          />
                        ))
                    }
                  </tbody>
                </table>
              </div>
              {palletStNum && (
                <PalletPanel
                  stNum={palletStNum}
                  rows={stPallets}
                  loading={palletLoading}
                  onClose={() => setPalletStNum(null)}
                />
              )}
            </div>
          ) : (
            <div className="dispatch-no-task">
              {tasks.length > 0 && "← Выберите рейс в таблице выше"}
            </div>
          )}

          </> /* end activeTab === "routes" */}

          {/* ============================================================
              BILLING TAB  (Sprint 17)
              ============================================================ */}
          {activeTab === "billing" && (
            <BillingRegistryTab
              orders={billingOrders}
              loading={billingLoading}
              dateFrom={billingDateFrom}
              dateTo={billingDateTo}
              company={billingCompany}
              status={billingStatus}
              selectedOrderId={selectedBillingOrder?.order_id ?? null}
              onDateFromChange={setBillingDateFrom}
              onDateToChange={setBillingDateTo}
              onCompanyChange={setBillingCompany}
              onStatusChange={setBillingStatus}
              onRefresh={loadBillingOrders}
              onOrderSelect={handleBillingOrderSelect}
            />
          )}

        </div>

        {/* ============================================================
            RIGHT FILTER PANEL  (~C# panel2, light-green background)
            ============================================================ */}
        {activeTab === "tasks" ? (
        <div className="dispatch-right-panel">
          <div className="dispatch-fp-label">Тип ТС</div>
          <select className="dispatch-fp-select" value={trTypeFilter}
            onChange={e => setTrTypeFilter(e.target.value)}>
            <option value="">Все</option>
            {transportTypes.map(t => (
              <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>
                {t.TRANSPORTTYPE}{t.NAME ? ` — ${t.NAME}` : ""}
              </option>
            ))}
          </select>

          <div className="dispatch-fp-label">АДР</div>
          <input className="dispatch-fp-input" type="text" value={addrMask}
            onChange={e => setAddrMask(e.target.value)} placeholder="Адрес / регион" />

          <div className="dispatch-fp-label">СТ</div>
          <textarea className="dispatch-fp-textarea" value={stMask} rows={3}
            onChange={e => setStMask(e.target.value)}
            placeholder={"Номер СТ\n(несколько через\nперенос строки)"} />
          <label className="dispatch-fp-check dispatch-fp-check-sm">
            <input type="checkbox" checked={stMaskExclude}
              onChange={e => setStMaskExclude(e.target.checked)} />
            НЕ эти СТ (исключить)
          </label>

          <div className="dispatch-fp-label">Артикул</div>
          <input className="dispatch-fp-input" type="text" value={articulFilter}
            onChange={e => setArticulFilter(e.target.value)} placeholder="Код артикула" />

          <div className="dispatch-fp-sep" />

          <label className="dispatch-fp-check">
            <input type="checkbox" checked={unassignedOnly}
              onChange={e => setUnassignedOnly(e.target.checked)} />
            НЕ РАСПРЕДЕЛЕННЫЕ
          </label>
          <label className="dispatch-fp-check">
            <input type="checkbox" checked={assembledOnly}
              onChange={e => {
                setAssembledOnly(e.target.checked);
                if (e.target.checked) setNotAssembledOnly(false);
              }} />
            Только собранные
          </label>
          <label className="dispatch-fp-check">
            <input type="checkbox" checked={notAssembledOnly}
              onChange={e => {
                setNotAssembledOnly(e.target.checked);
                if (e.target.checked) setAssembledOnly(false);
              }} />
            Только НЕ собранные
          </label>

          <div className="dispatch-fp-sep" />

          <div className="dispatch-fp-label">Дата до</div>
          <input className="dispatch-fp-input" type="date" value={dateTo}
            onChange={e => setDateTo(e.target.value)} />

          <div className="dispatch-fp-label">V&lt; (м³)</div>
          <input className="dispatch-fp-input" type="number" min={0} step={0.1}
            value={maxVolM3 ?? ""}
            onChange={e => setMaxVolM3(e.target.value ? Number(e.target.value) : null)}
            placeholder="—" />

          <div className="dispatch-fp-label">M&lt; (кг)</div>
          <input className="dispatch-fp-input" type="number" min={0} step={10}
            value={maxWeightKg ?? ""}
            onChange={e => setMaxWeightKg(e.target.value ? Number(e.target.value) : null)}
            placeholder="—" />
        </div>
        ) : activeTab === "billing" && selectedBillingOrder ? (
        <div className="dispatch-right-panel billing-detail-panel">
          <BillingOrderDetailPanel
            order={selectedBillingOrder}
            tasks={billingOrderTasks}
            loading={billingOrderTasksLoading}
            onClose={() => { setSelectedBillingOrder(null); setBillingOrderTasks([]); }}
          />
        </div>
        ) : activeTab === "routes" ? (
        <div className="dispatch-right-panel">
          <div className="dispatch-fp-label">Фильтр по ID</div>
          <input className="dispatch-fp-input" type="number" value={routeTaskId}
            onChange={e => setRouteTaskId(e.target.value)} placeholder="Номер рейса" />

          <div className="dispatch-fp-label">Авто</div>
          <input className="dispatch-fp-input" type="text" value={routeCarMask}
            onChange={e => setRouteCarMask(e.target.value)} placeholder="Гос. номер" />

          <div className="dispatch-fp-label">Компания (ТК)</div>
          <input className="dispatch-fp-input" type="text" value={routeCompanyMask}
            onChange={e => setRouteCompanyMask(e.target.value)} placeholder="ООО Транс" />

          <div className="dispatch-fp-sep" />

          <label className="dispatch-fp-check">
            <input type="checkbox" checked={routeNoPayments}
              onChange={e => setRouteNoPayments(e.target.checked)} />
            Без оплат
          </label>

          <div className="dispatch-fp-sep" />

          <div className="dispatch-fp-label">До даты</div>
          <input className="dispatch-fp-input" type="date" value={routeDateTo}
            onChange={e => setRouteDateTo(e.target.value)} />
        </div>
        ) : null}
      </div>

      {createDialog && (
        <CreateTaskDialog
          filterDate={filterDate}
          transportTypes={transportTypes}
          vehicles={vehicles}
          drivers={drivers}
          selectedCount={selectedStNums.size}
          onConfirm={handleCreate}
          onClose={() => setCreateDialog(false)}
        />
      )}

      {billingDialog && selectedTask && (
        <OpenBillingDialog
          task={selectedTask}
          loading={openingBilling}
          onConfirm={handleOpenBilling}
          onClose={() => setBillingDialog(false)}
        />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Warehouse color mapping (§3.4)
// ---------------------------------------------------------------------------

const WARE_COLOR_CLASS: Record<number, string> = {
  5: "dispatch-ware-5",
  6: "dispatch-ware-6",
  7: "dispatch-ware-7",
  9201: "dispatch-ware-9201",
  9202: "dispatch-ware-9202",
  9203: "dispatch-ware-9203",
};

function wareColorClass(wareId: number): string {
  return WARE_COLOR_CLASS[wareId] ?? "";
}

// ---------------------------------------------------------------------------
// AvailableStRow
// ---------------------------------------------------------------------------

function AvailableStRow({
  st, checked, onToggle, isChild = false, idx = 0, onShiftClick, onSelectByField,
}: {
  st: AvailableSt;
  checked: boolean;
  onToggle: () => void;
  isChild?: boolean;
  idx?: number;
  onShiftClick?: (idx: number) => void;
  onSelectByField?: (field: "RAION" | "REGION", value: string | null) => void;
}) {
  const rowClass = [
    "dispatch-gr",
    checked ? "selected" : wareColorClass(st.WARE_ID),
    isChild ? "dispatch-grid-cluster-child" : "",
  ].filter(Boolean).join(" ");

  function handleRowClick(e: React.MouseEvent) {
    if (e.shiftKey && onShiftClick) onShiftClick(idx);
    else onToggle();
  }

  function handleFieldClick(e: React.MouseEvent, field: "RAION" | "REGION", value: string | null) {
    if (!onSelectByField) return;
    e.stopPropagation();
    onSelectByField(field, value);
  }

  return (
    <tr className={rowClass} onClick={handleRowClick}>
      <td onClick={e => e.stopPropagation()}>
        <input type="checkbox" checked={checked} onChange={onToggle} />
      </td>
      <td className="num-c dispatch-ware-cell" title={`Склад ${st.WARE_ID}`}>{st.WARE_ID}</td>
      <td className="num-r">{st.PALLETS_COUNT}</td>
      <td className="num-r">{st.WEIGHT_KG.toFixed(0)}</td>
      <td className="num-r">{st.VOLUME_M3 != null ? st.VOLUME_M3.toFixed(2) : "—"}</td>
      <td className={onSelectByField ? "dispatch-region-cell" : ""}
          onClick={e => handleFieldClick(e, "REGION", st.REGION)}
          title={onSelectByField ? "Выделить все СТ региона" : ""}>{st.REGION ?? "—"}</td>
      <td className="col-flex">{st.ADDR ?? "—"}</td>
      <td className="dispatch-gc-stnum">{st.ST_NUMBER}</td>
      <td>{st.TRANSTASK_ID ? `#${st.TRANSTASK_ID}` : "—"}</td>
      <td>{fmtDate(st.STDATE)}</td>
      <td>{st.VERIFY_PERC != null ? <VerifyBar perc={st.VERIFY_PERC} /> : "—"}</td>
      <td className={onSelectByField ? "dispatch-region-cell" : ""}
          onClick={e => handleFieldClick(e, "RAION", st.RAION)}
          title={onSelectByField ? "Выделить все СТ района" : ""}>{st.RAION ?? "—"}</td>
      <td><TransportTypeBadge value={st.TRANSPORT_TYPE} /></td>
      <td className="num-c" title={st.STOL ? "Требуется стол-лифт / гидроборт" : ""}>{st.STOL ? "♿" : ""}</td>
      <td className="dispatch-prim1" title={st.PRIM1 ?? ""}>{st.PRIM1 ? st.PRIM1.slice(0, 20) : ""}</td>
      <td className="num-c">{st.SUGAR ? <span className="dispatch-sugar">С</span> : ""}</td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// ClusterGroup — cluster header row + child ST rows
// ---------------------------------------------------------------------------

function ClusterGroup({
  cluster, expanded, onToggle, selectedNums, onToggleSt,
}: {
  cluster: TransportCluster;
  expanded: boolean;
  onToggle: () => void;
  selectedNums: Set<string>;
  onToggleSt: (stNum: string) => void;
}) {
  const selCount = cluster.STS.filter(s => selectedNums.has(s.ST_NUMBER)).length;
  return (
    <>
      <tr className="dispatch-grid-cluster-hdr" onClick={onToggle}>
        <td colSpan={16}>
          <span className="dispatch-grid-cluster-arrow">{expanded ? "▼" : "▶"}</span>
          <b>{cluster.RAION}</b>
          <span className="dispatch-grid-cluster-meta">
            {" "}— {cluster.ST_COUNT} СТ · {cluster.PALLET_COUNT} пал · {cluster.WEIGHT_KG.toFixed(0)} кг
          </span>
          {selCount > 0 && <span className="dispatch-cluster-sel">{selCount} выбр.</span>}
        </td>
      </tr>
      {expanded && cluster.STS.map(st => (
        <AvailableStRow key={st.ST_NUMBER} st={st}
          checked={selectedNums.has(st.ST_NUMBER)}
          onToggle={() => onToggleSt(st.ST_NUMBER)}
          isChild />
      ))}
    </>
  );
}

// ---------------------------------------------------------------------------
// RouteTaskStRow — row in routes tab trip detail (§3.8.2)
// ---------------------------------------------------------------------------

function RouteTaskStRow({
  st, disabled, isPalletOpen, onUnassign, onSetLoadType, onSetOrder, onShowPallets,
}: {
  st: TaskSt;
  disabled: boolean;
  isPalletOpen: boolean;
  onUnassign: () => void;
  onSetLoadType: (lt: string) => void;
  onSetOrder: (ord: number) => void;
  onShowPallets: () => void;
}) {
  const [ordEdit, setOrdEdit] = useState(false);
  const [ordVal, setOrdVal] = useState(String(st.ORD ?? ""));

  function commitOrder() {
    setOrdEdit(false);
    const n = parseInt(ordVal, 10);
    if (!isNaN(n) && n !== st.ORD) onSetOrder(n);
    else setOrdVal(String(st.ORD ?? ""));
  }

  return (
    <tr className="dispatch-gr">
      <td className="num-c dispatch-ware-cell" title={`Склад ${st.WARE_ID}`}>{st.WARE_ID ?? "—"}</td>
      <td className="num-r">{st.PALLETS_COUNT}</td>
      <td>
        {ordEdit ? (
          <input className="dispatch-ord-input" type="number" min={0} value={ordVal} autoFocus
            onChange={e => setOrdVal(e.target.value)}
            onBlur={commitOrder}
            onKeyDown={e => {
              if (e.key === "Enter") commitOrder();
              if (e.key === "Escape") { setOrdEdit(false); setOrdVal(String(st.ORD ?? "")); }
            }} />
        ) : (
          <span className="dispatch-ord-val"
            onClick={() => { if (!disabled) setOrdEdit(true); }}
            title={disabled ? "" : "Изменить порядок"}>
            {st.ORD ?? "—"}
          </span>
        )}
      </td>
      <td className="col-flex">
        {st.REGION || st.ADDR || "—"}
        {st.RAION && <span className="dispatch-st-raion-sm"> · {st.RAION}</span>}
      </td>
      <td className="dispatch-gc-stnum">{st.ST_NUMBER}</td>
      <td>{st.VERIFY_PERC != null ? <VerifyPill perc={st.VERIFY_PERC} /> : "—"}</td>
      <td>{st.ZONE ?? "—"}</td>
      <td style={{ whiteSpace: "nowrap" }}>{fmtTime(st.TIME_FROM) || "—"}</td>
      <td style={{ whiteSpace: "nowrap" }}>{fmtTime(st.TIME_TO) || "—"}</td>
      <td>
        {disabled
          ? <LoadTypeBadge value={st.LOAD_TYPE} />
          : <select className="dispatch-loadtype-select" value={st.LOAD_TYPE ?? ""}
              onChange={e => onSetLoadType(e.target.value)}>
              <option value="">—</option>
              <option value="Г">Г</option>
              <option value="П">П</option>
            </select>
        }
      </td>
      <td>
        <button
          className={`dispatch-pallet-btn${isPalletOpen ? " active" : ""}`}
          onClick={onShowPallets}
          title={isPalletOpen ? "Скрыть паллеты" : "Показать паллеты"}>
          📦
        </button>
      </td>
      <td>
        <button className="dispatch-unassign-btn" disabled={disabled} onClick={onUnassign} title="Снять СТ с рейса">✕</button>
      </td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// TaskStTableRow — row in trip detail table
// ---------------------------------------------------------------------------

function TaskStTableRow({
  st, disabled, isPalletOpen, onUnassign, onSetLoadType, onSetOrder, onShowPallets,
}: {
  st: TaskSt;
  disabled: boolean;
  isPalletOpen: boolean;
  onUnassign: () => void;
  onSetLoadType: (lt: string) => void;
  onSetOrder: (ord: number) => void;
  onShowPallets: () => void;
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
    <tr className="dispatch-gr">
      <td>
        {ordEdit ? (
          <input className="dispatch-ord-input" type="number" min={0} value={ordVal} autoFocus
            onChange={e => setOrdVal(e.target.value)}
            onBlur={commitOrder}
            onKeyDown={e => {
              if (e.key === "Enter") commitOrder();
              if (e.key === "Escape") { setOrdEdit(false); setOrdVal(String(st.ORD ?? "")); }
            }} />
        ) : (
          <span className="dispatch-ord-val"
            onClick={() => { if (!disabled) setOrdEdit(true); }}
            title={disabled ? "" : "Изменить порядок"}>
            {st.ORD ?? "—"}
          </span>
        )}
      </td>
      <td className="dispatch-gc-stnum">{st.ST_NUMBER}</td>
      <td className="col-flex">
        {st.REGION || st.ADDR || "—"}
        {st.RAION && <span className="dispatch-st-raion-sm"> · {st.RAION}</span>}
      </td>
      <td className="num-r">{st.PALLETS_COUNT}</td>
      <td className="num-r">{st.WEIGHT_KG.toFixed(0)}</td>
      <td>{st.ZONE ?? "—"}</td>
      <td style={{ whiteSpace: "nowrap" }}>{timeWindow}</td>
      <td>
        {disabled
          ? <LoadTypeBadge value={st.LOAD_TYPE} />
          : <select className="dispatch-loadtype-select" value={st.LOAD_TYPE ?? ""}
              onChange={e => onSetLoadType(e.target.value)}>
              <option value="">—</option>
              <option value="Г">Г</option>
              <option value="П">П</option>
            </select>
        }
      </td>
      <td>
        <button
          className={`dispatch-pallet-btn${isPalletOpen ? " active" : ""}`}
          onClick={onShowPallets}
          title={isPalletOpen ? "Скрыть паллеты" : "Показать паллеты"}>
          📦
        </button>
      </td>
      <td>
        <button className="dispatch-unassign-btn" disabled={disabled} onClick={onUnassign} title="Снять СТ с рейса">✕</button>
      </td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// Sprint 6: Pallet panel
// ---------------------------------------------------------------------------

function PalletPanel({
  stNum, rows, loading, onClose,
}: {
  stNum: string;
  rows: StPalletRow[];
  loading: boolean;
  onClose: () => void;
}) {
  return (
    <div className="dispatch-pallet-panel">
      <div className="dispatch-pallet-panel-hdr">
        <b>Паллеты СТ {stNum}</b>
        <button className="dispatch-pallet-close-btn" onClick={onClose} title="Закрыть">✕</button>
      </div>
      {loading ? (
        <div className="dispatch-grid-empty">Загрузка...</div>
      ) : rows.length === 0 ? (
        <div className="dispatch-grid-empty">Нет данных о паллетах</div>
      ) : (
        <PalletGroupedTable rows={rows} />
      )}
    </div>
  );
}

function PalletGroupedTable({ rows }: { rows: StPalletRow[] }) {
  type PalletGroup = { zone: string | null; loadType: string | null; ord: number | null; rows: StPalletRow[] };
  const pallets = new Map<string, PalletGroup>();
  for (const row of rows) {
    if (!pallets.has(row.PALLET_UID)) {
      pallets.set(row.PALLET_UID, { zone: row.ZONE, loadType: row.LOAD_TYPE, ord: row.ORD, rows: [] });
    }
    if (row.ARTICUL) pallets.get(row.PALLET_UID)!.rows.push(row);
  }

  return (
    <table className="dispatch-grid dispatch-pallet-grid">
      <thead>
        <tr>
          <th>Паллет UID</th>
          <th>Зона</th>
          <th>Борт</th>
          <th style={{ width: 40 }}>ПОР</th>
          <th>Артикул</th>
          <th className="num-r">Вес,кг</th>
          <th className="num-r">Упак.</th>
          <th className="num-r">Объём</th>
        </tr>
      </thead>
      <tbody>
        {Array.from(pallets.entries()).map(([uid, p]) => {
          const totalWeight = p.rows.reduce((s, r) => s + r.ORDER_WEIGHT, 0);
          const totalPack = p.rows.reduce((s, r) => s + r.PACK_COUNT, 0);
          return (
            <Fragment key={uid}>
              <tr className="dispatch-pallet-hdr-row">
                <td><b>{uid}</b></td>
                <td>{p.zone ?? "—"}</td>
                <td><LoadTypeBadge value={p.loadType} /></td>
                <td className="num-c">{p.ord ?? "—"}</td>
                <td className="dispatch-pallet-art-count">{p.rows.length} артикулов</td>
                <td className="num-r"><b>{totalWeight.toFixed(0)}</b></td>
                <td className="num-r"><b>{totalPack}</b></td>
                <td className="num-r"></td>
              </tr>
              {p.rows.map((r, i) => (
                <tr key={i} className="dispatch-pallet-art-row">
                  <td colSpan={4} />
                  <td className="dispatch-pallet-art">{r.ARTICUL}</td>
                  <td className="num-r">{r.ORDER_WEIGHT.toFixed(0)}</td>
                  <td className="num-r">{r.PACK_COUNT}</td>
                  <td className="num-r">{r.ROW_VOLUME_M3.toFixed(3)}</td>
                </tr>
              ))}
            </Fragment>
          );
        })}
      </tbody>
    </table>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function LoadTypeBadge({ value }: { value: string | null }) {
  if (!value) return <span className="dispatch-lt-empty">—</span>;
  return <span className={`dispatch-lt-badge dispatch-lt-${value.toLowerCase()}`}>{value}</span>;
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
  const cls = perc >= 100 ? "done" : perc > 0 ? "partial" : "zero";
  return (
    <div className="dispatch-readiness">
      <div className="dispatch-readiness-track">
        <div className={`dispatch-readiness-fill dispatch-readiness-${cls}`}
          style={{ width: `${Math.min(perc, 100)}%` }} />
      </div>
      <span className="dispatch-readiness-label">
        {perc >= 100 ? "Собран" : `${perc}%${unready ? ` (−${unready})` : ""}`}
      </span>
    </div>
  );
}

type VehicleAvail = {
  vehicle_id: number; vehicle_num: string; vehicle_type: string;
  marka: string; max_pallets: number; gidrobort: boolean;
  free_at: string | null; delay_min: number; status: "green" | "yellow" | "red"; detail: string;
};

const AVAIL_DOT: Record<string, string> = { green: "🟢", yellow: "🟡", red: "🔴" };

function CreateTaskDialog({
  filterDate, transportTypes, vehicles, drivers, selectedCount, onConfirm, onClose,
}: {
  filterDate: string;
  transportTypes: TransportType[];
  vehicles: Vehicle[];
  drivers: Driver[];
  selectedCount: number;
  onConfirm: (params: { transtype: string; shipment_date: string; vehicle: string; driver_id: number | null; dock: string }) => void;
  onClose: () => void;
}) {
  const [transtype, setTranstype] = useState(transportTypes[0]?.TRANSPORTTYPE || "10");
  const [shipDate, setShipDate] = useState(filterDate);
  const [shipTime, setShipTime] = useState("09:00");
  const [vehicle, setVehicle] = useState("");
  const [driverId, setDriverId] = useState<number | null>(null);
  const [dock, setDock] = useState("");
  const [avail, setAvail] = useState<VehicleAvail[]>([]);
  const [availLoading, setAvailLoading] = useState(false);

  const selectedAvail = avail.find(a => a.vehicle_num === vehicle);

  // Reload availability when date/time changes
  useEffect(() => {
    if (!shipDate || !shipTime) return;
    setAvailLoading(true);
    apiFetch<VehicleAvail[]>(
      `/api/admin/transport/vehicles/available?shipment_time=${shipDate}+${shipTime}&pallets=0`
    )
      .then(setAvail)
      .catch(() => setAvail([]))
      .finally(() => setAvailLoading(false));
  }, [shipDate, shipTime]);

  // Merge availability into vehicle list
  const availMap = new Map(avail.map(a => [a.vehicle_num, a]));

  return (
    <div className="dispatch-dialog-overlay" onClick={onClose}>
      <div className="dispatch-dialog" onClick={e => e.stopPropagation()}>
        <h3>Создать маршрут{selectedCount > 0 ? ` · ${selectedCount} СТ` : ""}</h3>
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
          <div style={{ display: "flex", gap: 6 }}>
            <input type="date" value={shipDate} onChange={e => setShipDate(e.target.value)} />
            <input type="time" value={shipTime} onChange={e => setShipTime(e.target.value)}
              style={{ width: 90 }} />
          </div>
        </label>
        <label className="dispatch-dialog-field">
          <span>Машина {availLoading && <span style={{ fontSize: 10, color: "#94a3b8" }}>обновление…</span>}</span>
          <select value={vehicle} onChange={e => setVehicle(e.target.value)}>
            <option value="">— не выбрана —</option>
            {vehicles.map(v => {
              const a = availMap.get(v.NUM);
              const dot = a ? AVAIL_DOT[a.status] : "";
              return (
                <option key={v.ID} value={v.NUM}>
                  {dot} {v.NUM} · {v.MARKA ?? "?"}{v.PALLETS ? ` · ${v.PALLETS}пал` : ""}
                  {a?.free_at ? ` · св. ${a.free_at}` : ""}
                </option>
              );
            })}
          </select>
          {selectedAvail && selectedAvail.status === "red" && (
            <div className="dispatch-avail-warn">
              ⚠ {selectedAvail.detail} — конфликт возможен
            </div>
          )}
          {selectedAvail && selectedAvail.status === "yellow" && (
            <div className="dispatch-avail-info">
              ℹ {selectedAvail.detail}
            </div>
          )}
        </label>
        <label className="dispatch-dialog-field">
          <span>Водитель</span>
          <select value={driverId ?? ""} onChange={e => setDriverId(e.target.value ? Number(e.target.value) : null)}>
            <option value="">— не выбран —</option>
            {drivers.map(d => (
              <option key={d.ID} value={d.ID}>
                {d.FULL_NAME ?? `#${d.ID}`}
                {d.SOBSTVENNYY === 0 && d.DOVERENNOST_OT ? ` (${d.DOVERENNOST_OT})` : ""}
              </option>
            ))}
          </select>
        </label>
        <label className="dispatch-dialog-field">
          <span>Докст.</span>
          <input type="text" value={dock} onChange={e => setDock(e.target.value)} placeholder="Д1" />
        </label>
        <div className="dispatch-dialog-actions">
          <button className="dispatch-new-btn"
            onClick={() => onConfirm({ transtype, shipment_date: shipDate, vehicle, driver_id: driverId, dock })}>
            Создать{selectedCount > 0 ? ` (${selectedCount} СТ)` : ""}
          </button>
          <button className="dispatch-cancel-edit-btn" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// OpenBillingDialog (Sprint 15)
// ---------------------------------------------------------------------------

function OpenBillingDialog({
  task, loading, onConfirm, onClose,
}: {
  task: TransportTask;
  loading: boolean;
  onConfirm: (existingOrderId: number | null) => void;
  onClose: () => void;
}) {
  const [existingOrders, setExistingOrders] = useState<BillingOrder[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState<number | null>(null);
  const [companies, setCompanies] = useState<string[]>([]);

  const company = task.TK_NAME ?? "";
  const shipDate = fmtDate(task.SHIPMENT_DATE);

  useEffect(() => {
    apiFetch<string[]>("/api/admin/transport/billing/companies")
      .then(setCompanies)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!company) return;
    setLoadingOrders(true);
    apiFetch<BillingOrder[]>(
      `/api/admin/transport/billing/orders?company=${encodeURIComponent(company)}&closed=0&payed=0`
    )
      .then(orders => setExistingOrders(orders.filter(o => !o.closed && !o.payed)))
      .catch(() => {})
      .finally(() => setLoadingOrders(false));
  }, [company]);

  return (
    <div className="dispatch-dialog-overlay">
      <div className="dispatch-dialog">
        <div className="dispatch-dialog-title">Выставить счёт</div>
        <div className="dispatch-dialog-field">
          <span>Рейс</span>
          <span>#{task.ID} · {task.TRANSPORT ?? "—"}</span>
        </div>
        <div className="dispatch-dialog-field">
          <span>Транспортная компания</span>
          <span className="billing-dialog-company">{company || "Неизвестная ТК"}</span>
          {companies.length > 0 && (
            <datalist id="billing-companies-list">
              {companies.map(c => <option key={c} value={c} />)}
            </datalist>
          )}
        </div>
        <div className="dispatch-dialog-field">
          <span>Дата</span>
          <span>{shipDate}</span>
        </div>
        <div className="dispatch-dialog-field">
          <span>Цена рейса</span>
          <span>{task.PRICE != null ? task.PRICE.toLocaleString("ru-RU") + " ₽" : "—"}</span>
        </div>

        {loadingOrders && (
          <p className="billing-dialog-hint">Загружаю существующие счета…</p>
        )}
        {!loadingOrders && existingOrders.length > 0 && (
          <div className="billing-link-section">
            <div className="billing-link-label">Привязать к счёту:</div>
            <label className="billing-link-radio">
              <input type="radio" name="order_choice" value="new"
                checked={selectedOrderId === null}
                onChange={() => setSelectedOrderId(null)} />
              Создать новый счёт
            </label>
            {existingOrders.map(o => (
              <label key={o.order_id} className="billing-link-radio">
                <input type="radio" name="order_choice" value={o.order_id}
                  checked={selectedOrderId === o.order_id}
                  onChange={() => setSelectedOrderId(o.order_id)} />
                {o.num ?? `#${o.order_id}`}
                {o.date_from ? ` (${o.date_from}${o.date_to && o.date_to !== o.date_from ? ` – ${o.date_to}` : ""})` : ""}
              </label>
            ))}
          </div>
        )}

        {!loadingOrders && existingOrders.length === 0 && (
          <p className="billing-dialog-hint">
            Будет создан новый биллинг-заказ и рейс привязан к нему.
            После выставления счёта рейс нельзя расформировать.
          </p>
        )}

        <div className="dispatch-dialog-actions">
          <button className="dispatch-new-btn"
            onClick={() => onConfirm(selectedOrderId)} disabled={loading}>
            {loading ? "…" : selectedOrderId ? "Добавить к счёту" : "Создать счёт"}
          </button>
          <button className="dispatch-cancel-edit-btn" onClick={onClose} disabled={loading}>
            Отмена
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// BillingOrderCard (Sprint 16)
// ---------------------------------------------------------------------------

function billingStatusLabel(order: BillingOrder): { text: string; cls: string } {
  if (order.payed)  return { text: "🟢 Оплачен",  cls: "billing-status-paid" };
  if (order.closed) return { text: "🔵 Закрыт",   cls: "billing-status-closed" };
  return              { text: "🟡 Выставлен", cls: "billing-status-open" };
}

function BillingOrderCard({
  order, loading, onClose, onPay,
}: {
  order: BillingOrder;
  loading: boolean;
  onClose: () => void;
  onPay: () => void;
}) {
  const { text, cls } = billingStatusLabel(order);
  return (
    <div className="billing-order-card">
      <div className="billing-order-card-header">
        <span className="billing-order-num">{order.num ?? `#${order.order_id}`}</span>
        <span className={`billing-order-status ${cls}`}>{text}</span>
        <span className="billing-order-company">{order.company ?? "—"}</span>
        <span className="billing-order-period">{order.date_from} – {order.date_to}</span>
        {order.total_price != null && order.total_price > 0 && (
          <span className="billing-order-price">{order.total_price.toLocaleString("ru-RU")} ₽</span>
        )}
        {order.num_plat && (
          <span className="billing-order-numplat">№ платёж.: {order.num_plat}</span>
        )}
      </div>
      <div className="billing-order-card-actions">
        {!order.closed && !order.payed && (
          <button className="billing-close-btn" onClick={onClose} disabled={loading}>
            Закрыть счёт
          </button>
        )}
        {order.closed && !order.payed && (
          <button className="billing-pay-btn" onClick={onPay} disabled={loading}>
            Отметить оплаченным
          </button>
        )}
        {order.payed && (
          <span className="billing-done-label">Счёт закрыт и оплачен</span>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// BillingRegistryTab (Sprint 17)
// ---------------------------------------------------------------------------

type BillingStatusFilter = "all" | "open" | "closed" | "paid";

function billingOrderStatusText(order: BillingOrder): string {
  if (order.payed)  return "Оплачен";
  if (order.closed) return "Закрыт";
  return "Выставлен";
}

function exportBillingCsv(orders: BillingOrder[]) {
  const BOM = "﻿";
  const header = "Счёт;Компания;Дата от;Дата до;Рейсов;Сумма ₽;Статус;№ платёжного";
  const rows = orders.map(o =>
    [
      o.num ?? o.order_id,
      o.company ?? "",
      o.date_from ?? "",
      o.date_to ?? "",
      o.task_count ?? 0,
      o.total_price ?? 0,
      billingOrderStatusText(o),
      o.num_plat ?? "",
    ].join(";")
  );
  const csv = BOM + [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `billing-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function BillingRegistryTab({
  orders, loading, dateFrom, dateTo, company, status, selectedOrderId,
  onDateFromChange, onDateToChange, onCompanyChange, onStatusChange, onRefresh, onOrderSelect,
}: {
  orders: BillingOrder[];
  loading: boolean;
  dateFrom: string;
  dateTo: string;
  company: string;
  status: BillingStatusFilter;
  selectedOrderId: number | null;
  onDateFromChange: (v: string) => void;
  onDateToChange: (v: string) => void;
  onCompanyChange: (v: string) => void;
  onStatusChange: (v: BillingStatusFilter) => void;
  onRefresh: () => void;
  onOrderSelect: (order: BillingOrder) => void;
}) {
  // Totals by company
  const totals: Record<string, number> = {};
  for (const o of orders) {
    const key = o.company ?? "—";
    totals[key] = (totals[key] ?? 0) + (o.total_price ?? 0);
  }

  return (
    <div className="billing-registry">
      <div className="billing-registry-toolbar">
        <span className="billing-registry-title">Реестр счетов</span>
        <label>
          <span className="billing-fp-label">С</span>
          <input type="date" className="billing-fp-input" value={dateFrom}
            onChange={e => onDateFromChange(e.target.value)} />
        </label>
        <label>
          <span className="billing-fp-label">По</span>
          <input type="date" className="billing-fp-input" value={dateTo}
            onChange={e => onDateToChange(e.target.value)} />
        </label>
        <input type="text" className="billing-fp-input billing-fp-wide" placeholder="Компания (ТК)"
          value={company} onChange={e => onCompanyChange(e.target.value)} />
        <select className="billing-fp-select" value={status}
          onChange={e => onStatusChange(e.target.value as BillingStatusFilter)}>
          <option value="all">Все статусы</option>
          <option value="open">Выставлен</option>
          <option value="closed">Закрыт</option>
          <option value="paid">Оплачен</option>
        </select>
        <button className="billing-refresh-btn" onClick={onRefresh} disabled={loading}>⟳</button>
        <button className="billing-csv-btn" onClick={() => exportBillingCsv(orders)}
          disabled={orders.length === 0}>
          ⬇ Скачать CSV
        </button>
      </div>

      {loading
        ? <div className="billing-registry-loading">Загрузка…</div>
        : orders.length === 0
          ? <div className="billing-registry-empty">Нет счетов за выбранный период</div>
          : <>
              <table className="billing-registry-table">
                <thead>
                  <tr>
                    <th>Счёт</th>
                    <th>Компания</th>
                    <th>Дата от</th>
                    <th>Дата до</th>
                    <th>Рейсов</th>
                    <th>Сумма ₽</th>
                    <th>Статус</th>
                    <th>№ платёжного</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(o => (
                    <tr key={o.order_id}
                      className={selectedOrderId === o.order_id ? "billing-row-selected" : "billing-row-clickable"}
                      onClick={() => onOrderSelect(o)}>
                      <td className="billing-num-cell">{o.num ?? `#${o.order_id}`}</td>
                      <td>{o.company ?? "—"}</td>
                      <td>{o.date_from ?? "—"}</td>
                      <td>{o.date_to ?? "—"}</td>
                      <td className="billing-count-cell">{o.task_count ?? 0}</td>
                      <td className="billing-price-cell">
                        {(o.total_price ?? 0) > 0
                          ? (o.total_price ?? 0).toLocaleString("ru-RU") + " ₽"
                          : "—"}
                      </td>
                      <td>
                        <span className={`billing-status-tag ${
                          o.payed ? "billing-status-paid" :
                          o.closed ? "billing-status-closed" : "billing-status-open"
                        }`}>{billingOrderStatusText(o)}</span>
                      </td>
                      <td className="billing-numplat-cell">{o.num_plat ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="billing-totals">
                <b>Итого по ТК:</b>
                {Object.entries(totals).map(([tk, sum]) => (
                  <span key={tk} className="billing-totals-row">
                    {tk}: <b>{sum.toLocaleString("ru-RU")} ₽</b>
                  </span>
                ))}
              </div>
            </>
      }
    </div>
  );
}

// ---------------------------------------------------------------------------
// BillingOrderDetailPanel (Sprint 23)
// ---------------------------------------------------------------------------

function exportOrderTasksCsv(order: BillingOrder, tasks: BillingOrderTask[]) {
  const BOM = "﻿";
  const header = "Рейс;Авто;Дата;Статус;Сумма ₽";
  const rows = tasks.map(t =>
    [t.tt_id, t.transport ?? "", t.shipment_date ?? "", t.status ?? "", t.price].join(";")
  );
  const total = tasks.reduce((s, t) => s + t.price, 0);
  rows.push(["", "", "", "ИТОГО", total].join(";"));
  const csv = BOM + [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `order-${order.num ?? order.order_id}-tasks.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function BillingOrderDetailPanel({
  order, tasks, loading, onClose,
}: {
  order: BillingOrder;
  tasks: BillingOrderTask[];
  loading: boolean;
  onClose: () => void;
}) {
  const { text, cls } = billingStatusLabel(order);
  const total = tasks.reduce((s, t) => s + t.price, 0);

  return (
    <div className="billing-detail-container">
      <div className="billing-detail-header">
        <span className="billing-detail-num">{order.num ?? `#${order.order_id}`}</span>
        <span className={`billing-order-status ${cls}`}>{text}</span>
        <button className="billing-detail-close-btn" onClick={onClose} title="Закрыть">✕</button>
      </div>
      <div className="billing-detail-meta">
        <span>{order.company ?? "—"}</span>
        <span>{order.date_from} – {order.date_to}</span>
        {order.num_plat && <span>№ плат.: {order.num_plat}</span>}
      </div>

      {loading ? (
        <div className="billing-detail-loading">Загрузка…</div>
      ) : tasks.length === 0 ? (
        <div className="billing-detail-empty">Рейсов нет</div>
      ) : (
        <>
          <table className="billing-detail-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Авто</th>
                <th>Дата</th>
                <th className="billing-price-cell">Сумма ₽</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map(t => (
                <tr key={t.tt_id}>
                  <td className="billing-detail-id">#{t.tt_id}</td>
                  <td>{t.transport ?? "—"}</td>
                  <td>{t.shipment_date ?? "—"}</td>
                  <td className="billing-price-cell">
                    {t.price > 0 ? t.price.toLocaleString("ru-RU") + " ₽" : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="billing-detail-total">
            Итого: <b>{total.toLocaleString("ru-RU")} ₽</b>
          </div>
          <button className="billing-csv-btn billing-detail-export-btn"
            onClick={() => exportOrderTasksCsv(order, tasks)}>
            ⬇ Скачать CSV
          </button>
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sprint 5 components
// ---------------------------------------------------------------------------

const TR_TYPE_MAP: Record<string, { label: string; cls: string }> = {
  "10":    { label: "Тент 10т",  cls: "tr-10"  },
  "15":    { label: "Тент 15т",  cls: "tr-15"  },
  "20реф": { label: "Реф 20т",   cls: "tr-ref" },
  "20":    { label: "Тент 20т",  cls: "tr-20"  },
};

function TransportTypeBadge({ value }: { value: string | null }) {
  if (!value || value === "0") return <span className="dispatch-tr-empty">—</span>;
  const info = TR_TYPE_MAP[value];
  return info
    ? <span className={`dispatch-tr-badge dispatch-tr-${info.cls}`} title={value}>{info.label}</span>
    : <span className="dispatch-tr-badge dispatch-tr-other" title={value}>{value}</span>;
}

function VerifyBar({ perc }: { perc: number }) {
  const cls = perc >= 100 ? "done" : perc >= 50 ? "partial" : "low";
  return (
    <div className="dispatch-verify-bar" title={`Сборка: ${perc}%`}>
      <div className="dispatch-verify-bar-track">
        <div className={`dispatch-verify-bar-fill dispatch-verify-${cls}`} style={{ width: `${Math.min(perc, 100)}%` }} />
      </div>
      <span className="dispatch-verify-bar-label">{perc}%</span>
    </div>
  );
}

function DriverOwnerBadge({ isOwn, tkName }: { isOwn: number | null; tkName: string | null }) {
  if (isOwn === 1) return <span className="dispatch-own-badge">Свой</span>;
  if (isOwn === 0) return <span className="dispatch-hired-badge">{tkName ? tkName : "Наёмный"}</span>;
  return null;
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
// Demo data
// ---------------------------------------------------------------------------

function demoTasks(date: string): TransportTask[] {
  return [
    {
      ID: 1247, TRANSPORT: "Т368ХН", TRANSTYPE: "10", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: 6, VODITEL_NAME: "Сташков Иван Викторович",
      VODITEL_TEL: "8-952-74-109-09", TK_NAME: null, IS_OWN_DRIVER: 1,
      PRIMECHANIE: null, DOCK: "Д1", SHIPMENT_TIME: null,
      TEMP_REGION: "Москва, Химки, Лобня", REGIONS: "Москва, Химки, Лобня",
      TEMP_WEIGHT: 1800, PRICE: null, VOLUME_M3: 14.5, LOGIST: "ivanov",
      PAY_ORDER_ID: null, PALLET_COUNT: 12, ST_COUNT: 3, DELETED: 0,
      READY_PERC: 67, UNREADY_COUNT: 4,
    },
    {
      ID: 1248, TRANSPORT: "В703РО", TRANSTYPE: "15", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: 7, VODITEL_NAME: "Петров Алексей",
      VODITEL_TEL: null, TK_NAME: "ООО Транс-Авто", IS_OWN_DRIVER: 0,
      PRIMECHANIE: null, DOCK: "Д2", SHIPMENT_TIME: null,
      TEMP_REGION: "Красногорск", REGIONS: "Красногорск",
      TEMP_WEIGHT: 950, PRICE: null, VOLUME_M3: 7.2, LOGIST: "petrov",
      PAY_ORDER_ID: null, PALLET_COUNT: 8, ST_COUNT: 2, DELETED: 0,
      READY_PERC: 100, UNREADY_COUNT: 0,
    },
    {
      ID: 1249, TRANSPORT: null, TRANSTYPE: "10", CONDITION: "Спланирован",
      SHIPMENT_DATE: date, VODITEL_ID: null, VODITEL_NAME: null,
      VODITEL_TEL: null, TK_NAME: null, IS_OWN_DRIVER: null,
      PRIMECHANIE: null, DOCK: null, SHIPMENT_TIME: null,
      TEMP_REGION: null, REGIONS: null, TEMP_WEIGHT: null,
      PRICE: null, VOLUME_M3: null, LOGIST: null,
      PAY_ORDER_ID: null, PALLET_COUNT: 0, ST_COUNT: 0, DELETED: 0,
      READY_PERC: 0, UNREADY_COUNT: 0,
    },
  ];
}

function demoClusters(date: string): TransportCluster[] {
  const sts = demoAvailableSts(date);
  return [
    { RAION: "ЦАО", ST_COUNT: 1, PALLET_COUNT: 3, WEIGHT_KG: 450, VOLUME_M3: 2.1, STS: [sts[0]] },
    { RAION: "Химки", ST_COUNT: 1, PALLET_COUNT: 6, WEIGHT_KG: 890, VOLUME_M3: 4.2, STS: [sts[2]] },
    { RAION: "(без района)", ST_COUNT: 2, PALLET_COUNT: 9, WEIGHT_KG: 1400, VOLUME_M3: 6.8, STS: [sts[1], sts[3]] },
  ];
}

function demoAvailableSts(date: string): AvailableSt[] {
  return [
    { ST_NUMBER: "0441", ADDR: "Москва, ул. Ленина 5", REGION: "Москва", RAION: "ЦАО",
      PALLETS_COUNT: 3, WEIGHT_KG: 450, VOLUME_M3: 2.1, STDATE: date, DATE_LOAD: date,
      TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null,
      NAPR: null, WARE_ID: 5, VERIFY_PERC: 100, SUGAR: 0 },
    { ST_NUMBER: "0442", ADDR: "Красногорск, пр. Мира 12", REGION: "Красногорск", RAION: null,
      PALLETS_COUNT: 5, WEIGHT_KG: 780, VOLUME_M3: 3.8, STDATE: date, DATE_LOAD: date,
      TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null,
      NAPR: null, WARE_ID: 5, VERIFY_PERC: 75, SUGAR: 0 },
    { ST_NUMBER: "0443", ADDR: "Химки, ул. Победы 3", REGION: "Химки", RAION: null,
      PALLETS_COUNT: 6, WEIGHT_KG: 890, VOLUME_M3: 4.2, STDATE: date, DATE_LOAD: date,
      TRANSTASK_ID: null, TRANSPORT_TYPE: "15", NEEDS_HYDRO_BOARD: 1, STOL: 1, PRIM1: "Гидроборт",
      NAPR: null, WARE_ID: 6, VERIFY_PERC: 0, SUGAR: 1 },
    { ST_NUMBER: "0445", ADDR: "Лобня, ул. Свободы 8", REGION: "Лобня", RAION: null,
      PALLETS_COUNT: 4, WEIGHT_KG: 620, VOLUME_M3: 3.0, STDATE: date, DATE_LOAD: date,
      TRANSTASK_ID: null, TRANSPORT_TYPE: "10", NEEDS_HYDRO_BOARD: 0, STOL: 0, PRIM1: null,
      NAPR: null, WARE_ID: 7, VERIFY_PERC: 50, SUGAR: 0 },
  ];
}
