import { useEffect } from "react";
import { BottomTabs } from "./hud/BottomTabs";
import { DetailPanel } from "./hud/DetailPanel";
import { FleetTable } from "./hud/FleetTable";
import { FlowPanel } from "./hud/FlowPanel";
import { KpiRow } from "./hud/KpiRow";
import { SceneToolbar } from "./hud/SceneToolbar";
import { TopBar } from "./hud/TopBar";
import { TwinCanvas } from "./scene/TwinCanvas";
import { useTwin } from "./store/twinStore";

const TICK_MS = 100;

export function App() {
  const panelsHidden = useTwin((s) => s.panelsHidden);
  const layoutVersion = useTwin((s) => s.layoutVersion);
  useEffect(() => {
    let last = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now();
      // Ограничение шага: после неактивной вкладки модель не «проматывает» минуты одним скачком.
      useTwin.getState().tick(Math.min(0.5, (now - last) / 1000));
      last = now;
    }, TICK_MS);
    return () => window.clearInterval(timer);
  }, []);
  return (
    <div className={`app ${panelsHidden ? "panels-hidden" : ""}`}>
      <TwinCanvas key={layoutVersion} />
      <TopBar />
      <div className="hud">
        <KpiRow />
        <FlowPanel />
        <DetailPanel />
        <BottomTabs />
        <FleetTable />
      </div>
      <SceneToolbar />
    </div>
  );
}
