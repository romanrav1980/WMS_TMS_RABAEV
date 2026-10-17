"""Rendered abandonment recovery using mocked HTTP only; no native mutations."""
import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright,expect
from assembly_ui_recovery_smoke import Fixture,ORIGIN
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/retailcase/2026-10-15/assembly-ui-review'


class AbandonFixture(Fixture):
 def __init__(self,browser,kind='open_step'):
  self.ledger={};self.abandon_posts=[];self.lose=False;self.get404=False;self.bad=None;self.refuse=False;self.original_refuse=False;self.denied=False
  super().__init__(browser,kind)
  self.control_key=f'assembly-scale:abandonment:{ORIGIN}:qa:10'
 def control(self):return self.page.evaluate('(key)=>localStorage.getItem(key)',self.control_key)
 def route(self,route):
  r=route.request;path=r.url.split(ORIGIN)[-1]
  if '/assembly-scale/abandonments'in path:
   if self.denied:return route.fulfill(status=403,json=dict(detail=dict(message='revoked current scope')))
   if r.method=='POST':
    body=r.post_data_json;self.abandon_posts.append(deepcopy(body))
    if self.refuse:return route.fulfill(status=409,json=dict(detail=dict(message='already created')))
    original=body['original'];ack=dict(operation_id=body['operation_id'],status='ABANDONED',kind=body['kind'],task_id=10,
     session_id=body.get('session_id',original.get('session_id')),step_id=original.get('step_id'),original_operation_id=original.get('operation_id'),original=original,stock_posted=False)
    self.ledger[body['operation_id']]=ack
    if self.lose:self.lose=False;return route.abort('connectionreset')
   else:
    if self.get404:return route.fulfill(status=404,json=dict(detail=dict(message='not visible')))
    ack=deepcopy(self.ledger.get(unquote(path.rsplit('/',1)[1])))
   if self.bad:self.bad(ack)
   return route.fulfill(json=ack)
  if self.original_refuse and r.method=='POST'and path.endswith('/steps'):
   return route.fulfill(status=409,json=dict(detail=dict(message='intent tombstoned')))
  return super().route(route)
 def begin(self):
  self.page.get_by_label('Причина отмены',exact=True).fill('Ошибка исходного сканирования')
  self.page.locator('[data-help-id="assembly.abandon.submit"]').click()


def main():
 OUT.mkdir(parents=True,exist_ok=True);checks=[]
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  for kind in ('open_session','open_step'):
   f=AbandonFixture(browser,kind);f.lose=True;f.login();f.begin()
   expect(f.page.get_by_text('Нет связи с сервером',exact=False)).to_be_visible()
   assert f.saved()and f.control()and len(f.abandon_posts)==1
   original=deepcopy(f.abandon_posts[0]);assert original['original']==f.saved_body
   f.login();expect(f.page.locator('[data-help-id="assembly.abandon.read"]')).to_be_visible();assert len(f.abandon_posts)==1
   f.get404=True;f.page.locator('[data-help-id="assembly.abandon.read"]').click()
   expect(f.page.get_by_text('Отмена пока не видна.',exact=False)).to_be_visible();assert f.saved()and f.control()and len(f.abandon_posts)==1
   f.page.locator('[data-help-id="assembly.abandon.submit"]').click()
   expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_have_count(0)
   assert f.abandon_posts==[original,original]and f.saved()is None and f.control()is None
   checks.append(kind+'_lost_abandon_ack_reload_get404_exact_retry_clears_only_verified_pair');f.close()
  for change in ('operation','session','original','stock','task'):
   f=AbandonFixture(browser)
   def bad(ack,change=change):
    if change=='operation':ack['operation_id']='foreign'
    elif change=='session':ack['session_id']='foreign'
    elif change=='original':ack['original']['quantity']='2'
    elif change=='stock':ack['stock_posted']=True
    else:ack['task_id']=20
   f.bad=bad;f.login();f.begin();expect(f.page.get_by_text('Отмена не подтверждает',exact=False)).to_be_visible()
   assert f.saved()and f.control();checks.append('wrong_abandon_ack_'+change+'_preserves_both');f.close()
  f=AbandonFixture(browser);f.lose=True;f.login();f.begin();expect(f.page.get_by_text('Нет связи с сервером',exact=False)).to_be_visible()
  f.page.evaluate('(key)=>localStorage.removeItem(key)',f.key)
  f.page.locator('[data-help-id="assembly.abandon.read"]').click()
  expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_have_count(0)
  assert f.saved()is None and f.control()is None;checks.append('crash_after_original_clear_control_read_recovers_pair');f.close()
  f=AbandonFixture(browser);f.refuse=True;f.login();f.begin();expect(f.page.get_by_text('Сервер не разрешил отмену',exact=False)).to_be_visible()
  assert f.saved()and f.control();f.page.locator('[data-help-id="assembly.recover-retry"]').click()
  expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_have_count(0)
  assert f.saved()is None and f.control()is None and f.posts[0]['body']==f.saved_body
  checks.append('already_created_refusal_resolves_only_by_frozen_original_success_ack');f.close()
  f=AbandonFixture(browser);f.lose=True;f.original_refuse=True;f.login();f.begin();expect(f.page.get_by_text('Нет связи с сервером',exact=False)).to_be_visible()
  f.page.locator('[data-help-id="assembly.recover-retry" ]').click();expect(f.page.get_by_text('intent tombstoned',exact=False)).to_be_visible()
  assert f.saved()and f.control();f.page.locator('[data-help-id="assembly.abandon.read" ]').click()
  expect(f.page.locator('[data-help-id="assembly.recover-retry" ]')).to_have_count(0)
  assert f.saved()is None and f.control()is None;checks.append('tombstoned_original_409_keeps_pair_until_exact_abandoned_read');f.close()
  for corrupt in ('foreign','broken'):
   f=AbandonFixture(browser);f.lose=True;f.login();f.begin();expect(f.page.get_by_text('Нет связи с сервером',exact=False)).to_be_visible()
   value=json.loads(f.control())
   if corrupt=='foreign':value['meta']['actor']='other'
   else:value['body']['request']['original']['quantity']='99'
   f.page.evaluate('([key,value])=>localStorage.setItem(key,value)',[f.control_key,json.dumps(value)])
   f.login();expect(f.page.locator('[data-help-id="assembly.abandon.submit"]')).to_have_count(0)
   assert len(f.abandon_posts)==1 and f.saved()and f.control();checks.append(corrupt+'_control_blocks_new_post_without_discard');f.close()
  f=AbandonFixture(browser);f.denied=True;f.login();f.begin();expect(f.page.get_by_text('Допуск изменён.',exact=False)).to_be_visible()
  expect(f.page.locator('[data-help-id="assembly.abandon.submit" ]')).to_be_disabled();expect(f.page.locator('[data-help-id="assembly.recover-retry" ]')).to_be_disabled()
  assert f.saved()and f.control();checks.append('current_scope_403_blocks_further_actions_keeps_both_journals');f.close()
  for kind in ('finish','case_close'):
   f=AbandonFixture(browser,kind);f.login();expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_be_visible()
   expect(f.page.locator('[data-help-id="assembly.abandon.submit"]')).to_have_count(0)
   assert not f.abandon_posts;checks.append(kind+'_has_no_unsupported_abandon_action');f.close()
  browser.close()
 report=dict(status='PASS',checks=checks,evidence='RENDERED_CHROMIUM_MOCKED_HTTP',native_mutations=False,physical_hardware=False)
 (OUT/'abandonment-browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=True))


if __name__=='__main__':main()



