(() => {
  "use strict";
  let documentId = null, busy = false;
  const button = document.getElementById("receiptReverse");
  const reason = document.getElementById("receiptReverseReason");
  const status = document.getElementById("receiptReverseMessage");
  const context = () => {
    const auth = window.wmsAdminAuth;
    return { base: (auth.state.apiBase || "http://127.0.0.1:8088").replace(/\/$/, ""),
      actor: auth.state.user?.username || "" };
  };
  const key = () => JSON.stringify(["nicora.receiptReverseIntent", context().base, context().actor]);
  window.addEventListener("wms-receipt-selected", event => {
    documentId = event.detail.naklad_id;
    status.textContent = "Сторно допускается для полного поступления, которое ещё находится в зоне приёмки без расхода и резерва.";
  });
  button.addEventListener("click", async () => {
    if (busy) return;
    busy = true; button.disabled = true;
    let storageKey;
    try {
      storageKey = key();
      let intent = JSON.parse(localStorage.getItem(storageKey) || "null");
      if (!intent) {
        if (!Number.isSafeInteger(Number(documentId)) || Number(documentId) < 1)
          throw new Error("Выберите поставку.");
        const text = reason.value.trim();
        if (!text) throw new Error("Укажите причину сторно.");
        intent = { document_id: Number(documentId),
          body: { operation_id: "RECEIPT.REVERSE.UI:" + crypto.randomUUID(), reason: text } };
        localStorage.setItem(storageKey, JSON.stringify(intent));
      } else if (Number(documentId) !== intent.document_id || reason.value.trim() !== intent.body.reason) {
        reason.value = intent.body.reason;
        throw new Error("Есть незавершённое сторно накладной " + intent.document_id +
          ". Откройте её и повторите сохранённую команду.");
      }
      const response = await fetch(context().base + "/api/inventory/stock-posting/receipt-documents/" +
        intent.document_id + "/reverse", { method: "POST",
        headers: window.wmsAdminAuth.headers({ "Content-Type": "application/json" }),
        body: JSON.stringify(intent.body) });
      const data = await response.json();
      if (!response.ok) {
        if (data.detail?.outcome_confirmed === true || [400,401,403,422].includes(response.status))
          localStorage.removeItem(storageKey);
        throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data));
      }
      localStorage.removeItem(storageKey);
      status.textContent = "Сторно подтверждено. Операция " + data.operation_id + ". История сохранена.";
    } catch (error) {
      let saved = false;
      try { saved = Boolean(storageKey && localStorage.getItem(storageKey)); } catch (_) { /* No request starts without durable intent. */ }
      status.textContent = error.message + (saved ? " Команда сохранена; повтор использует тот же ID." : "");
    } finally {
      busy = false; button.disabled = !window.wmsAdminAuth.hasPermission("stock_receipt_reverse");
    }
  });
})();
