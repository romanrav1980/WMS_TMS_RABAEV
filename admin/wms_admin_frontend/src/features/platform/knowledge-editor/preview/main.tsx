// Dev-превью C0056 до интеграции в App (Codex): реальный вход и реальный API, без моков. В production-сборку не входит.
import ReactDOM from "react-dom/client";
import { KnowledgePanel, SessionGate } from "../..";
import { KnowledgeEditorPage } from "..";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <SessionGate><KnowledgeEditorPage /><KnowledgePanel /></SessionGate>
);
