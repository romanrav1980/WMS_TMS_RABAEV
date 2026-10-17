import { HelpHint } from "../help/HelpHint";
import type { StoreDisposition } from "../contracts";

const counters = [["missing", "Недостача"], ["refused", "Отказ"], ["damaged", "Повреждено"], ["extra", "Излишек"]] as const;
const allCounters = ["accepted", "missing", "refused", "damaged", "extra"] as const;

export interface SnapshotLeaf { uid: string; article?: string; quantity?: string; base_uom?: string }

// Exact decimal preview only. Oracle remains authoritative for all receipt effects.
function decimalUnits(value: string): bigint | null {
 if (!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(value)) return null;
 const [whole, fraction = ""] = value.split(".");
 return BigInt(whole + fraction.padEnd(9, "0"));
}

function rowError(row: StoreDisposition, leaf?: SnapshotLeaf): string {
 if (!row.accepted) return "Введите фактически принятое количество.";
 if (allCounters.some((field) => decimalUnits(row[field]) === null)) return "Укажите неотрицательные числа: до 9 знаков после запятой.";
 if (leaf) {
  const shipped = decimalUnits(leaf.quantity || "");
  if (shipped === null) return "Плановое количество не определено. Обновите поставку.";
  const accounted = [row.accepted, row.missing, row.refused, row.damaged].reduce((sum, value) => sum + (decimalUnits(value) ?? 0n), 0n);
  if (accounted !== shipped) return `Принято + недостача + отказ + повреждено должно быть ${leaf.quantity} ${leaf.base_uom || ""}. Излишек указывается отдельно.`;
 }
 return "";
}

function hasDifferences(row: StoreDisposition): boolean {
 return counters.some(([field]) => row[field] !== "" && decimalUnits(row[field]) !== 0n);
}

function CountRow({ row, leaf, index, onChange }: {
 row: StoreDisposition; leaf?: SnapshotLeaf; index: number;
 onChange: (index: number, field: keyof StoreDisposition, value: string) => void;
}) {
 const error = rowError(row, leaf), id = `store-count-${index}`;
 return <fieldset className="store-app-discrepancy-row">
  <legend>{leaf?.article ?? row.lot_uid}</legend>
  <p className="store-app-count-shipped">Отправлено: <strong>{leaf?.quantity ?? "—"} {leaf?.base_uom ?? ""}</strong></p>
  <label className="store-app-count-accepted" htmlFor={id}>
   Фактически принято{leaf?.base_uom ? `, ${leaf.base_uom}` : ""}
   <input id={id} inputMode="decimal" autoComplete="off" value={row.accepted}
    title="Введите количество, которое вы действительно пересчитали и принимаете" data-help-id="discrepancy.accepted"
    aria-invalid={!!error} aria-describedby={error ? `${id}-error` : undefined}
    onChange={(event) => onChange(index, "accepted", event.target.value)} />
  </label>
  <details className="store-app-count-differences" open={hasDifferences(row) || undefined}>
   <summary title="Указать недостачу, отказ, повреждение или излишек без потери введённых количеств" data-help-id="discrepancy.expand">Расхождения{hasDifferences(row) ? " · указаны" : ""}</summary>
   <div className="store-app-count-counters">{counters.map(([field, label]) => <label key={field} htmlFor={`${id}-${field}`}>
    {label}<input id={`${id}-${field}`} inputMode="decimal" autoComplete="off" value={row[field]}
     title={`Введите «${label}» в базовых единицах товара`} data-help-id={`discrepancy.${field}`}
     aria-invalid={decimalUnits(row[field]) === null} onChange={(event) => onChange(index, field, event.target.value)} />
   </label>)}</div>
  </details>
  {error && <p id={`${id}-error`} className="store-app-count-error" role="status">{error}</p>}
 </fieldset>;
}

export function DiscrepancyFields({ leaves, rows, onChange, disabled, forced, enabled, onToggle, note, onNote, helpArticle }: {
 leaves: SnapshotLeaf[];
 rows: StoreDisposition[];
 onChange: (rows: StoreDisposition[]) => void;
 disabled: boolean;
 forced: boolean;
 enabled: boolean;
 onToggle: (value: boolean) => void;
 note: string;
 onNote: (value: string) => void;
 helpArticle: string;
}) {
 function change(index: number, field: keyof StoreDisposition, value: string) {
  const normalized = value.replace(/,/g, ".").replace(/\s/g, "");
  onChange(rows.map((row, i) => (i === index ? { ...row, [field]: normalized } : row)));
 }
 return <fieldset className="store-app-discrepancy" disabled={disabled}>
  <legend>Фактические количества <HelpHint helpId="discrepancy.counts" tip="Принято + недостача + отказ + повреждено должно равняться отправленному" article={helpArticle} /></legend>
  {!forced && <label>
   <input type="checkbox" checked={enabled} title="Показать поля фактического количества для каждой позиции" data-help-id="discrepancy.enable" onChange={(event) => onToggle(event.target.checked)} />
   Указать фактические количества и расхождения
  </label>}
  {(enabled || forced) && <>
   {rows.map((row, index) => <CountRow key={row.lot_uid} row={row} leaf={leaves.find((leaf) => leaf.uid === row.lot_uid)} index={index} onChange={change} />)}
   <label>
    Причина расхождения{rows.some(hasDifferences) ? " · обязательна" : ""}
    <textarea maxLength={2000} value={note} title="Опишите причину недостачи, отказа, повреждения или излишка" data-help-id="discrepancy.reason" onChange={(event) => onNote(event.target.value)} />
   </label>
   {rows.some(hasDifferences) && !note.trim() && <p className="store-app-count-error" role="status">Укажите причину расхождения перед подтверждением.</p>}
  </>}
 </fieldset>;
}

export function initialDiscrepancyRows(leaves: SnapshotLeaf[]): StoreDisposition[] {
 return leaves.map((leaf) => ({ lot_uid: leaf.uid, accepted: leaf.quantity || "0", missing: "0", refused: "0", damaged: "0", extra: "0" }));
}

// Для PAPER_COUNT плановое количество нельзя молча выдавать за фактический пересчёт — пересчитанное поле начинается пустым.
export function initialPaperCountRows(leaves: SnapshotLeaf[]): StoreDisposition[] {
 return leaves.map((leaf) => ({ lot_uid: leaf.uid, accepted: "", missing: "0", refused: "0", damaged: "0", extra: "0" }));
}

export function paperCountComplete(rows: StoreDisposition[], leaves?: SnapshotLeaf[]): boolean {
 if (!rows.length || new Set(rows.map((row) => row.lot_uid)).size !== rows.length) return false;
 if (leaves && (leaves.length !== rows.length || leaves.some((leaf) => !rows.some((row) => row.lot_uid === leaf.uid)))) return false;
 return rows.every((row) => !rowError(row, leaves?.find((leaf) => leaf.uid === row.lot_uid)));
}
