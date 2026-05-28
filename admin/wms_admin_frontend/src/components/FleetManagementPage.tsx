/**
 * FleetManagementPage — управление флотом (ТС + Водители).
 * Sprint 97: вкладка «Транспортные средства» CRUD
 * Sprint 98: вкладка «Водители» CRUD
 */

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Vehicle {
  ID: number;
  NUM_PLAT: string;
  TRANSTYPE_ID: string | null;
  TRANSTYPE_NAME: string | null;
  MAX_WEIGHT_KG: number;
  MAX_PALLETS: number;
  SOBSTVENNYY: number;
  DOVERENNOST_OT: string | null;
}

interface Driver {
  ID: number;
  FULL_NAME: string;
  PHONE: string | null;
  LICENSE_NUMBER: string | null;
  COMPANY: string | null;
}

interface TransportType {
  TRANSPORTTYPE: string;
  NAME: string;
}

interface VehicleForm {
  num_plat: string;
  transtype_id: string;
  max_weight_kg: string;
  max_pallets: string;
  sobstvennyy: boolean;
  doverennost_ot: string;
}

interface DriverForm {
  name: string;
  phone: string;
  license_number: string;
  company: string;
}

const emptyVehicleForm = (): VehicleForm => ({
  num_plat: "",
  transtype_id: "",
  max_weight_kg: "10000",
  max_pallets: "20",
  sobstvennyy: true,
  doverennost_ot: "",
});

const emptyDriverForm = (): DriverForm => ({
  name: "",
  phone: "",
  license_number: "",
  company: "",
});

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export function FleetManagementPage({ onBack }: { onBack: () => void }) {
  const [activeTab, setActiveTab] = useState<"vehicles" | "drivers">("vehicles");

  return (
    <div className="fleet-shell">
      <header className="fleet-topbar">
        <button className="fleet-back" onClick={onBack}>◄</button>
        <div className="fleet-title">
          <h1>Управление флотом</h1>
          <span className="fleet-subtitle">Транспортные средства и водители</span>
        </div>
      </header>

      <div className="fleet-tabs">
        <button
          className={`fleet-tab-btn${activeTab === "vehicles" ? " fleet-tab-active" : ""}`}
          onClick={() => setActiveTab("vehicles")}
        >
          🚛 Транспортные средства
        </button>
        <button
          className={`fleet-tab-btn${activeTab === "drivers" ? " fleet-tab-active" : ""}`}
          onClick={() => setActiveTab("drivers")}
        >
          👤 Водители
        </button>
      </div>

      <div className="fleet-content">
        {activeTab === "vehicles" ? <VehiclesTab /> : <DriversTab />}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Vehicles Tab — Sprint 97
// ---------------------------------------------------------------------------

function VehiclesTab() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [types, setTypes] = useState<TransportType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialog, setDialog] = useState<"add" | "edit" | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<VehicleForm>(emptyVehicleForm());
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [v, t] = await Promise.all([
        apiFetch<Vehicle[]>("/api/admin/transport/vehicles/full"),
        apiFetch<TransportType[]>("/api/admin/transport/types"),
      ]);
      setVehicles(v);
      setTypes(t);
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm(emptyVehicleForm()); setEditId(null); setDialog("add"); };
  const openEdit = (v: Vehicle) => {
    setForm({
      num_plat: v.NUM_PLAT,
      transtype_id: v.TRANSTYPE_ID ?? "",
      max_weight_kg: String(v.MAX_WEIGHT_KG),
      max_pallets: String(v.MAX_PALLETS),
      sobstvennyy: v.SOBSTVENNYY === 1,
      doverennost_ot: v.DOVERENNOST_OT ?? "",
    });
    setEditId(v.ID);
    setDialog("edit");
  };

  const handleDelete = async (id: number, num: string) => {
    if (!confirm(`Удалить ТС «${num}»?`)) return;
    try {
      await apiFetch(`/api/admin/transport/vehicles/${id}`, { method: "DELETE" });
      await load();
    } catch (e) { setError(String(e)); }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const body = {
        num_plat: form.num_plat.trim(),
        transtype_id: form.transtype_id || null,
        max_weight_kg: parseInt(form.max_weight_kg) || 10000,
        max_pallets: parseInt(form.max_pallets) || 20,
        sobstvennyy: form.sobstvennyy,
        doverennost_ot: form.doverennost_ot.trim() || null,
      };
      if (dialog === "add") {
        await apiFetch("/api/admin/transport/vehicles", { method: "POST", body: JSON.stringify(body) });
      } else if (editId !== null) {
        await apiFetch(`/api/admin/transport/vehicles/${editId}`, { method: "PATCH", body: JSON.stringify(body) });
      }
      setDialog(null);
      await load();
    } catch (e) { setError(String(e)); }
    finally { setSaving(false); }
  };

  return (
    <div className="fleet-section">
      <div className="fleet-toolbar">
        <button className="fleet-add-btn" onClick={openAdd}>+ Добавить ТС</button>
        {loading && <span className="fleet-loading">Загрузка…</span>}
        {error && <span className="fleet-error" onClick={() => setError(null)}>⚠ {error}</span>}
      </div>

      <table className="fleet-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Гос. номер</th>
            <th>Тип ТС</th>
            <th>Гр/под., кг</th>
            <th>Паллет</th>
            <th>Компания</th>
            <th>Владелец</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {vehicles.map(v => (
            <tr key={v.ID}>
              <td className="fleet-id">{v.ID}</td>
              <td className="fleet-numplat">{v.NUM_PLAT}</td>
              <td>{v.TRANSTYPE_NAME ?? v.TRANSTYPE_ID ?? "—"}</td>
              <td className="fleet-num">{v.MAX_WEIGHT_KG.toLocaleString()}</td>
              <td className="fleet-num">{v.MAX_PALLETS}</td>
              <td>{v.DOVERENNOST_OT ?? "—"}</td>
              <td>
                <span className={`fleet-owner-badge ${v.SOBSTVENNYY === 1 ? "fleet-own" : "fleet-hired"}`}>
                  {v.SOBSTVENNYY === 1 ? "Свой" : "Наёмный"}
                </span>
              </td>
              <td className="fleet-actions">
                <button className="fleet-edit-btn" onClick={() => openEdit(v)}>✏</button>
                <button className="fleet-del-btn" onClick={() => handleDelete(v.ID, v.NUM_PLAT)}>✕</button>
              </td>
            </tr>
          ))}
          {!loading && vehicles.length === 0 && (
            <tr><td colSpan={8} className="fleet-empty">Нет транспортных средств</td></tr>
          )}
        </tbody>
      </table>

      {dialog && (
        <div className="fleet-modal-overlay" onClick={() => setDialog(null)}>
          <div className="fleet-modal" onClick={e => e.stopPropagation()}>
            <div className="fleet-modal-title">
              {dialog === "add" ? "Добавить ТС" : "Редактировать ТС"}
            </div>
            <div className="fleet-form-grid">
              <label>Гос. номер *</label>
              <input value={form.num_plat} onChange={e => setForm(f => ({ ...f, num_plat: e.target.value }))} />
              <label>Тип ТС</label>
              <select value={form.transtype_id} onChange={e => setForm(f => ({ ...f, transtype_id: e.target.value }))}>
                <option value="">— не выбрано —</option>
                {types.map(t => <option key={t.TRANSPORTTYPE} value={t.TRANSPORTTYPE}>{t.NAME}</option>)}
              </select>
              <label>Грузоподъёмность, кг</label>
              <input type="number" min={0} value={form.max_weight_kg} onChange={e => setForm(f => ({ ...f, max_weight_kg: e.target.value }))} />
              <label>Вместимость, паллет</label>
              <input type="number" min={0} value={form.max_pallets} onChange={e => setForm(f => ({ ...f, max_pallets: e.target.value }))} />
              <label>Владелец</label>
              <select value={form.sobstvennyy ? "1" : "0"} onChange={e => setForm(f => ({ ...f, sobstvennyy: e.target.value === "1" }))}>
                <option value="1">Собственный</option>
                <option value="0">Наёмный</option>
              </select>
              <label>Транспортная компания</label>
              <input
                value={form.doverennost_ot}
                onChange={e => setForm(f => ({ ...f, doverennost_ot: e.target.value }))}
                placeholder="для наёмных"
              />
            </div>
            <div className="fleet-modal-actions">
              <button className="fleet-modal-cancel" onClick={() => setDialog(null)}>Отмена</button>
              <button className="fleet-modal-save" onClick={handleSave} disabled={saving || !form.num_plat.trim()}>
                {saving ? "Сохранение…" : "Сохранить"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Drivers Tab — Sprint 98
// ---------------------------------------------------------------------------

function DriversTab() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialog, setDialog] = useState<"add" | "edit" | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<DriverForm>(emptyDriverForm());
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<Driver[]>("/api/admin/transport/drivers/full");
      setDrivers(data);
    } catch (e) { setError(String(e)); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm(emptyDriverForm()); setEditId(null); setDialog("add"); };
  const openEdit = (d: Driver) => {
    setForm({
      name: d.FULL_NAME,
      phone: d.PHONE ?? "",
      license_number: d.LICENSE_NUMBER ?? "",
      company: d.COMPANY ?? "",
    });
    setEditId(d.ID);
    setDialog("edit");
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Удалить водителя «${name}»?`)) return;
    try {
      await apiFetch(`/api/admin/transport/drivers/${id}`, { method: "DELETE" });
      await load();
    } catch (e) { setError(String(e)); }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const body = {
        name: form.name.trim(),
        phone: form.phone.trim() || null,
        license_number: form.license_number.trim() || null,
        company: form.company.trim() || null,
      };
      if (dialog === "add") {
        await apiFetch("/api/admin/transport/drivers", { method: "POST", body: JSON.stringify(body) });
      } else if (editId !== null) {
        await apiFetch(`/api/admin/transport/drivers/${editId}`, { method: "PATCH", body: JSON.stringify(body) });
      }
      setDialog(null);
      await load();
    } catch (e) { setError(String(e)); }
    finally { setSaving(false); }
  };

  return (
    <div className="fleet-section">
      <div className="fleet-toolbar">
        <button className="fleet-add-btn" onClick={openAdd}>+ Добавить водителя</button>
        {loading && <span className="fleet-loading">Загрузка…</span>}
        {error && <span className="fleet-error" onClick={() => setError(null)}>⚠ {error}</span>}
      </div>

      <table className="fleet-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>ФИО</th>
            <th>Телефон</th>
            <th>Удостоверение</th>
            <th>ТК (наёмный)</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {drivers.map(d => (
            <tr key={d.ID}>
              <td className="fleet-id">{d.ID}</td>
              <td>{d.FULL_NAME}</td>
              <td>{d.PHONE ?? "—"}</td>
              <td>{d.LICENSE_NUMBER ?? "—"}</td>
              <td>{d.COMPANY ?? "—"}</td>
              <td className="fleet-actions">
                <button className="fleet-edit-btn" onClick={() => openEdit(d)}>✏</button>
                <button className="fleet-del-btn" onClick={() => handleDelete(d.ID, d.FULL_NAME)}>✕</button>
              </td>
            </tr>
          ))}
          {!loading && drivers.length === 0 && (
            <tr><td colSpan={6} className="fleet-empty">Нет водителей</td></tr>
          )}
        </tbody>
      </table>

      {dialog && (
        <div className="fleet-modal-overlay" onClick={() => setDialog(null)}>
          <div className="fleet-modal" onClick={e => e.stopPropagation()}>
            <div className="fleet-modal-title">
              {dialog === "add" ? "Добавить водителя" : "Редактировать водителя"}
            </div>
            <div className="fleet-form-grid">
              <label>ФИО *</label>
              <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              <label>Телефон</label>
              <input value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} />
              <label>Номер ВУ</label>
              <input value={form.license_number} onChange={e => setForm(f => ({ ...f, license_number: e.target.value }))} />
              <label>Транспортная компания</label>
              <input value={form.company} onChange={e => setForm(f => ({ ...f, company: e.target.value }))} placeholder="для наёмных" />
            </div>
            <div className="fleet-modal-actions">
              <button className="fleet-modal-cancel" onClick={() => setDialog(null)}>Отмена</button>
              <button className="fleet-modal-save" onClick={handleSave} disabled={saving || !form.name.trim()}>
                {saving ? "Сохранение…" : "Сохранить"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
