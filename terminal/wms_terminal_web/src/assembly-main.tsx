import React from "react";
import ReactDOM from "react-dom/client";
import { AssemblyScaleApp } from "./features/inventory";

if ("serviceWorker" in navigator && import.meta.env.PROD) {
 window.addEventListener("load", () => {
  navigator.serviceWorker.register("/assembly/sw.js", { scope: "/assembly/" }).catch(() => {});
 });
}
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><AssemblyScaleApp /></React.StrictMode>);
