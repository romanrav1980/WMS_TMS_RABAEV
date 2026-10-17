import { useEffect, useMemo, useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { formatMoment, useApiRead } from "../access-admin";
import { editorHelp } from "./help";
import { readLocalDraft, writeLocalDraft, clearLocalDraft } from "./localDraft";
import { ARTICLE_ID, splitList } from "./types";
import type { Article, ArticleDraft, ArticleHistory, ArticleSummary, KnowledgeSpace } from "./types";

type View = "edit" | "preview" | "history";
const fromArticle = (a: Article): ArticleDraft => ({ article_id: a.article_id, space_id: a.space_id, title: a.title, summary: a.summary, body: a.body,
  related: a.related.join(", "), sources: a.sources.join("\n"), required_permissions: a.required_permissions.join(", "), reason: "", expected_version: a.version });
const same = (a: ArticleDraft, b: ArticleDraft) => JSON.stringify({ ...a, reason: "" }) === JSON.stringify({ ...b, reason: "" });

/** Редактор статьи: черновик, предпросмотр безопасного текста, история; публикация и архив — отдельные команды. */
export function ArticleEditor({ article, spaces, known, reload, blocked, busy, onSave, onPublish, onArchive }: {
  article: Article | null; spaces: KnowledgeSpace[]; known: ArticleSummary[]; reload: number; blocked: boolean; busy: boolean;
  onSave: (payload: Record<string, unknown>, label: string) => void; onPublish: (reason: string) => void; onArchive: (reason: string) => void;
}) {
  const base = useMemo<ArticleDraft>(() => article ? fromArticle(article) : { article_id: "", space_id: spaces[0]?.space_id ?? "general", title: "", summary: "", body: "",
    related: "", sources: "", required_permissions: "", reason: "", expected_version: 0 }, [article, spaces]);
  const [draft, setDraft] = useState<ArticleDraft>(base);
  const [view, setView] = useState<View>("edit");
  const [local, setLocal] = useState(() => readLocalDraft(base.article_id));
  const [stateReason, setStateReason] = useState("");
  const history = useApiRead<ArticleHistory[]>(article && view === "history" ? `/api/knowledge/articles/${encodeURIComponent(article.article_id)}/history?limit=50` : null, reload);
  useEffect(() => { setDraft(base); setLocal(readLocalDraft(base.article_id)); setView("edit"); }, [base]);
  // Автосохранение рабочей копии в браузере (не на сервере), чтобы перезагрузка/обрыв не теряли текст.
  useEffect(() => {
    if (same(draft, base) && !draft.reason) return;
    const timer = window.setTimeout(() => writeLocalDraft(base.article_id, draft), 500);
    return () => window.clearTimeout(timer);
  }, [draft, base]);
  const offerRestore = local !== null && !same(local.draft, base) && same(draft, base);
  const relatedIds = splitList(draft.related);
  const unknownRelated = relatedIds.filter(id => !known.some(k => k.article_id === id));
  const permsChanged = article && splitList(draft.required_permissions).join(",") !== article.required_permissions.join(",");
  const invalid = !ARTICLE_ID.test(draft.article_id) ? "код статьи: латиница в нижнем регистре, цифры и дефис, 2–80 символов"
    : !draft.title.trim() ? "нужен заголовок" : !draft.summary.trim() ? "нужно краткое описание" : !draft.body.trim() ? "нужен текст"
    : draft.body.length > 20000 ? "текст длиннее 20000 символов" : /<[a-z!/][^>]*>/i.test(draft.body) ? "HTML не допускается — только текст"
    : relatedIds.length > 30 ? "не больше 30 связанных статей" : !draft.reason.trim() ? "укажите причину изменения" : "";
  const lock = blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : "";
  const save = () => onSave({ article_id: draft.article_id, space_id: draft.space_id, title: draft.title.trim(), summary: draft.summary.trim(), body: draft.body,
    related: relatedIds, sources: splitList(draft.sources), required_permissions: splitList(draft.required_permissions), expected_version: draft.expected_version,
    reason: draft.reason.trim() }, `Статья ${draft.article_id}`);
  const field = (name: keyof ArticleDraft, label: string, title: string, props: Record<string, unknown> = {}) =>
    <label>{label}<input value={String(draft[name])} onChange={e => setDraft({ ...draft, [name]: e.target.value })} title={title} data-help-id={"knowledge.editor.field." + name} {...props} /></label>;
  return <section className="ke-editor" aria-label="Редактор статьи">
    <header className="ke-editor-head">
      <h3>{article ? `${article.title}` : "Новая статья"} {article && <small>{article.status} · v{article.version} · {article.updated_by ?? "—"} {formatMoment(article.updated_at)}</small>}</h3>
      <div role="tablist" aria-label="Режим" className="ke-views">
        {([["edit", "Текст", editorHelp.save], ["preview", "Как увидит читатель", editorHelp.previewTab], ["history", "История", editorHelp.historyTab]] as const).map(([id, label, help]) =>
          <button key={id} role="tab" aria-selected={view === id} disabled={id === "history" && !article} title={id === "history" && !article ? "История появится после первого сохранения." : help.text}
            data-help-id={help.id} onClick={() => setView(id)}>{label}</button>)}
      </div>
    </header>
    {offerRestore && local && <div className="aa-pending" role="region" aria-label="Несохранённый текст">
      <strong>В браузере есть несохранённый текст от {formatMoment(local.saved_at)}.</strong>
      {local.draft.expected_version !== base.expected_version && <span>Копия сделана на версии {local.draft.expected_version}, сейчас на сервере версия {base.expected_version}: после восстановления сравните текст перед сохранением.</span>}
      <div className="aa-actions">
        <HelpButton help={editorHelp.restore} onClick={() => setDraft({ ...local.draft, article_id: base.article_id || local.draft.article_id, expected_version: base.expected_version })}>Восстановить</HelpButton>
        <HelpButton help={editorHelp.discard} onClick={() => { clearLocalDraft(base.article_id); setLocal(null); }}>Удалить копию</HelpButton>
      </div></div>}
    {view === "edit" && <div className="aa-form">
      {field("article_id", "Код статьи (article_id)", "Постоянный идентификатор для ссылок и help_id; после создания не меняется.", { disabled: Boolean(article), maxLength: 80 })}
      <label>Пространство<select value={draft.space_id} onChange={e => setDraft({ ...draft, space_id: e.target.value })} title={editorHelp.space.text} data-help-id="knowledge.editor.field.space">
        {spaces.map(s => <option key={s.space_id} value={s.space_id}>{s.title}</option>)}</select></label>
      {field("title", "Заголовок", "Короткий заголовок: о каком действии статья.", { maxLength: 200 })}
      {field("summary", "Краткое описание", "Одна-две фразы, видны в поиске справки.", { maxLength: 1000 })}
      <label>Текст ({draft.body.length}/20000) <span className="aa-note">Пустая строка разделяет абзацы. HTML не используется.</span>
        <textarea value={draft.body} rows={14} onChange={e => setDraft({ ...draft, body: e.target.value })} title="Безопасный текст статьи: что делает действие, когда доступно, результат, повтор и ошибки." data-help-id="knowledge.editor.field.body" /></label>
      {field("related", "Связанные статьи (article_id через запятую)", "Стабильные article_id; читатель увидит только доступные ему.")}
      {unknownRelated.length > 0 && <p className="aa-note">Не найдены среди известных статей: {unknownRelated.join(", ")} — сервер может отклонить сохранение.</p>}
      <label>Источники (по строке)<textarea value={draft.sources} rows={3} onChange={e => setDraft({ ...draft, sources: e.target.value })} title="Проектные источники для проверки актуальности; читателю показываются в «Источниках»." data-help-id="knowledge.editor.field.sources" /></label>
      {field("required_permissions", "Права чтения (через запятую, пусто — всем вошедшим)", "Кто может читать статью. Изменение прав чтения требует публикатора.")}
      {permsChanged && <p className="aa-note">Права чтения изменены: сохранение выполнит только публикатор (редактор не расширяет доступ).</p>}
      {field("reason", "Причина изменения", "Сохраняется в истории статьи.", { maxLength: 500 })}
      <div className="aa-actions">
        <HelpButton help={editorHelp.save} unavailable={lock || invalid} onClick={save}>Сохранить черновик</HelpButton><HelpHint help={editorHelp.save} />
      </div>
      {article && <div className="ke-state">
        <label>Причина публикации/архива<input value={stateReason} maxLength={500} onChange={e => setStateReason(e.target.value)} title="Сохраняется в истории." data-help-id="knowledge.editor.field.state_reason" /></label>
        <div className="aa-actions">
          <HelpButton help={editorHelp.publish} unavailable={lock || (!stateReason.trim() && "укажите причину") || (!same(draft, base) && "сначала сохраните черновик")} onClick={() => onPublish(stateReason.trim())}>Опубликовать</HelpButton>
          <HelpButton help={editorHelp.archive} unavailable={lock || (!stateReason.trim() && "укажите причину") || (article.status === "ARCHIVED" && "уже в архиве")} onClick={() => onArchive(stateReason.trim())}>В архив</HelpButton>
        </div></div>}
    </div>}
    {view === "preview" && <article className="ke-preview" aria-label="Предпросмотр">
      <h3>{draft.title || "Без заголовка"}</h3><p className="ke-summary">{draft.summary}</p>
      {draft.body.split("\n\n").map((p, i) => <p key={i}>{p}</p>)}
      <h4>Связанные инструкции</h4>
      {relatedIds.length === 0 ? <p className="aa-note">Нет.</p> : <ul>{relatedIds.map(id => { const k = known.find(x => x.article_id === id);
        return <li key={id}>{k ? k.title : <span className="aa-bad">«{id}» — статья не найдена</span>}</li>; })}</ul>}
      <details><summary title="Источники и права чтения статьи." data-help-id="knowledge.editor.preview.provenance">Источники и доступ</summary>
        {splitList(draft.sources).map(s => <p key={s}>{s}</p>)}<p>Права чтения: {splitList(draft.required_permissions).join(", ") || "все вошедшие"}</p></details>
    </article>}
    {view === "history" && <div>
      {history.loading && <p role="status">Загрузка истории…</p>}{history.error && <p role="alert">{history.error}</p>}
      {history.data && <table className="aa-table"><thead><tr><th>Версия</th><th>Статус</th><th>Кто</th><th>Когда</th><th>Причина</th></tr></thead>
        <tbody>{history.data.map(hh => <tr key={hh.version + hh.status + hh.created_at}><td data-label="Версия">{hh.version}</td><td data-label="Статус">{hh.status}</td>
          <td data-label="Кто">{hh.actor}</td><td data-label="Когда">{formatMoment(hh.created_at)}</td><td data-label="Причина">{hh.reason}</td></tr>)}</tbody></table>}
    </div>}
  </section>;
}
