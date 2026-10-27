import { useEffect, useId, useRef, useState } from "react";
import type { ButtonHTMLAttributes, CSSProperties, MouseEvent } from "react";
import { helpActions } from "./catalog";
import type { HelpAction, HelpEntry } from "./catalog";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  action?: HelpAction;
  help?: HelpEntry;
  /** Причина недоступности. Кнопка остаётся фокусируемой и объясняет причину вместо молчаливого disabled. */
  unavailable?: string | false | null;
};

const EDGE = 8;  // отступ подсказки от края окна, px

/** C-0186: подсказка ставится по прямоугольнику кнопки в пределах окна (fixed): у левого/правого края и на узком экране она не
 *  обрезается и не создаёт горизонтальную прокрутку; нет места сверху — показывается под кнопкой. */
function placement(button: HTMLElement, tip: HTMLElement): CSSProperties {
  const b = button.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
  const left = Math.max(EDGE, Math.min(b.right - w, innerWidth - EDGE - w));
  const top = b.top - h - 6 >= EDGE ? b.top - h - 6 : Math.min(b.bottom + 6, innerHeight - EDGE - h);
  return { position: "fixed", left, top, right: "auto", bottom: "auto" };
}

/** Кнопка с подсказкой «что произойдёт и зачем» на hover/focus; Escape скрывает подсказку, data-help-id связывает с помощью. */
export function HelpButton({ action, help, unavailable, children, className, onClick, ...props }: Props) {
  const id = useId();
  const [dismissed, setDismissed] = useState(false);
  const [style, setStyle] = useState<CSSProperties | undefined>(undefined);
  const button = useRef<HTMLButtonElement>(null), tip = useRef<HTMLSpanElement>(null);
  const entry: HelpEntry = help ?? helpActions[action ?? "article"];
  const blocked = Boolean(unavailable) || Boolean(props.disabled);
  const reason = unavailable ? "Недоступно: " + unavailable + ". " : "";
  // Подсказка видна по :hover/:focus-within (CSS); после показа её место пересчитывается по фактическому размеру.
  const place = () => requestAnimationFrame(() => { if (button.current && tip.current && tip.current.offsetWidth) setStyle(placement(button.current, tip.current)); });
  useEffect(() => {
    if (!style) return;
    window.addEventListener("scroll", place, true); window.addEventListener("resize", place);
    return () => { window.removeEventListener("scroll", place, true); window.removeEventListener("resize", place); };
  }, [style]);
  const click = (event: MouseEvent<HTMLButtonElement>) => {
    if (unavailable) { event.preventDefault(); setDismissed(false); return; }
    onClick?.(event);
  };
  return <span className={"help-action" + (dismissed ? " help-dismissed" : "") + (blocked ? " help-blocked" : "")}>
    <button {...props} ref={button} type={props.type ?? "button"} className={className} title={reason + entry.text} data-help-id={entry.id} data-help-article={entry.article}
      aria-describedby={id} aria-disabled={blocked || undefined} disabled={unavailable ? false : props.disabled} onClick={click}
      onFocus={event => { setDismissed(false); place(); props.onFocus?.(event); }} onMouseEnter={event => { setDismissed(false); place(); props.onMouseEnter?.(event); }}
      onKeyDown={event => { if (event.key === "Escape") setDismissed(true); props.onKeyDown?.(event); }}>{children}</button>
    <span role="tooltip" id={id} ref={tip} className="help-tooltip" style={style}>{reason}{entry.text}</span>
  </span>;
}
