import { API_BASE } from "../../../api";
import type { BindBody } from "./api";

/** Долговечное намерение привязки (C-0133): тело и operation_id создаются один раз и сохраняются ДО отправки.
 *  Ключ — сервер API + пользователь + склад: чужое намерение не воспроизводится. sent=true — отправка уже была,
 *  исход мог дойти до сервера. Повреждённая запись не перезаписывается. Пароль не хранится. */
export type Intent = { body: BindBody; sent: boolean };
export type Stored = { kind: "none" } | { kind: "ok"; intent: Intent } | { kind: "damaged"; raw: string };

const key = (user: string, wh: string) => `tradecase.bind:${API_BASE}:${user}:${wh}`;
const valid = (v: unknown): v is Intent => {
  const i = v as Intent, b = i?.body;
  return Boolean(b && typeof i.sent === "boolean" && /^TC\.BIND\.UI:[A-Za-z0-9-]{8,80}$/.test(b.operation_id) && typeof b.supply_id === "string" && b.supply_id
    && Number.isSafeInteger(b.expected_supply_version) && typeof b.scanned_pallet === "string" && b.scanned_pallet.length > 0 && b.scanned_pallet.length <= 50);
};

export function readIntent(user: string, wh: string): Stored {
  if (!user || !wh) return { kind: "none" };
  let raw: string | null;
  try { raw = localStorage.getItem(key(user, wh)); } catch { return { kind: "damaged", raw: "Хранилище браузера недоступно. Отправка привязки заблокирована." }; }
  if (raw === null) return { kind: "none" };
  try { const v = JSON.parse(raw); return valid(v) ? { kind: "ok", intent: v } : { kind: "damaged", raw }; } catch { return { kind: "damaged", raw }; }
}

function write(user: string, wh: string, intent: Intent) {
  const raw = JSON.stringify(intent);
  localStorage.setItem(key(user, wh), raw);
  if (localStorage.getItem(key(user, wh)) !== raw) throw new Error("Намерение не сохранено в браузере — запись не отправлена.");
}

/** Новое намерение: только если сохранённого нет (иначе сначала разрешить прежнее). */
export function createIntent(user: string, wh: string, supply_id: string, version: number, scanned: string): Intent {
  if (readIntent(user, wh).kind !== "none") throw new Error("Сначала завершите сохранённую привязку на этом складе.");
  const intent = { body: { operation_id: "TC.BIND.UI:" + crypto.randomUUID(), supply_id, expected_supply_version: version, scanned_pallet: scanned }, sent: false };
  write(user, wh, intent); return intent;
}

export const markSent = (user: string, wh: string, intent: Intent) => write(user, wh, { ...intent, sent: true });
export const clearIntent = (user: string, wh: string) => localStorage.removeItem(key(user, wh));
