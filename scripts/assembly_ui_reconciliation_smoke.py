"""Rendered operator HOLD/controller recovery; mocked HTTP, no Oracle writes."""
import base64
from copy import deepcopy
import json
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from assembly_ui_recovery_smoke import Fixture,ORIGIN,ROOT,session,step
OUT=ROOT/'reports/retailcase/2026-10-15/assembly-ui-review'


class RecoveryFixture(Fixture):
 def __init__(self,browser):
  super().__init__(browser);self.state['steps']=[step('DISCREPANCY')];self.state['state']='BLOCKED'
  self.recon=dict(reconciliation_id='recon.request',session_id='original.session',step_id='old.step',case_task_id=10,state='REQUESTED',requester_id='qa',controller_id=None,expected_weight_kg='.5',expected_content_version=3)
  self.hold_drop=False;self.auth_drop=False;self.recon404=False;self.wrong_ack=False;self.wrong_read=False;self.auth403=False
 def route(self,route):
  r=route.request;path=r.url.split(ORIGIN)[-1]
  if path=='/api/terminal/auth/me':
   actor=base64.b64decode(r.headers['authorization'].split()[1]).decode().split(':')[0]
   return route.fulfill(json=dict(username=actor,display_name=actor,user_group='NONE',permissions=['case_pick_manage']if actor=='controller'else[]))
  if path.endswith('/reconciliations')and r.method=='POST':
   body=r.post_data_json;self.posts.append(dict(path=path,body=body));assert 'unaccepted_goods_removed'not in body
   self.recon['reconciliation_id']=body['operation_id'];self.state['state']='BLOCKED';self.state['reconciliation']=deepcopy(self.recon)
   if self.hold_drop:self.hold_drop=False;return route.abort('failed')
   return route.fulfill(json=self.recon)
  if '/reconciliations/'in path and r.method=='GET':
   if self.auth403:return route.fulfill(status=403,json={'detail':{'message':'current permission revoked'}})
   if self.recon404:return route.fulfill(status=404,json={'detail':{'message':'not visible'}})
   return route.fulfill(json={**self.recon,'reconciliation_id':'foreign'if self.wrong_read else self.recon['reconciliation_id']})
  if path.endswith('/authorize')and r.method=='POST':
   body=r.post_data_json;self.posts.append(dict(path=path,body=body));assert body['unaccepted_goods_removed']is True
   self.recon.update(state='AUTHORIZED',controller_id='controller')
   if self.auth_drop:self.auth_drop=False;return route.abort('failed')
   return route.fulfill(json={**self.recon,'operation_id':'wrong'if self.wrong_ack else body['operation_id']})
  return super().route(route)
 def controller_login(self,actor='controller',reload=False):
  if not reload:self.page.goto(ORIGIN+'/assembly/?reconciliation_id=recon.request')
  self.page.get_by_label('Логин',exact=True).fill(actor);self.page.get_by_label('Пароль',exact=True).fill('test-only');self.page.locator('[data-help-id="assembly.login.submit"]').click()
 def authorize_fill(self):
  self.page.locator('[data-help-id="assembly.recovery.controller-reason"]').fill('Проверка удаления непринятого товара')
  expect(self.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_be_disabled()
  self.page.locator('[data-help-id="assembly.recovery.removed"]').check()
 def auth_key(self):return f'assembly-scale:recovery_authorize:{ORIGIN}:controller:10'


def main():
 checks=[];OUT.mkdir(parents=True,exist_ok=True)
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  f=RecoveryFixture(browser);f.state['state']='OPEN';f.state['steps']=[step('ARMED')];f.hold_drop=True;f.login()
  expect(f.page.get_by_text('Теперь уберите только непринятый',exact=False)).to_have_count(0)
  f.page.locator('[data-help-id="assembly.recovery.reason"]').fill('Неожиданный товар на весах')
  f.page.locator('[data-help-id="assembly.recovery.request"]').click()
  expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_be_visible();expect(f.page.get_by_text('Теперь уберите только непринятый',exact=False)).to_have_count(0)
  original=deepcopy(f.posts[0]);f.page.reload();f.login()
  expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_be_visible();assert len(f.posts)==1
  f.page.locator('[data-help-id="assembly.recover-retry"]').click()
  expect(f.page.get_by_text('Теперь уберите только непринятый',exact=False)).to_be_visible();assert f.posts==[original,original]
  expect(f.page.locator('[data-help-id="assembly.recovery.controller-link"]')).to_have_attribute('href','/assembly/?reconciliation_id='+quote(original['body']['operation_id'],safe=''))
  expect(f.page.locator('[data-help-id="assembly.placed"]')).to_have_count(0)
  f.page.screenshot(path=str(OUT/'recovery-hold-mocked-http.png'),full_page=True);checks.append('operator_hold_ack_before_removal_lost_response_reload_exact_retry_no_flag');f.close()
  f=RecoveryFixture(browser);f.controller_login('qa');expect(f.page.get_by_text('Оператор этой заявки не может',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_be_disabled();assert not f.posts;checks.append('requester_cannot_self_authorize_or_get_admin_password_prompt');f.close()
  f=RecoveryFixture(browser);f.auth_drop=True;f.controller_login();f.authorize_fill();f.page.locator('[data-help-id="assembly.recovery.authorize"]').click()
  expect(f.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_have_text('Повторить ту же отправку');original=deepcopy(f.posts[0]);assert f.page.evaluate('(k)=>localStorage.getItem(k)',f.auth_key())
  f.recon404=True;f.page.reload();f.controller_login(reload=True)
  expect(f.page.get_by_text('not visible',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_be_enabled();assert len(f.posts)==1
  f.recon404=False;f.page.locator('[data-help-id="assembly.recovery.authorize"]').click();expect(f.page.get_by_text('Подтверждение сохранено.',exact=False)).to_be_visible();assert f.posts==[original,original]
  assert f.page.evaluate('(k)=>localStorage.getItem(k)',f.auth_key())is None;checks.append('controller_exact_auth_reload_404_keeps_original_snapshot_and_body');f.close()
  f=RecoveryFixture(browser);f.wrong_ack=True;f.controller_login();f.authorize_fill();f.page.locator('[data-help-id="assembly.recovery.authorize"]').click()
  expect(f.page.get_by_text('Ответ не подтверждает исходную сверку.',exact=False)).to_be_visible();assert f.page.evaluate('(k)=>localStorage.getItem(k)',f.auth_key());checks.append('wrong_authorization_operation_ack_never_clears_intent');f.close()
  f=RecoveryFixture(browser);f.wrong_read=True;f.controller_login();expect(f.page.get_by_text('Ответ не подтверждает исходную сверку.',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_have_count(0);assert not f.posts;checks.append('foreign_reconciliation_read_cannot_enable_authorization');f.close()
  f=RecoveryFixture(browser);f.auth403=True;f.controller_login();expect(f.page.get_by_text('current permission revoked',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.recovery.authorize"]')).to_have_count(0);assert not f.posts;checks.append('controller_current_scope_denial_blocks_new_actions');f.close()
  for width in (360,390,1440):
   f=RecoveryFixture(browser);f.page.set_viewport_size({'width':width,'height':900});f.controller_login();expect(f.page.locator('[data-help-id="assembly.recovery.controller-reason"]')).to_be_visible()
   assert f.page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),width
   if width==390:f.page.screenshot(path=str(OUT/'controller-390-mocked-http.png'),full_page=True)
   f.close()
  checks.append('controller_recovery_responsive_360_390_1440_no_horizontal_overflow')
  browser.close()
 report=dict(status='PASS',checks=checks,evidence='RENDERED_CHROMIUM_MOCKED_HTTP',native_mutations=False,physical_hardware=False)
 (OUT/'reconciliation-browser-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()


