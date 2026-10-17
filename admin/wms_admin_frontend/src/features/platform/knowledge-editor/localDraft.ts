import { apiOperationScope } from "../../../api";
import type { ArticleDraft } from "./types";

/** Рабочая копия статьи в браузере: переживает перезагрузку и потерю связи. Не является сохранением на сервере. */
export type LocalDraft = { draft: ArticleDraft; saved_at: string };
const key = (articleId: string) => `retailcase.knowledge.draft:${apiOperationScope()}:${articleId || "new"}`;

export function readLocalDraft(articleId: string): LocalDraft | null {
  try {
    const raw = localStorage.getItem(key(articleId));
    if (!raw) return null;
    const value = JSON.parse(raw) as LocalDraft;
    return value && typeof value.draft?.body === "string" && typeof value.saved_at === "string" ? value : null;
  } catch { return null; }
}

/** sessionId — ключ сеанса редактирования: article_id открытой статьи или "" для новой (копия под "new"). */
export function writeLocalDraft(sessionId: string, draft: ArticleDraft): boolean {
  try { localStorage.setItem(key(sessionId), JSON.stringify({ draft, saved_at: new Date().toISOString() })); return true; }
  catch { return false; }
}

/** Отпечаток содержимого статьи: только поля, которые уходят на сервер. */
export function draftFingerprint(value: { article_id: string; space_id: string; title: string; summary: string; body: string; related: unknown; sources: unknown; required_permissions: unknown }): string {
  const list = (v: unknown) => (Array.isArray(v) ? v : String(v ?? "").split(/[\n,]/)).map(x => String(x).trim()).filter(Boolean).join("|");
  return JSON.stringify([value.article_id, value.space_id, value.title.trim(), value.summary.trim(), value.body, list(value.related), list(value.sources), list(value.required_permissions)]);
}

/** Удалить локальную копию только если она совпадает с подтверждённым сервером телом (C-0071):
 *  более новый ввод и чужой черновик «new» другой вкладки не стираются. Копия новой статьи хранится под ключом "new". */
export function clearLocalDraftIfSent(articleId: string, sent: Record<string, unknown>): void {
  const sentPrint = draftFingerprint(sent as Parameters<typeof draftFingerprint>[0]);
  for (const id of [articleId, ""]) {
    const local = readLocalDraft(id);
    if (!local || local.draft.article_id !== articleId) continue;
    try {
      if (draftFingerprint(local.draft) === sentPrint) localStorage.removeItem(key(id));
      // Новая статья уже создана, а ввод после отправки новее: переносим копию под ключ статьи, чтобы её предложили при открытии.
      else if (id === "" && !readLocalDraft(articleId)) {
        localStorage.setItem(key(articleId), JSON.stringify(local));
        localStorage.removeItem(key(""));
      }
    } catch { /* хранилище недоступно — копия останется */ }
  }
}

/** Явное удаление пользователем («Удалить копию») — только своего ключа. */
export function clearLocalDraft(articleId: string): void {
  try { localStorage.removeItem(key(articleId)); } catch { /* хранилище недоступно — копия останется до следующей попытки */ }
}
