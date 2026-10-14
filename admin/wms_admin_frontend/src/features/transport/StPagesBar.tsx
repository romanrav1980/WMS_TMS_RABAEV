import {ST_PAGE_SIZE} from "./useAvailableStPages";
import "./StPages.css";

// NI02.2: что именно загружено. Общего числа строк сервер не отдаёт, поэтому оно не показывается и не обещается.
export function StPagesBar({rows,pages,hasMore,loading,error,period,onMore,onRetry}:{rows:number;pages:number;hasMore:boolean;loading:boolean;error:string;period:string;onMore:()=>void;onRetry:()=>void}){
 return <div className="st-pages" role="status" aria-live="polite">
  {error
   ?<><span className="st-pages-error">{error}</span><button type="button" onClick={onRetry} disabled={loading}>Повторить</button></>
   :<span className="st-pages-count" title={"Период: "+period+". Сортировка, итоги, «выделить всё» и CSV относятся только к загруженным строкам."}>
     {loading&&!rows?"Загружаем СТ…":<>Загружено {rows} СТ{pages>1?" · страниц "+pages:""}{hasMore?" · есть ещё":rows?" · всё по фильтру":""}</>}
    </span>}
  {!error&&hasMore&&<button type="button" className="st-pages-more" onClick={onMore} disabled={loading} title={"Загрузить следующие "+ST_PAGE_SIZE+" СТ по тем же фильтрам"}>{loading?"Загружаем…":"Загрузить ещё "+ST_PAGE_SIZE}</button>}
  <span className="st-pages-period">период {period}</span>
 </div>;
}
