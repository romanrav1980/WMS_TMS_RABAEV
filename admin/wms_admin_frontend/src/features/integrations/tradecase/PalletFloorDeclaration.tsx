import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech } from "./ui";

type Body = { operation_id: string; identifier: string; pallet_type_id: number; expected_version: number; scan_pallet: string; scan_cell: string; evidence_reference: string };
type Snapshot = { uid: string; sscc: string | null; warehouse: number; cell: string | null; has_physical_stock: boolean; version: number;
  current_type_name?: string; types: { id: number; code: string; name: string }[] };
type Result = { operation_id: string; uid: string; warehouse: number; pallet_type_id: number; version: number; stock_changed: boolean; status: string };
const saved = journal<Body>("palletfloor", "TC.PALLET.FLOOR", b => typeof b.identifier === "string" && b.identifier.length > 0 && b.identifier.length <= 200
  && Number.isSafeInteger(b.pallet_type_id) && b.pallet_type_id > 0 && Number.isSafeInteger(b.expected_version) && b.expected_version >= 0
  && typeof b.scan_pallet === "string" && b.scan_pallet.length > 0 && b.scan_pallet.length <= 200 && typeof b.scan_cell === "string" && b.scan_cell.length > 0
  && b.scan_cell.length <= 60 && typeof b.evidence_reference === "string" && b.evidence_reference.length > 0 && b.evidence_reference.length <= 100, "тип паллеты");
const help = (id: string, text: string) => ({ id: "tradecase.palletfloor." + id, text, anchor: "pallet-floor" });

export function PalletFloorDeclaration({ wh, user }: { wh: string; user: string }) {
  const [identifier, setIdentifier] = useState(""), [requested, setRequested] = useState(""), [reload, setReload] = useState(0);
  const [type, setType] = useState(""), [scan, setScan] = useState(""), [cell, setCell] = useState(""), [reference, setReference] = useState("");
  const read = useRead<Snapshot>(requested ? "/api/inventory/pallet-floor-types?identifier=" + encodeURIComponent(requested) : null, reload);
  const snapshot = !read.loading && !read.error && requested === identifier.trim() && read.data?.warehouse === Number(wh) ? read.data : null;
  const command = useCommand<Body, Result>(saved, "/api/inventory/pallet-floor-types", user, wh, {
    PALLET_FLOOR_VERSION_CHANGED: "тип паллеты уже изменён; перечитайте данные", PALLET_FLOOR_CURRENT_WARE_FORBIDDEN: "нет доступа к складу",
  }, (r, b) => r.operation_id === b.operation_id && r.uid === b.identifier && r.warehouse === Number(wh) && r.pallet_type_id === b.pallet_type_id
    && r.version === b.expected_version + 1 && r.status === "APPLIED" && r.stock_changed === false ? "Тип паллеты сохранён." : null);
  const locked = command.busy || command.stored.kind !== "none";
  const readCurrent = () => { setType(""); setScan(""); setCell(""); setReference(""); setRequested(identifier.trim()); setReload(n => n + 1); };
  return <section className="tc-bind" aria-label="Тип физической паллеты">
    <h4>Тип физической паллеты <HelpLink anchor="pallet-floor" /></h4>
    <label>Идентификатор паллеты<input value={identifier} disabled={locked} maxLength={200} onChange={e => { setIdentifier(e.target.value); setRequested(""); }}
      title="Отсканируйте паллету с товаром, для которой подтверждаете тип поддона" data-help-id="tradecase.palletfloor.identifier" /></label>
    <Act help={help("read", "Прочитать текущую паллету, её ячейку и доступные типы поддона.")} disabled={locked || !identifier.trim()} onClick={readCurrent}>Показать тип паллеты</Act>
    {read.loading && <p role="status">Читаем паллету…</p>}
    {read.error && <p role="alert" className="tc-err">Паллета недоступна. Проверьте идентификатор и доступ к складу и собственнику.</p>}
    {read.data && !read.loading && read.data.warehouse !== Number(wh) && <p role="alert" className="tc-err">Выберите склад этой паллеты.</p>}
    {snapshot && <><dl className="tc-fields"><dt>Ячейка</dt><dd>{snapshot.cell ?? "—"}</dd><dt>Сохранённый тип</dt><dd>{snapshot.current_type_name ?? "Не указан"}</dd></dl>
      {!snapshot.has_physical_stock ? <p role="status">На паллете нет складского остатка. Подтверждение типа недоступно.</p> : <>
        <label>Фактический тип поддона<select value={type} disabled={locked} onChange={e => setType(e.target.value)} title="Выберите тип поддона, на котором находится товар" data-help-id="tradecase.palletfloor.type">
          <option value="">Выберите тип</option>{snapshot.types.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}</select></label>
        <label>Скан паллеты<input value={scan} disabled={locked} maxLength={200} onChange={e => setScan(e.target.value)} title="Отсканируйте показанную паллету перед подтверждением" data-help-id="tradecase.palletfloor.scan" /></label>
        <label>Скан ячейки<input value={cell} disabled={locked} maxLength={60} onChange={e => setCell(e.target.value)} title="Отсканируйте текущую ячейку паллеты" data-help-id="tradecase.palletfloor.cell" /></label>
        <label>Основание<input value={reference} disabled={locked} maxLength={100} onChange={e => setReference(e.target.value)} title="Укажите документ или результат осмотра, по которому подтверждаете тип поддона" data-help-id="tradecase.palletfloor.reference" /></label>
        <Act help={help("confirm", "Сохранить фактический тип поддона для расчёта мест в машине. Количество товара не изменится.")}
          disabled={locked || !snapshot.types.some(t => t.id === Number(type)) || ![snapshot.uid, snapshot.sscc].includes(scan.trim()) || cell.trim() !== snapshot.cell || !reference.trim()}
          onClick={() => command.start({ identifier: snapshot.uid, pallet_type_id: Number(type), expected_version: snapshot.version, scan_pallet: scan.trim(), scan_cell: cell.trim(), evidence_reference: reference.trim() }, () => setReload(n => n + 1))}>Подтвердить тип</Act>
      </>}
    </>}
    {command.stored.kind === "ok" && <Act help={help("retry", "Повторить сохранённое подтверждение с тем же номером операции и теми же данными.")} disabled={command.busy}
      onClick={() => command.stored.kind === "ok" && command.send(command.stored.intent, () => setReload(n => n + 1))}>Повторить подтверждение типа</Act>}
    {command.stored.kind === "damaged" && <p role="alert" className="tc-err">Сохранённое подтверждение повреждено. Передайте сведения специалисту поддержки.</p>}
    {command.msg && <p role="status" className={command.msg.tone === "bad" ? "tc-err" : "tc-note"}>{command.msg.text}</p>}
    {!!command.msg?.tech && <Tech value={command.msg.tech} label="Ответ сервера" />}
  </section>;
}
