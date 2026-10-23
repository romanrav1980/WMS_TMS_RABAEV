export type PaperTask = Record<string, unknown> & { task_id: number; task_signature: string; qty_exact: string };
export type PaperSnapshot = { task: PaperTask; reference: string; barcode_svg: string; prepared_at: string };
const STATE: Record<string, string> = { PLANNED: "Запланировано", ASSIGNED: "Назначено", IN_PROGRESS: "В работе", DONE: "Выполнено - копия", CANCELLED: "Отменено - копия" };
const ACTION: Record<string, string> = { PUTAWAY: "Размещение", REPLENISHMENT: "Пополнение", PICK: "Отбор", PICKING: "Отбор", MOVE: "Перемещение",
  PICKING_MOVE: "Перемещение для сборки", RAW_TO_PRODUCTION: "Передача сырья в производство", FG_TO_STORAGE: "Размещение готовой продукции" };
const UNIT: Record<string, string> = { EA: "шт.", BOX: "кор.", HU: "место", CASE: "короб", KG: "кг", PALLET: "паллета" };
export const paperText = (value: unknown): string => typeof value === "string" || typeof value === "number" ? String(value) : "-";

export function parsePaper(value: unknown, taskId: number): PaperSnapshot {
  const p = value as Partial<PaperSnapshot> | null;
  if (!p || !p.task || p.task.task_id !== taskId || !/^[A-F0-9]{64}$/.test(p.task.task_signature ?? "") ||
      p.reference !== `WTASK:${taskId}:${p.task.task_signature}` || typeof p.barcode_svg !== "string" ||
      !p.barcode_svg.startsWith("<svg ") || typeof p.prepared_at !== "string" || !Number.isFinite(Date.parse(p.prepared_at)) ||
      typeof p.task.qty_exact !== "string" || !/^(?:\d+(?:\.\d+)?|\.\d+)$/.test(p.task.qty_exact)) {
    throw new Error("Сервер вернул неполный бланк. Повторите чтение задания.");
  }
  return p as PaperSnapshot;
}

export function paperSignature(reference: string, taskId: number): string {
  const match = /^WTASK:([1-9]\d*):([A-F0-9]{64})$/i.exec(reference.trim());
  if (!match) throw new Error("Считайте штрихкод с бланка или вставьте его полный текст.");
  if (!Number.isSafeInteger(Number(match[1])) || Number(match[1]) !== taskId) {
    throw new Error(`Этот бланк относится к заданию №${match[1]}. Откройте его карточку.`);
  }
  return match[2].toUpperCase();
}

export function paperFields(t: PaperTask): [string, string][] {
  const cell = (field: string, slot: string, code: string) => paperText(t[field]) + (t[code] != null ? ` · слот ${paperText(t[code])}` : t[slot] != null ? ` · слот №${paperText(t[slot])}` : "");
  return [
    ["Действие", ACTION[paperText(t.task_type)] ?? "Действие не указано"],
    ["Состояние", STATE[paperText(t.status)] ?? "Состояние не распознано"],
    ["Исполнитель", paperText(t.assigned_to_name ?? t.assigned_to ?? "Не назначен")],
    ["Товар / грузовое место", paperText(t.product_name ?? t.raw_articul ?? t.target_articul ?? "Грузовое место")],
    ["Количество", `${t.qty_exact.startsWith(".") ? "0" + t.qty_exact : t.qty_exact} ${UNIT[paperText(t.unit_code)] ?? paperText(t.unit_code)}`],
    ["Со склада", paperText(t.from_warehouse_name ?? t.from_ware_id)],
    ["Откуда", cell("from_cell", "from_cell_slot_id", "from_slot_code")],
    ["На склад", paperText(t.to_warehouse_name ?? t.to_ware_id)],
    ["Куда", cell("to_cell", "to_cell_slot_id", "to_slot_code")],
    ["Идентификатор паллеты", paperText(t.uid_pallet ?? t.sscc)],
  ];
}

export function printPaper(popup: Window, paper: PaperSnapshot): void {
  const doc = popup.document;
  doc.documentElement.lang = "ru";
  doc.title = `Складское задание №${paper.task.task_id}`;
  const style = doc.createElement("style");
  style.textContent = "@page{size:A4 landscape;margin:12mm}body{font:14px Arial,sans-serif;color:#111;margin:16px}h1{font-size:24px}dl{display:grid;grid-template-columns:180px 1fr;gap:7px;margin:20px 0}dt{font-weight:bold}dd{margin:0;overflow-wrap:anywhere}img{display:block;width:100%;max-width:260mm;height:25mm;object-fit:fill}p{margin:16px 0}small{display:block;color:#444}@media print{body{margin:0}}";
  doc.head.append(style);
  doc.body.replaceChildren();
  const title = doc.createElement("h1"); title.textContent = doc.title; doc.body.append(title);
  const fields = doc.createElement("dl");
  for (const [label, value] of paperFields(paper.task)) {
    const dt = doc.createElement("dt"), dd = doc.createElement("dd");
    dt.textContent = label; dd.textContent = value; fields.append(dt, dd);
  }
  doc.body.append(fields);
  const image = doc.createElement("img"); image.alt = `Штрихкод задания №${paper.task.task_id}`;
  image.onload = () => { if (!popup.closed) { popup.focus(); popup.print(); } };
  image.onerror = () => { const p = doc.createElement("p"); p.textContent = "Штрихкод не загрузился. Закройте бланк и повторите подготовку."; doc.body.append(p); };
  image.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(paper.barcode_svg); doc.body.append(image);
  const notes = doc.createElement("p"); notes.textContent = "Фактическое количество: __________    Начало: __________    Окончание: __________"; doc.body.append(notes);
  const remarks = doc.createElement("p"); remarks.textContent = "Замечания: __________________________________________________________________________________"; doc.body.append(remarks);
  const footer = doc.createElement("small"); footer.textContent = "Сформирован " + new Intl.DateTimeFormat("ru-RU", { dateStyle: "short", timeStyle: "short", timeZone: "UTC" }).format(new Date(paper.prepared_at)) + " UTC. Печать не подтверждает выполнение задания."; doc.body.append(footer);
}
