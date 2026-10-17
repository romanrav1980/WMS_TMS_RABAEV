import { useId, useState } from "react";
import type { ButtonHTMLAttributes, MouseEvent } from "react";
import { helpActions } from "./catalog";
import type { HelpAction, HelpEntry } from "./catalog";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  action?: HelpAction;
  help?: HelpEntry;
  /** Причина недоступности. Кнопка остаётся фокусируемой и объясняет причину вместо молчаливого disabled. */
  unavailable?: string | false | null;
};

/** Кнопка с подсказкой «что произойдёт и зачем» на hover/focus; Escape скрывает подсказку, data-help-id связывает с помощью. */
export function HelpButton({ action, help, unavailable, children, className, onClick, ...props }: Props) {
  const id = useId();
  const [dismissed, setDismissed] = useState(false);
  const entry: HelpEntry = help ?? helpActions[action ?? "article"];
  const blocked = Boolean(unavailable) || Boolean(props.disabled);
  const reason = unavailable ? "Недоступно: " + unavailable + ". " : "";
  const click = (event: MouseEvent<HTMLButtonElement>) => {
    if (unavailable) { event.preventDefault(); setDismissed(false); return; }
    onClick?.(event);
  };
  return <span className={"help-action" + (dismissed ? " help-dismissed" : "") + (blocked ? " help-blocked" : "")}>
    <button {...props} type={props.type ?? "button"} className={className} title={reason + entry.text} data-help-id={entry.id} data-help-article={entry.article}
      aria-describedby={id} aria-disabled={blocked || undefined} disabled={unavailable ? false : props.disabled} onClick={click}
      onFocus={event => { setDismissed(false); props.onFocus?.(event); }} onMouseEnter={event => { setDismissed(false); props.onMouseEnter?.(event); }}
      onKeyDown={event => { if (event.key === "Escape") setDismissed(true); props.onKeyDown?.(event); }}>{children}</button>
    <span role="tooltip" id={id} className="help-tooltip">{reason}{entry.text}</span>
  </span>;
}
