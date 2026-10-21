import type { HuNode, HuSnapshot } from "./huTreeModel";

export type MassFact = { label: string; value: string; basis: string };
/** Display source strings exactly. No floating point arithmetic or promoted hardware provenance. */
export function massText(value: unknown): string | null {
 return typeof value === "string" && value.length <= 80 && /^\d+(?:\.\d+)?$/.test(value) ? value + " кг" : null;
}
export function huMassFacts(node: HuNode, snapshot: HuSnapshot): { facts: MassFact[]; legacyTotal: string | null; missing: string[] } {
 const facts: MassFact[] = [], missing: string[] = [];
 const qc = node.kind === "CASE" && node.scale_qc && massText(node.gross_weight_kg);
 if (qc) facts.push({ label: "GROSS из контроля CASE", value: qc,
  basis: "Основание scale_qc. Не отгрузочное измерение всей внешней HU; аппаратность и актуальность этим экраном не устанавливаются." });
 const stock = node.kind === "STOCK" && massText(node.weight_kg);
 if (stock) facts.push({ label: "Учётный вес товара", value: stock, basis: "Учётный вес; не измерение весами." });
 const tare = massText(node.tare_weight_kg);
 if (tare) facts.push({ label: "Собственная тара", value: tare, basis: "Учётное поле снимка; не новая квитанция весов." });
 else if (node.kind !== "STOCK") missing.push("Собственная тара выбранного места не передана либо имеет неподдерживаемый формат.");
 if (!qc && !stock) missing.push("Основание массы выбранного места не передано.");
 const placement = node.uid === snapshot.root ? snapshot.placement : null;
 const recorded = massText(placement?.gross_weight_kg);
 if (placement && recorded) facts.push({ label: "Записанный GROSS размещения", value: recorded,
  basis: placement.version_matches ? "Запись размещения, версия совпадает. Это не новое отгрузочное измерение."
   : "Версия отличается: историческая запись не подтверждает текущую массу состава." });
 if (snapshot.unknown_weight_leaves != null && snapshot.unknown_weight_leaves > 0)
  missing.push(`Сервер сообщает товарных ветвей без массы: ${snapshot.unknown_weight_leaves}.`);
 if (snapshot.unknown_tare_containers != null && snapshot.unknown_tare_containers > 0)
  missing.push(`Сервер сообщает мест без основания тары: ${snapshot.unknown_tare_containers}.`);
 const allTareKnown = snapshot.nodes.filter(n => n.kind !== "STOCK").every(n => massText(n.tare_weight_kg) !== null);
 const legacyTotal = node.uid === snapshot.root && !snapshot.historical_composition && allTareKnown
  && snapshot.unknown_weight_leaves === 0 && snapshot.unknown_tare_containers === 0 ? massText(snapshot.gross_weight_kg) : null;
 return { facts, legacyTotal, missing };
}
