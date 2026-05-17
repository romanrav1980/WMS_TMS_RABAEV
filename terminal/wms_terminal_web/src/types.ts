export type LegacyBlock = {
  function_name: string;
  values: Record<string, string>;
};

export type LegacyExecuteResponse = {
  payload: string;
  blocks: LegacyBlock[];
};

export type DbPingResponse = {
  user_name: string;
  service_name: string;
  db_name: string;
};

export type TerminalSession = {
  userId: string;
  userName: string;
  wareId?: string;
  rights: Record<string, string>;
  signedInAt: string;
};

export type FlowKey = "home" | "product" | "lot" | "place" | "production" | "legacy" | "diagnostics";

export type JournalStatus = "draft" | "sent" | "accepted" | "rejected";

export type JournalEntry = {
  id: string;
  flow: string;
  resourceKey: string;
  status: JournalStatus;
  payload: unknown;
  createdAt: string;
  updatedAt: string;
  message?: string;
};

export type LotCheckPayload = {
  user_id: string;
  error_count: number;
  errors: Array<{
    uid: string;
    qty: number;
    condition: string;
    ean?: string;
    plan_qty?: number;
    usscc?: string;
  }>;
  vp_lines: Array<{
    pallet_uid: string;
    uid: string;
    checked_at: string;
  }>;
};

export type PlaceCheckPayload = {
  pallet_id: string;
  errors: Array<{
    uid: string;
    qty: number;
    condition: string;
    ean?: string;
  }>;
  inventory_lines: Array<{
    uid: string;
    qty: number;
    pallet_id: string;
    user_id: string;
  }>;
};
