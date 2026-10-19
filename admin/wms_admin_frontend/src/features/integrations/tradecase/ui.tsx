import type { ButtonHTMLAttributes, ReactNode } from "react";
import { helpUrl, when } from "./api";
import type { Help } from "./api";

/** Кнопка с конкретной подсказкой действия (title + data-help-id) — как HelpButton платформы, без импорта из неё. */
export function Act({ help, children, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { help: Help; children: ReactNode }) {
  return <button type="button" {...props} title={help.text} data-help-id={help.id} data-help-url={helpUrl(help.anchor)}>{children}</button>;
}

/** Ссылка на раздел локальной справки (файл /help/tradecase-documents.html). */
export const HelpLink = ({ anchor, label = "Справка" }: { anchor: string; label?: string }) =>
  <a className="tc-help" href={helpUrl(anchor)} target="_blank" rel="noopener" title="Открыть инструкцию по этому разделу в новой вкладке" data-help-id={"tradecase.help." + anchor}>{label}</a>;

export const Time = ({ value }: { value: unknown }) => { const t = when(value); return <span title={t.title}>{t.text}</span>; };

/** Технические коды и исходный JSON — только в раскрываемом блоке. */
export const Tech = ({ value, label = "Технические сведения" }: { value: unknown; label?: string }) =>
  <details className="tc-tech"><summary title="Показать внутренние коды и исходные данные сервера" data-help-id="tradecase.tech">{label}</summary><pre>{JSON.stringify(value, null, 2)}</pre></details>;

export const str = (v: unknown) => v === null || v === undefined || v === "" ? "—" : String(v);
export const yes = (v: unknown) => v === true ? "да" : v === false ? "нет" : "—";
export const BUYOUT: Record<string, string> = { BEFORE_PICK: "до сборки", AFTER_PICK: "после сборки", IN_TRANSIT: "в пути" };
export const OSG: Record<string, string> = { SHIP_DATE: "от даты отгрузки", DELIVERY_DATE: "от даты доставки" };
export const ORDER_KIND: Record<string, string> = { OUTBOUND: "основной", TOPUP: "добивочный" };
export const UOM: Record<string, string> = { BOX: "кор.", EA: "шт." };
export const docStatus = (s: string) => s === "ACCEPTED" ? <span className="tc-chip ok">Основание принято</span>
  : s === "CANCELLED" ? <span className="tc-chip off">Отменено</span> : <span className="tc-chip">{s}</span>;
