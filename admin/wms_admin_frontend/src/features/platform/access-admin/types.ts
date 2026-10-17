// Контракт ACCESS_KNOWLEDGE_API_V1 (backend — Codex). Отсутствующие поля не означают нули.
export type ScopeKind = "WAREHOUSE" | "DC" | "STORE" | "REGION" | "CARRIER" | "ZONE" | "ORG_BRANCH" | "GROUP" | "SELF" | "NETWORK" | "PLATFORM";
export type ObjectKind = "WAREHOUSE" | "DC" | "STORE" | "REGION" | "CARRIER" | "ZONE";
export const OBJECT_KINDS: ObjectKind[] = ["WAREHOUSE", "DC", "STORE", "REGION", "CARRIER", "ZONE"];

export type AccessAssignment = {
  assignment_id: string; username: string; role_id: string; scope_kind: ScopeKind; scope_id: string | null;
  membership: "CURRENT" | "SNAPSHOT"; snapshot_version: number | null; valid_from: string; valid_until: string | null;
  revoked_at: string | null; assigned_by: string; reason: string; version: number;
  /** Состояние по сроку на серверном времени (C-0067); не гарантия права на каждый объект. */
  assignment_state?: "ACTIVE" | "SCHEDULED" | "EXPIRED" | "REVOKED";
};
/** capabilities — серверная политика навигации (native), не сумма ролей на клиенте (C-0069/C-0071). */
export type AccessCapabilities = { access_admin?: boolean; knowledge_editor?: boolean; knowledge_publish?: boolean; manage_roles?: boolean; manage_objects?: boolean; manage_groups?: boolean; manage_assignments?: boolean };
export type AccessMe = { username: string; legacy_group: string; assignments: AccessAssignment[]; access_revision: number; capabilities?: AccessCapabilities };
export type AccessRole = { role_id: string; title: string; permissions: string[]; active: boolean | number; version: number };
export type AccessCatalog = { roles: AccessRole[]; scope_kinds: ScopeKind[]; rights: string[] };
export type AccessGroupSummary = { group_id: string; title: string; member_kind: ObjectKind; version: number; active: boolean | number };
export type AccessGroup = AccessGroupSummary & { members: { kind: ObjectKind; object_id: string; title: string }[] };
export type AccessObject = { kind: ObjectKind; object_id: string; title: string; parent_kind: ObjectKind | null; parent_id: string | null; version: number; active: boolean | number };
export type ExplainResult = { allowed: boolean; reasons: Record<string, unknown>[]; access_revision: number };

export type AccessCommandType = "ROLE_SAVE" | "GROUP_SAVE" | "OBJECT_SAVE" | "ASSIGN" | "REVOKE";
export type CommandReceipt = { operation_id: string; command_type: string; object_id: string; version: number; replayed?: boolean };
export type GroupImpact = { group_id: string; version: number; added: { kind: ObjectKind; object_id: string }[]; removed: { kind: ObjectKind; object_id: string }[];
  affected_assignments: Record<string, unknown>[]; affected_total: number; preview_limit: number; activation_changed: boolean; snapshot_note: string };
