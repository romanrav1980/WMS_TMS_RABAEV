import axios from "axios";
import { API_BASE_URL } from "../config";
import { createJournalEntry, saveJournalEntry } from "../store/localJournal";
import type { JournalEntry, LotCheckPayload } from "../types";
import { confirmLotCheck } from "./wmsApi";

type Intent = { pallet: string; actor: string; payload: LotCheckPayload; journal: JournalEntry; uncertain: boolean };
const key = (pallet: string, actor: string) => JSON.stringify(["nicora.lotQuality", API_BASE_URL, actor, pallet]);

export function hasLotQualityIntent(pallet: string, actor: string): boolean {
  return !!localStorage.getItem(key(pallet, actor));
}

export async function postLotQuality(pallet: string, actor: string, payload: LotCheckPayload, retry: boolean): Promise<void> {
  const slot = key(pallet, actor);
  let intent = JSON.parse(localStorage.getItem(slot) || "null") as Intent | null;
  if (retry && !intent) throw new Error("Нет сохранённой проверки.");
  if (!retry && intent) throw new Error("Сначала повторите сохранённую проверку.");
  if (!intent) {
    const operation = "LOT.QC.UI:" + crypto.randomUUID();
    const submitted = { ...payload, user_id: actor, operation_id: operation };
    intent = { pallet, actor, payload: submitted, uncertain: false,
      journal: createJournalEntry("lot-check", pallet, { palletIdentifier: pallet, ...submitted }) };
    localStorage.setItem(slot, JSON.stringify(intent));
  }
  if (intent.actor !== actor || intent.pallet !== pallet) throw new Error("Сохранённая проверка принадлежит другому оператору.");
  intent.journal.status = "sent";
  localStorage.setItem(slot, JSON.stringify(intent));
  // The persisted intent is mandatory; an optional journal failure cannot erase it.
  try { await saveJournalEntry(intent.journal); } catch { /* The intent still retains every parameter. */ }
  try {
    await confirmLotCheck(intent.pallet, intent.payload);
  } catch (error) {
    const detail = axios.isAxiosError(error) ? error.response?.data?.detail : undefined;
    const knownRejection = detail?.outcome_confirmed === true && !intent.uncertain;
    intent.uncertain = intent.uncertain || !knownRejection;
    intent.journal.status = knownRejection ? "rejected" : "uncertain";
    intent.journal.message = axios.isAxiosError(error) ? error.message : String(error);
    intent.journal.updatedAt = new Date().toISOString();
    if (knownRejection) localStorage.removeItem(slot);
    else localStorage.setItem(slot, JSON.stringify(intent));
    try { await saveJournalEntry(intent.journal); } catch { /* Original request remains persisted. */ }
    throw error;
  }
  intent.journal.status = "accepted";
  intent.journal.message = "END_LOT_CHECK_PASSED";
  intent.journal.updatedAt = new Date().toISOString();
  try { localStorage.removeItem(slot); } catch { /* A surviving intent safely replays the committed result. */ }
  try { await saveJournalEntry(intent.journal); } catch { /* Oracle success remains authoritative. */ }
}
