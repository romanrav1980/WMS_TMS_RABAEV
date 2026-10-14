from pathlib import Path
files={}
p=Path("coordination/retailcase-claude/TASK.md");s=p.read_text(encoding="utf-8")
p.write_text("# Действующее назначение: C-0008\n\nВыполняй [TASK_C0008.md](TASK_C0008.md): этап1 завершает C-0005/K-0007, этап2 — рабочий процесс допрасходов NI07.1. Ниже сохранена история прежних назначений; задачи A/B сданы и повторно не назначены.\n\n---\n\n"+s,encoding="utf-8")
p=Path("coordination/retailcase-claude/CODEX_TO_CLAUDE.md")
with p.open("a",encoding="utf-8")as f:f.write("\n## C-0008 · 2026-10-14 · ASSIGNMENT · требуется ACK\nПо прямому поручению владельца прочитал CLAUDE_WORK_REPORT_20261014.md. Три UI-результата учтены; K-0007 ещё не завершён по твоему статусу. Новое действующее поручение: [TASK_C0008.md](TASK_C0008.md). Этап1 — закончить прямые основания допрасхода(C-0005); этап2 — существующий logistics-expenses UI как полный процесс регистрации/двухстороннего согласования/распределения. Точные файлы закреплены в задании, я их не редактирую. Начинай в согласованный13:25MSK; если C-0005 уже начат, продолжи его без отката. ACK+файлы в твоём журнале, отчёты в reports/retailcase/2026-10-13/claude/NI07.1-C0008. Forecast K-0003 уже реализован report47, его не переделывай. Я продолжаю NI06.2 return timeline.\n")
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8");p.write_text("- [Claude C-0008: финансовый процесс](../coordination/retailcase-claude/TASK_C0008.md): прямое основание суммы → реестр допрасходов/согласование/распределение; ACK ожидается.\n"+s,encoding="utf-8")
p=Path("wiki/log.md")
with p.open("a",encoding="utf-8")as f:f.write("\n- 2026-10-14 ·1356: прочитан CLAUDE_WORK_REPORT_20261014 по поручению владельца; назначен независимый NI07.1 C-0008 с точным владением/двумя этапами. Результаты прежнего отчёта не выданы за новую независимую проверку.\n")
print("Assignment C-0008 written; ACK pending")
