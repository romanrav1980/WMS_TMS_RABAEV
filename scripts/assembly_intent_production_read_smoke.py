"""Actual production UI GET-only replay of an already committed abandonment receipt."""
import json
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='http://127.0.0.1:8088'
OUT=ROOT/'reports/retailcase/2026-10-15/assembly-intent'
ACTOR='WHREQ15.OP'


def main():
 proof=json.loads((OUT/'native.json').read_text(encoding='utf-8-sig'))
 assert proof['status']=='PASS'and proof['ack']['status']=='ABANDONED'
 body=proof['body'];assert body['kind']=='OPEN_SESSION'and body['original']['task_id']==1136
 credentials=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))
 password=credentials[ACTOR]
 if isinstance(password,dict):password=password['password']
 meta=dict(server=ORIGIN,actor=ACTOR,task_id=1136)
 original=dict(version=1,kind='open_session',target_session=body['original']['session_id'],body=body['original'])
 control=dict(version=1,original=original,request=body)
 original_key=f'assembly-scale:open_session:{ORIGIN}:{ACTOR}:1136'
 control_key=f'assembly-scale:abandonment:{ORIGIN}:{ACTOR}:1136'
 entries={key:dict(meta=meta,body=value,savedAt='2026-10-15T12:00:00Z')for key,value in ((original_key,original),(control_key,control))}
 results=[]
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  for width in (360,390,1440):
   context=browser.new_context(viewport=dict(width=width,height=960))
   page=context.new_page();requests=[];receipt=[]
   page.add_init_script('for(const [key,value]of Object.entries('+json.dumps(entries)+'))localStorage.setItem(key,JSON.stringify(value));')
   page.on('request',lambda r:requests.append(dict(method=r.method,path=urlsplit(r.url).path))if urlsplit(r.url).path.startswith('/api/')else None)
   def response(r):
    if '/api/inventory/assembly-scale/abandonments/'in r.url:receipt.append(dict(status=r.status,path=urlsplit(r.url).path))
   page.on('response',response)
   page.goto(ORIGIN+'/assembly/?task_id=1136')
   page.get_by_label('Логин',exact=True).fill(ACTOR);page.get_by_label('Пароль',exact=True).fill(password)
   page.locator('[data-help-id="assembly.login.submit"]').click()
   expect(page.locator('[data-help-id="assembly.abandon.read"]')).to_be_visible()
   assert not any(r['method']!='GET'for r in requests)
   page.screenshot(path=str(OUT/f'production-abandonment-pending-{width}.png'),full_page=True)
   page.locator('[data-help-id="assembly.abandon.read"]').click()
   expect(page.locator('[data-help-id="assembly.abandon.read"]')).to_have_count(0)
   persisted=page.evaluate('({local:{...localStorage},session:{...sessionStorage}})')
   assert original_key not in persisted['local']and control_key not in persisted['local']
   assert password not in json.dumps(persisted,ensure_ascii=False)
   assert receipt and all(r['status']==200 for r in receipt)
   assert not any(r['method']!='GET'for r in requests)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=str(OUT/f'production-abandonment-read-{width}.png'),full_page=True)
   results.append(dict(width=width,receipt=receipt,api_requests=requests,password_persistent=False,both_local_intents_resolved=True,horizontal_overflow=False))
   context.close()
  browser.close()
 report=dict(status='PASS',evidence='ACTUAL_PRODUCTION_UI_NATIVE_GET_ONLY',results=results,api_mutations=False,native_stock_writes=False,physical_hardware=False,native_receipt_operation=body['operation_id'])
 (OUT/'production-ui-read.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(dict(status='PASS',widths=[360,390,1440],api_mutations=False,physical_hardware=False)))


if __name__=='__main__':main()


