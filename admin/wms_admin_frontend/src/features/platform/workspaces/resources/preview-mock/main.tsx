// MOCK-превью C0074: учебный набор данных для приёмки UI до готовности API. В production-сборку не входит; не выдаётся за реальные данные.
import { useState } from "react";
import ReactDOM from "react-dom/client";
import { KnowledgePanel } from "../../../help/KnowledgePanel";
import { PlannerBody } from "../ResourcePlanner";
import type { GanttSelection } from "../timelineTypes";
import { mockTimeline } from "./mockTimeline";
import "../../ops.css";

function MockGantt() {
  const [tz, setTz] = useState<string | null>(new URLSearchParams(location.search).get("tz") === "unknown" ? null : "Europe/Moscow");
  const [selection, setSelection] = useState<GanttSelection>(null);
  return <main className="ops" style={{ display: "block" }}>
    <div className="ops-panel" style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap", marginBottom: 10 }}>
      <span className="rg-mock">MOCK · учебные данные, не реальный склад</span>
      <label><input type="checkbox" checked={tz == null} onChange={e => setTz(e.target.checked ? null : "Europe/Moscow")} /> пояс склада не подтверждён</label>
    </div>
    <section className="ops-panel"><PlannerBody timeline={mockTimeline(tz)} selection={selection} onSelect={setSelection} /></section>
  </main>;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(<><MockGantt /><KnowledgePanel /></>);
