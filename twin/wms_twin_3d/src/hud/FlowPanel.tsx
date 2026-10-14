import { useState } from "react";
import { useTwin } from "../store/twinStore";
import { computeFlow } from "../ui/kpi";

// Поток площадки: шаги процесса WMS → TMS с текущими объёмами, как «Site flow» в NuriTrack.
export function FlowPanel() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const [collapsed, setCollapsed] = useState(false);
  const flow = computeFlow(world);
  return (
    <section className="panel flow-panel">
      <header>
        <b>Поток площадки</b>
        <button type="button" className="link" onClick={() => setCollapsed(!collapsed)}>{collapsed ? "Развернуть" : "Свернуть"}</button>
      </header>
      {!collapsed && (
        <ol className="flow">
          {flow.map((step) => (
            <li key={step.key}>
              <span className="flow-icon">{step.icon}</span>
              <span className="flow-text">
                <b>{step.title}</b>
                <small>{step.note}</small>
              </span>
              <span className="flow-value">{step.value}</span>
            </li>
          ))}
        </ol>
      )}
      <footer className="hint">Симуляция по реальным шагам процесса WMS/TMS</footer>
    </section>
  );
}
