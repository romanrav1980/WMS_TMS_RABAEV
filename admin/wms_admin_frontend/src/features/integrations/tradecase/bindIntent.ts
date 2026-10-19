import type { BindBody } from "./api";
import { journal } from "./intent";
import type { Intent as GenericIntent, Stored as GenericStored } from "./intent";

/** Намерение привязки (C-0133) на общем журнале команд; ключ tradecase.bind:API:пользователь:склад сохранён. */
export type Intent = GenericIntent<BindBody>;
export type Stored = GenericStored<BindBody>;
const bind = journal<BindBody>("bind", "TC.BIND.UI", b => typeof b.supply_id === "string" && Boolean(b.supply_id) && Number.isSafeInteger(b.expected_supply_version)
  && typeof b.scanned_pallet === "string" && b.scanned_pallet.length > 0 && b.scanned_pallet.length <= 50, "привязку");

export const readIntent = bind.read;
export const createIntent = (user: string, wh: string, supply_id: string, version: number, scanned: string): Intent =>
  bind.create(user, wh, { supply_id, expected_supply_version: version, scanned_pallet: scanned });
export const markSent = bind.markSent;
export const clearIntent = bind.clear;
