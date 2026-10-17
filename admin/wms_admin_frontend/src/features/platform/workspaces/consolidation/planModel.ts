import { RAW_ADMIN_BASE } from "../../../../api";

// Ожидаемый состав паллеты (план консолидации), C0116. Источник — /api/consolidation-plans (installed native/API).
// План и физическое дерево — разные вещи: planned root может ещё не существовать физически.

export type PlanStatus = "ACTIVE" | "CANCELLED";
export type PlanRow = { plan_id: string; version: number; status: PlanStatus; root_identifier: string; warehouse_id: number; cell: string; expected_count: number; updated_at: string };
export type PlanPage = { warehouse_id: number; items: PlanRow[]; has_more: boolean; next_after: string | null };
export type PlanMember = { fulfillment_id: number; shipment_id: number | null; pallet_identifier: string | null; source_warehouse_id?: number | null };
export type MemberState = "IN_ROOT" | "NOT_PICKED" | "MISSING" | "SHIPMENT_CHANGED" | "REQUEST_CHANGED" | "BINDING_CHANGED" | string;
export type Readiness = { ready: boolean; location_ready: boolean; expected_count: number; missing_count: number; extra_count: number; changed_count: number;
  unknown_leaf_count: number; plan_version: number; members: (PlanMember & { state: MemberState })[]; quality_release_approved?: boolean };
export type PlanDetail = { plan_id: string; version: number; status: PlanStatus; root_identifier: string; warehouse_id: number; cell: string; members: PlanMember[]; readiness: Readiness };
export type PlanAck = { operation_id: string; plan_id: string; version: number; status: PlanStatus };

export class PlanShapeError extends Error {}
const rec = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const int = (v: unknown) => typeof v === "number" && Number.isSafeInteger(v);
const str = (v: unknown) => typeof v === "string" && v.length > 0;
function need(cond: unknown, what: string): asserts cond { if (!cond) throw new PlanShapeError("Неожиданный ответ API планов: " + what); }

const validRow = (r: unknown): r is PlanRow => rec(r) && str(r.plan_id) && int(r.version) && (r.status === "ACTIVE" || r.status === "CANCELLED")
  && str(r.root_identifier) && int(r.warehouse_id) && typeof r.cell === "string" && int(r.expected_count) && typeof r.updated_at === "string";

export function parsePage(v: unknown, warehouse: number): PlanPage {
  need(rec(v) && Array.isArray(v.items) && typeof v.has_more === "boolean", "нет items/has_more");
  need(v.warehouse_id === warehouse, "ответ другого склада");
  need(v.items.every(validRow), "строка плана неполная");
  need(v.next_after === null || str(v.next_after), "курсор");
  return v as unknown as PlanPage;
}

export function parseDetail(v: unknown, planId: string): PlanDetail {
  need(rec(v) && v.plan_id === planId && validRow({ ...v, expected_count: 0, updated_at: "" }), "карточка плана");
  need(Array.isArray(v.members) && v.members.every(m => rec(m) && int(m.fulfillment_id)), "состав плана");
  const r = v.readiness;
  need(rec(r) && typeof r.ready === "boolean" && typeof r.location_ready === "boolean" && Array.isArray(r.members)
    && ["expected_count", "missing_count", "extra_count", "changed_count", "unknown_leaf_count"].every(k => int(r[k])), "готовность");
  return v as unknown as PlanDetail;
}

export function parseAck(v: unknown, planId: string, operationId: string): PlanAck {
  need(rec(v) && v.operation_id === operationId && v.plan_id === planId && int(v.version) && (v.status === "ACTIVE" || v.status === "CANCELLED")
    && v.stock_changed === false, "квитанция не подтверждает именно эту операцию");
  return v as unknown as PlanAck;
}

/** Состояние сборки в плане — по коду сервера; неизвестный код показывается как есть. */
export const STATE_TEXT: Record<string, { label: string; tone: "ok" | "plan" | "bad" | "warn" }> = {
  IN_ROOT: { label: "в составе", tone: "ok" }, NOT_PICKED: { label: "не собрана", tone: "plan" }, MISSING: { label: "отсутствует", tone: "bad" },
  SHIPMENT_CHANGED: { label: "изменена отгрузка — проверить", tone: "warn" }, REQUEST_CHANGED: { label: "изменён заказ — проверить", tone: "warn" },
  BINDING_CHANGED: { label: "изменена привязка — проверить", tone: "warn" },
};
export const stateText = (s: string) => STATE_TEXT[s] ?? { label: s, tone: "warn" as const };

/** Обычные страницы справки на API origin (C0116); открываются в новой вкладке, черновик плана не теряется. */
export const planHelpUrl = (anchor: "save" | "refresh" | "cancel" | "conflict") => `${RAW_ADMIN_BASE.replace(/\/wms-admin$/, "")}/help/consolidation-plan.html#${anchor}`;

/** UTC-момент обновления — коротко, с одной общей пометкой «UTC» в шапке списка, а не на каждой карточке. */
export const utcShort = (iso: string) => {
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})[^Z+-]*(Z|\+00:00)$/);
  return m ? `${m[3]}.${m[2]} ${m[4]}:${m[5]}` : iso; // не UTC — показываем исходную строку, без пересчёта браузером
};
