import React from "react";
import ReactDOM from "react-dom/client";
import { StoreReceivingApp } from "./features/delivery";

if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/store/sw.js", { scope: "/store/" }).catch(() => {
      // The live application remains usable; its command journal owns retry.
    });
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><StoreReceivingApp /></React.StrictMode>
);
