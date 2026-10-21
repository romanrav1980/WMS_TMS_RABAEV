import { useState } from "react";
import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech } from "./ui";

type Body = { operation_id: string; task_id: number; shipment_identifier: string; scanned_pallet: string; expected_stock_version: number };
type Snapshot = { warehouse_id: number; task_id: number; pallet_identifier: string; article: string; cell: string; quantity: string;
  stock_version: number; base_uom: string; bound_shipments: number; bound_shipment_identifier: string | null };
type Result = { operation_id: string; warehouse_task_id: number; pallet_identifier: string; shipment_identifier: string; status: string; quantity: string; base_uom: string };
const unit = (value: string) => value === "EA" || value === "PCS" ? "шт." : value === "KG" ? "кг" : "ед.";
const saved = journal<Body>("fullpal", "TC.FULLPAL.UI", b => Number.isSafeInteger(b.task_id) && b.task_id > 0
  && Number.isSafeInteger(b.expected_stock_version) && b.expected_stock_version >= 0 && typeof b.scanned_pallet === "string"
  && b.scanned_pallet.length > 0 && b.scanned_pallet.length <= 150 && typeof b.shipment_identifier === "string"
  && b.shipment_identifier.length > 0 && b.shipment_identifier.length <= 150, "связь целой паллеты");
const help = (id: string, text: string) => ({ id: "tradecase.fullpal." + id, text, anchor: "full-pallet" });

export function FullPalletBinding({ wh, user }: { wh: string; user: string }) {
  const [task, setTask] = useState(""), [requested, setRequested] = useState(""), [reload, setReload] = useState(0);
  const [pallet, setPallet] = useState(""), [shipment, setShipment] = useState("");
  const read = useRead<Snapshot>(requested ? `/api/warehouse-tasks/${requested}/full-pallet-shipment` : null, reload);
  const snapshot = !read.loading && !read.error && requested === task.trim() && read.data?.warehouse_id === Number(wh) ? read.data : null;
  const command = useCommand<Body, Result>(saved, "", user, wh, {
    TASK_CURRENT_EXECUTE_FORBIDDEN: "нет права выполнить привязку", FULLPAL_BIND_FORBIDDEN: "нет права выполнить привязку",
    FULLPAL_ST_COMPOSITION_MISMATCH: "состав подготовленного места не совпадает с целой паллетой",
  }, (r, b) => r.operation_id === b.operation_id && r.warehouse_task_id === b.task_id && r.pallet_identifier === b.scanned_pallet
    && r.shipment_identifier === b.shipment_identifier && r.status === "PICKED" ? `Паллета связана с местом отгрузки: ${r.quantity} ${unit(r.base_uom)}` : null,
    { path: b => `/api/warehouse-tasks/${b.task_id}/full-pallet-shipment`, payload: b => ({ operation_id: b.operation_id,
      shipment_identifier: b.shipment_identifier, scanned_pallet: b.scanned_pallet, expected_stock_version: b.expected_stock_version }) });
  const pending = command.stored.kind !== "none", locked = pending || command.busy;
  return <section className="tc-bind" aria-label="Целая паллета в отгрузке">
    <h4>Целая паллета в отгрузке <HelpLink anchor="full-pallet" /></h4>
    <p>После перемещения в экспедицию свяжите физическую паллету с подготовленным местом отгрузки.</p>
    <label>Завершённое задание<input inputMode="numeric" value={task} disabled={locked} onChange={e => { setTask(e.target.value.replace(/\D/g, "")); setRequested(""); }}
      title="Укажите номер завершённого задания отбора целой паллеты" data-help-id="tradecase.fullpal.task" /></label>
    <Act help={help("read", "Прочитать фактически перемещённую паллету, её количество, адрес и существующую привязку.")}
      disabled={locked || !/^[1-9]\d*$/.test(task)} onClick={() => { setRequested(task.trim()); setReload(n => n + 1); }}>Показать целую паллету</Act>
    {read.loading && <p role="status">Читаем результат перемещения…</p>}
    {read.error && <p className="tc-err" role="alert">Паллета недоступна. Проверьте номер завершённого задания, склад и доступ к собственнику.</p>}
    {read.data && read.data.warehouse_id !== Number(wh) && !read.loading && <p className="tc-err" role="alert">Выберите склад этого задания.</p>}
    {snapshot && <><dl className="tc-fields"><dt>Идентификатор паллеты</dt><dd>{snapshot.pallet_identifier}</dd><dt>Товар</dt><dd>{snapshot.article}</dd>
      <dt>Количество</dt><dd>{snapshot.quantity} {unit(snapshot.base_uom)}</dd><dt>Ячейка</dt><dd>{snapshot.cell}</dd></dl>
      {snapshot.bound_shipments > 0 ? <p role="status">{snapshot.bound_shipments === 1 ? `Связана с местом отгрузки ${snapshot.bound_shipment_identifier}.` : "Найдены несколько привязок. Передайте сведения специалисту поддержки."}</p> : <>
        <label>Скан паллеты<input value={pallet} maxLength={150} disabled={locked} onChange={e => setPallet(e.target.value)} title="Отсканируйте показанную физическую паллету" data-help-id="tradecase.fullpal.pallet" /></label>
        <label>Скан места отгрузки<input value={shipment} maxLength={150} disabled={locked} onChange={e => setShipment(e.target.value)} title="Отсканируйте подготовленное место того же заказа, содержащее весь объём паллеты" data-help-id="tradecase.fullpal.shipment" /></label>
        <Act help={help("bind", "Связать паллету с подготовленным местом. Погрузка и выезд оформляются в рейсе.")} disabled={locked || pallet.trim() !== snapshot.pallet_identifier || !shipment.trim()}
          onClick={() => command.start({ task_id: snapshot.task_id, shipment_identifier: shipment.trim(), scanned_pallet: pallet.trim(), expected_stock_version: snapshot.stock_version }, () => setReload(n => n + 1))}>Связать с отгрузкой</Act>
      </>}</>}
    {command.stored.kind === "ok" && <Act help={help("retry", "Повторить сохранённый запрос с тем же номером операции и тем же составом.")} disabled={command.busy}
      onClick={() => command.stored.kind === "ok" && command.send(command.stored.intent, () => setReload(n => n + 1))}>Повторить сохранённую связь</Act>}
    {command.stored.kind === "damaged" && <p className="tc-err" role="alert">Сохранённый запрос повреждён. Передайте сведения специалисту поддержки; новая отправка заблокирована.</p>}
    {command.msg && <p role="status" className={command.msg.tone === "bad" ? "tc-err" : "tc-note"}>{command.msg.text}</p>}
    {!!command.msg?.tech && <Tech value={command.msg.tech} label="Ответ сервера" />}
  </section>;
}
