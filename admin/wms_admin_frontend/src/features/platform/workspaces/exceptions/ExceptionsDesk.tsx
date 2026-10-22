import { useMemo, useState } from "react";
import { useApiRead } from "../../access-admin";
import { HelpButton } from "../../help/HelpButton";
import { rawLink } from "../OpsParts";
import { fmtTime } from "../resources/timelineModel";
import { WarehousePicker } from "../resources/WarehousePicker";
import { useUrlWarehouse } from "../useUrlWarehouse";
import { readPending, savePending, sendPending } from "./exceptionsCommands";
import type { ExceptionsIntent } from "./exceptionsCommands";
import { ACTIONS, ACTION_TITLE, EXTERNAL_TITLE, STATE_TITLE, compositionText, parseSnapshot, refusalText, releaseBlocked } from "./exceptionsModel";
import type { CaseAction, CaseDetail, Discrepancy, ExceptionsSnapshot, QualityCase } from "./exceptionsModel";
import { excHelp } from "./help";

type Section = "quarantine" | "cases" | "discrepancies";
const SECTIONS: { id: Section; title: string }[] = [{ id: "quarantine", title: "Карантин" }, { id: "cases", title: "Дела качества" }, { id: "discrepancies", title: "Расхождения пересчёта" }];
type Field = { name: string; label: string; value: string; min?: number };
type Form = { key: string; title: string; fields: Field[]; send: (values: Record<string, string>) => void } | null;
type Run = (title: string, kind: ExceptionsIntent["kind"], body: Record<string, unknown>) => void;

/** Рабочее место исключений склада (C-0152): карантин, решение контролёра, утверждение списания руководством, расхождения пересчёта.
 *  Решения выполняет сервер существующими командами; права склада и собственника проверяются там же. */
export function ExceptionsDesk({ reload }: { reload: number }) {
  const [wh, setWh] = useUrlWarehouse();
  return <>
    <div className="ops-panel rg-window" style={{ gridColumn: "1/-1" }}><WarehousePicker capability="tradecase" value={wh} onChange={setWh} /></div>
    {wh ? <ExceptionsBody key={wh} wh={wh} reload={reload} /> : <p className="ops-panel ops-note" style={{ gridColumn: "1/-1" }}>Выберите склад: исключения показываются по одному складу.</p>}
  </>;
}

function ExceptionsBody({ wh, reload }: { wh: string; reload: number }) {
  const [local, setLocal] = useState(0), [tick, setTick] = useState(0);
  const read = useApiRead<unknown>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/exceptions`, reload + local);
  const parsed = useMemo((): { snap: ExceptionsSnapshot | null; error: string } => {
    if (read.data == null) return { snap: null, error: "" };
    try { return { snap: parseSnapshot(read.data, Number(wh)), error: "" }; } catch (e) { return { snap: null, error: (e as Error).message }; }
  }, [read.data, wh]);
  // Журнал команды читается из браузера при каждом изменении: переживает перезагрузку.
  const pending = useMemo(() => readPending(wh), [wh, tick]), intent = pending.intent;
  const [section, setSection] = useState<Section>("quarantine"), [form, setForm] = useState<Form>(null);
  const [message, setMessage] = useState(""), [busy, setBusy] = useState(false);
  const send = async (make: () => ExceptionsIntent) => {
    let next: ExceptionsIntent;
    try { next = make(); } catch (e) { setMessage((e as Error).message); return; }
    setBusy(true); setMessage("");
    const result = await sendPending(next);
    setBusy(false); setTick(n => n + 1);
    if (result.kind === "ack") { setForm(null); setMessage(`Выполнено: ${next.title}.`); }
    else setMessage(result.kind === "refused" ? refusalText(result.code) : result.message);
    setLocal(n => n + 1);
  };
  const run: Run = (title, kind, body) => send(() => savePending(wh, kind, title, body));
  const blocked = busy || Boolean(intent) || Boolean(pending.damaged), snap = parsed.snap;
  const props = { snap: snap!, blocked, run, form, setForm, wh };
  return <section className="ops-panel" style={{ gridColumn: "1/-1" }} aria-label="Исключения склада">
    <h3>Исключения склада</h3>
    <p className="ops-note">{snap ? `Снимок сервера ${fmtTime(null, snap.observed_at)}` : read.loading ? "Загрузка…" : ""}{" "}
      <HelpButton help={excHelp.refresh} onClick={() => setLocal(n => n + 1)}>Обновить</HelpButton></p>
    {(read.error || parsed.error) && <p role="alert" className="ops-err">{read.error.includes("QUALITY_NOT_AVAILABLE")
      ? "Учёт дел качества на сервере ещё не включён: карантин и решения неизвестны." : `Исключения не прочитаны: ${read.error || parsed.error}`}</p>}
    {pending.damaged && <p role="alert" className="ops-err">{pending.damaged}</p>}
    {intent && <div role="status" className="ops-err">Команда «{intent.title}» не подтверждена.{" "}
      <HelpButton help={excHelp.retry} disabled={busy} onClick={() => send(() => intent)}>Повторить</HelpButton></div>}
    {message && <p role="status" className="ops-note">{message}</p>}
    <div role="tablist" aria-label="Разделы исключений" className="ops-roles">{SECTIONS.map(s =>
      <button key={s.id} role="tab" type="button" aria-selected={section === s.id} title={excHelp.section.text} data-help-id={excHelp.section.id + "." + s.id}
        onClick={() => { setSection(s.id); setForm(null); }}>{s.title}{snap ? ` · ${s.id === "quarantine" ? snap.quarantine.length : s.id === "cases" ? snap.cases.length : snap.discrepancies?.length ?? "—"}` : ""}</button>)}</div>
    {snap && section === "quarantine" && <QuarantineSection {...props} />}
    {snap && section === "cases" && <CasesSection {...props} reload={reload + local} />}
    {snap && section === "discrepancies" && <DiscrepancySection rows={snap.discrepancies} />}
  </section>;
}

type SectionProps = { snap: ExceptionsSnapshot; blocked: boolean; run: Run; form: Form; setForm: (f: Form) => void; wh: string };

function FormRow({ form, blocked, setForm }: { form: NonNullable<Form>; blocked: boolean; setForm: (f: Form) => void }) {
  const ready = form.fields.every(f => f.value.trim().length >= (f.min ?? 1));
  return <div className="ops-form" style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
    {form.fields.map((f, i) => <input key={f.name} aria-label={f.label} placeholder={f.label} value={f.value} style={{ minWidth: 0, flex: "1 1 140px" }}
      onChange={e => setForm({ ...form, fields: form.fields.map((x, j) => j === i ? { ...x, value: e.target.value } : x) })} />)}
    <HelpButton help={excHelp.confirm} disabled={blocked || !ready}
      onClick={() => form.send(Object.fromEntries(form.fields.map(f => [f.name, f.value.trim()])))}>{form.title}</HelpButton>
  </div>;
}

function QuarantineSection({ snap, blocked, run, form, setForm }: SectionProps) {
  const cases = new Map(snap.cases.map(c => [c.case_id, c]));
  const putIn: NonNullable<Form> = { key: "in", title: "В карантин", fields: [{ name: "pallet_uid", label: "Паллета", value: "" }, { name: "target_cell", label: "Карантинная ячейка", value: "" },
    { name: "reason", label: "Основание", value: "", min: 3 }], send: v => run(`паллета ${v.pallet_uid} в карантин`, "QUARANTINE", v) };
  return <div>
    <p><HelpButton help={excHelp.quarantineIn} disabled={blocked} onClick={() => setForm(putIn)}>Поставить в карантин</HelpButton></p>
    {form?.key === "in" && <FormRow form={form} blocked={blocked} setForm={setForm} />}
    {snap.quarantine.length === 0 ? <p className="ops-note">В карантинных ячейках склада нет паллет (паллеты недоступных собственников не показываются).</p> :
    <ul className="ops-list">{snap.quarantine.map(p => {
      const c = p.case_id != null ? cases.get(p.case_id) : undefined, hold = releaseBlocked(c);
      const open: NonNullable<Form> = { key: "open:" + p.pallet_uid, title: "Открыть дело", fields: [{ name: "reason", label: "Основание (что с товаром)", value: "", min: 3 }],
        send: v => run(`дело по паллете ${p.pallet_uid}`, "CASE", { action: "OPEN", pallet_uid: p.pallet_uid, reason: v.reason }) };
      const out: NonNullable<Form> = { key: "out:" + p.pallet_uid, title: "Выпустить", fields: [{ name: "target_cell", label: "Ячейка хранения", value: "" }, { name: "reason", label: "Основание", value: "", min: 3 }],
        send: v => run(`выпуск паллеты ${p.pallet_uid}`, "QUARANTINE", { pallet_uid: p.pallet_uid, ...v }) };
      return <li key={p.pallet_uid}><span><b>{p.pallet_uid}</b> <small>ячейка {p.cell} · {p.article} · {p.base_qty} {p.base_uom}</small><br />
        <small>{c ? `дело ${c.case_id}: ${STATE_TITLE[c.state]}` : "дела качества нет"}</small>
        {form && (form.key === open.key || form.key === out.key) && <FormRow form={form} blocked={blocked} setForm={setForm} />}</span>
        <span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <HelpButton help={excHelp.open} disabled={blocked} unavailable={hold ? "у паллеты уже есть активное дело" : undefined} onClick={() => setForm(open)}>Открыть дело</HelpButton>
          <HelpButton help={excHelp.quarantineOut} disabled={blocked} unavailable={hold ? "паллету держит дело качества до решения «годен»" : undefined} onClick={() => setForm(out)}>Выпустить</HelpButton>
        </span></li>;
    })}</ul>}
  </div>;
}

function CasesSection({ snap, blocked, run, form, setForm, wh, reload }: SectionProps & { reload: number }) {
  const [open, setOpen] = useState<number | null>(null);
  const detail = useApiRead<CaseDetail>(open != null ? `/api/tradecase/warehouses/${encodeURIComponent(wh)}/exceptions/cases/${open}` : null, reload);
  if (snap.cases.length === 0) return <p className="ops-note">Дел качества нет (дела недоступных собственников не показываются).</p>;
  const act = (c: QualityCase, a: CaseAction): NonNullable<Form> => a === "POST"
    // Проведение: складская проводка списывает остаток и коды; подтверждение — повторным нажатием, данных не требуется.
    ? { key: `${c.case_id}:${a}`, title: "Подтвердить проведение", fields: [],
        send: () => run(`проведение списания · дело ${c.case_id}`, "WRITE_OFF", { case_id: c.case_id, expected_version: c.version }) }
    : { key: `${c.case_id}:${a}`, title: ACTION_TITLE[a],
    fields: [{ name: "note", label: a === "APPROVE" ? "Основание утверждения (документ)" : "Заключение контролёра", value: "", min: 3 }],
    send: v => run(`${ACTION_TITLE[a]} · дело ${c.case_id}`, "CASE", a === "APPROVE" ? { action: "APPROVE", case_id: c.case_id, expected_version: c.version, note: v.note }
      : { action: "DECIDE", case_id: c.case_id, expected_version: c.version, decision: a, note: v.note }) };
  return <ul className="ops-list">{snap.cases.map(c => <li key={c.case_id}><span>
    <b>Дело {c.case_id}</b> <small>{STATE_TITLE[c.state]} · паллета {c.pallet_uid} · ячейка {c.cell}</small><br />
    <small>Основание: {c.reason} · открыл {c.opened_by} {fmtTime(null, c.opened_at)}</small><br />
    <small>Состав: {compositionText(c.composition)}</small>
    {c.decision_note && <><br /><small>Решение {c.decided_by}: {c.decision_note}</small></>}
    {c.state === "WAITING_POSTING" && <><br /><small className="ops-err">Списание утверждено ({c.approved_by}: {c.approval_note}), но ещё не проведено: товар остаётся в карантине до «Провести списание».</small></>}
    {c.state === "POSTED" && <><br /><small>Списано складской проводкой {c.posted_by ?? ""} {c.posted_at ? fmtTime(null, c.posted_at) : ""} · {EXTERNAL_TITLE[c.external_status ?? ""] ?? "ответ SAP/СКМ неизвестен"}</small></>}
    {form && form.key.startsWith(c.case_id + ":") && <FormRow form={form} blocked={blocked} setForm={setForm} />}
    {open === c.case_id && (detail.error ? <p className="ops-err">{detail.error}</p> : detail.data && <ul>{detail.data.units.slice(0, 50).map(u =>
      <li key={u.unit_key}><small>{u.unit_key} · {u.sku_id} · {u.owner_id} · {u.base_qty} {u.base_uom}{u.unchanged ? "" : " · изменился после открытия"}</small></li>)}</ul>)}
  </span><span style={{ display: "flex", flexDirection: "column", gap: 4 }}>
    {ACTIONS[c.state].map(a => <HelpButton key={a} help={a === "POST" ? excHelp.post : excHelp.action} disabled={blocked} onClick={() => setForm(act(c, a))}>{ACTION_TITLE[a]}</HelpButton>)}
    <HelpButton help={excHelp.detail} onClick={() => setOpen(v => v === c.case_id ? null : c.case_id)}>{open === c.case_id ? "Скрыть коды" : "Коды"}</HelpButton>
  </span></li>)}</ul>;
}

function DiscrepancySection({ rows }: { rows: Discrepancy[] | null }) {
  if (rows === null) return <p className="ops-note">Раздел закрыт: просмотр пересчёта на этом складе вам недоступен (это не значит, что расхождений нет).</p>;
  return <div>
    <p><HelpButton help={excHelp.tasks} onClick={() => window.open(rawLink("warehouse-tasks.html"), "_blank", "noopener")}>Складские задания</HelpButton></p>
    {rows.length === 0 ? <p className="ops-note">Открытых пересчётов и расхождений нет.</p> :
    <ul className="ops-list">{rows.map(r => <li key={r.inventory_task_id}><span><b>Пересчёт {r.inventory_task_id}</b> <small>{r.status} · ячейка {r.cell} · {r.article}</small><br />
      <small>план {r.planned_qty ?? "нет данных"} · факт {r.fact_qty ?? "не посчитано"}{r.assigned_to ? ` · ${r.assigned_to}` : ""}</small></span><span /></li>)}</ul>}
  </div>;
}
