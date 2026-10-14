from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts.py");s=p.read_text(encoding="utf-8").replace("    def rates(","    def rate_history(self,ware: int,currency: str,before: int,limit: int,actor: str) -> dict[str,Any]: ...\n    def rates(",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");s=p.read_text(encoding="utf-8").replace("    def rates(","    def rate_history(self,ware: int,currency: str,before: int,limit: int,actor: str) -> dict[str,Any]:\n        from .rate_history import read_rate_history\n        return read_rate_history(self.gateway,ware,currency,before,limit,actor)\n\n    def rates(",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");s=p.read_text(encoding="utf-8").replace("APIRouter,Depends,HTTPException","APIRouter,Depends,HTTPException,Query",1);idx=s.index('@router.post("/calculate")')
s=s[:idx]+"""@router.get("/warehouses/{ware_id}/rates/history")
def rate_history(ware_id: int,currency: str=Query(pattern=r"^[A-Z]{3}$"),before_version: int=Query(default=0,ge=0),limit: int=Query(default=25,ge=1,le=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.rate_history(ware_id,currency,before_version,limit,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

"""+s[idx:];out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.html");s=p.read_text(encoding="utf-8")
marker='<section class="panel"><label>Фактический рейс'
panel="""<section class="panel" data-permission="create_tt_price"><h2>Месячная ставка с общими работами</h2>
<label>Месяц<input id="lcMonth" type="month" title="Ставка начнёт действовать с первого числа указанного месяца"></label>
<label>Комплектация на коробку<input id="lcBaseRate" inputmode="decimal" title="Базовая ставка комплектации без общей месячной работы"></label>
<label>Общие затраты месяца<input id="lcCommonAmount" inputmode="decimal" title="Подтверждённая финансовым контролёром сумма общих работ в выбранной валюте"></label>
<label>Расчётная база коробок<input id="lcBasisBoxes" inputmode="numeric" title="Положительное целое число коробок для распределения общих месячных затрат"></label>
<button id="lcSaveMonthly" title="Сохранить новую версию: базовая ставка плюс общие затраты, разделённые на число коробок">Включить общие работы в ставку</button>
<p>Используются причина и номер решения выше. Общая работа включается в ставку; отдельного начисления не создаётся.</p>
<button id="lcReadHistory" title="Показать сохранённые версии ставок выбранного склада и валюты">История ставок</button><div id="lcHistory"></div></section>"""
assert marker in s;s=s.replace(marker,panel+marker,1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/logistics-costs.js");s=p.read_text(encoding="utf-8")
s=s.replace('intent.path==="/rates"?','intent.path.startsWith("/rates")?',1)
s=s.replace('["lcRates","lcLines"]','["lcRates","lcLines","lcHistory"]',1).replace('"lcTrip"])','"lcTrip","lcMonth","lcBaseRate","lcCommonAmount","lcBasisBoxes"])',1)
idx=s.index(' el("lcCalculate").addEventListener')
s=s[:idx]+""" el("lcSaveMonthly").addEventListener("click",()=>prepare("/rates/monthly",()=>{const ware=positive("lcWare"),c=currency();if(!rates||rates.ware!==ware)throw Error("Сначала обновите версии ставок.");return{warehouse_id:ware,currency:c,month:el("lcMonth").value,picking_rate:el("lcBaseRate").value.trim(),common_work_amount:el("lcCommonAmount").value.trim(),basis_boxes:el("lcBasisBoxes").value.trim(),expected_version:rates.rows.find(r=>r.currency===c)?.version_no||0,reason:el("lcReason").value.trim(),decision_reference:el("lcReference").value.trim()};}));
 el("lcReadHistory").addEventListener("click",()=>read(async current=>{const result=await request("/warehouses/"+positive("lcWare")+"/rates/history?currency="+encodeURIComponent(currency())+"&limit=100");if(!current())return;el("lcHistory").replaceChildren(...result.rows.map(r=>{const p=document.createElement("p"),c=r.components;p.textContent="Версия "+r.version_no+" · с "+r.effective_from+" · "+r.rate_value+" / BOX"+(c?" = комплектация "+c.picking_rate+" + общие работы "+c.common_work_rate+" ("+c.common_work_amount+" / "+c.basis_boxes+" коробок)":"");return p;}));say(result.next_before_version?"Показаны последние 100 версий; более ранние доступны через выгрузку истории.":"История ставок прочитана.");}));
"""+s[idx:];out[p.as_posix()]=s
print(json.dumps(out))
