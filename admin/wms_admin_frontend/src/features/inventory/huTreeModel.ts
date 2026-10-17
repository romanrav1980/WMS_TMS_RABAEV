/** Existing warehouse-hus/composition read model; absent facts remain unknown. */
export type HuNode = {
 uid: string; kind: string; type?: string; sscc?: string | null; version?: number;
 status?: string; cell?: string; depth?: number; case_task_id?: number; wave_id?: number;
 article?: string; quantity?: string; base_uom?: string; open_task_count?: number;
 tare_weight_kg?: string | null; weight_kg?: string | null; gross_weight_kg?: string | null;
 net_weight_kg?: string | null; scale_qc?: Record<string, unknown>;
};
export type HuSnapshot = {
 root: string; warehouse: number; cell: string; nodes: HuNode[];
 links: { parent: string; child: string }[]; ancestors: { uid: string; version?: number; cell?: string }[];
 leaf_count?: number; physical_unit_count?: number; historical_composition?: boolean;
 gross_weight_kg?: string | null; unknown_weight_leaves?: number; unknown_tare_containers?: number;
 placement?: { task_id: number; task_status: string; slot_code: string; version_matches: boolean;
  gross_weight_kg?: string | null; measurement_source: string } | null;
};
export type HuReference = { kind: "case" | "wave" | "warehouse-task"; id: number };
export function positiveId(value: unknown): value is number {
 return typeof value === "number" && Number.isSafeInteger(value) && value > 0;
}
function record(value: unknown): value is Record<string, unknown> {
 return typeof value === "object" && value !== null && !Array.isArray(value);
}
export function parseHuSnapshot(value: unknown): HuSnapshot {
 if (!record(value) || typeof value.root !== "string" || !positiveId(value.warehouse)
  || typeof value.cell !== "string" || !Array.isArray(value.nodes) || !Array.isArray(value.links)
  || !Array.isArray(value.ancestors) || value.nodes.length < 1 || value.nodes.length > 200
  || value.links.length > 199 || value.ancestors.length > 16) throw new Error("Состав не соответствует ограниченному контракту HU.");
 for (const key of ["leaf_count", "physical_unit_count", "unknown_weight_leaves", "unknown_tare_containers"]) if (value[key] != null
  && (typeof value[key] !== "number" || !Number.isSafeInteger(value[key]) || value[key] < 0)) throw new Error("Некорректный счётчик состава.");
 if (typeof value.physical_unit_count === "number" && value.physical_unit_count > 10000) throw new Error("Превышен лимит физических единиц.");
 if (value.gross_weight_kg != null && typeof value.gross_weight_kg !== "string") throw new Error("Некорректный справочный итог массы.");
 if (value.historical_composition != null && typeof value.historical_composition !== "boolean") throw new Error("Неизвестный признак исторического состава.");
 const ids = new Set<string>();
 for (const node of value.nodes) {
  if (!record(node) || typeof node.uid !== "string" || !node.uid || typeof node.kind !== "string" || ids.has(node.uid))
   throw new Error("Повторный или неизвестный узел состава.");
  ids.add(node.uid);
  for (const key of ["case_task_id", "wave_id"]) if (node[key] != null && !positiveId(node[key])) throw new Error("Некорректная ссылка задания.");
  for (const key of ["version", "open_task_count", "depth"]) if (node[key] != null
   && (typeof node[key] !== "number" || !Number.isSafeInteger(node[key]) || node[key] < 0)) throw new Error("Некорректная версия или счётчик узла.");
  for (const key of ["type", "sscc", "status", "cell", "article", "quantity", "base_uom", "tare_weight_kg", "weight_kg", "gross_weight_kg", "net_weight_kg"])
   if (node[key] != null && typeof node[key] !== "string") throw new Error("Некорректное поле узла: " + key);
  if (node.scale_qc != null && !record(node.scale_qc)) throw new Error("Неизвестный формат основания массы.");
 }
 if (!ids.has(value.root)) throw new Error("Корень отсутствует в составе.");
 const parents = new Map<string, string>();
 for (const link of value.links) {
  if (!record(link) || typeof link.parent !== "string" || typeof link.child !== "string"
   || !ids.has(link.parent) || !ids.has(link.child) || parents.has(link.child) || link.child === value.root)
   throw new Error("Неоднозначная связь дерева.");
  parents.set(link.child, link.parent);
 }
 for (const id of ids) {
  let next = id; const seen = new Set<string>();
  while (next !== value.root) {
   if (seen.has(next) || seen.size >= 16 || !parents.has(next)) throw new Error("Цикл, глубина или неполное дерево HU.");
   seen.add(next); next = parents.get(next)!;
  }
 }
 for (const ancestor of value.ancestors) if (!record(ancestor) || typeof ancestor.uid !== "string") throw new Error("Некорректный родитель HU.");
 if (value.placement != null && (!record(value.placement) || !positiveId(value.placement.task_id)
  || typeof value.placement.version_matches !== "boolean" || typeof value.placement.task_status !== "string"
  || typeof value.placement.slot_code !== "string" || (value.placement.gross_weight_kg != null && typeof value.placement.gross_weight_kg !== "string"))) throw new Error("Некорректное основание размещения.");
 return value as HuSnapshot;
}
export function massDescription(node: HuNode): { value: string; basis: string } {
 if (node.scale_qc && node.gross_weight_kg != null) return {
  value: node.gross_weight_kg + " кг", basis: "Основание scale_qc snapshot. Это не общий вес внешней HU и не доказательство ASM_FINAL или аппаратной приёмки." };
 if (node.weight_kg != null) return { value: node.weight_kg + " кг", basis: "Вес STOCK из учётных данных. Измерение весами этим полем не подтверждено." };
 return { value: "Неизвестна", basis: "Основание GROSS не передано. Массы детей и тара автоматически не складываются." };
}
