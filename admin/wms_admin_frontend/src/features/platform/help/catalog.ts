/** Запись помощи: стабильный help_id, короткий ответ «что произойдёт и зачем», статья базы знаний. */
export type HelpEntry = { id: string; text: string; article: string; title?: string; details?: string[] };

export const helpActions = {
  open: { id: "knowledge.open", text: "Открыть инструкции и поиск по базе знаний, сохранив текущий экран.", article: "using-help" },
  close: { id: "knowledge.close", text: "Закрыть справку и вернуться к текущей работе.", article: "using-help" },
  search: { id: "knowledge.search", text: "Найти опубликованные инструкции по словам в заголовке и тексте.", article: "using-help" },
  article: { id: "knowledge.article", text: "Открыть инструкцию, чтобы узнать условия действия и ожидаемый результат.", article: "using-help" },
  retry: { id: "knowledge.retry", text: "Повторить чтение справки. Бизнес-команды не отправляются.", article: "using-help" },
  more: { id: "knowledge.more", text: "Открыть полную инструкцию в справке. Текущий экран и введённые данные сохраняются.", article: "using-help" },
  hint: { id: "knowledge.hint", text: "Показать краткую помощь по этому элементу.", article: "using-help" },
} as const satisfies Record<string, HelpEntry>;
export type HelpAction = keyof typeof helpActions;

/** Событие открытия статьи справки из любого экрана: KnowledgePanel открывается поверх, рабочий экран не сбрасывается. */
export const HELP_OPEN_EVENT = "retailcase:help-open";
export function openHelpArticle(article: string): void {
  window.dispatchEvent(new CustomEvent<string>(HELP_OPEN_EVENT, { detail: article }));
}
