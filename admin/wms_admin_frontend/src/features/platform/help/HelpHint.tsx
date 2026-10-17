import { useEffect, useId, useRef, useState } from "react";
import { helpActions, openHelpArticle } from "./catalog";
import type { HelpEntry } from "./catalog";

/** Значок «?» рядом с группой/полем: краткая помощь в popover и переход к статье.
 *  Мышь, клавиатура (Enter/Escape, фокус возвращается) и касание (явное открытие и кнопка «Закрыть»). Бизнес-команд не вызывает. */
export function HelpHint({ help, label }: { help: HelpEntry; label?: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const trigger = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const close = () => { setOpen(false); trigger.current?.focus(); };
  useEffect(() => {
    if (!open) return;
    panel.current?.focus();
    const onKey = (event: KeyboardEvent) => { if (event.key === "Escape") { event.stopPropagation(); close(); } };
    const onDown = (event: PointerEvent) => {
      if (!panel.current?.contains(event.target as Node) && event.target !== trigger.current) setOpen(false);
    };
    window.addEventListener("keydown", onKey, true);
    window.addEventListener("pointerdown", onDown);
    return () => { window.removeEventListener("keydown", onKey, true); window.removeEventListener("pointerdown", onDown); };
  }, [open]);
  return <span className="help-hint">
    <button ref={trigger} type="button" className="help-hint-trigger" aria-expanded={open} aria-controls={id}
      aria-label={"Помощь: " + (label ?? help.title ?? help.text)} title={helpActions.hint.text} data-help-id={help.id + ".hint"}
      onClick={() => setOpen(value => !value)}>?</button>
    {open && <div ref={panel} id={id} role="dialog" aria-label={help.title ?? label ?? "Помощь"} tabIndex={-1} className="help-hint-panel">
      {help.title && <strong>{help.title}</strong>}
      <p>{help.text}</p>
      {help.details?.map(line => <p key={line}>{line}</p>)}
      <div className="help-hint-actions">
        <button type="button" title={helpActions.more.text} data-help-id={helpActions.more.id} onClick={() => { setOpen(false); openHelpArticle(help.article); }}>Подробнее</button>
        <button type="button" title="Закрыть подсказку и вернуться к элементу." data-help-id="knowledge.hint.close" onClick={close}>Закрыть</button>
      </div>
    </div>}
  </span>;
}
