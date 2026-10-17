// Dev-превью карточки квитанции запуска: реальный вход и реальный API (только чтение). В production-сборку не входит.
import ReactDOM from "react-dom/client";
import { KnowledgePanel, SessionGate } from "../../..";
import { LaunchReceiptCard } from "../LaunchReceiptCard";
import "../../ops.css";
import "../../../access-admin/access-admin.css";

const q = new URLSearchParams(location.search);
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <SessionGate><main className="ops" style={{ display: "block" }}><div className="ops-panel" style={{ maxWidth: 760 }}>
    <LaunchReceiptCard initialWave={q.get("wave_id") ?? ""} initialOperation={q.get("operation_id") ?? ""} /></div></main><KnowledgePanel /></SessionGate>
);
