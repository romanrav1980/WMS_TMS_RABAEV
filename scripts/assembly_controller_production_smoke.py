"""Production read-only controller UI against native completed TEST history."""
import sys,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
g=OracleGateway();secret=g.fetch_all("select PASS from RUSERS where ID='admin'")[0]['pass']
out=ROOT/'reports/retailcase/2026-10-15/assembly-scale';checks=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 try:
  for width in (360,390,1440):
   context=browser.new_context(viewport=dict(width=width,height=900));page=context.new_page();errors=[];writes=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('request',lambda r:writes.append(r.method+' '+r.url.split('/api/',1)[-1]) if '/api/' in r.url and r.method not in ('GET','HEAD') else None)
   response=page.goto('http://127.0.0.1:8088/assembly/?reconciliation_id=ASM15.RECON1032');assert response.status==200
   page.locator('input[autocomplete="username"]').fill('admin');page.locator('input[type="password"]').fill(secret)
   page.get_by_role('button',name='Войти',exact=True).click()
   expect(page.get_by_text('Сверка завершена. Старый непринятый шаг отменён без товарной проводки.',exact=True)).to_be_visible()
   assert page.get_by_role('button',name='Подтвердить и запросить замер',exact=True).count()==0
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=str(out/f'controller-native-{width}.png'),full_page=True)
   page.get_by_role('button',name='Справка',exact=True).click()
   help_panel=page.get_by_role('dialog',name='Справка')
   expect(help_panel.get_by_role('heading',name='Сборка на весах: порядок работы')).to_be_visible()
   assert 'Для восстановления запросите сверку' in help_panel.inner_text()
   page.get_by_role('button',name='Закрыть справку',exact=True).click()
   assert secret not in page.evaluate('JSON.stringify({...localStorage})')
   assert not writes and not errors,(writes,errors)
   checks.append(dict(width=width,actual_native_history=True,no_mutation=True,no_overflow=True,help_current=True))
   context.close()
 finally:browser.close()
report=dict(status='PASS',checks=checks,hardware=False,production_build=True)
(out/'controller-native-ui.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
