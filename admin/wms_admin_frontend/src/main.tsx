import { migrateRetailcaseStorage } from "./replay/storageBrandMigration";
import ReactDOM from "react-dom/client";
import App from "./App";

try {
  migrateRetailcaseStorage(localStorage);
} catch (error) {
  const container = document.getElementById("root");
  if (container) {
    container.setAttribute("role", "alert");
    container.textContent = "Сохранённые команды требуют разбора. " + String(error);
  }
  throw error;
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <App />
);
