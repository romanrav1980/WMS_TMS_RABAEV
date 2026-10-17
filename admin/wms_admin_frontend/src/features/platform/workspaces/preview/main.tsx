// Dev-превью C0056 до интеграции (Codex): реальный вход и реальный API, без моков. В production-сборку не входит.
import ReactDOM from "react-dom/client";
import { KnowledgePanel, SessionGate } from "../..";
import { WorkplaceHome } from "..";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <SessionGate><WorkplaceHome /><KnowledgePanel /></SessionGate>
);
