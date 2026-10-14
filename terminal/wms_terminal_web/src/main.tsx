import { migrateRetailcaseStorage } from "./store/storageBrandMigration";
import React from "react";
import ReactDOM from "react-dom/client";
import { ConfigProvider } from "antd";
import ruRU from "antd/locale/ru_RU";
import App from "./App";
import "./styles.css";

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch((error) => {
      console.warn("Service worker registration failed", error);
    });
  });
}

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

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={ruRU}
      theme={{
        token: {
          colorPrimary: "#0b5ed7",
          borderRadius: 8,
          fontFamily: "Inter, Segoe UI, Arial, sans-serif"
        }
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
);
