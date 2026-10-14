import json
from pathlib import Path
out={}
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.html");s=p.read_text(encoding="utf-8").replace('</section><section class="panel" id="sdResult">','''</section>
<section class="panel"><h2>Предложение диапазона</h2>
<p>Сохранение создаёт черновик с исходными данными и автором. Слотирование и действующие задания пока не изменяются.</p>
<label>Основание сохранения или отмены<input id="sdDraftReason" maxlength="2000"></label>
<button id="sdSaveDraft" disabled>Сохранить рассчитанное предложение</button>
<button id="sdRetryDraft">Повторить неподтверждённую команду</button>
<label>Идентификатор предложения<input id="sdProposal" maxlength="100"></label>
<button id="sdReadDraft">Открыть предложение</button><button id="sdCancelDraft">Отменить черновик</button>
<p id="sdDraftMessage" role="status"></p><pre id="sdDraftResult"></pre></section>
<section class="panel" id="sdResult">''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/slotting-demand.js");s=p.read_text(encoding="utf-8")
s=s.replace('  let sequence = 0, identity = "";','  let sequence = 0, identity = "", lastPreview = null, busy = false;\n  const pendingKey = () => "retailcase.slotting.draft:" + auth().state.apiBase + ":" + auth().state.user?.username;\n  const actorScope = () => auth().state.apiBase + "|" + auth().state.user?.username;')
s=s.replace('    const serial = ++sequence, selected = scope(); el("sdResult").replaceChildren();','    const serial = ++sequence, selected = scope(); el("sdResult").replaceChildren();\n    lastPreview = null; el("sdSaveDraft").disabled = true;')
s=s.replace('      const q = result.scenario, unit = result.base_uom;','      lastPreview = {scope: selected, body, result, ware, article};\n      el("sdSaveDraft").disabled = result.range_recommendation?.status !== "NOMINAL_RECOMMENDATION";\n      const q = result.scenario, unit = result.base_uom;')
s=s.replace('++sequence; el("sdResult").replaceChildren();','++sequence; lastPreview = null; el("sdSaveDraft").disabled = true; el("sdResult").replaceChildren();')
pos=s.index('  el("sdRead").addEventListener')
code="""  const draftPath = (ware, article) => "/api/inventory/slotting/warehouses/" + ware + "/articles/" + encodeURIComponent(article) + "/recommendations";
  async function sendDraft(record) {
    const owner = actorScope(), key = pendingKey();
    if (record.actorScope !== owner) throw Error("Команда принадлежит другому пользователю или серверу.");
    const response = await fetch(auth().state.apiBase.replace(/\\/$/, "") + record.path,
      {method: "POST", headers: {...auth().headers(), "Content-Type": "application/json"}, body: JSON.stringify(record.body)});
    const result = await response.json();
    if (!response.ok) throw Error(result.detail?.message || result.detail?.code || JSON.stringify(result.detail));
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved?.body.operation_id === record.body.operation_id) localStorage.removeItem(key);
    if (owner !== actorScope()) return;
    el("sdProposal").value = result.proposal_id;
    el("sdDraftMessage").textContent = result.status === "DRAFT" ? "Черновик сохранён. Диапазон не применён." : "Отмена записана; история сохранена.";
    el("sdDraftResult").textContent = JSON.stringify(result, null, 2);
  }
  async function mutation(kind) {
    if (busy) return;
    busy = true;
    try {
      const execute = async () => {
        let record = JSON.parse(localStorage.getItem(pendingKey()) || "null");
        if (kind !== "retry") {
          if (record) throw Error("Сначала повторите неподтверждённую исходную команду.");
          const reason = el("sdDraftReason").value.trim();
          if (reason.length < 8) throw Error("Укажите основание, не менее 8 символов.");
          if (kind === "save") {
            if (!lastPreview || lastPreview.scope !== scope() || lastPreview.result.range_recommendation?.status !== "NOMINAL_RECOMMENDATION")
              throw Error("Сначала рассчитайте полный текущий вариант.");
            record = {actorScope: actorScope(), path: draftPath(lastPreview.ware, lastPreview.article),
              body: {...lastPreview.body, operation_id: "RANGE.DRAFT:" + crypto.randomUUID(),
                expected_source_signature: lastPreview.result.source_signature, reason}};
          } else {
            const ware = Number(el("sdWare").value), article = el("sdArticle").value.trim(), proposal = el("sdProposal").value.trim();
            if (!Number.isSafeInteger(ware) || ware <= 0 || !article || !proposal) throw Error("Укажите склад, артикул и идентификатор предложения.");
            record = {actorScope: actorScope(), path: draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/cancel",
              body: {operation_id: "RANGE.CANCEL:" + crypto.randomUUID(), reason}};
          }
          localStorage.setItem(pendingKey(), JSON.stringify(record));
        }
        if (!record) throw Error("Неподтверждённой команды нет.");
        el("sdDraftMessage").textContent = "Отправляется исходная команда " + record.body.operation_id + ". При сбое повторите её без изменений.";
        await sendDraft(record);
      };
      if (navigator.locks) await navigator.locks.request(pendingKey(), execute);
      else await execute();
    } catch (error) {el("sdDraftMessage").textContent = error.message;}
    finally {busy = false;}
  }
  async function readDraft() {
    const selected = scope(), owner = actorScope();
    el("sdDraftResult").textContent = "";
    try {
      const ware = Number(el("sdWare").value), article = el("sdArticle").value.trim(), proposal = el("sdProposal").value.trim();
      if (!Number.isSafeInteger(ware) || ware <= 0 || !article || !proposal) throw Error("Укажите склад, артикул и предложение.");
      const response = await fetch(auth().state.apiBase.replace(/\\/$/, "") + draftPath(ware, article) + "/" + encodeURIComponent(proposal),
        {headers: auth().headers()});
      const result = await response.json();
      if (!response.ok) throw Error(result.detail?.message || JSON.stringify(result.detail));
      if (selected !== scope() || owner !== actorScope()) return;
      el("sdDraftResult").textContent = JSON.stringify(result, null, 2);
      el("sdDraftMessage").textContent = "Состояние: " + result.status + " · автор: " + result.created_by + ". Это история предложения.";
    } catch (error) {if (selected === scope() && owner === actorScope()) el("sdDraftMessage").textContent = error.message;}
  }
  el("sdSaveDraft").addEventListener("click", () => mutation("save"));
  el("sdRetryDraft").addEventListener("click", () => mutation("retry"));
  el("sdCancelDraft").addEventListener("click", () => mutation("cancel"));
  el("sdReadDraft").addEventListener("click", readDraft);
"""
s=s[:pos]+code+s[pos:]
s=s.replace('identity = current; ++sequence;', 'identity = current; el("sdDraftResult").textContent = ""; el("sdDraftMessage").textContent = ""; ++sequence;')
out[str(p)]=s
print(json.dumps(out))
