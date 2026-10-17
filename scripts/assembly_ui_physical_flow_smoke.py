"""Rendered warehouse request/bind recovery and physical instruction checks; HTTP mocked, no Oracle writes."""
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from copy import deepcopy
from playwright.sync_api import sync_playwright,expect
from assembly_ui_recovery_smoke import Fixture,ORIGIN,context
OUT=Path(__file__).resolve().parents[1]/'reports/retailcase/2026-10-15/assembly-ui-review'
class ScaleFixture(Fixture):
 def __init__(self,browser,active=False):
  self.intent=None;self.weigh_posts=[];self.lose=False;self.not_found=False;self.denied=False;self.bad=False;self.stage='REQUESTED';self.expiry=None;self.bound=False;self.bind_posts=[];self.bind_lost=False
  super().__init__(browser);self.active=active
  if active:self.task_state='WAIT_CONTROL';self.lines_closed=True
  self.weigh_key=f'assembly-scale:warehouse_weigh:{ORIGIN}:qa:10';self.bind_key=f'assembly-scale:shipment_bind:{ORIGIN}:qa:10'
 def current(self):
  now=datetime.now(timezone.utc)+timedelta(days=10000)
  value=dict(request_id=self.intent['request_id'],device_id='wrong'if self.bad else'd',purpose=self.intent['purpose'],case_task_id=10,state=self.stage,current_context='CURRENT',capture_key=None,claim_id='claim'if self.stage=='CLAIMED'else None,stock_posted=False,zero_progress_required=True,measurement_stage='ZERO_CONFIRMED'if self.expiry else'WAITING_ZERO',load_allowed=bool(self.expiry),claim_expires_at=self.expiry.isoformat()if self.expiry else None,server_now=now.isoformat(),zero_source_sha256='B'*64 if self.expiry else None,zero_confirmed_at=now.isoformat()if self.expiry else None)
  if self.stage=='CAPTURED':value.update(capture_key='C'*64,claim_id='claim',measurement_stage='CAPTURED',load_allowed=False)
  return value
 def route(self,route):
  r=route.request;path=r.url.split(ORIGIN)[-1]
  if '/help/articles/'in path:return route.fulfill(json=dict(article_id=path.rsplit('/',1)[1],title='Local knowledge',summary='Published fixture',body='Weighing steps',revision=7,related=[dict(article_id='scanner',title='Scanner'),dict(article_id='scales',title='Scales')]))
  if '/context?'in path:
   value=context(self.active);value.update(active_session=deepcopy(self.state)if self.active else None,task_state=self.task_state,resource_session_id=54,shipment_binding_state='BOUND'if self.bound else'REQUIRED',bound_pallet_identifier='ST'if self.bound else None,prepared_shipments=[dict(pallet_identifier='ST',shipment_id=20,fulfillment_id=30,state='PLANNED')],final_signature_domain='ASM_FINAL'if self.bound else None,final_signature_version=3 if self.bound else None,final_composition_signature='E'*64 if self.bound else None)
   if self.lines_closed:
    for line in value['lines']:line.update(status='PICKED',remaining_quantity='0')
   return route.fulfill(json=value)
  if '/warehouse-scales/requests'in path:
   if self.denied:return route.fulfill(status=403,json={'detail':'revoked'})
   if r.method=='POST':
    self.intent=r.post_data_json;self.weigh_posts.append(deepcopy(self.intent))
    if self.lose:self.lose=False;return route.abort('connectionreset')
   if self.not_found:return route.fulfill(status=404,json={'detail':'not visible'})
   return route.fulfill(json=self.current())
  if path.endswith('/bind-shipment'):
   self.bind_posts.append(r.post_data_json);self.bound=True
   if self.bind_lost:self.bind_lost=False;return route.abort('connectionreset')
   return route.fulfill(json=dict(case_pick_task_id=10,pallet_identifier='ST',status='BOUND',fulfillment_status='PICKED',idempotent=True))
  return super().route(route)
 def request_empty(self):
  self.page.get_by_label('Идентификатор паллеты / сборочной тары',exact=True).fill('carrier');self.page.locator('[data-help-id="assembly.empty-request"]').click()
 def saved_weight(self):return self.page.evaluate('(key)=>localStorage.getItem(key)',self.weigh_key)
 def zero(self,seconds=4):self.stage='CLAIMED';self.expiry=datetime.now(timezone.utc)+timedelta(days=10000,seconds=seconds)


def weigh_checks(browser,checks):
 f=ScaleFixture(browser);f.lose=True;f.login();f.request_empty();expect(f.page.locator('[data-help-id="assembly.weigh-retry"]')).to_be_visible();assert f.saved_weight();original=f.weigh_posts[0]
 assert original['zero_progress_required']is True and original['resource_session_id']==54 and original['scan_container']=='carrier'
 f.not_found=True;f.login();expect(f.page.get_by_text('Результат пока не виден.',exact=False)).to_be_visible();assert len(f.weigh_posts)==1 and f.saved_weight()
 f.not_found=False;f.page.locator('[data-help-id="assembly.weigh-retry"]').click();f.page.wait_for_timeout(150);assert f.weigh_posts==[original,original];checks.append('lost_empty_ack_reload_get404_exact_body_no_auto_post');f.close()
 f=ScaleFixture(browser);f.login();f.request_empty();f.zero(4);f.page.locator('[data-help-id="assembly.weigh-read"]').click();expect(f.page.locator('.asm-weigh-go')).to_be_visible();assert len(f.weigh_posts)==1
 f.page.evaluate("window.dispatchEvent(new Event('offline'))");expect(f.page.locator('.asm-weigh-go')).to_have_count(0);checks.append('server_clock_far_from_pc_still_valid_zero_then_offline_hides_instruction');f.close()
 f=ScaleFixture(browser);f.login();f.request_empty();f.zero(1.5);f.page.locator('[data-help-id="assembly.weigh-read"]').click();expect(f.page.locator('.asm-weigh-go')).to_be_visible();f.page.wait_for_timeout(1700);expect(f.page.locator('.asm-weigh-go')).to_have_count(0);checks.append('claim_ttl_expires_without_poll_response_no_timezone_dependency');f.close()
 f=ScaleFixture(browser);f.login();f.request_empty();f.zero(10);f.page.locator('[data-help-id="assembly.weigh-read"]').click();expect(f.page.locator('.asm-weigh-go')).to_be_visible();f.denied=True;f.page.locator('[data-help-id="assembly.weigh-read"]').click();expect(f.page.locator('[data-help-id="assembly.weigh-retry"]')).to_be_disabled();expect(f.page.locator('.asm-weigh-go')).to_have_count(0);assert f.saved_weight();checks.append('revoked_sender_operator_poll_disables_physical_instruction_preserves_intent');f.close()
 for mode in ['null','foreign']:
  f=ScaleFixture(browser);meta=dict(server=ORIGIN,actor='other'if mode=='foreign'else'qa',task_id=10);value=dict(meta=meta,body=None,savedAt='now');f.page.add_init_script('localStorage.setItem('+json.dumps(f.weigh_key)+','+json.dumps(json.dumps(value))+');');f.login();f.page.get_by_label('Идентификатор паллеты / сборочной тары',exact=True).fill('carrier');expect(f.page.locator('[data-help-id="assembly.empty-request"]')).to_be_disabled();assert f.saved_weight()and not f.weigh_posts;checks.append(mode+'_physical_journal_blocks_new_request');f.close()
 f=ScaleFixture(browser);f.bad=True;f.login();f.request_empty();expect(f.page.get_by_text('Ответ весов не подтверждает',exact=False)).to_be_visible();assert f.saved_weight();checks.append('wrong_weigh_ack_identity_preserves_original_request');f.close()


def bind_checks(browser,checks):
 f=ScaleFixture(browser,True);f.bind_lost=True;f.login();f.page.locator('[data-help-id="assembly.finish-open"]').click();f.page.get_by_label('Идентификатор паллеты / полной сборочной тары',exact=True).fill('carrier');f.page.get_by_label('Подготовленная отгрузка',exact=True).select_option('ST');f.page.locator('[data-help-id="assembly.bind-submit"]').click();expect(f.page.locator('[data-help-id="assembly.bind-read"]')).to_be_visible();f.page.wait_for_timeout(200);original=f.bind_posts[0]
 f.login();expect(f.page.locator('[data-help-id="assembly.bind-read"]')).to_have_count(0);assert f.bind_posts==[original];checks.append('lost_bind_ack_reload_get_context_proves_exact_binding_no_auto_post');f.close()
 f=ScaleFixture(browser,True);f.bound=True;f.login();f.page.locator('[data-help-id="assembly.finish-open"]').click();f.page.get_by_label('Идентификатор паллеты / полной сборочной тары',exact=True).fill('carrier');f.page.locator('[data-help-id="assembly.final-request"]').click();expect(f.page.locator('[data-help-id="assembly.weigh-retry"]')).to_be_visible();body=f.weigh_posts[0];assert body['purpose']=='FINAL_GROSS'and body['expected_composition_signature']=='E'*64 and body['tare_capture_key']=='A'*64 and'resource_session_id'not in body;checks.append('final_request_current_asm_domain_signature_same_tare_no_resource_override');f.close()


def layout_checks(browser,checks):
 for width in [360,390,1440]:
  f=ScaleFixture(browser);f.page.set_viewport_size(dict(width=width,height=900));f.login()
  missing=f.page.locator('button,a,input,select,textarea').evaluate_all("nodes=>nodes.filter(n=>n.getClientRects().length && (!n.title || !n.dataset.helpId)).map(n=>n.outerHTML)")
  assert not missing,missing
  assert f.page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  f.page.locator('[data-help-id$=".help"]').click();expect(f.page.locator('[data-help-id="help.related"]')).to_have_count(2);f.page.locator('[data-help-id="help.close"]').click()
  f.page.screenshot(path=str(OUT/f'physical-setup-{width}.png'),full_page=True);checks.append(f'layout_{width}_tooltips_localhelp_nooverflow');f.close()
 f=ScaleFixture(browser);f.task_state='CANCELLED';f.login();expect(f.page.locator('[data-help-id="assembly.empty-request"]')).to_have_count(0);expect(f.page.locator('[data-help-id="assembly.open-session"]')).to_have_count(0);assert not f.weigh_posts;checks.append('cancelled_without_open_session_readonly_no_new_weight_or_session');f.close()
 f=ScaleFixture(browser);f.login();f.request_empty();f.page.wait_for_timeout(150);f.stage='CAPTURED';f.page.wait_for_timeout(2200);expect(f.page.locator('[data-help-id="assembly.weigh-retry"]')).to_have_count(0);assert f.saved_weight()is None and len(f.weigh_posts)==1;checks.append('strict_captured_identity_resolves_request_get_without_extra_post');f.close()


def main():
 OUT.mkdir(parents=True,exist_ok=True);checks=[]
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True);weigh_checks(browser,checks);bind_checks(browser,checks);layout_checks(browser,checks);browser.close()
 report=dict(status='PASS',checks=checks,evidence='RENDERED_CHROMIUM_MOCKED_HTTP',native_mutations=False,physical_hardware=False);(OUT/'physical-flow-browser-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
