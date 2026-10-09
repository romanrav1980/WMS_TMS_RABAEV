# Просмотр Markdown в проекте

Файлы `*.md` в workspace TMS открываются по умолчанию в custom editor расширения **Markdown Preview Enhanced**.

Настройка находится в `.vscode/settings.json`:

```json
"workbench.editorAssociations": {
  "*.md": "markdown-preview-enhanced"
}
```

Расширение `shd101wyy.markdown-preview-enhanced` указано в `.vscode/extensions.json` как рекомендуемое. Если требуется редактировать исходный Markdown, выполнить **Reopen Editor With… → Text Editor**. Для ручного открытия preview из текстового редактора доступны команды расширения и сочетание `Ctrl+Shift+V`.
