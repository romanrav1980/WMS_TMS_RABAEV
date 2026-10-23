import type { HelpEntry } from "../../help/catalog";

const h = (id: string, text: string): HelpEntry => ({ id: "paper." + id, text, article: "paper-tasks" });

export const paperHelp = {
  refresh: h("refresh", "Перечитать незавершённые задания склада. Показывается не больше 100 заданий; сузьте список по исполнителю."),
  filter: h("filter", "Показать задания одного исполнителя (его логин в системе)."),
  open: h("open", "Открыть бланк этого задания: проверить, распечатать или сверить версию со штрихкода."),
  close: h("close", "Скрыть бланк задания."),
  scan: h("scan", "Сверить штрихкод с бумажного бланка с текущим заданием. Если задание изменилось, бланк устарел."),
} satisfies Record<string, HelpEntry>;
