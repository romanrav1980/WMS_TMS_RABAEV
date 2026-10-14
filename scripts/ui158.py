import json
from pathlib import Path
out={}
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.html");s=p.read_text(encoding="utf-8")
s=s.replace('<button id="sdReadDraft">Открыть предложение</button><button id="sdCancelDraft">Отменить черновик</button>', '''<button id="sdReadDraft">Открыть предложение</button><button id="sdCancelDraft">Отменить черновик</button>
<label><input id="sdGeometryChecked" type="checkbox">Геометрия целой паллеты и ячейки проверена</label>
<label><input id="sdCompatibilityChecked" type="checkbox">Совместимость товара с диапазоном проверена</label>
<button id="sdApproveDraft">Утвердить диапазон</button>
<p>Утверждение активирует новый диапазон. Старый остаётся для завершения прежних заданий и вымывания запаса; новые пополнения туда не назначаются.</p>
<label>Идентификатор назначения артикула для завершения вымывания<input id="sdDrainMapping" type="number" min="1"></label>
<button id="sdCloseDrain">Завершить вымывание пустого назначения</button>
<button id="sdClearDraftPending">Очистить локальный повтор после проверки результата</button>''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.js");s=p.read_text(encoding="utf-8")
s=s.replace('    el("sdProposal").value = result.proposal_id;', '    if (result.proposal_id) el("sdProposal").value = result.proposal_id;')
s=s.replace('result.status === "DRAFT" ? "Сохранение записано. Откройте предложение для актуального состояния; диапазон не применён." : "Отмена записана; история сохранена."',
'''result.status === "DRAFT" ? "Сохранение записано. Откройте предложение для актуального состояния; диапазон не применён." :
      result.status === "APPROVED" ? "Диапазон утверждён; прежние задания сохранены, старые назначения вымываются." :
      result.status === "DRAIN_CLOSED" ? "Пустое назначение выведено из диапазона; история сохранена." : "Отмена записана; история сохранена."''')
old='''            if (!Number.isSafeInteger(ware) || ware <= 0 || !article || !proposal) throw Error("Укажите склад, артикул и идентификатор предложения.");
            record = {actorScope: actorScope(), path: draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/cancel",
              body: {operation_id: "RANGE.CANCEL:" + crypto.randomUUID(), reason}};'''
new='''            if (!Number.isSafeInteger(ware) || ware <= 0 || !article || (kind !== "close" && !proposal)) throw Error("Укажите склад, артикул и идентификатор предложения.");
            let path, body;
            if (kind === "close") {
              const mapping = Number(el("sdDrainMapping").value);
              if (!Number.isSafeInteger(mapping) || mapping <= 0) throw Error("Укажите идентификатор вымываемого назначения.");
              path = draftPath(ware, article) + "/actions/close-drain";
              body = {operation_id: "RANGE.CLOSE:" + crypto.randomUUID(), pick_face_articul_id: mapping, reason};
            } else if (kind === "approve") {
              if (!el("sdGeometryChecked").checked || !el("sdCompatibilityChecked").checked) throw Error("Перед утверждением нужна фактическая проверка геометрии и совместимости.");
              path = draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/approve";
              body = {operation_id: "RANGE.APPROVE:" + crypto.randomUUID(), geometry_checked: true, product_compatibility_checked: true, reason};
            } else {
              path = draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/cancel";
              body = {operation_id: "RANGE.CANCEL:" + crypto.randomUUID(), reason};
            }
            record = {actorScope: actorScope(), path, body};'''
if old not in s:raise ValueError("UI mutation anchor missing")
s=s.replace(old,new)
s=s.replace('  el("sdReadDraft").addEventListener("click", readDraft);','''  el("sdReadDraft").addEventListener("click", readDraft);
  el("sdApproveDraft").addEventListener("click", () => mutation("approve"));
  el("sdCloseDrain").addEventListener("click", () => mutation("close"));
  el("sdClearDraftPending").addEventListener("click", () => {
    if (busy) return;
    try {
      const record = JSON.parse(localStorage.getItem(pendingKey()) || "null");
      if (!record) throw Error("Локального повтора нет.");
      localStorage.setItem(pendingKey() + ":last-cleared", JSON.stringify(record));
      localStorage.removeItem(pendingKey());
      el("sdDraftMessage").textContent = "Локальный повтор " + record.body.operation_id + " очищен. Запись Oracle сохранена; прежний запрос оставлен в локальной истории.";
    } catch (error) {el("sdDraftMessage").textContent = error.message;}
  });''')
s=s.replace('++sequence; lastPreview = null; el("sdSaveDraft").disabled = true;', '++sequence; lastPreview = null; el("sdGeometryChecked").checked = false; el("sdCompatibilityChecked").checked = false; el("sdSaveDraft").disabled = true;')
out[str(p)]=s
print(json.dumps(out))
