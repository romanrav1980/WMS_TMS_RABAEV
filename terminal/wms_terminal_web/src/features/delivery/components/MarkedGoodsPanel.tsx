import { useEffect, useState } from "react";
import { storeAppApiBase } from "../api";
import { HelpHint } from "../help/HelpHint";
import { ScanField } from "../../platform";
import { MarkedGoodsSummary } from "./MarkedGoodsSummary";
import type { StoreMarkControl, StoreUnitScan, StoreAggregateScan } from "../contracts";

type Draft = { scans: StoreUnitScan[]; aggregation_scans: StoreAggregateScan[] };
const empty: Draft = { scans: [], aggregation_scans: [] };

function isValidScan(x: unknown, profiles: StoreMarkControl["profiles"]): x is StoreUnitScan {
 const scan = x as StoreUnitScan;
 return !!scan && typeof scan.code === "string" && new TextEncoder().encode(scan.code).length <= 4000 && scan.code.length > 0
  && (profiles || []).some((p) => p.system_code === scan.system_code && p.profile_code === scan.profile_code)
  && (!scan.disposition || ["ACCEPTED", "REFUSED", "DAMAGED"].includes(scan.disposition));
}

export function MarkedGoodsPanel({ control, partialAllowed, username, scopeKey, disabled, onScans, onAggregates, onValidity }: {
 control: StoreMarkControl;
 partialAllowed: boolean;
 username: string;
 scopeKey: string;
 disabled: boolean;
 onScans: (v: StoreUnitScan[]) => void;
 onAggregates: (v: StoreAggregateScan[]) => void;
 onValidity: (v: boolean) => void;
}) {
 const profiles = control.profiles || [];
 const [draft, setDraft] = useState<Draft>(empty);
 const [selected, setSelected] = useState("0");
 const [kind, setKind] = useState<"UNIT" | "BOX" | "PALLET">("UNIT");
 const [code, setCode] = useState("");
 const [message, setMessage] = useState("");
 const [invalid, setInvalid] = useState(false);
 const [disposition, setDisposition] = useState<"ACCEPTED" | "REFUSED" | "DAMAGED">("ACCEPTED");
 const profile = profiles[Number(selected)];
 const mode = profile?.scan_mode;
 const effective = mode === "UNIT_OR_AGGREGATION" ? kind : (mode as "UNIT" | "BOX" | "PALLET" | undefined);
 const key = "store-app-mark:" + storeAppApiBase() + ":" + username + ":" + scopeKey;

 useEffect(() => {
  try {
   const raw = localStorage.getItem(key);
   const parsed: unknown = raw === null ? empty : JSON.parse(raw);
   const value = parsed as Draft;
   if (!value || !Array.isArray(value.scans) || !Array.isArray(value.aggregation_scans)
    || value.scans.length > 20000 || value.aggregation_scans.length > 1000
    || !value.scans.every((x) => isValidScan(x, profiles))
    || !value.aggregation_scans.every((x) => isValidScan(x, profiles) && ["BOX", "PALLET"].includes(x.level))) {
    throw new Error("invalid");
   }
   setDraft(value); onScans(value.scans); onAggregates(value.aggregation_scans); setInvalid(false); onValidity(true); setMessage("");
  } catch {
   setDraft(empty); onScans([]); onAggregates([]); setInvalid(true); onValidity(false);
   setMessage("Сохранённый черновик маркировки повреждён. Новая отправка заблокирована; очистите сканы и начните заново.");
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
 }, [key]);

 function save(value: Draft) {
  try { localStorage.setItem(key, JSON.stringify(value)); setDraft(value); onScans(value.scans); onAggregates(value.aggregation_scans); setMessage(""); return true; }
  catch { setMessage("Не удалось сохранить сканы на устройстве."); return false; }
 }

 function add() {
  if (disabled || invalid || !profile || !effective || !code) return;
  if (new TextEncoder().encode(code).length > 4000) { setMessage("Код превышает 4000 байт."); return; }
  if ([...draft.scans, ...draft.aggregation_scans].some((x) => x.system_code === profile.system_code && x.profile_code === profile.profile_code && x.code === code)) {
   setMessage("Этот код уже добавлен."); return;
  }
  const value: StoreUnitScan = { system_code: profile.system_code, profile_code: profile.profile_code, code, disposition };
  if (effective === "UNIT") { if (draft.scans.length >= 20000) return; if (save({ ...draft, scans: [...draft.scans, value] })) setCode(""); }
  else { if (draft.aggregation_scans.length >= 1000) return; if (save({ ...draft, aggregation_scans: [...draft.aggregation_scans, { ...value, level: effective }] })) setCode(""); }
 }

 function clearScans() {
  if (disabled) return;
  try {
   const raw = localStorage.getItem(key);
   if (raw) localStorage.setItem(key + ":history:" + crypto.randomUUID(), raw);
   if (save(empty)) { setInvalid(false); onValidity(true); }
  } catch { setMessage("Не удалось сохранить архив сканов. Очистка не выполнена."); }
 }

 if (!control.supported) return <p className="store-app-message">Состав недоступен для сверки маркировки: {control.reason || "причина не передана сервером"}.</p>;

 return <section><fieldset className="store-app-marked" disabled={disabled || invalid}>
  <legend>Сверка маркировки <HelpHint helpId="marked.summary" tip="Обязательно для маркированного товара независимо от выбранной стратегии приёмки" article="store-receiving-barcode" /></legend>
  <MarkedGoodsSummary control={control} />
  <p>Единиц: {draft.scans.length}. Агрегаций: {draft.aggregation_scans.length}. Полноту состава проверяет сервер.</p>
  <label>Профиль
   <select title="Выберите обязательный профиль маркировки для считанного кода" data-help-id="marked.profile" value={selected} onChange={(event) => { setSelected(event.target.value); setCode(""); }}>
    {profiles.map((p, i) => <option key={i} value={i}>{p.system_code} / {p.profile_code} · {p.scan_mode}</option>)}
   </select>
  </label>
  {mode === "UNIT_OR_AGGREGATION" && <label>Способ сканирования
   <select title="Укажите код отдельной единицы, коробки или паллеты" data-help-id="marked.kind" value={kind} onChange={(event) => { setKind(event.target.value as typeof kind); setCode(""); }}>
    <option value="UNIT">QR штуки</option><option value="BOX">Код коробки</option><option value="PALLET">Код паллеты</option>
   </select>
  </label>}
  {partialAllowed && <label>Решение для сканируемого состава
   <select title="Укажите, принимаете ли этот состав, отказываете или отмечаете повреждение" data-help-id="marked.disposition" value={disposition} onChange={(event) => setDisposition(event.target.value as typeof disposition)}>
    <option value="ACCEPTED">Принято</option><option value="REFUSED">Отказ</option><option value="DAMAGED">Повреждено</option>
   </select>
  </label>}
  <ScanField label={effective === "UNIT" ? "QR / DataMatrix единицы" : effective === "BOX" ? "Код коробки" : "Код паллеты"}
   value={code} onChange={setCode} onSubmit={() => add()} disabled={disabled || invalid} />
  <button type="button" data-help-id="marked.add" title="Добавить отсканированный код единицы или агрегата в проверку"
   disabled={disabled || invalid || !profile || !effective || !code} onClick={add}>Добавить скан</button>
  <p role="status" className="store-app-message">{message}</p>
 </fieldset><button type="button" title="Сохранить прежние локальные сканы в архив и начать сверку заново" data-help-id="marked.clear" disabled={disabled} onClick={clearScans}>Очистить сканы</button></section>;
}
