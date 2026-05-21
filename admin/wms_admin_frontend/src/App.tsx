import { Component, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import "./styles.css";
import { SHIFT_MINUTES, clock, inferWaveByMinute } from "./demoData";
import { loadReplayData } from "./data/loaders";
import { CapacityPanel, DetailCard, KpiRow, LeftPanel, ResourcePerformancePanel, RightPanel } from "./components/Panels";
import { Timeline } from "./components/Timeline";
import { TopologyAdminPage } from "./components/TopologyAdminPage";
import { TopologyGridEditorPage } from "./components/TopologyGridEditorPage";
import { WarehouseScene } from "./components/WarehouseScene";
import { activeCollisions, currentMetrics, dockPalletsAt, pickFaceFillAt, replenishmentTasksAt, resourceStateAt, visibleEvents } from "./replay/reducer";
import type { DetailSelection, ReplayData } from "./types";

export default function App() {
  const [data, setData] = useState<ReplayData | null>(null);
  const [minute, setMinute] = useState(initialMinute());
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(5);
  const [selectedWaveId, setSelectedWaveId] = useState("");
  const [page, setPage] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("page") === "topology" ? "topology" : "twin";
  });
  const [selection, setSelection] = useState<DetailSelection>(null);
  const [modelSettings, setModelSettings] = useState({
    pickerSpeedPct: 100,
    reachtruckOpsPct: 100,
    caseReplenishmentPerHour: 5,
    palletDropMinutes: 3,
    palletExchangeMinutes: 3,
    dockPalletsPerHour: 15,
    trailTtlMinutes: 20
  });

  useEffect(() => {
    loadReplayData().then(setData);
  }, []);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setMinute((value) => value >= SHIFT_MINUTES ? 0 : value + 1);
    }, Math.max(20, 900 / speed));
    return () => window.clearInterval(timer);
  }, [playing, speed]);

  const waveOptions = useMemo(() => {
    if (!data) return [];
    return Array.from(new Set(data.events.map((event) => event.wave_id).filter(Boolean))).sort() as string[];
  }, [data]);

  const state = useMemo(() => {
    if (!data) return null;
    const events = visibleEvents(data.events, minute, selectedWaveId);
    const metrics = currentMetrics(data.metrics, minute);
    const resources = resourceStateAt(data.layout, data.events, minute, selectedWaveId, modelSettings.trailTtlMinutes);
    const collisions = activeCollisions(data.events, minute, 120, selectedWaveId);
    const tasks = replenishmentTasksAt(data.events, minute);
    const pickFaceFill = pickFaceFillAt(data.stock, data.events, minute);
    const dockPallets = dockPalletsAt(data.events, minute);
    const unitsDone = Number(metrics?.done_pick_lines || events.filter((event) => event.event_type === "PICKER_TASK_DONE").length);
    const totalUnits = Number(metrics?.total_pick_lines || data.report.totals?.pick_lines || Math.max(1, unitsDone));
    const activePickers = resources.filter((resource) => resource.kind === "picker" && resource.status !== "ожид.").length;
    const avgSpeed = activePickers
      ? resources.filter((resource) => resource.kind === "picker").reduce((sum, resource) => sum + resource.speedRatio, 0) / activePickers / 100 * 1.21
      : 0;
    const forecastMultiplier = modelSettings.pickerSpeedPct / 100 * modelSettings.reachtruckOpsPct / 100 * (modelSettings.dockPalletsPerHour / 15);
    return { events, resources, collisions, tasks, pickFaceFill, dockPallets, unitsDone, totalUnits, activePickers, avgSpeed: avgSpeed * modelSettings.pickerSpeedPct / 100, forecastMultiplier };
  }, [data, minute, selectedWaveId, modelSettings]);

  if (page === "topology") {
    return (
      <AppErrorBoundary resetKey={page}>
        <TopologyAdminPage onBack={() => setPage("twin")} onCreateNew={() => setPage("topology-editor")} />
      </AppErrorBoundary>
    );
  }

  if (page === "topology-editor") {
    return (
      <AppErrorBoundary resetKey={page}>
        <TopologyGridEditorPage onBack={() => setPage("topology")} />
      </AppErrorBoundary>
    );
  }

  if (!data || !state) {
    return <main className="loading-screen"><b>WMS PRO</b><span>Загружаем цифровой двойник склада...</span></main>;
  }

  const currentWave = selectedWaveId || inferWaveByMinute(minute);
  const runId = data.report.run_id || data.layout.run_id || "demo";
  const overdueCount = state.tasks.filter((task) => task.overdueMinutes > 0 && task.status !== "DONE").length;

  return (
    <AppErrorBoundary resetKey={page}>
    <div className="admin-app">
      <aside className="mini-sidebar">
        <div className="brand-mark">W</div>
        {["⌂", "↗", "▦", "▣", "▤", "▥"].map((icon, index) => <button key={index}>{icon}</button>)}
        <button className="active">⌁</button>
        <button title="Управление топологией склада" onClick={() => setPage("topology")}>⌗</button>
        <button>●</button>
      </aside>

      <main className="admin-workspace">
        <header className="twin-topbar">
          <div className="twin-title">
            <div className="cube-logo"><span /><i /><b /></div>
            <div><h1>Цифровой двойник склада</h1><p><span className="online-dot" /> Онлайн · React admin</p></div>
          </div>
          <div className="twin-top-controls">
            <label>Смена<select><option>1 (08:00-20:00)</option></select></label>
            <label>Волна<select value={selectedWaveId} onChange={(event) => setSelectedWaveId(event.target.value)}><option value="">Все волны</option>{waveOptions.map((wave) => <option key={wave}>{wave}</option>)}</select></label>
            <label>Зона<select><option>Все зоны</option></select></label>
            <div className="twin-clock"><span>Время</span><b>{clock(minute)}</b></div>
            <button className="icon-button">⌕</button>
            <button className="icon-button alert">{state.collisions.length}</button>
            <div className="profile compact-profile"><span className="avatar" /><div><b>admin</b><small>operator</small></div></div>
          </div>
        </header>

        <section className="twin-page">
          <KpiRow
            unitsDone={state.unitsDone}
            totalUnits={state.totalUnits}
            activePickers={state.activePickers}
            collisions={state.collisions}
            overdue={overdueCount}
            avgSpeed={state.avgSpeed}
          />

          <section className="twin-grid">
            <LeftPanel tasks={state.tasks} trucks={state.resources.filter((resource) => resource.kind === "reachtruck")} onSelect={setSelection} />
            <article className="twin-scene-card">
              <div className="scene-toolbar">
                <div><b>{runId}</b><span>{data.layout.cells.length} ячеек · U-маршруты через фронт/пожарный/задний проход · {state.events.length} событий</span></div>
                <div className="layer-toggles">
                  <label><input type="checkbox" defaultChecked /> Комплектовщики</label>
                  <label><input type="checkbox" defaultChecked /> RTP</label>
                  <label><input type="checkbox" defaultChecked /> Маршруты</label>
                  <label><input type="checkbox" defaultChecked /> Коллизии</label>
                  <label><input type="checkbox" defaultChecked /> Heatmap</label>
                </div>
              </div>
              <WarehouseScene
                layout={data.layout}
                resources={state.resources}
                collisions={state.collisions}
                pickFaceFill={state.pickFaceFill}
                dockPallets={state.dockPallets}
                tasks={state.tasks}
                minute={minute}
                selectedWaveId={selectedWaveId}
                onSelect={setSelection}
              />
              <ModelSettingsPanel
                settings={modelSettings}
                forecastMultiplier={state.forecastMultiplier}
                onChange={(key, value) => setModelSettings((current) => ({ ...current, [key]: value }))}
              />
              <CapacityPanel report={data.report} />
              <DetailCard selection={selection} collisions={state.collisions} tasks={state.tasks} />
              <div className="legend-card"><span><i className="green" /> Норма</span><span><i className="blue" /> Движение</span><span><i className="amber" /> Риск</span><span><i className="red" /> Коллизия</span><span><i className="gray" /> Ожидание</span></div>
              <div className="route-widget">
                <h3>Прогресс маршрутов ({currentWave})</h3>
                {[101, 102, 103, 104].map((route, index) => {
                  const percent = Math.max(8, 35 - index * 9);
                  return <div className="route-row" key={route}><span>R-{route}</span><span className="route-bar"><i className={index === 3 && state.collisions.length ? "red" : percent > 30 ? "amber" : "blue"} style={{ width: `${percent}%` }} /></span><span>{index === 3 && state.collisions.length ? "Заблокирован" : `${percent}%`}</span></div>;
                })}
              </div>
            </article>
            <RightPanel collisions={state.collisions} onSelect={setSelection} />
          </section>

          <Timeline
            minute={minute}
            playing={playing}
            speed={speed}
            events={data.events}
            onMinute={setMinute}
            onPlayToggle={() => setPlaying((value) => !value)}
            onSpeed={setSpeed}
          />
          <ResourcePerformancePanel metrics={data.metrics} events={data.events} report={data.report} minute={minute} />
        </section>
      </main>
    </div>
    </AppErrorBoundary>
  );
}

class AppErrorBoundary extends Component<{ children: ReactNode; resetKey: string }, { error: Error | null }> {
  state: { error: Error | null } = { error: null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidUpdate(prevProps: { resetKey: string }) {
    if (prevProps.resetKey !== this.props.resetKey && this.state.error) {
      this.setState({ error: null });
    }
  }

  componentDidCatch(error: Error) {
    console.error("Admin UI runtime error", error);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="loading-screen error-screen">
        <b>Ошибка интерфейса</b>
        <span>{this.state.error.message}</span>
        <button onClick={() => this.setState({ error: null })}>Вернуться к странице</button>
      </main>
    );
  }
}

type ModelSettings = {
  pickerSpeedPct: number;
  reachtruckOpsPct: number;
  caseReplenishmentPerHour: number;
  palletDropMinutes: number;
  palletExchangeMinutes: number;
  dockPalletsPerHour: number;
  trailTtlMinutes: number;
};

function ModelSettingsPanel({ settings, forecastMultiplier, onChange }: {
  settings: ModelSettings;
  forecastMultiplier: number;
  onChange: (key: keyof ModelSettings, value: number) => void;
}) {
  return (
    <div className="model-settings-card">
      <header><b>Настройки модели</b><span>forecast x{forecastMultiplier.toFixed(2)}</span></header>
      <SettingSlider label="Комплектовщики" value={settings.pickerSpeedPct} min={60} max={180} suffix="%" onChange={(value) => onChange("pickerSpeedPct", value)} />
      <SettingSlider label="RTP операции" value={settings.reachtruckOpsPct} min={60} max={140} suffix="%" onChange={(value) => onChange("reachtruckOpsPct", value)} />
      <SettingSlider label="Коробочное пополнение" value={settings.caseReplenishmentPerHour} min={2} max={10} suffix="/час" onChange={(value) => onChange("caseReplenishmentPerHour", value)} />
      <SettingSlider label="Спуск паллеты" value={settings.palletDropMinutes} min={2} max={6} suffix="мин" onChange={(value) => onChange("palletDropMinutes", value)} />
      <SettingSlider label="Убрать/поставить" value={settings.palletExchangeMinutes} min={0} max={6} suffix="мин" onChange={(value) => onChange("palletExchangeMinutes", value)} />
      <SettingSlider label="Ворота" value={settings.dockPalletsPerHour} min={8} max={24} suffix="/час" onChange={(value) => onChange("dockPalletsPerHour", value)} />
      <SettingSlider label="Шлейф маршрута" value={settings.trailTtlMinutes} min={5} max={20} suffix="мин" onChange={(value) => onChange("trailTtlMinutes", value)} />
    </div>
  );
}

function SettingSlider({ label, value, min, max, suffix, onChange }: {
  label: string;
  value: number;
  min: number;
  max: number;
  suffix: string;
  onChange: (value: number) => void;
}) {
  return (
    <label className="setting-slider">
      <span>{label}<b>{value}{suffix}</b></span>
      <input type="range" min={min} max={max} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function initialMinute(): number {
  const hash = new URLSearchParams(window.location.hash.replace(/^#/, "").replace(/;/g, "&"));
  const query = new URLSearchParams(window.location.search);
  return Number(query.get("minute") || hash.get("minute") || 102);
}
