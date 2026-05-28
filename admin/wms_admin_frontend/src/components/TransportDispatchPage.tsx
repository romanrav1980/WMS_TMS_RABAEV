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
  VOLUME_M3: number | null;
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
const ST_PAGE_SIZE = 100;

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

async function downloadBlob(path: string, filename: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Basic ${btoa(API_BASIC_AUTH)}` },
  });
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
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

  // Sprint 49 — dense mode for STs table
  const [stDenseMode, setStDenseMode] = useState(false);

  // Sprint 52 — sortable STs table
  const [stSortField, setStSortField] = useState<string | null>(null);
  const [stSortDir, setStSortDir]     = useState<"asc" | "desc">("asc");

  // Sprint 60 — pagination for STs table
  const [stPage, setStPage] = useState(0);

  // Sprint 61 — warehouse quick-filter
  const [wareIdFilter, setWareIdFilter] = useState("");

  // Sprint 53 — collapsible filter panel
  const [fpCollapsed, setFpCollapsed] = useState(() => lsGet("tms_fpCollapsed", "0") === "1");

  // Sprint 47 — localStorage persistence helpers
  function lsGet(key: string, fallback: string): string {
    try { return localStorage.getItem(key) || fallback; } catch { return fallback; }
  }

  const [filterDate, setFilterDate] = useState(() => lsGet("tms_filterDate", todayIso()));
  const [stDate, setStDate] = useState(() => lsGet("tms_stDate", todayIso()));
  const [selectedStNums, setSelectedStNums] = useState<Set<string>>(new Set());

  const [viewMode, setViewMode] = useState<"flat" | "clusters">(
    () => (lsGet("tms_viewMode", "flat") as "flat" | "clusters")
  );
  const [clusters, setClusters] = useState<TransportCluster[]>([]);
  const [expandedRaions, setExpandedRaions] = useState<Set<string>>(new Set());

  // Filters (Sprint 78: checkbox filters persisted in localStorage)
  const [addrMask, setAddrMask] = useState("");
  const [stMask, setStMask] = useState("");
  const [stMaskExclude, setStMaskExclude] = useState(false);
  const [assembledOnly, setAssembledOnly] = useState(() => lsGet("tms_assembledOnly", "0") === "1");
  const [notAssembledOnly, setNotAssembledOnly] = useState(() => lsGet("tms_notAssembledOnly", "0") === "1");
  const [unassignedOnly, setUnassignedOnly] = useState(() => lsGet("tms_unassignedOnly", "1") === "1");
  const [dateTo, setDateTo] = useState<string>(() => lsGet("tms_dateTo", ""));
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

  // Sprint 42 — toast notifications
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  function showToast(msg: string) {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToastMsg(msg);
    toastTimerRef.current = setTimeout(() => setToastMsg(null), 3000);
  }
  const [createDialog, setCreateDialog] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editDraft, setEditDraft] = useState<TaskUpdateDraft>({});
  const editRef = useRef(editDraft);
  editRef.current = editDraft;
  const lastClickedIdxRef = useRef<number | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastRefreshAt, setLastRefreshAt] = useState<string>("");

  const [editingTranstypeId, setEditingTranstypeId] = useState<number | null>(null);
  const [palletStNum, setPalletStNum] = useState<string | null>(null);
  const [stPallets, setStPallets] = useState<StPalletRow[]>([]);
  const [palletLoading, setPalletLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"tasks" | "routes" | "billing">(
    () => (lsGet("tms_activeTab", "tasks") as "tasks" | "routes" | "billing")
  );
  const [routeShipDate, setRouteShipDate] = useState(() => lsGet("tms_routeShipDate", todayIso()));
  const [routeTaskId, setRouteTaskId] = useState("");
  const [routeCarMask, setRouteCarMask] = useState("");
  const [routeCompanyMask, setRouteCompanyMask] = useState("");
  const [routeDateTo, setRouteDateTo] = useState("");
  const [routeNoPayments, setRouteNoPayments] = useState(false);
  const [routesXlsxLoading, setRoutesXlsxLoading] = useState(false);
  const [routeBriefMode, setRouteBriefMode] = useState(false);
  const [selectedTripStNums, setSelectedTripStNums] = useState<Set<string>>(new Set());
  // Sprint 72 — inline filter within trip detail STs
  const [tripStFilter, setTripStFilter] = useState("");
  // Sprint 74 — collapse trip detail STs section
  const [tripDetailCollapsed, setTripDetailCollapsed] = useState(false);
  // Sprint 89 — show only unready STs in trip detail
  const [tripStUnreadyOnly, setTripStUnreadyOnly] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [billingDialog, setBillingDialog] = useState(false);
  const [openingBilling, setOpeningBilling] = useState(false);
  const [clusterCreateRaion, setClusterCreateRaion] = useState<string | null>(null);
  const [clusterCreateLoading, setClusterCreateLoading] = useState(false);
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
  // Sprint 47 — persist key state to localStorage
  useEffect(() => { try { localStorage.setItem("tms_filterDate",   filterDate);   } catch { /* */ } }, [filterDate]);
  useEffect(() => { try { localStorage.setItem("tms_routeShipDate", routeShipDate); } catch { /* */ } }, [routeShipDate]);
  useEffect(() => { try { localStorage.setItem("tms_viewMode",     viewMode);     } catch { /* */ } }, [viewMode]);
  useEffect(() => { try { localStorage.setItem("tms_activeTab",    activeTab);    } catch { /* */ } }, [activeTab]);
  useEffect(() => { try { localStorage.setItem("tms_fpCollapsed",  fpCollapsed ? "1" : "0"); } catch { /* */ } }, [fpCollapsed]);
  // Sprint 78 — persist filter checkbox state
  useEffect(() => { try { localStorage.setItem("tms_unassignedOnly",    unassignedOnly    ? "1" : "0"); } catch { /* */ } }, [unassignedOnly]);
  useEffect(() => { try { localStorage.setItem("tms_assembledOnly",     assembledOnly     ? "1" : "0"); } catch { /* */ } }, [assembledOnly]);
  useEffect(() => { try { localStorage.setItem("tms_notAssembledOnly",  notAssembledOnly  ? "1" : "0"); } catch { /* */ } }, [notAssembledOnly]);
  // Sprint 82 — persist ST date and date-to filter
  useEffect(() => { try { localStorage.setItem("tms_stDate",  stDate);  } catch { /* */ } }, [stDate]);
  useEffect(() => { try { localStorage.setItem("tms_dateTo",  dateTo);  } catch { /* */ } }, [dateTo]);

  // Sprint 44 — global Escape handler
  // Sprint 68 — Ctrl+Enter: assign selected STs to current trip
  // Sprint 69 — Delete: bulk-unassign selected trip STs
  // ------------------------------------------------------------------
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement;
      const tag = target.tagName;
      const inputType = tag === "INPUT" ? ((target as HTMLInputElement).type || "text") : "";
      const inTextInput = tag === "TEXTAREA"
        || tag === "SELECT"
        || (tag === "INPUT" && !["checkbox", "radio", "button", "submit"].includes(inputType));
      // Ctrl+Enter → add selected STs to trip
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        if (inTextInput) return;
        if (selectedStNums.size > 0 && selectedTask && activeTab === "tasks") {
          e.preventDefault();
          handleAssign();
        }
        return;
      }
      // Delete → unassign selected trip STs
      if (e.key === "Delete") {
        if (inTextInput) return;
        if (selectedTripStNums.size > 0 && selectedTask && activeTab === "tasks") {
          e.preventDefault();
          handleBulkUnassign();
        }
        return;
      }
      if (e.key !== "Escape") return;
      if (inTextInput) return;
      if (createDialog) { setCreateDialog(false); return; }
      if (clusterCreateRaion) { setClusterCreateRaion(null); return; }
      if (editMode) { setEditMode(false); return; }
      if (selectedStNums.size > 0) { setSelectedStNums(new Set()); return; }
      if (selectedTripStNums.size > 0) { setSelectedTripStNums(new Set()); }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [createDialog, clusterCreateRaion, editMode, selectedStNums, selectedTripStNums, selectedTask, activeTab]);

  // ------------------------------------------------------------------
  // Auto-refresh every 60 s (Sprint 37)
  // ------------------------------------------------------------------
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(() => {
      if (loading || createDialog || editMode || clusterCreateRaion || billingDialog) return;
      loadAvailableSts();
      loadTasks();
      if (viewMode === "clusters") loadClusters();
      setLastRefreshAt(new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }));
    }, 60_000);
    return () => clearInterval(id);
  }, [autoRefresh, loading, createDialog, editMode, clusterCreateRaion, billingDialog,
      loadAvailableSts, loadTasks, loadClusters, viewMode]);

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
    setSelectedTripStNums(new Set());
    setTripStFilter(""); // Sprint 72: reset filter on task switch
    setTripDetailCollapsed(false); // Sprint 74: expand detail on task switch
    setTripStUnreadyOnly(false); // Sprint 89: reset unready-only toggle on task switch
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
    setError(null);
    try {
      const res = await apiFetch<{ task_id: number; price: number }>(
        `/api/admin/transport/tasks/${selectedTask.ID}/recalculate-price`,
        { method: "POST" }
      );
      setSelectedTask(prev => prev ? { ...prev, PRICE: res.price } : prev);
      setTasks(prev => prev.map(t => t.ID === selectedTask.ID ? { ...t, PRICE: res.price } : t));
    } catch (e) { setError(String(e)); } finally { setPriceRecalcLoading(false); }
  }

  async function handleSetPrice(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedTask || !manualPrice) return;
    const price = parseFloat(manualPrice);
    if (isNaN(price) || price < 0) return;
    setPriceLoading(true);
    setError(null);
    try {
      await apiFetch(`/api/admin/transport/tasks/${selectedTask.ID}/price`, {
        method: "PATCH",
        body: JSON.stringify({ price }),
      });
      setSelectedTask(prev => prev ? { ...prev, PRICE: price } : prev);
      setTasks(prev => prev.map(t => t.ID === selectedTask.ID ? { ...t, PRICE: price } : t));
      setManualPrice("");
    } catch (e) { setError(String(e)); } finally { setPriceLoading(false); }
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
  // Sprint 57 — quick add ST by number
  const [quickAddInput, setQuickAddInput] = useState("");

  async function handleQuickAddSt() {
    const num = quickAddInput.trim();
    if (!selectedTask || !num) return;
    setLoading(true);
    try {
      const result = await apiFetch<{ assigned: number; warnings: string[] }>(
        `/api/admin/transport/tasks/${selectedTask.ID}/sts`,
        { method: "POST", body: JSON.stringify({ st_numbers: [num] }) }
      );
      if (result.warnings.length > 0) setError(result.warnings.join("; "));
      setQuickAddInput("");
      const reloads: Promise<void>[] = [selectTask(selectedTask), loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
      showToast(`СТ ${num} добавлен в рейс #${selectedTask.ID}`);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

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
      showToast(`${result.assigned} СТ добавлено в рейс #${selectedTask.ID}`);
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

  async function handleBulkUnassign() {
    if (!selectedTask || selectedTripStNums.size === 0) return;
    if (!confirm(`Снять ${selectedTripStNums.size} СТ с рейса #${selectedTask.ID}?`)) return;
    setLoading(true);
    try {
      await Promise.all(
        Array.from(selectedTripStNums).map(st =>
          apiFetch(
            `/api/admin/transport/tasks/${selectedTask.ID}/sts/${encodeURIComponent(st)}`,
            { method: "DELETE" }
          )
        )
      );
      const unassignedCount = selectedTripStNums.size;
      setSelectedTripStNums(new Set());
      const reloads: Promise<void>[] = [selectTask(selectedTask), loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
      showToast(`${unassignedCount} СТ снято с рейса #${selectedTask.ID}`);
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
      showToast(`Рейс #${taskId} создан`);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleCreateFromCluster(params: {
    raion: string; transtype: string; vehicle: string; driver_id: number | null; dock: string;
  }) {
    setClusterCreateLoading(true);
    try {
      const res = await apiFetch<{ task_id: number; st_count: number; warnings: string[] }>(
        `/api/admin/transport/clusters/${encodeURIComponent(params.raion)}/create-task`,
        {
          method: "POST",
          body: JSON.stringify({
            stdate: stDate,
            transtype: params.transtype,
            vehicle: params.vehicle || null,
            driver_id: params.driver_id,
            dock: params.dock || null,
            ware_ids: null,
          }),
        }
      );
      if (res.warnings.length > 0) setError(res.warnings.join("; "));
      setClusterCreateRaion(null);
      await Promise.all([loadTasks(), loadClusters(), loadAvailableSts()]);
      const newTask = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${res.task_id}`);
      setActiveTab("tasks");
      selectTask(newTask);
      showToast(`Рейс #${res.task_id} создан из кластера «${params.raion}», ${res.st_count} СТ`);
    } catch (e) { setError(String(e)); } finally { setClusterCreateLoading(false); }
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
    // Sprint 87 — warn if any trip STs are not fully assembled
    const unreadyCount = taskSts.filter(s => s.VERIFY_PERC !== null && s.VERIFY_PERC < 100).length;
    const confirmMsg = unreadyCount > 0
      ? `⚠ ${unreadyCount} из ${taskSts.length} СТ не полностью собраны.\nЗакрыть рейс #${selectedTask.ID} как отгруженный?`
      : `Закрыть рейс #${selectedTask.ID} как отгруженный?`;
    if (!confirm(confirmMsg)) return;
    const closedId = selectedTask.ID;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${closedId}/close`, { method: "POST" });
      setSelectedTask(null); setTaskSts([]);
      await loadTasks();
      showToast(`Рейс #${closedId} закрыт`);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  async function handleCancel() {
    if (!selectedTask) return;
    if (!confirm(`Отменить рейс #${selectedTask.ID}? Это действие необратимо.`)) return;
    const cancelledId = selectedTask.ID;
    setLoading(true);
    try {
      await apiFetch(`/api/admin/transport/tasks/${cancelledId}/cancel`, { method: "POST" });
      setSelectedTask(null); setTaskSts([]);
      await loadTasks();
      showToast(`Рейс #${cancelledId} отменён`);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  // Sprint 88 — reschedule trip to next day
  async function handleRescheduleNextDay() {
    if (!selectedTask) return;
    const newDate = shiftDate(selectedTask.SHIPMENT_DATE ?? todayIso(), 1);
    if (!confirm(`Перенести рейс #${selectedTask.ID} на ${newDate}?`)) return;
    setLoading(true);
    try {
      await apiFetch(
        `/api/admin/transport/tasks/${selectedTask.ID}`,
        { method: "PATCH", body: JSON.stringify({ shipment_date: newDate }) }
      );
      const updated = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${selectedTask.ID}`);
      setSelectedTask(updated);
      setTasks(prev => prev.map(t => t.ID === updated.ID ? updated : t));
      showToast(`Рейс #${selectedTask.ID} перенесён на ${newDate}`);
    } catch (e) { setError(String(e)); } finally { setLoading(false); }
  }

  // Sprint 38 — copy trip
  function handlePrintRoute() {
    if (!selectedTask || taskSts.length === 0) return;
    const task = selectedTask;
    const sts = taskSts;
    const date = task.SHIPMENT_DATE ?? "";
    const rows = sts.map((s, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${s.ORD ?? "—"}</td>
        <td>${s.ADDR ?? ""}</td>
        <td>${s.RAION ?? ""}</td>
        <td>${s.PALLETS_COUNT}</td>
        <td>${s.WEIGHT_KG.toFixed(0)}</td>
        <td style="min-width:80px">&nbsp;</td>
      </tr>`).join("");
    const html = `<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
      <title>Маршрутный лист №${task.ID}</title>
      <style>
        body { font: 12px Arial, sans-serif; margin: 20px; }
        h2 { font-size: 14px; margin-bottom: 4px; }
        .meta { font-size: 12px; margin-bottom: 12px; border: 1px solid #aaa; padding: 6px 10px; }
        .meta span { margin-right: 24px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #888; padding: 4px 6px; font-size: 11px; }
        th { background: #f0f0f0; }
        tfoot td { font-weight: bold; }
        @media print { @page { size: A4 portrait; margin: 15mm; } }
      </style></head><body>
      <h2>Маршрутный лист — Рейс #${task.ID}</h2>
      <div class="meta">
        <span>Дата: <b>${date}</b></span>
        <span>Машина: <b>${task.TRANSPORT ?? "—"}</b>${task.TRANSTYPE ? ` (${task.TRANSTYPE})` : ""}</span>
        <span>Водитель: <b>${task.VODITEL_NAME ?? "—"}</b></span>
        <span>Док: <b>${task.DOCK ?? "—"}</b></span>
        <span>Статус: <b>${task.CONDITION ?? "Новый"}</b></span>
      </div>
      <table>
        <thead><tr>
          <th>#</th><th>Пор.</th><th>Адрес</th><th>Район</th>
          <th>Пал.</th><th>Вес кг</th><th>Подпись</th>
        </tr></thead>
        <tbody>${rows}</tbody>
        <tfoot><tr>
          <td colspan="4">ИТОГО</td>
          <td>${sts.reduce((s, x) => s + x.PALLETS_COUNT, 0)}</td>
          <td>${sts.reduce((s, x) => s + x.WEIGHT_KG, 0).toFixed(0)}</td>
          <td></td>
        </tr></tfoot>
      </table>
      <script>window.onload=()=>{window.print();}<\/script>
      </body></html>`;
    const w = window.open("", "_blank");
    if (w) { w.document.write(html); w.document.close(); }
  }

  async function handleCopyTask() {
    if (!selectedTask) return;
    setLoading(true);
    try {
      const res = await apiFetch<{ task_id: number }>(
        "/api/admin/transport/tasks",
        { method: "POST", body: JSON.stringify({ transtype: selectedTask.TRANSTYPE, shipment_date: selectedTask.SHIPMENT_DATE }) }
      );
      const taskId = res.task_id;
      const patch: Record<string, string | number | null> = {};
      if (selectedTask.TRANSPORT)   patch.transport   = selectedTask.TRANSPORT;
      if (selectedTask.VODITEL_ID)  patch.voditel_id  = selectedTask.VODITEL_ID;
      if (selectedTask.DOCK)        patch.dock        = selectedTask.DOCK;
      if (selectedTask.SHIPMENT_TIME) patch.shipment_time = selectedTask.SHIPMENT_TIME;
      if (Object.keys(patch).length > 0) {
        await apiFetch(`/api/admin/transport/tasks/${taskId}`, {
          method: "PATCH",
          body: JSON.stringify(patch),
        });
      }
      const reloads: Promise<unknown>[] = [loadTasks(), loadAvailableSts()];
      if (viewMode === "clusters") reloads.push(loadClusters());
      await Promise.all(reloads);
      const newTask = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${taskId}`);
      setActiveTab("tasks");
      selectTask(newTask);
      showToast(`Рейс #${taskId} создан как копия рейса #${selectedTask.ID}`);
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

  async function handleDetachFromBilling() {
    if (!billingOrder || !selectedTask) return;
    if (billingOrder.closed || billingOrder.payed) {
      setError("Нельзя снять рейс с закрытого или оплаченного счёта");
      return;
    }
    if (!confirm(`Снять рейс #${selectedTask.ID} со счёта ${billingOrder.num ?? `#${billingOrder.order_id}`}?`)) return;
    setBillingActionLoading(true);
    try {
      await apiFetch(
        `/api/admin/transport/billing/orders/${billingOrder.order_id}/tasks/${selectedTask.ID}`,
        { method: "DELETE" }
      );
      const updated = { ...selectedTask, PAY_ORDER_ID: null };
      setSelectedTask(updated);
      setTasks(prev => prev.map(t => t.ID === updated.ID ? updated : t));
      setBillingOrder(null);
    } catch (e) { setError(String(e)); } finally { setBillingActionLoading(false); }
  }

  async function handleRoutesXlsx() {
    setRoutesXlsxLoading(true);
    try {
      const p = new URLSearchParams();
      if (routeShipDate) p.set("shipment_date", routeShipDate);
      if (routeDateTo) p.set("date_to", routeDateTo);
      if (routeTaskId) p.set("task_id", routeTaskId);
      if (routeCarMask) p.set("transport_mask", routeCarMask);
      if (routeCompanyMask) p.set("company_mask", routeCompanyMask);
      if (routeNoPayments) p.set("no_payments_only", "true");
      await downloadBlob(
        `/api/admin/transport/tasks/export.xlsx?${p}`,
        `transport_tasks_${routeShipDate || "all"}.xlsx`,
      );
    } catch (e) { setError(String(e)); } finally { setRoutesXlsxLoading(false); }
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

  // Sprint 45 — jump from assigned ST to its trip in the routes tab
  async function handleGotoTrip(taskId: number) {
    setActiveTab("routes");
    const found = tasks.find(t => t.ID === taskId);
    if (found) { selectTask(found); return; }
    try {
      const task = await apiFetch<TransportTask>(`/api/admin/transport/tasks/${taskId}`);
      setRouteShipDate(task.SHIPMENT_DATE ?? routeShipDate);
      await loadTasks();
      selectTask(task);
    } catch { /* ignore */ }
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

  function toggleStSort(field: string) {
    if (stSortField === field) {
      setStSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setStSortField(field);
      setStSortDir("asc");
    }
  }

  // Sprint 61 — warehouse quick-filter (client-side)
  const wareOptions = [...new Set(availableSts.map(s => s.WARE_ID))].sort((a, b) => a - b);
  const wareFilteredSts = wareIdFilter
    ? availableSts.filter(s => String(s.WARE_ID) === wareIdFilter)
    : availableSts;

  const sortedSts = stSortField
    ? [...wareFilteredSts].sort((a, b) => {
        const va = (a as Record<string, unknown>)[stSortField] ?? "";
        const vb = (b as Record<string, unknown>)[stSortField] ?? "";
        const cmp = va < vb ? -1 : va > vb ? 1 : 0;
        return stSortDir === "asc" ? cmp : -cmp;
      })
    : wareFilteredSts;

  // Sprint 60 — paginated slice; reset to page 0 when data, sort, or ware-filter changes
  useEffect(() => { setStPage(0); }, [availableSts, stSortField, stSortDir, wareIdFilter]);
  const stTotalPages = Math.max(1, Math.ceil(sortedSts.length / ST_PAGE_SIZE));
  const pagedSts = sortedSts.slice(stPage * ST_PAGE_SIZE, (stPage + 1) * ST_PAGE_SIZE);

  function handleStToggle(stNum: string, idx: number) {
    lastClickedIdxRef.current = idx;
    toggleSt(stNum);
  }

  function handleShiftClick(idx: number) {
    const last = lastClickedIdxRef.current;
    if (last === null) { handleStToggle(sortedSts[idx].ST_NUMBER, idx); return; }
    const [a, b] = [Math.min(last, idx), Math.max(last, idx)];
    const range = sortedSts.slice(a, b + 1).map(s => s.ST_NUMBER);
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
  // Sprint 39 — active filter count + reset
  // ------------------------------------------------------------------
  const activeFilterCount = [
    addrMask,
    stMask,
    stMaskExclude,
    assembledOnly,
    notAssembledOnly,
    !unassignedOnly,
    dateTo,
    maxWeightKg != null,
    maxVolM3 != null,
    trTypeFilter,
    articulFilter,
  ].filter(Boolean).length;

  function handleResetFilters() {
    setAddrMask("");
    setStMask("");
    setStMaskExclude(false);
    setAssembledOnly(false);
    setNotAssembledOnly(false);
    setUnassignedOnly(true);
    setDateTo("");
    setMaxWeightKg(null);
    setMaxVolM3(null);
    setTrTypeFilter("");
    setArticulFilter("");
  }

  // Sprint 46 — date step helpers (±1 day)
  function shiftDate(iso: string, days: number): string {
    const d = new Date(iso);
    d.setDate(d.getDate() + days);
    return d.toISOString().slice(0, 10);
  }

  // ------------------------------------------------------------------
  // PMV counters
  // ------------------------------------------------------------------
  const selSts = availableSts.filter(s => selectedStNums.has(s.ST_NUMBER));
  const selP = selSts.reduce((s, x) => s + (x.PALLETS_COUNT || 0), 0);
  const selM = selSts.reduce((s, x) => s + (x.WEIGHT_KG || 0), 0);
  const selV = selSts.reduce((s, x) => s + (x.VOLUME_M3 || 0), 0);

  // Sprint 55 — totals for ALL visible STs (Sprint 61: warehouse-filtered)
  const allP = wareFilteredSts.reduce((s, x) => s + (x.PALLETS_COUNT || 0), 0);
  const allM = wareFilteredSts.reduce((s, x) => s + (x.WEIGHT_KG || 0), 0);
  const allV = wareFilteredSts.reduce((s, x) => s + (x.VOLUME_M3 || 0), 0);
  const tripP = taskSts.reduce((s, x) => s + (x.PALLETS_COUNT || 0), 0);
  const tripM = taskSts.reduce((s, x) => s + (x.WEIGHT_KG || 0), 0);
  const tripV = taskSts.reduce((s, x) => s + (x.VOLUME_M3 || 0), 0);

  // Sprint 72 — filter within trip detail STs
  // Sprint 89 — also filter by unready-only toggle
  const filteredTaskSts = (() => {
    let sts = taskSts;
    if (tripStFilter) {
      const q = tripStFilter.toLowerCase();
      sts = sts.filter(s =>
        s.ST_NUMBER.toLowerCase().includes(q)
        || (s.ADDR ?? "").toLowerCase().includes(q)
        || (s.REGION ?? "").toLowerCase().includes(q)
      );
    }
    if (tripStUnreadyOnly) {
      sts = sts.filter(s => s.VERIFY_PERC !== null && s.VERIFY_PERC < 100);
    }
    return sts;
  })();

  const selectedVehicle = vehicles.find(v => v.NUM === selectedTask?.TRANSPORT);

  // Sprint 40 — day summary (computed from already-loaded tasks list)
  const dayTotalTasks   = tasks.length;
  const dayTotalPallets = tasks.reduce((s, t) => s + (t.PALLET_COUNT || 0), 0);
  const dayTotalWeight  = tasks.reduce((s, t) => s + (t.TEMP_WEIGHT  || 0), 0);
  const dayClosedTasks  = tasks.filter(t => t.CONDITION === "Отгружен").length;

  // Sprint 43 — sortable trips table (tasks tab)
  const [tasksSortField, setTasksSortField] = useState<string | null>(null);
  const [tasksSortDir, setTasksSortDir]   = useState<"asc" | "desc">("asc");

  function toggleTasksSort(field: string) {
    if (tasksSortField === field) {
      setTasksSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setTasksSortField(field);
      setTasksSortDir("asc");
    }
  }

  const sortedTasks = tasksSortField
    ? [...tasks].sort((a, b) => {
        const vaRaw = (a as Record<string, unknown>)[tasksSortField];
        const vbRaw = (b as Record<string, unknown>)[tasksSortField];
        const aEmpty = vaRaw == null || vaRaw === "";
        const bEmpty = vbRaw == null || vbRaw === "";
        if (aEmpty && bEmpty) return 0;
        if (aEmpty) return 1;
        if (bEmpty) return -1;
        const va = typeof vaRaw === "string" ? vaRaw.toLowerCase() : vaRaw;
        const vb = typeof vbRaw === "string" ? vbRaw.toLowerCase() : vbRaw;
        const cmp = va < vb ? -1 : va > vb ? 1 : 0;
        return tasksSortDir === "asc" ? cmp : -cmp;
      })
    : tasks;

  // Sprint 41 — client-side status filter for routes tab
  const [routeCondFilter, setRouteCondFilter] = useState<"all" | "active" | "closed" | "cancelled">("all");
  const routeCondCounts = {
    active:    tasks.filter(t => t.CONDITION !== "Отгружен" && t.CONDITION !== "Отменён").length,
    closed:    tasks.filter(t => t.CONDITION === "Отгружен").length,
    cancelled: tasks.filter(t => t.CONDITION === "Отменён").length,
  };
  const filteredRouteTasks = routeCondFilter === "all"       ? tasks
    : routeCondFilter === "active"    ? tasks.filter(t => t.CONDITION !== "Отгружен" && t.CONDITION !== "Отменён")
    : routeCondFilter === "closed"    ? tasks.filter(t => t.CONDITION === "Отгружен")
    : tasks.filter(t => t.CONDITION === "Отменён");

  // Sprint 59 — quick search in routes tab
  const [routeSearchQuery, setRouteSearchQuery] = useState("");
  const searchedRouteTasks = routeSearchQuery.trim()
    ? filteredRouteTasks.filter(t => {
        const q = routeSearchQuery.trim().toLowerCase();
        return (
          String(t.ID).includes(q) ||
          (t.TRANSPORT ?? "").toLowerCase().includes(q) ||
          (t.VODITEL_NAME ?? "").toLowerCase().includes(q) ||
          (t.REGIONS ?? "").toLowerCase().includes(q) ||
          (t.TK_NAME ?? "").toLowerCase().includes(q)
        );
      })
    : filteredRouteTasks;

  // Sprint 85 — routes tab summary (visible trips aggregate)
  const routeTotalPallets = searchedRouteTasks.reduce((s, t) => s + (t.PALLET_COUNT || 0), 0);
  const routeTotalWeight  = searchedRouteTasks.reduce((s, t) => s + (t.TEMP_WEIGHT  || 0), 0);
  const routeClosedCount  = searchedRouteTasks.filter(t => t.CONDITION === "Отгружен").length;

  // Sprint 81 — ↑/↓ keyboard navigation between trips
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key !== "ArrowUp" && e.key !== "ArrowDown") return;
      const tag = (e.target as HTMLElement).tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
      const list = activeTab === "tasks" ? sortedTasks : searchedRouteTasks;
      if (list.length === 0) return;
      e.preventDefault();
      const idx = selectedTask ? list.findIndex(t => t.ID === selectedTask.ID) : -1;
      const next = e.key === "ArrowDown"
        ? (list[idx + 1] ?? list[0])
        : (list[idx - 1] ?? list[list.length - 1]);
      if (next) selectTask(next);
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [activeTab, sortedTasks, searchedRouteTasks, selectedTask]);

  // Sprint 81 — scroll selected trip row into view on keyboard navigation
  useEffect(() => {
    if (!selectedTask) return;
    document.querySelector(`[data-taskid="${selectedTask.ID}"]`)
      ?.scrollIntoView({ block: "nearest" });
  }, [selectedTask]);

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

      {/* Sprint 42 — toast notification */}
      {toastMsg && (
        <div className="dispatch-toast" onClick={() => setToastMsg(null)}>
          ✓ {toastMsg}
        </div>
      )}

      <div className="dispatch-workspace">
        {/* ============================================================
            LEFT — Cluster sidebar (Sprint 31, visible when clusters mode)
            ============================================================ */}
        {viewMode === "clusters" && activeTab === "tasks" && (
          <ClusterSidebar
            clusters={clusters}
            expandedRaions={expandedRaions}
            onToggle={toggleRaion}
            onCreateTask={raion => setClusterCreateRaion(raion)}
          />
        )}

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
              {/* Sprint 65 — selection count badge */}
              {selectedStNums.size > 0 && (
                <span className="dispatch-tab-badge">{selectedStNums.size}</span>
              )}
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
            {viewMode === "clusters" && (
              <div className="dispatch-cluster-expand-btns">
                <button className="dispatch-cluster-exp-btn" title="Развернуть все районы"
                  onClick={() => setExpandedRaions(new Set(clusters.map(c => c.RAION)))}>⊞ Все</button>
                <button className="dispatch-cluster-exp-btn" title="Свернуть все районы"
                  onClick={() => setExpandedRaions(new Set())}>⊟ Нет</button>
              </div>
            )}
            <span className="dispatch-pmv dispatch-pmv-all" title="Итоги по всем видимым СТ">
              П={allP}&nbsp;·&nbsp;{allM.toFixed(0)}&nbsp;кг&nbsp;·&nbsp;{allV.toFixed(1)}&nbsp;м³
            </span>
            {selectedStNums.size > 0 && selectedTask && (
              <button className="dispatch-add-btn" onClick={handleAssign} disabled={loading}
                title="Ctrl+Enter">
                Добавить в рейс #{selectedTask.ID}
              </button>
            )}
            {selectedStNums.size > 0 && !selectedTask && (
              <span className="dispatch-hint">↓ Выберите рейс</span>
            )}
            <button className="dispatch-refresh-btn"
              onClick={() => { loadAvailableSts(); if (viewMode === "clusters") loadClusters(); }}
              title="Обновить список СТ">⟳</button>
            <label className="dispatch-autorefresh-toggle" title="Автообновление каждые 60 сек">
              <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
              Авто
            </label>
            {autoRefresh && lastRefreshAt && <span className="dispatch-last-refresh">{lastRefreshAt}</span>}
            {/* Sprint 61 — warehouse quick-filter */}
            {wareOptions.length > 1 && (
              <select className="dispatch-ware-select"
                value={wareIdFilter}
                onChange={e => { setWareIdFilter(e.target.value); setSelectedStNums(new Set()); }}
                title="Фильтр по складу">
                <option value="">Все склады</option>
                {wareOptions.map(w => (
                  <option key={w} value={String(w)}>Скл. {w}</option>
                ))}
              </select>
            )}
            <span className="dispatch-tcount">
              {wareIdFilter
                ? `${wareFilteredSts.length} / ${availableSts.length} СТ`
                : `${availableSts.length} СТ`}
            </span>
            {/* Sprint 63 — not-assembled badge; Sprint 64 — click to select */}
            {(() => {
              const notReadySts = wareFilteredSts.filter(s => s.VERIFY_PERC != null && s.VERIFY_PERC < 100);
              return notReadySts.length > 0
                ? <button className="dispatch-notready-badge dispatch-notready-select-btn"
                    title="Кликни, чтобы выделить все несобранные СТ"
                    onClick={() => setSelectedStNums(prev => {
                      const next = new Set(prev);
                      notReadySts.forEach(s => next.add(s.ST_NUMBER));
                      return next;
                    })}>
                    ⚠ {notReadySts.length} не собрано
                  </button>
                : null;
            })()}
            {/* Sprint 49 — dense mode toggle */}
            <label className="dispatch-dense-toggle" title="Компактный режим: уменьшить отступы в таблице СТ">
              <input type="checkbox" checked={stDenseMode} onChange={e => setStDenseMode(e.target.checked)} />
              Компактно
            </label>
          </div>

          {/* ---- Available STs table ---- */}
          <div className="dispatch-st-section">
            <table className={`dispatch-grid${stDenseMode ? " dispatch-grid-dense" : ""}`}>
              <thead>
                <tr>
                  <th style={{ width: 22 }}>
                    {viewMode === "flat" && sortedSts.length > 0 && (
                      <input
                        type="checkbox"
                        title="Выделить / снять все"
                        checked={sortedSts.length > 0 && sortedSts.every(s => selectedStNums.has(s.ST_NUMBER))}
                        onChange={() => {
                          const allSelected = sortedSts.every(s => selectedStNums.has(s.ST_NUMBER));
                          if (allSelected) {
                            setSelectedStNums(new Set());
                          } else {
                            setSelectedStNums(new Set(sortedSts.map(s => s.ST_NUMBER)));
                          }
                        }}
                      />
                    )}
                  </th>
                  <th className="dispatch-sortable-th" title="Склад" onClick={() => toggleStSort("WARE_ID")}>Скл{stSortField === "WARE_ID" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("PALLETS_COUNT")}>Пал.{stSortField === "PALLETS_COUNT" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("WEIGHT_KG")}>Вес{stSortField === "WEIGHT_KG" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("VOLUME_M3")}>Объём{stSortField === "VOLUME_M3" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("REGION")}>Регион{stSortField === "REGION" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("ADDR")}>Адрес{stSortField === "ADDR" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("ST_NUMBER")}>СТ №{stSortField === "ST_NUMBER" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("TRANSTASK_ID")}>В рейсе{stSortField === "TRANSTASK_ID" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("STDATE")}>Дата СТ{stSortField === "STDATE" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("VERIFY_PERC")}>%{stSortField === "VERIFY_PERC" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("RAION")}>Район{stSortField === "RAION" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" onClick={() => toggleStSort("TRANSPORT_TYPE")}>Тип ТС{stSortField === "TRANSPORT_TYPE" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th className="dispatch-sortable-th" title="Направление" onClick={() => toggleStSort("NAPR")}>Напр.{stSortField === "NAPR" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                  <th title="Стол-лифт">Стол</th>
                  <th title="Примечание">Прим.</th>
                  <th className="dispatch-sortable-th" title="Полнопалетная отборка" onClick={() => toggleStSort("SUGAR")}>Полнопал.{stSortField === "SUGAR" ? (stSortDir === "asc" ? " ▲" : " ▼") : ""}</th>
                </tr>
              </thead>
              <tbody>
                {viewMode === "flat" && (
                  sortedSts.length === 0
                    ? <tr><td colSpan={17} className="dispatch-grid-empty">Нет свободных СТ по текущим фильтрам</td></tr>
                    : pagedSts.map((st, pageIdx) => {
                        const idx = stPage * ST_PAGE_SIZE + pageIdx;
                        return (
                          <AvailableStRow key={st.ST_NUMBER} st={st} idx={idx}
                            checked={selectedStNums.has(st.ST_NUMBER)}
                            onToggle={() => handleStToggle(st.ST_NUMBER, idx)}
                            onShiftClick={handleShiftClick}
                            onSelectByField={handleSelectByField}
                            onGotoTrip={handleGotoTrip} />
                        );
                      })
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
                          onCreateTask={() => setClusterCreateRaion(cluster.RAION)}
                        />
                      ))
                )}
              </tbody>
            </table>
          </div>

          {/* Sprint 60 — pagination bar */}
          {viewMode === "flat" && stTotalPages > 1 && (
            <div className="dispatch-st-pagination">
              <button className="dispatch-page-btn" onClick={() => setStPage(0)} disabled={stPage === 0}>◄◄</button>
              <button className="dispatch-page-btn" onClick={() => setStPage(p => p - 1)} disabled={stPage === 0}>◄</button>
              <span className="dispatch-page-info">Стр. {stPage + 1} из {stTotalPages} · {sortedSts.length} СТ</span>
              <button className="dispatch-page-btn" onClick={() => setStPage(p => p + 1)} disabled={stPage >= stTotalPages - 1}>►</button>
              <button className="dispatch-page-btn" onClick={() => setStPage(stTotalPages - 1)} disabled={stPage >= stTotalPages - 1}>►►</button>
            </div>
          )}

          {/* Sprint 51 — sticky selection bar */}
          {selectedStNums.size > 0 && (
            <div className="dispatch-sel-bar">
              <span className="dispatch-sel-bar-count">{selectedStNums.size} выбр.</span>
              <span className="dispatch-sel-bar-sep">·</span>
              <span className="dispatch-sel-bar-stat">P={selP}</span>
              <span className="dispatch-sel-bar-sep">·</span>
              <span className="dispatch-sel-bar-stat">M={selM.toFixed(0)} кг</span>
              <span className="dispatch-sel-bar-sep">·</span>
              <span className="dispatch-sel-bar-stat">V={selV.toFixed(2)} м³</span>
              <button className="dispatch-sel-bar-create" onClick={() => setCreateDialog(true)}>+ Создать маршрут</button>
              {selectedTask && (
                <button className="dispatch-sel-bar-add" onClick={handleAssign} disabled={loading}
                  title="Ctrl+Enter">
                  Добавить в #{selectedTask.ID}
                </button>
              )}
              <button className="dispatch-sel-bar-csv" onClick={() => exportSelectedStsCsv(selSts, stDate)} title="Скачать выделенные СТ в CSV">⬇ CSV</button>
              <button className="dispatch-sel-bar-clear" onClick={() => setSelectedStNums(new Set())} title="Снять выделение">✕</button>
            </div>
          )}

          {/* ---- Trips table ---- */}
          <div className="dispatch-trips-section">
            <div className="dispatch-trips-toolbar">
              <b>Рейсы на</b>
              <button className="dispatch-day-step-btn" onClick={() => setFilterDate(d => shiftDate(d, -1))} title="Предыдущий день">◄</button>
              <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
              <button className="dispatch-day-step-btn" onClick={() => setFilterDate(d => shiftDate(d, 1))} title="Следующий день">►</button>
              {filterDate !== todayIso() && (
                <button className="dispatch-today-btn" onClick={() => setFilterDate(todayIso())} title="Перейти к сегодня">Сегодня</button>
              )}
              <button className="dispatch-new-btn" onClick={() => setCreateDialog(true)}>
                {selectedStNums.size > 0 ? `+ Создать маршрут (${selectedStNums.size})` : "+ Создать маршрут"}
              </button>
              <button className="dispatch-refresh-btn" onClick={loadTasks} title="Обновить рейсы">⟳</button>
              <span className="dispatch-tcount">{tasks.length} рейс(ов)</span>
            </div>
            {/* Sprint 40 — day summary strip */}
            {dayTotalTasks > 0 && (
              <div className="dispatch-day-summary">
                <span className="dispatch-ds-item">
                  <span className="dispatch-ds-label">Рейсов</span>
                  <span className="dispatch-ds-value">{dayTotalTasks}</span>
                </span>
                <span className="dispatch-ds-sep">·</span>
                <span className="dispatch-ds-item">
                  <span className="dispatch-ds-label">Паллет</span>
                  <span className="dispatch-ds-value">{dayTotalPallets}</span>
                </span>
                <span className="dispatch-ds-sep">·</span>
                <span className="dispatch-ds-item">
                  <span className="dispatch-ds-label">Вес кг</span>
                  <span className="dispatch-ds-value">{dayTotalWeight.toFixed(0)}</span>
                </span>
                <span className="dispatch-ds-sep">·</span>
                <span className="dispatch-ds-item">
                  <span className="dispatch-ds-label">Отгружено</span>
                  <span className="dispatch-ds-value">{dayClosedTasks} / {dayTotalTasks}</span>
                </span>
              </div>
            )}
            <div className="dispatch-trips-table-wrap">
              <table className="dispatch-grid">
                <thead>
                  <tr>
                    {(["SHIPMENT_TIME:Время","ID:ID","ST_COUNT:СТ","PALLET_COUNT:Пал.",
                       "TRANSTYPE:Тип","TRANSPORT:Машина","SHIPMENT_DATE:Дата","VODITEL_NAME:Водитель",
                       "DOCK:Докст.","REGIONS:Районы","PRICE:Цена","CONDITION:Статус","READY_PERC:%",
                       "TK_NAME:ТК","LOGIST:Логист"] as const
                    ).map(col => {
                      const [field, label] = col.split(":");
                      const active = tasksSortField === field;
                      return (
                        <th key={field} className="dispatch-sortable-th"
                          onClick={() => toggleTasksSort(field)}
                          title={`Сортировать по «${label}»`}>
                          {label}{active ? (tasksSortDir === "asc" ? " ▲" : " ▼") : ""}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {sortedTasks.length === 0
                    ? <tr><td colSpan={15} className="dispatch-grid-empty">Нет рейсов на {filterDate}. Нажмите «+ Создать рейс».</td></tr>
                    : sortedTasks.map(task => (
                        <tr key={task.ID}
                          data-taskid={task.ID}
                          className={["dispatch-gr",
                            selectedTask?.ID === task.ID ? "selected" : "",
                            task.CONDITION === "Отгружен" ? "grid-closed" : "",
                            task.CONDITION === "Отменён" ? "grid-cancelled" : "",
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
                          <td>{task.TK_NAME ?? "—"}</td>
                          <td>{task.LOGIST ?? "—"}</td>
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
                  {/* Sprint 74 — collapse toggle */}
                  <button className="dispatch-trip-collapse-btn"
                    onClick={() => setTripDetailCollapsed(c => !c)}
                    title={tripDetailCollapsed ? "Развернуть состав" : "Свернуть состав"}>
                    {tripDetailCollapsed ? "▼" : "▲"}
                  </button>
                  <b>Рейс #{selectedTask.ID}</b>
                  <span className={`dispatch-cond-big ${condClass(selectedTask.CONDITION)}`}>
                    {selectedTask.CONDITION ?? "Новый"}
                  </span>
                  {selectedTask.READY_PERC != null && (
                    <ReadinessBar perc={selectedTask.READY_PERC} unready={selectedTask.UNREADY_COUNT} />
                  )}
                  <span className="dispatch-pmv" style={{ marginLeft: "auto" }}>
                    P={tripP}&nbsp; M={tripM.toFixed(0)}&nbsp; V={tripV.toFixed(2)}
                  </span>
                  {!editMode
                    ? <button className="dispatch-edit-btn" onClick={() => { setEditMode(true); setEditDraft({}); }}>Редактировать</button>
                    : <>
                        <button className="dispatch-save-btn" onClick={handleSaveEdit} disabled={loading}>Сохранить</button>
                        <button className="dispatch-cancel-edit-btn" onClick={() => setEditMode(false)}>Отмена</button>
                      </>
                  }
                  <button className="dispatch-copy-task-btn" onClick={handleCopyTask}
                    disabled={loading} title="Создать новый рейс с теми же реквизитами (без СТ)">
                    📋 Копировать
                  </button>
                  <button className="dispatch-print-btn" onClick={handlePrintRoute}
                    disabled={taskSts.length === 0} title="Распечатать маршрутный лист">
                    🖨 Печать
                  </button>
                  {selectedTask.CONDITION !== "Отгружен" && !editMode && (
                    <button className="dispatch-reschedule-btn"
                      onClick={handleRescheduleNextDay} disabled={loading}
                      title={`Перенести на ${shiftDate(selectedTask.SHIPMENT_DATE ?? todayIso(), 1)}`}>
                      →+1
                    </button>
                  )}
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

              {/* Sprint 74 — collapsible STs section */}
              {!tripDetailCollapsed && <>

              {/* Sprint 30/32 — Live load metrics + overload warning */}
              {selectedVehicle?.PALLETS && tripP > 0 && (
                <div className="dispatch-load-bar-wrap">
                  <LoadBar
                    label="Паллеты"
                    value={tripP}
                    max={selectedVehicle.PALLETS}
                    unit="пал"
                  />
                  {tripP > selectedVehicle.PALLETS && (
                    <div className="dispatch-overload-warn">
                      ⚠ Перегруз: {tripP} пал &gt; {selectedVehicle.PALLETS} пал (норма для {selectedVehicle.NUM})
                    </div>
                  )}
                </div>
              )}

              {selectedTripStNums.size > 0 && selectedTask.CONDITION !== "Отгружен" && !selectedTask.PAY_ORDER_ID && (
                <div className="dispatch-trip-bulk-bar">
                  <span>{selectedTripStNums.size} СТ выбрано</span>
                  <button className="dispatch-bulk-unassign-btn" onClick={handleBulkUnassign} disabled={loading}
                    title="Delete">
                    Снять выбранные
                  </button>
                  <button className="dispatch-cancel-edit-btn" onClick={() => setSelectedTripStNums(new Set())}>
                    Отмена
                  </button>
                </div>
              )}

              {/* Sprint 57 — quick-add ST by number */}
              {selectedTask.CONDITION !== "Отгружен" && !selectedTask.PAY_ORDER_ID && (
                <div className="dispatch-quick-add-row">
                  <span className="dispatch-quick-add-label">+ СТ №:</span>
                  <input
                    className="dispatch-quick-add-input"
                    type="text"
                    value={quickAddInput}
                    placeholder="Введите номер СТ…"
                    onChange={e => setQuickAddInput(e.target.value)}
                    onKeyDown={e => { if (e.key === "Enter") handleQuickAddSt(); }}
                  />
                  <button className="dispatch-quick-add-btn"
                    onClick={handleQuickAddSt}
                    disabled={loading || !quickAddInput.trim()}>
                    Добавить
                  </button>
                </div>
              )}

              {/* Sprint 70 — select-all / deselect-all for trip STs */}
              {/* Sprint 72 — filter within trip STs */}
              {taskSts.length > 0 && (
                <div className="dispatch-trip-sts-toolbar">
                  {selectedTask.CONDITION !== "Отгружен" && !selectedTask.PAY_ORDER_ID && <>
                    <button className="dispatch-trip-selall-btn"
                      onClick={() => setSelectedTripStNums(new Set(filteredTaskSts.map(s => s.ST_NUMBER)))}
                      title="Выделить все СТ рейса">
                      Все
                    </button>
                    <button className="dispatch-trip-selall-btn"
                      onClick={() => setSelectedTripStNums(new Set())}
                      disabled={selectedTripStNums.size === 0}
                      title="Снять выделение">
                      Нет
                    </button>
                  </>}
                  <input
                    className="dispatch-trip-filter-input"
                    type="text"
                    value={tripStFilter}
                    onChange={e => setTripStFilter(e.target.value)}
                    placeholder="Фильтр по СТ/адресу…"
                  />
                  {tripStFilter && (
                    <button className="dispatch-trip-filter-clear" onClick={() => setTripStFilter("")} title="Сбросить">×</button>
                  )}
                  {/* Sprint 89 — unready-only toggle */}
                  {taskSts.some(s => s.VERIFY_PERC !== null && s.VERIFY_PERC < 100) && (
                    <button
                      className={`dispatch-trip-unready-btn${tripStUnreadyOnly ? " active" : ""}`}
                      onClick={() => setTripStUnreadyOnly(v => !v)}
                      title="Показать только несобранные СТ">
                      ⚠ Несобр.
                    </button>
                  )}
                  <span className="dispatch-trip-sts-count">
                    {(tripStFilter || tripStUnreadyOnly) ? `${filteredTaskSts.length} / ${taskSts.length}` : taskSts.length} СТ
                  </span>
                  {/* Sprint 77 — export trip STs to CSV */}
                  <button className="dispatch-trip-csv-btn"
                    onClick={() => exportTaskStsCsv(filteredTaskSts, selectedTask.ID)}
                    title="Скачать состав рейса в CSV">
                    ⬇ CSV
                  </button>
                </div>
              )}

              <div className="dispatch-trip-sts-wrap">
                <table className="dispatch-grid">
                  <thead>
                    <tr>
                      <th style={{ width: 22 }}></th>
                      <th style={{ width: 34 }}>#</th>
                      <th style={{ width: 80 }}>СТ №</th>
                      <th>Адрес</th>
                      <th>Пал.</th>
                      <th>Вес</th>
                      <th title="Объём м³">Объём</th>
                      <th title="% сборки">%</th>
                      <th>Зона</th>
                      <th>Окно</th>
                      <th>Погр.</th>
                      <th style={{ width: 26 }} title="Паллеты">📦</th>
                      <th style={{ width: 26 }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {taskSts.length === 0
                      ? <tr><td colSpan={13} className="dispatch-grid-empty">Рейс пуст. Выберите СТ выше и нажмите «Добавить в рейс».</td></tr>
                      : filteredTaskSts.length === 0
                        ? <tr><td colSpan={13} className="dispatch-grid-empty">Нет СТ, совпадающих с фильтром.</td></tr>
                      : filteredTaskSts.map(st => (
                          <TaskStTableRow
                            key={st.ST_NUMBER}
                            st={st}
                            disabled={loading || selectedTask.CONDITION === "Отгружен" || !!selectedTask.PAY_ORDER_ID}
                            isPalletOpen={palletStNum === st.ST_NUMBER}
                            checked={selectedTripStNums.has(st.ST_NUMBER)}
                            onToggleCheck={() => setSelectedTripStNums(prev => {
                              const next = new Set(prev);
                              if (next.has(st.ST_NUMBER)) next.delete(st.ST_NUMBER);
                              else next.add(st.ST_NUMBER);
                              return next;
                            })}
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

              </> /* end Sprint 74 collapsible */}
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
            <button className="dispatch-day-step-btn" onClick={() => setRouteShipDate(d => shiftDate(d, -1))} title="Предыдущий день">◄</button>
            <input type="date" value={routeShipDate} onChange={e => setRouteShipDate(e.target.value)} />
            <button className="dispatch-day-step-btn" onClick={() => setRouteShipDate(d => shiftDate(d, 1))} title="Следующий день">►</button>
            {routeShipDate !== todayIso() && (
              <button className="dispatch-today-btn" onClick={() => setRouteShipDate(todayIso())} title="Перейти к сегодня">Сегодня</button>
            )}
            <button className="dispatch-refresh-btn" onClick={loadTasks} title="Обновить рейсы">⟳</button>
            <span className="dispatch-tcount">{searchedRouteTasks.length}/{tasks.length} рейс(ов)</span>
            <input
              className="dispatch-route-search"
              type="text"
              value={routeSearchQuery}
              onChange={e => setRouteSearchQuery(e.target.value)}
              placeholder="Поиск: ID, авто, водитель, регион…"
            />
            {routeSearchQuery && (
              <button className="dispatch-route-search-clear" onClick={() => setRouteSearchQuery("")} title="Сбросить поиск">×</button>
            )}
            {/* Sprint 41 — status filter buttons */}
            <div className="dispatch-cond-filter">
              {(["all", "active", "closed", "cancelled"] as const).map(f => {
                const labels: Record<string, string> = { all: "Все", active: "Активен", closed: "Отгружен", cancelled: "Отменён" };
                const counts: Record<string, number> = { all: tasks.length, ...routeCondCounts };
                return (
                  <button key={f}
                    className={`dispatch-cond-filter-btn${routeCondFilter === f ? " active" : ""}${f !== "all" ? ` cond-${f}` : ""}`}
                    onClick={() => setRouteCondFilter(f)}>
                    {labels[f]}
                    {counts[f] > 0 && <span className="dispatch-cond-filter-cnt">{counts[f]}</span>}
                  </button>
                );
              })}
            </div>
            <label className="routes-brief-toggle" title="Свёрнутый режим: скрыть второстепенные колонки">
              <input type="checkbox" checked={routeBriefMode}
                onChange={e => setRouteBriefMode(e.target.checked)} />
              Кратко
            </label>
            <button className="billing-xlsx-btn routes-xlsx-btn"
              onClick={handleRoutesXlsx}
              disabled={routesXlsxLoading || tasks.length === 0}
              title="Экспорт в Excel">
              {routesXlsxLoading ? "…" : "⬇ Excel"}
            </button>
            <button className="dispatch-trip-csv-btn"
              onClick={() => exportRoutesCsv(searchedRouteTasks, routeShipDate)}
              disabled={searchedRouteTasks.length === 0}
              title="Экспорт таблицы маршрутов в CSV">
              ⬇ CSV
            </button>
          </div>

          {/* ---- Routes table ---- */}
          <div className="dispatch-trips-table-wrap dispatch-routes-table-wrap">
            <table className={`dispatch-grid${routeBriefMode ? " routes-brief" : ""}`}>
              <thead>
                <tr>
                  <th>Отгрузка</th><th>#</th><th>Пал.</th><th>Вес</th>
                  {!routeBriefMode && <th>Объём</th>}
                  {!routeBriefMode && <th>Тип</th>}
                  <th>Машина</th><th>Водитель</th><th>ДОК</th>
                  <th>Регионы</th>
                  {!routeBriefMode && <th>Цена</th>}
                  {!routeBriefMode && <th>ТК</th>}
                  {!routeBriefMode && <th>Логист</th>}
                  <th>Статус</th>
                  {!routeBriefMode && <th title="% сборки">%</th>}
                  {!routeBriefMode && <th title="Биллинг">💰</th>}
                </tr>
              </thead>
              <tbody>
                {searchedRouteTasks.length === 0
                  ? <tr><td colSpan={routeBriefMode ? 8 : 16} className="dispatch-grid-empty">Нет рейсов по фильтрам</td></tr>
                  : searchedRouteTasks.map(task => (
                      <tr key={task.ID}
                        data-taskid={task.ID}
                        className={["dispatch-gr",
                          selectedTask?.ID === task.ID ? "selected" : "",
                          task.CONDITION === "Отгружен" ? "grid-closed" : "",
                          task.CONDITION === "Отменён" ? "grid-cancelled" : "",
                        ].filter(Boolean).join(" ")}
                        onClick={() => selectTask(task)}>
                        <td>{fmtDate(task.SHIPMENT_DATE)}</td>
                        <td><b>#{task.ID}</b></td>
                        <td className="num-r">{task.PALLET_COUNT}</td>
                        <td className="num-r">{task.TEMP_WEIGHT != null ? task.TEMP_WEIGHT.toFixed(0) : "—"}</td>
                        {!routeBriefMode && <td className="num-r">{task.VOLUME_M3 != null ? task.VOLUME_M3.toFixed(2) : "—"}</td>}
                        {!routeBriefMode && (
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
                        )}
                        <td>{task.TRANSPORT ?? "—"}</td>
                        <td>
                          {task.VODITEL_NAME ?? "—"}
                          {!routeBriefMode && <DriverOwnerBadge isOwn={task.IS_OWN_DRIVER} tkName={task.TK_NAME} />}
                        </td>
                        <td>{task.DOCK ?? "—"}</td>
                        <td className="col-flex">{task.REGIONS ?? task.TEMP_REGION ?? "—"}</td>
                        {!routeBriefMode && <td>{task.PRICE != null ? task.PRICE.toLocaleString("ru-RU") + " ₽" : "—"}</td>}
                        {!routeBriefMode && <td>{task.TK_NAME ?? "—"}</td>}
                        {!routeBriefMode && <td>{task.LOGIST ?? "—"}</td>}
                        <td><span className={`dispatch-cond ${condClass(task.CONDITION)}`}>{task.CONDITION ?? "Новый"}</span></td>
                        {!routeBriefMode && <td>{task.READY_PERC != null ? <ReadinessBar perc={task.READY_PERC} unready={task.UNREADY_COUNT} /> : "—"}</td>}
                        {!routeBriefMode && <td>{task.PAY_ORDER_ID ? <span className="billing-badge-sm">💰</span> : "—"}</td>}
                      </tr>
                    ))
                }
              </tbody>
            </table>
          </div>

          {/* Sprint 85 — routes tab summary strip */}
          {searchedRouteTasks.length > 0 && (
            <div className="dispatch-routes-summary">
              <span>Рейсов: <b>{searchedRouteTasks.length}</b></span>
              <span>Пал.: <b>{routeTotalPallets}</b></span>
              <span>Вес: <b>{routeTotalWeight.toFixed(0)} кг</b></span>
              <span>Отгружено: <b>{routeClosedCount}</b></span>
            </div>
          )}

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
                    P={tripP}&nbsp; M={tripM.toFixed(0)}&nbsp; V={tripV.toFixed(2)}
                  </span>
                  <button className="dispatch-copy-task-btn" onClick={handleCopyTask}
                    disabled={loading} title="Создать новый рейс с теми же реквизитами (без СТ)">
                    📋 Копировать
                  </button>
                  <button className="dispatch-print-btn" onClick={handlePrintRoute}
                    disabled={taskSts.length === 0} title="Распечатать маршрутный лист">
                    🖨 Печать
                  </button>
                  {selectedTask.CONDITION !== "Отгружен" && (
                    <button className="dispatch-reschedule-btn"
                      onClick={handleRescheduleNextDay} disabled={loading}
                      title={`Перенести на ${shiftDate(selectedTask.SHIPMENT_DATE ?? todayIso(), 1)}`}>
                      →+1
                    </button>
                  )}
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
                    onDetach={handleDetachFromBilling}
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
              {/* Sprint 32 — load bar in routes tab */}
              {selectedVehicle?.PALLETS && tripP > 0 && (
                <div className="dispatch-load-bar-wrap">
                  <LoadBar label="Паллеты" value={tripP} max={selectedVehicle.PALLETS} unit="пал" />
                  {tripP > selectedVehicle.PALLETS && (
                    <div className="dispatch-overload-warn">
                      ⚠ Перегруз: {tripP} пал &gt; {selectedVehicle.PALLETS} пал (норма для {selectedVehicle.NUM})
                    </div>
                  )}
                </div>
              )}

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
        <div className={`dispatch-right-panel${fpCollapsed ? " dispatch-fp-collapsed" : ""}`}>
          <div className="dispatch-fp-header-row">
            {!fpCollapsed && (
              <span className="dispatch-fp-title">
                Фильтры
                {activeFilterCount > 0 && (
                  <span className="dispatch-fp-badge">{activeFilterCount}</span>
                )}
              </span>
            )}
            {fpCollapsed && activeFilterCount > 0 && (
              <span className="dispatch-fp-badge dispatch-fp-badge-alone">{activeFilterCount}</span>
            )}
            {!fpCollapsed && activeFilterCount > 0 && (
              <button className="dispatch-fp-reset-btn" onClick={handleResetFilters} title="Сбросить все фильтры">
                × Сбросить
              </button>
            )}
            <button className="dispatch-fp-collapse-btn" onClick={() => setFpCollapsed(v => !v)}
              title={fpCollapsed ? "Развернуть панель фильтров" : "Свернуть панель фильтров"}>
              {fpCollapsed ? "›" : "‹"}
            </button>
          </div>
          {!fpCollapsed && <><div className="dispatch-fp-label">Тип ТС</div>
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
          </>}
        </div>
        ) : activeTab === "billing" && selectedBillingOrder ? (
        <div className="dispatch-right-panel billing-detail-panel">
          <BillingOrderDetailPanel
            order={selectedBillingOrder}
            tasks={billingOrderTasks}
            loading={billingOrderTasksLoading}
            onClose={() => { setSelectedBillingOrder(null); setBillingOrderTasks([]); }}
            onDetachTask={async (tt_id: number) => {
              if (!selectedBillingOrder) return;
              await apiFetch(
                `/api/admin/transport/billing/orders/${selectedBillingOrder.order_id}/tasks/${tt_id}`,
                { method: "DELETE" }
              );
              setBillingOrderTasks(prev => prev.filter(t => t.tt_id !== tt_id));
              setBillingOrders(prev => prev.map(o =>
                o.order_id === selectedBillingOrder.order_id
                  ? { ...o, task_count: (o.task_count ?? 1) - 1 }
                  : o
              ));
            }}
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

      {clusterCreateRaion && (() => {
        const cluster = clusters.find(c => c.RAION === clusterCreateRaion);
        if (!cluster) return null;
        return (
          <ClusterQuickCreateDialog
            cluster={cluster}
            stDate={stDate}
            transportTypes={transportTypes}
            vehicles={vehicles}
            drivers={drivers}
            loading={clusterCreateLoading}
            onConfirm={handleCreateFromCluster}
            onClose={() => setClusterCreateRaion(null)}
          />
        );
      })()}
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
  st, checked, onToggle, isChild = false, idx = 0, onShiftClick, onSelectByField, onGotoTrip,
}: {
  st: AvailableSt;
  checked: boolean;
  onToggle: () => void;
  isChild?: boolean;
  idx?: number;
  onShiftClick?: (idx: number) => void;
  onSelectByField?: (field: "RAION" | "REGION", value: string | null) => void;
  onGotoTrip?: (taskId: number) => void;
}) {
  // Sprint 50 — green left-border for fully-assembled STs
  // Sprint 83 — amber left-border for unready STs (VERIFY_PERC < 100 and not null)
  const rowClass = [
    "dispatch-gr",
    checked ? "selected" : wareColorClass(st.WARE_ID),
    !checked && (st.VERIFY_PERC ?? 0) >= 100 ? "dispatch-st-ready" : "",
    !checked && st.VERIFY_PERC !== null && st.VERIFY_PERC < 100 ? "dispatch-avail-unready" : "",
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
      <td>{st.TRANSTASK_ID
        ? <button className="dispatch-goto-trip-btn"
            title={`Перейти к рейсу #${st.TRANSTASK_ID}`}
            onClick={e => { e.stopPropagation(); onGotoTrip?.(st.TRANSTASK_ID!); }}>
            #{st.TRANSTASK_ID} →
          </button>
        : "—"}</td>
      <td>{fmtDate(st.STDATE)}</td>
      <td>{st.VERIFY_PERC != null ? <VerifyBar perc={st.VERIFY_PERC} /> : "—"}</td>
      <td className={onSelectByField ? "dispatch-region-cell" : ""}
          onClick={e => handleFieldClick(e, "RAION", st.RAION)}
          title={onSelectByField ? "Выделить все СТ района" : ""}>{st.RAION ?? "—"}</td>
      <td><TransportTypeBadge value={st.TRANSPORT_TYPE} /></td>
      <td title={st.NAPR ?? ""}>{st.NAPR ? <span className="dispatch-napr-badge">{st.NAPR}</span> : ""}</td>
      <td className="num-c" title={st.STOL ? "Требуется стол-лифт / гидроборт" : ""}>{st.STOL ? "♿" : ""}</td>
      <td className="dispatch-prim1" title={st.PRIM1 ?? ""}>{st.PRIM1 ? st.PRIM1.slice(0, 20) : ""}</td>
      <td className="num-c">{st.SUGAR ? <span className="dispatch-polnopallet" title="Полнопалетная отборка">П</span> : ""}</td>
    </tr>
  );
}

// ---------------------------------------------------------------------------
// ClusterGroup — cluster header row + child ST rows
// ---------------------------------------------------------------------------

function ClusterGroup({
  cluster, expanded, onToggle, selectedNums, onToggleSt, onCreateTask,
}: {
  cluster: TransportCluster;
  expanded: boolean;
  onToggle: () => void;
  selectedNums: Set<string>;
  onToggleSt: (stNum: string) => void;
  onCreateTask?: () => void;
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
          {onCreateTask && (
            <button
              className="cluster-create-task-btn"
              onClick={e => { e.stopPropagation(); onCreateTask(); }}
              title={`Создать рейс из всех СТ района «${cluster.RAION}»`}
            >
              ⚡ Рейс
            </button>
          )}
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
// LoadBar — Sprint 30, live capacity bar (pallets vs vehicle max)
// ---------------------------------------------------------------------------

function LoadBar({ label, value, max, unit }: { label: string; value: number; max: number; unit: string }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  const color = pct >= 100 ? "#ef4444" : pct >= 85 ? "#f59e0b" : "#22c55e";
  return (
    <div className="load-bar-row">
      <span className="load-bar-label">{label}</span>
      <div className="load-bar-track">
        <div className="load-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="load-bar-text" style={{ color }}>{value} / {max} {unit} ({pct}%)</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// ClusterSidebar — Sprint 31, left panel with cluster summary cards
// ---------------------------------------------------------------------------

function ClusterSidebar({
  clusters, expandedRaions, onToggle, onCreateTask,
}: {
  clusters: TransportCluster[];
  expandedRaions: Set<string>;
  onToggle: (raion: string) => void;
  onCreateTask: (raion: string) => void;
}) {
  const total = clusters.reduce((s, c) => ({ st: s.st + c.ST_COUNT, pal: s.pal + c.PALLET_COUNT, kg: s.kg + c.WEIGHT_KG }), { st: 0, pal: 0, kg: 0 });

  return (
    <aside className="cluster-sidebar">
      <div className="cluster-sidebar-header">
        <span className="cluster-sidebar-title">Кластеры</span>
        <span className="cluster-sidebar-total">{clusters.length} р-нов · {total.st} СТ · {total.pal} пал</span>
      </div>
      <div className="cluster-sidebar-list">
        {clusters.length === 0 && (
          <div className="cluster-sidebar-empty">Нет свободных СТ</div>
        )}
        {clusters.map(c => {
          const active = expandedRaions.has(c.RAION);
          return (
            <div
              key={c.RAION}
              className={`cluster-card${active ? " cluster-card-active" : ""}`}
              onClick={() => onToggle(c.RAION)}
            >
              <div className="cluster-card-name">{c.RAION}</div>
              <div className="cluster-card-meta">
                <span>{c.ST_COUNT} СТ</span>
                <span>{c.PALLET_COUNT} пал</span>
                <span>{c.WEIGHT_KG.toFixed(0)} кг</span>
              </div>
              <button
                className="cluster-card-create-btn"
                onClick={e => { e.stopPropagation(); onCreateTask(c.RAION); }}
                title={`Создать рейс из района «${c.RAION}»`}
              >
                ⚡ Рейс
              </button>
            </div>
          );
        })}
      </div>
    </aside>
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
  // Sprint 90 — copy ST number to clipboard on click
  const [stCopied, setStCopied] = useState(false);

  function copyStNum() {
    navigator.clipboard.writeText(st.ST_NUMBER).then(() => {
      setStCopied(true);
      setTimeout(() => setStCopied(false), 1500);
    }).catch(() => {});
  }

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
      <td className="dispatch-gc-stnum dispatch-st-copy-cell"
        onClick={copyStNum} title="Копировать номер СТ">
        {st.ST_NUMBER}
        {stCopied && <span className="dispatch-st-copied">✓</span>}
      </td>
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
  st, disabled, isPalletOpen, checked, onToggleCheck, onUnassign, onSetLoadType, onSetOrder, onShowPallets,
}: {
  st: TaskSt;
  disabled: boolean;
  isPalletOpen: boolean;
  checked?: boolean;
  onToggleCheck?: () => void;
  onUnassign: () => void;
  onSetLoadType: (lt: string) => void;
  onSetOrder: (ord: number) => void;
  onShowPallets: () => void;
}) {
  const [ordEdit, setOrdEdit] = useState(false);
  const [ordVal, setOrdVal] = useState(String(st.ORD ?? ""));
  // Sprint 90 — copy ST number to clipboard on click
  const [stCopied, setStCopied] = useState(false);

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

  function copyStNum() {
    navigator.clipboard.writeText(st.ST_NUMBER).then(() => {
      setStCopied(true);
      setTimeout(() => setStCopied(false), 1500);
    }).catch(() => {});
  }

  const unready = st.VERIFY_PERC != null && st.VERIFY_PERC < 100;

  return (
    <tr className={`dispatch-gr${checked ? " selected" : ""}${unready ? " dispatch-gr-unready" : ""}`}>
      <td onClick={e => e.stopPropagation()}>
        {onToggleCheck && !disabled && (
          <input type="checkbox" checked={!!checked} onChange={onToggleCheck} />
        )}
      </td>
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
      <td className="dispatch-gc-stnum dispatch-st-copy-cell"
        onClick={copyStNum} title="Копировать номер СТ">
        {st.ST_NUMBER}
        {stCopied && <span className="dispatch-st-copied">✓</span>}
      </td>
      <td className="col-flex">
        {st.REGION || st.ADDR || "—"}
        {st.RAION && <span className="dispatch-st-raion-sm"> · {st.RAION}</span>}
      </td>
      <td className="num-r">{st.PALLETS_COUNT}</td>
      <td className="num-r">{st.WEIGHT_KG.toFixed(0)}</td>
      <td className="num-r">{st.VOLUME_M3 != null ? st.VOLUME_M3.toFixed(2) : "—"}</td>
      <td>{st.VERIFY_PERC != null ? <VerifyBar perc={st.VERIFY_PERC} /> : "—"}</td>
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
// ClusterQuickCreateDialog — Sprint 29, Phase 2 полуавто
// ---------------------------------------------------------------------------

function ClusterQuickCreateDialog({
  cluster, stDate, transportTypes, vehicles, drivers, loading, onConfirm, onClose,
}: {
  cluster: TransportCluster;
  stDate: string;
  transportTypes: TransportType[];
  vehicles: Vehicle[];
  drivers: Driver[];
  loading: boolean;
  onConfirm: (params: { raion: string; transtype: string; vehicle: string; driver_id: number | null; dock: string }) => void;
  onClose: () => void;
}) {
  const [transtype, setTranstype] = useState(transportTypes[0]?.TRANSPORTTYPE || "10");
  const [vehicle, setVehicle] = useState("");
  const [driverId, setDriverId] = useState<number | null>(null);
  const [dock, setDock] = useState("");
  const [avail, setAvail] = useState<VehicleAvail[]>([]);
  const [availLoading, setAvailLoading] = useState(false);

  useEffect(() => {
    if (!stDate) return;
    setAvailLoading(true);
    apiFetch<VehicleAvail[]>(
      `/api/admin/transport/vehicles/available?shipment_time=${stDate}+09:00&pallets=${cluster.PALLET_COUNT}`
    )
      .then(setAvail)
      .catch(() => setAvail([]))
      .finally(() => setAvailLoading(false));
  }, [stDate, cluster.PALLET_COUNT]);

  const availMap = new Map(avail.map(a => [a.vehicle_num, a]));
  const selectedAvail = availMap.get(vehicle);

  return (
    <div className="dispatch-dialog-overlay" onClick={onClose}>
      <div className="dispatch-dialog" onClick={e => e.stopPropagation()}>
        <h3>⚡ Рейс из кластера «{cluster.RAION}»</h3>
        <div className="cluster-dialog-summary">
          {cluster.ST_COUNT} СТ · {cluster.PALLET_COUNT} пал · {cluster.WEIGHT_KG.toFixed(0)} кг · {cluster.VOLUME_M3.toFixed(2)} м³
        </div>
        <div className="cluster-dialog-date">Дата: {stDate}</div>
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
            <div className="dispatch-avail-warn">⚠ {selectedAvail.detail} — конфликт возможен</div>
          )}
          {selectedAvail && selectedAvail.status === "yellow" && (
            <div className="dispatch-avail-info">ℹ {selectedAvail.detail}</div>
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
          <button className="dispatch-new-btn" disabled={loading}
            onClick={() => onConfirm({ raion: cluster.RAION, transtype, vehicle, driver_id: driverId, dock })}>
            {loading ? "Создаём…" : `Создать рейс (${cluster.ST_COUNT} СТ)`}
          </button>
          <button className="dispatch-cancel-edit-btn" onClick={onClose} disabled={loading}>Отмена</button>
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
  order, loading, onClose, onPay, onDetach,
}: {
  order: BillingOrder;
  loading: boolean;
  onClose: () => void;
  onPay: () => void;
  onDetach?: () => void;
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
        {onDetach && !order.closed && !order.payed && (
          <button className="billing-detach-btn" onClick={onDetach} disabled={loading}>
            Снять с биллинга
          </button>
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
  const [registryXlsxLoading, setRegistryXlsxLoading] = useState(false);

  async function handleRegistryXlsx() {
    setRegistryXlsxLoading(true);
    try {
      const p = new URLSearchParams();
      if (dateFrom) p.set("date_from", dateFrom);
      if (dateTo)   p.set("date_to",   dateTo);
      if (company)  p.set("company",   company);
      if (status === "open")   { p.set("closed", "0"); p.set("payed", "0"); }
      if (status === "closed") { p.set("closed", "1"); p.set("payed", "0"); }
      if (status === "paid")   p.set("payed", "1");
      await downloadBlob(
        `/api/admin/transport/billing/orders/export.xlsx?${p}`,
        "billing_registry.xlsx",
      );
    } catch (e) { alert(String(e)); } finally { setRegistryXlsxLoading(false); }
  }

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
        <button className="billing-xlsx-btn" onClick={handleRegistryXlsx}
          disabled={registryXlsxLoading || orders.length === 0}>
          {registryXlsxLoading ? "…" : "⬇ Excel"}
        </button>
        <button className="billing-csv-btn" onClick={() => exportBillingCsv(orders)}
          disabled={orders.length === 0}>
          ⬇ CSV
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
// Sprint 54 — export selected STs to CSV
// ---------------------------------------------------------------------------

function exportSelectedStsCsv(sts: AvailableSt[], date: string) {
  const BOM = "﻿";
  const header = "СТ №;Адрес;Регион;Район;Паллет;Вес кг;Объём м³;% сборки;Тип ТС;Рейс";
  const rows = sts.map(s => [
    s.ST_NUMBER,
    s.ADDR ?? "",
    s.REGION ?? "",
    s.RAION ?? "",
    s.PALLETS_COUNT,
    s.WEIGHT_KG,
    (s.VOLUME_M3 ?? 0).toFixed(2),
    s.VERIFY_PERC != null ? (s.VERIFY_PERC * 100).toFixed(0) + "%" : "",
    s.TRANSPORT_TYPE ?? "",
    s.TRANSTASK_ID ? `#${s.TRANSTASK_ID}` : "",
  ].join(";"));
  const total = sts.reduce((acc, s) => ({ p: acc.p + s.PALLETS_COUNT, m: acc.m + s.WEIGHT_KG }), { p: 0, m: 0 });
  rows.push(["ИТОГО", "", "", "", total.p, total.m.toFixed(0), "", "", "", ""].join(";"));
  const csv = BOM + [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `selected-sts-${date}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// Sprint 77 — Export trip detail STs to CSV
function exportTaskStsCsv(sts: TaskSt[], taskId: number) {
  const BOM = "﻿";
  const header = "#;СТ №;Адрес;Регион;Паллет;Вес кг;Объём м³;% сборки;Зона;Тип погр.";
  const rows = sts.map(s => [
    s.ORD ?? "",
    s.ST_NUMBER,
    `${s.REGION ?? ""}${s.ADDR ? " " + s.ADDR : ""}`.trim(),
    s.RAION ?? "",
    s.PALLETS_COUNT,
    s.WEIGHT_KG.toFixed(0),
    s.VOLUME_M3 != null ? s.VOLUME_M3.toFixed(2) : "",
    s.VERIFY_PERC != null ? s.VERIFY_PERC + "%" : "",
    s.ZONE ?? "",
    s.LOAD_TYPE ?? "",
  ].join(";"));
  const total = sts.reduce((a, s) => ({ p: a.p + s.PALLETS_COUNT, m: a.m + s.WEIGHT_KG }), { p: 0, m: 0 });
  rows.push(["ИТОГО", "", "", "", total.p, total.m.toFixed(0), "", "", "", ""].join(";"));
  const csv = BOM + [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `trip-${taskId}-sts.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// Sprint 86 — Export routes tab trips table to CSV
function exportRoutesCsv(tasks: TransportTask[], date: string) {
  const BOM = "﻿";
  const header = "ID;Дата;Время;Машина;Водитель;ТК;Пал.;Вес кг;Объём м³;Регионы;Цена ₽;Статус;% сборки;ДОК;Логист";
  const rows = tasks.map(t => [
    t.ID,
    t.SHIPMENT_DATE ? fmtDate(t.SHIPMENT_DATE) : "",
    t.SHIPMENT_TIME ? fmtTime(t.SHIPMENT_TIME) : "",
    t.TRANSPORT ?? "",
    t.VODITEL_NAME ?? "",
    t.TK_NAME ?? "",
    t.PALLET_COUNT,
    t.TEMP_WEIGHT != null ? t.TEMP_WEIGHT.toFixed(0) : "",
    t.VOLUME_M3 != null ? t.VOLUME_M3.toFixed(2) : "",
    t.REGIONS ?? t.TEMP_REGION ?? "",
    t.PRICE != null ? t.PRICE : "",
    t.CONDITION ?? "",
    t.READY_PERC != null ? t.READY_PERC + "%" : "",
    t.DOCK ?? "",
    t.LOGIST ?? "",
  ].join(";"));
  const csv = BOM + [header, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `routes-${date}.csv`;
  a.click();
  URL.revokeObjectURL(url);
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
  order, tasks, loading, onClose, onDetachTask,
}: {
  order: BillingOrder;
  tasks: BillingOrderTask[];
  loading: boolean;
  onClose: () => void;
  onDetachTask?: (tt_id: number) => Promise<void>;
}) {
  const [detachingId, setDetachingId] = useState<number | null>(null);
  const [xlsxLoading, setXlsxLoading] = useState(false);
  const { text, cls } = billingStatusLabel(order);
  const total = tasks.reduce((s, t) => s + t.price, 0);
  const canDetach = !order.closed && !order.payed && !!onDetachTask;

  async function handleDetach(tt_id: number) {
    if (!onDetachTask) return;
    if (!confirm(`Снять рейс #${tt_id} со счёта ${order.num ?? `#${order.order_id}`}?`)) return;
    setDetachingId(tt_id);
    try { await onDetachTask(tt_id); } finally { setDetachingId(null); }
  }

  async function handleDownloadXlsx() {
    setXlsxLoading(true);
    try {
      const num = (order.num ?? `order_${order.order_id}`).replace(/[/\\]/g, "-");
      await downloadBlob(
        `/api/admin/transport/billing/orders/${order.order_id}/export.xlsx`,
        `billing_${num}.xlsx`,
      );
    } catch (e) { alert(String(e)); } finally { setXlsxLoading(false); }
  }

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
                {canDetach && <th />}
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
                  {canDetach && (
                    <td>
                      <button className="billing-detach-task-btn"
                        onClick={() => handleDetach(t.tt_id)}
                        disabled={detachingId === t.tt_id}
                        title="Снять рейс со счёта">
                        {detachingId === t.tt_id ? "…" : "✕"}
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="billing-detail-total">
            Итого: <b>{total.toLocaleString("ru-RU")} ₽</b>
          </div>
          <div className="billing-detail-export-row">
            <button className="billing-xlsx-btn billing-detail-export-btn"
              onClick={handleDownloadXlsx} disabled={xlsxLoading}>
              {xlsxLoading ? "…" : "⬇ Excel"}
            </button>
            <button className="billing-csv-btn billing-detail-export-btn"
              onClick={() => exportOrderTasksCsv(order, tasks)}>
              ⬇ CSV
            </button>
          </div>
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
