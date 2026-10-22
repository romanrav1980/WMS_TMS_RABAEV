import { useEffect, useRef, useState } from "react";
import { ApiRequestError, apiFetch } from "../../../api";
import { listPath } from "./api";
import type { DocRow, Page } from "./api";
import { useRead } from "./useRead";
import { Act, HelpLink, Tech } from "./ui";

type Result = { proposed_boxes: number; items: { priority: number; proposed_boxes: number; uncovered_boxes: string;
  need: { document_id: string; recipient_title: string; sku_title: string; additional_boxes: string } }[] };
const help = (id: string, text: string) => ({ id: "tradecase.topup." + id, text, anchor: "topup" });
function failure(e: unknown) {
  if (e instanceof ApiRequestError) {
    if (e.status === 401) return "Войдите в систему и повторите расчёт.";
    if (e.status === 403) return "Нет доступа к складу или собственнику груза. Проверьте назначение прав.";
    const code = (e.detail as { code?: string })?.code ?? "";
    if (code.startsWith("TOPUP_NEED_EXPIRED")) return "Обновите устаревший снимок потребности и повторите расчёт.";
    if (code.startsWith("TOPUP_PRIMARY_SNAPSHOT_MISMATCH")) return "Основной подвоз в снимке не совпадает с планом рейса. Сверьте данные получателя.";
    if (code.startsWith("TOPUP_NEED_HORIZON_MISMATCH")) return "Выезд рейса не входит в период потребности. Выберите подходящий снимок.";
    if (code === "TOPUP_DUPLICATE_RECIPIENT_SKU") return "Оставьте один снимок на товар и получателя.";
    if (code === "TOPUP_LOADING_ALREADY_STARTED") return "Погрузка уже началась. Перед изменением состава согласуйте добивку с диспетчером.";
    if (e.status === 404) return "Снимок потребности не найден на этом складе. Проверьте его номер.";
    if (e.status === 409) return "Сверьте версии исходных данных, параметры упаковки и машины перед повторным расчётом.";
  }
  return "Не удалось получить расчёт. Повторите после восстановления связи.";
}

export function TopupPreview({ wh, trip, onSave, saveLocked }: { wh: string; trip: string; onSave?: (needIds: string[], age: number) => void; saveLocked?: boolean }) {
  const needs = useRead<Page<DocRow>>(listPath(wh, "NEED", null));
  const [choice, setChoice] = useState(""), [selected, setSelected] = useState<string[]>([]), [age, setAge] = useState("");
  const [result, setResult] = useState<Result | null>(null), [error, setError] = useState(""), [busy, setBusy] = useState(false), [detail, setDetail] = useState<unknown>(null);
  const active = useRef<AbortController | null>(null);
  const invalidate = () => { active.current?.abort(); active.current = null; setBusy(false); setResult(null); setError(""); setDetail(null); };
  useEffect(() => { invalidate(); setSelected([]); setChoice(""); return () => active.current?.abort(); }, [wh, trip]);
  function change(next: string[]) { invalidate(); setSelected(next); }
  function move(index: number, offset: number) { const next = [...selected]; [next[index], next[index + offset]] = [next[index + offset], next[index]]; change(next); }
  async function calculate() {
    invalidate(); const controller = new AbortController(); active.current = controller; setBusy(true);
    try {
      const value = await apiFetch<Result>(`/api/tradecase/warehouses/${encodeURIComponent(wh)}/trips/${encodeURIComponent(trip)}/topup-preview`, {
        method: "POST", signal: controller.signal, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ need_ids: selected, max_age_minutes: Number(age) }) });
      if (active.current === controller) setResult(value);
    } catch (e) { if (active.current === controller) { setError(failure(e)); setDetail(e instanceof ApiRequestError ? e.detail : null); } }
    finally { if (active.current === controller) { active.current = null; setBusy(false); } }
  }
  const valid = selected.length > 0 && /^\d+$/.test(age) && Number(age) >= 1 && Number(age) <= 1440;
  return <section className="tc-bind" aria-label="Распределение места под добивку">
    <h4>Распределение места под добивку <HelpLink anchor="topup" /></h4>
    <p>Добавьте потребности получателей в порядке приоритета. Расчёт распределит свободное место после основного груза.</p>
    <label>Снимок потребности<select value={choice} onChange={e => setChoice(e.target.value)} title="Выберите полученный снимок потребности этого склада" data-help-id="tradecase.topup.need">
      <option value="">Выберите снимок</option>{needs.data?.items.filter(n => !selected.includes(n.document_id)).map(n => <option key={n.document_id} value={n.document_id}>{n.document_id}</option>)}
    </select></label>
    {needs.error && <p className="tc-err" role="alert">{needs.error}</p>}
    {needs.data?.has_more && <p className="tc-note">Показаны первые 50 снимков. Номер другого снимка можно ввести вручную.</p>}
    <label>Или номер снимка<input value={choice} maxLength={100} onChange={e => setChoice(e.target.value)} title="Введите номер полученного снимка, если его нет в списке" data-help-id="tradecase.topup.need.id" /></label>
    <Act help={help("add", "Добавить снимок в конец приоритетов; товар не резервируется.")} disabled={!choice.trim() || selected.includes(choice.trim()) || selected.length >= 20}
      onClick={() => { change([...selected, choice.trim()]); setChoice(""); }}>Добавить потребность</Act>
    <ol>{selected.map((id, i) => <li key={id}>{id} {" "}
      <Act help={help("up", "Обработать эту потребность раньше предыдущей.")} disabled={i === 0} onClick={() => move(i, -1)}>↑</Act>{" "}
      <Act help={help("down", "Обработать эту потребность после следующей.")} disabled={i === selected.length - 1} onClick={() => move(i, 1)}>↓</Act>{" "}
      <Act help={help("remove", "Убрать потребность из расчёта.")} onClick={() => change(selected.filter(x => x !== id))}>Убрать</Act></li>)}</ol>
    <label>Допустимый возраст данных, мин<input type="number" min={1} max={1440} value={age} onChange={e => { invalidate(); setAge(e.target.value); }}
      title="Укажите допустимый возраст снимков для этого расчёта; значение не становится нормативом склада" data-help-id="tradecase.topup.age" /></label>
    <Act help={help("calculate", "Сверить основной груз и потребности, затем распределить свободное место. Заказ и резерв не создаются.")}
      disabled={!valid || busy} onClick={calculate}>Распределить место</Act>
    {busy && <p role="status">Сверяем потребности и вместимость…</p>}{error && <p className="tc-err" role="alert">{error}</p>}
    {!!detail && <Tech value={detail} label="Причина отказа сервера" />}
    {result && <div aria-label="Результат распределения"><p><b>Всего предложено: {result.proposed_boxes} кор.</b></p>
      {result.items.map(x => <article key={x.need.document_id} className="tc-panel"><h5>{x.priority}. {x.need.recipient_title} · {x.need.sku_title}</h5>
        <dl className="tc-fields"><dt>Потребность</dt><dd>{x.need.additional_boxes} кор.</dd><dt>Предложено</dt><dd>{x.proposed_boxes} кор.</dd><dt>Осталось покрыть</dt><dd>{x.uncovered_boxes} кор.</dd></dl></article>)}
      <p>Расчёт учитывает свободное место, уже подтверждённые добивки и пригодный запас сверх основных заказов. Маршрут, укладку и сроки доставки проверьте отдельно. Заказы SAP и складские задания расчётом не создаются.</p>
      {onSave && <Act help={help("save", "Сохранить расчёт как предложения для согласования. Повтор на тех же данных вернёт те же предложения; запас не удерживается.")}
        disabled={saveLocked} onClick={() => onSave(selected, Number(age))}>Сохранить как предложения</Act>}
      <Tech value={result} label="Версии и исходные данные расчёта" /></div>}
  </section>;
}
