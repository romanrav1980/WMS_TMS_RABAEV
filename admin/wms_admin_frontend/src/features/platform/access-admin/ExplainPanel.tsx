import { useState } from "react";
import { apiFetch } from "../../../api";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { accessHelp } from "./help";
import { readError } from "./useApiRead";
import { OBJECT_KINDS } from "./types";
import type { ExplainResult } from "./types";

/** Объяснение доступа: разрешено ли право на объекте и откуда (POST /api/access/explain, только чтение). */
export function ExplainPanel({ rights }: { rights: string[] }) {
  const [form, setForm] = useState({ permission: "", object_kind: "WAREHOUSE", object_id: "", username: "" });
  const [result, setResult] = useState<ExplainResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true); setError(""); setResult(null);
    try {
      setResult(await apiFetch<ExplainResult>("/api/access/explain", { method: "POST", body: JSON.stringify({
        permission: form.permission, object_kind: form.object_kind, object_id: form.object_id.trim() || null, username: form.username.trim() || null }) }));
    } catch (reason) { setError(readError(reason)); } finally { setBusy(false); }
  };
  return <section className="aa-form" aria-labelledby="aa-explain-title">
    <h3 id="aa-explain-title">Объяснение доступа <HelpHint help={accessHelp.tabExplain} /></h3>
    <label>Право<input list="aa-rights" value={form.permission} onChange={e => setForm({ ...form, permission: e.target.value.trim() })} title="Код права, например transport_dispatch_view." data-help-id="access.explain.permission" /></label>
    <datalist id="aa-rights">{rights.map(r => <option key={r} value={r} />)}</datalist>
    <label>Вид объекта<select value={form.object_kind} onChange={e => setForm({ ...form, object_kind: e.target.value })} title="Вид объекта проверки." data-help-id="access.explain.kind">
      {[...OBJECT_KINDS, "PLATFORM"].map(k => <option key={k}>{k}</option>)}</select></label>
    <label>Код объекта<input value={form.object_id} maxLength={80} onChange={e => setForm({ ...form, object_id: e.target.value })} title="Код склада, магазина и т. п. Для PLATFORM не нужен." data-help-id="access.explain.object" /></label>
    <label>Пользователь (пусто — вы)<input value={form.username} maxLength={50} onChange={e => setForm({ ...form, username: e.target.value })} title="Чужое объяснение требует права администрирования." data-help-id="access.explain.user" /></label>
    <HelpButton help={accessHelp.explainRun} unavailable={busy ? "идёт запрос" : !/^[a-z][a-z0-9_]*$/.test(form.permission) && "укажите код права"} onClick={() => void run()}>Проверить</HelpButton>
    {error && <p role="alert">{error}</p>}
    {result && <div role="status" className={"aa-msg " + (result.allowed ? "aa-ok" : "aa-bad")}>
      <strong>{result.allowed ? "Разрешено" : "Запрещено"}</strong> · ревизия доступа {result.access_revision}
      {result.reasons.length === 0 ? <p>Сервер не указал источник.</p> :
        <ul>{result.reasons.map((r, i) => <li key={i}>{Object.entries(r).map(([k, v]) => `${k}: ${typeof v === "object" ? JSON.stringify(v) : String(v)}`).join(" · ")}</li>)}</ul>}
    </div>}
  </section>;
}
