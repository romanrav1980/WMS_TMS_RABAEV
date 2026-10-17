import { useState } from "react";
import { help } from "../help";

// Plain numeric field + direct link only: a task_id is never a scannable barcode.
export function TaskPicker({ initial, onOpen }: { initial: number | null; onOpen: (taskId: number) => void }) {
  const [value, setValue] = useState(initial != null ? String(initial) : "");
  const n = Number(value);
  const valid = value.trim() !== "" && Number.isInteger(n) && n > 0;
  return <div className="asm-task-picker">
    <h2>Задание сборки</h2>
    <p className="asm-note">Номер назначенного задания или прямая ссылка ?task_id=&lt;номер&gt;.</p>
    <label>Номер задания
      <input inputMode="numeric" value={value} onChange={e => setValue(e.target.value.replace(/\D/g, ""))}
        onKeyDown={e => e.key === "Enter" && valid && onOpen(n)} title={help.taskId.title} data-help-id={help.taskId.id} /></label>
    <button type="button" disabled={!valid} onClick={() => onOpen(n)} title="Открыть контекст этого задания" data-help-id="assembly.task-id.open">Открыть</button>
  </div>;
}
