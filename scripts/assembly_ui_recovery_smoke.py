"""Rendered assembly recovery checks with explicitly mocked HTTP, never native stock writes."""
import json
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='http://127.0.0.1:3010'
OUT=ROOT/'reports/retailcase/2026-10-15/assembly-ui-review'


def step(state='APPLIED'):
 return dict(step_id='old.step',session_id='original.session',operation_id='original.operation',sequence=1,case_line_id=11,article='SKU',quantity='1',state=state,confirmation_mode='BUTTON',content_version=2,before_capture_id='b',after_capture_id='a',before_weight_kg='.5',after_weight_kg='1.5',delta_kg='1',min_delta_kg='.1',expected_delta_min_kg='.99',expected_delta_max_kg='1.01',consent_to_auto=False,button_intent=False,block_reason=None,stock_posted=state=='APPLIED')


def session(state='OPEN',task=10):
 return dict(session_id='original.session',task_id=task,device_id='d',post_cell='p',operator_id='qa',warehouse_id=2,scan_container='carrier',state=state,confirmation_mode='BUTTON',content_version=3,tare_capture_key='A'*64,tare_weight_kg='.5',last_weight_kg='1.5',expires_at='2099-01-01T00:00:00+00:00',block_reason=None,steps=[step()])


def context(active=True,task=10):
 return dict(task_id=task,task_state='IN_PROGRESS',content_version=3,scan_container='carrier',warehouse_id=2,
  lines=[dict(case_line_id=11,article='SKU',name='Test SKU',remaining_quantity='4',base_uom='EA',policy_state='CONFIGURED',source_cell='SRC',product_codes=['SKU','EAN'])],
  stations=[dict(device_id='d',post_cell='p',confirmation_mode='BUTTON',device_mode='TEST',device_policy_version=1,calibration_ref='cal',tare_captures=[])],active_session=session(task=task)if active else None)


class Fixture:
 def __init__(self,browser,kind=None,wrong=False):
  self.ctx=browser.new_context(viewport={'width':420,'height':900});self.page=self.ctx.new_page();self.posts=[];self.state=session();self.active=True;self.read404=False;self.revoke=False;self.wrong=wrong;self.finals=[];self.task20=False;self.hold20=False;self.held=None;self.task_state="IN_PROGRESS";self.lines_closed=False
  if kind:
   body=dict(step_id='old.step',operation_id='original.operation',case_line_id=11,quantity='1',scan_source_cell='src',scan_product='SKU',scan_container='carrier',expected_content_version=2,consent_to_auto=False)if kind=='open_step'else dict(final_capture_key='F'*64)
   key=f'assembly-scale:{kind}:{ORIGIN}:qa:10';entry=dict(meta=dict(server=ORIGIN,actor='qa',task_id=10),body=dict(version=1,kind=kind,target_session='original.session',body=body),savedAt='2026-10-15T00:00:00Z')
   if kind=='case_close':body=dict(operation_id='original.close',expected_content_version=3);entry['body']['body']=body
   if kind=='open_session':body=dict(session_id='original.session',task_id=10,device_id='d',expected_content_version=3,tare_capture_key='A'*64,scan_container='carrier');entry['body']['body']=body
   self.saved_body=body;self.key=key
   self.page.add_init_script('localStorage.setItem('+json.dumps(key)+','+json.dumps(json.dumps(entry))+');')
   if kind=='open_session':self.active=False
   if kind=='finish':self.active=False;self.state=session('FINALIZED')
  self.page.route('**/api/**',self.route)
 def route(self,route):
  r=route.request;path=r.url.split(ORIGIN)[-1]
  def reply(data,status=200):route.fulfill(status=status,json=data)
  if path=='/api/terminal/auth/me':return reply(dict(username='qa',display_name='QA',user_group='NONE',permissions=[]))
  if '/context?'in path:
   task=20 if 'task_id=20'in path else 10
   if task==20:
    self.task20=True
    if self.hold20:self.held=route;return
   value=context(self.active,task);value['active_session']=deepcopy(self.state)if self.active else None
   value['task_state']=self.task_state
   if self.task_state=='WAIT_CONTROL':value.update(shipment_binding_state='BOUND',bound_pallet_identifier='ST',prepared_shipments=[],final_composition_signature='E'*64,final_signature_domain='ASM_FINAL',final_signature_version=3)
   if self.lines_closed:
    for line in value['lines']:line.update(status='PICKED',remaining_quantity='0')
   if value['active_session']:value['active_session']['task_id']=task
   return reply(value)
  if '/final-captures?'in path:return reply(dict(readings=self.finals))
  if r.method=='GET' and '/sessions/'in path:
   if self.read404:return reply({'detail':{'message':'not visible'}},404)
   if self.revoke:return reply({'detail':{'message':'revoked'}},403)
   return reply(self.state)
  if r.method=='POST':
   self.posts.append(dict(path=path,body=r.post_data_json))
   if path=='/api/inventory/assembly-scale/sessions':return reply(self.state)
   if path.endswith('/steps'):
    return reply({**step(),'session_id':'wrong'if self.wrong else 'original.session'})
   if path.endswith('/close'):
    self.task_state='WAIT_CONTROL';return reply(dict(session_id='original.session',case_pick_task_id=10,operation_id=r.post_data_json['operation_id']if not self.wrong else 'wrong',status='WAIT_CONTROL',content_version=3,already_closed=False,physical_stock_changed=False))
   if path.endswith('/finish'):return reply(self.state)
   if path.endswith('/placed'):
    self.state['steps']=[step('APPLIED')]
    return reply(dict(step=step('APPLIED'),posting={'status':'APPLIED'}))
  return reply({'detail':'not part of mocked scenario'},404)
 def login(self):
  self.page.goto(ORIGIN+'/assembly/?task_id=10')
  self.page.get_by_label('Логин',exact=True).fill('qa');self.page.get_by_label('Пароль',exact=True).fill('test-only')
  self.page.locator('[data-help-id="assembly.login.submit"]').click()
 def saved(self):return self.page.evaluate('(key)=>localStorage.getItem(key)',self.key)
 def close(self):self.ctx.close()


def main():
 OUT.mkdir(parents=True,exist_ok=True);checks=[]
 with sync_playwright()as pw:
  browser=pw.chromium.launch(headless=True)
  for kind in ('open_session','open_step','finish','case_close'):
   f=Fixture(browser,kind);f.login();expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_be_visible();assert not f.posts
   f.read404=True;f.page.locator('[data-help-id="assembly.recover-read"]').click();expect(f.page.get_by_text('Результат пока не виден.',exact=False)).to_be_visible();assert f.saved() and not f.posts
   f.read404=False;f.page.locator('[data-help-id="assembly.recover-retry"]').click()
   expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_have_count(0)
   expected_path='/api/inventory/assembly-scale/sessions'if kind=='open_session'else '/api/inventory/assembly-scale/sessions/original.session/'+('steps'if kind=='open_step'else 'close'if kind=='case_close'else'finish')
   assert f.posts==[dict(path=expected_path,body=f.saved_body)]
   assert f.saved()is None;checks.append(kind+'_reload_404_preserves_original_url_body_exact_retry_no_auto_post');f.close()
  f=Fixture(browser,'open_step',wrong=True);f.login();f.page.locator('[data-help-id="assembly.recover-retry"]').click()
  expect(f.page.get_by_text('Ответ сервера не соответствует',exact=False)).to_be_visible();assert f.saved();checks.append('wrong_ack_identity_keeps_journal_and_blocks_new_command');f.close()
  f=Fixture(browser);f.state['steps']=[step('ARMED')];f.revoke=True;f.login()
  expect(f.page.get_by_text('Данные не подтверждены:',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.placed"]')).to_have_count(0);checks.append('poll_403_marks_stale_and_disables_placement');f.close()
  f=Fixture(browser);f.state['steps']=[step('ARMED')];f.login();f.page.locator('[data-help-id="assembly.placed"]').click()
  expect(f.page.get_by_text('✓ Укладка подтверждена',exact=False)).to_be_visible();assert f.posts[0]['path'].endswith('/old.step/placed');checks.append('placed_real_envelope_unwrapped_and_session_reread');f.close()
  f=Fixture(browser);now=datetime.now(timezone.utc)
  candidate=dict(capture_key='F'*64,weight_kg='1.5',measured_at=now.isoformat(),purpose='FINAL_GROSS',case_task_id=10,scan_container='carrier',case_content_version=3,device_id='d',post_cell='p',tare_capture_key='A'*64,basis='GROSS',device_policy_version=1,calibration_ref='cal',device_mode='TEST',composition_signature='E'*64,signature_domain='ASM_FINAL',composition_signature_version=3,status='ARCHIVED',stock_posted=False)
  f.task_state='WAIT_CONTROL'
  f.finals=[candidate,{**candidate,'capture_key':'B'*64,'measured_at':(now-timedelta(minutes=5)).isoformat()},{**candidate,'capture_key':'C'*64,'tare_capture_key':'C'*64},{**candidate,'capture_key':'D'*64,'calibration_ref':'other'}]
  f.login();f.page.locator('[data-help-id="assembly.finish-open"]').click();expect(f.page.locator('[data-help-id="assembly.finish-pick"]')).to_have_count(1)
  f.page.locator('[data-help-id="assembly.finish-pick"]').click();expect(f.page.locator('[data-help-id="assembly.finish-confirm"]')).to_be_enabled()
  f.page.locator('[data-help-id="assembly.finish-reload"]').click();expect(f.page.locator('[data-help-id="assembly.finish-confirm"]')).to_be_disabled();checks.append('final_candidates_filter_age_tare_calibration_and_clear_selection_on_reload');f.close()
  f=Fixture(browser);f.hold20=True;f.login();expect(f.page.locator('.asm-header')).to_be_visible()
  f.page.locator('[data-help-id="assembly.task-id.change"]').click();f.page.get_by_label('Номер задания',exact=True).fill('20');f.page.locator('[data-help-id="assembly.task-id.open"]').click()
  expect(f.page.get_by_text('Загрузка задания 20',exact=False)).to_be_visible();expect(f.page.locator('.asm-header')).to_have_count(0);assert not f.posts
  value=context(True,20);f.held.fulfill(json=value);expect(f.page.get_by_text('Задание 20',exact=True)).to_be_visible();checks.append('task_switch_never_renders_old_context_while_new_request_pending');f.close()
  f=Fixture(browser,'open_step');f.page.add_init_script('localStorage.setItem('+json.dumps(f.key)+',"broken JSON")');f.login()
  expect(f.page.get_by_text('Сохранённая команда повреждена',exact=False)).to_be_visible();expect(f.page.locator('[data-help-id="assembly.start-step"]')).to_have_count(0);assert not f.posts;checks.append('damaged_journal_blocks_new_commands_without_discard');f.close()
  f=Fixture(browser);f.lines_closed=True;f.login();f.page.locator('[data-help-id="assembly.finish-open"]').click();f.page.locator('[data-help-id="assembly.case-close-submit"]').click()
  expect(f.page.get_by_text('Сборка закрыта сервером.',exact=False)).to_be_visible();assert f.posts[0]['path']=='/api/inventory/assembly-scale/sessions/original.session/close';assert f.posts[0]['body']['expected_content_version']==3
  expect(f.page.locator('[data-help-id="assembly.start-step"]')).to_have_count(0);checks.append('in_app_close_uses_owner_command_and_refreshes_case_state');f.close()
  f=Fixture(browser,'open_session');legacy=dict(meta=dict(server=ORIGIN,actor='qa',task_id=10),body=f.saved_body,savedAt='2026-10-15T00:00:00Z');f.page.add_init_script('localStorage.setItem('+json.dumps(f.key)+','+json.dumps(json.dumps(legacy))+')');f.login()
  f.page.locator('[data-help-id="assembly.recover-retry"]').click();expect(f.page.locator('[data-help-id="assembly.recover-retry"]')).to_have_count(0);assert f.posts[0]['body']==f.saved_body;checks.append('legacy_c0112_open_session_recovers_exact_original_body');f.close()
  f=Fixture(browser,'case_close',wrong=True);f.login();f.page.locator('[data-help-id="assembly.recover-retry"]').click();expect(f.page.get_by_text('Ответ сервера не соответствует',exact=False)).to_be_visible();assert f.saved();checks.append('close_wrong_operation_ack_preserves_original_intent');f.close()
  f=Fixture(browser);f.state['steps']=[step('CANCELLED')];f.state['steps'][0]['stock_posted']=False;f.login();expect(f.page.get_by_text('Шаг отменён после сверки.',exact=False)).to_be_visible();expect(f.page.get_by_text('✓ Укладка подтверждена',exact=False)).to_have_count(0);checks.append('cancelled_step_is_neutral_never_stock_success');f.close()
  f=Fixture(browser);f.login();expect(f.page.locator('[data-help-id="assembly.finish-open"]')).to_have_count(0);expect(f.page.get_by_text('В задании остаются незавершённые строки.',exact=False)).to_be_visible();assert not f.posts;checks.append('unfinished_lines_never_offer_invalid_close_command');f.close()
  f=Fixture(browser);f.login();f.page.locator('[data-help-id="assembly.line"]').click();f.page.locator('[data-help-id="assembly.quantity"]').fill('5');f.page.get_by_label('Ячейка источника',exact=True).fill('SRC');f.page.get_by_label('Товар',exact=True).fill('EAN');f.page.get_by_label('Сборочная тара (повторно)',exact=True).fill('carrier')
  expect(f.page.locator('[data-help-id="assembly.start-step"]')).to_be_disabled();f.page.locator('[data-help-id="assembly.quantity"]').fill('1');expect(f.page.locator('[data-help-id="assembly.start-step"]')).to_be_enabled()
  for field in ('Ячейка источника','Товар','Сборочная тара (повторно)'):
   input=f.page.get_by_label(field,exact=True);original=input.input_value();input.fill('wrong');expect(f.page.locator('[data-help-id="assembly.start-step"]')).to_be_disabled();input.fill(original)
  assert not f.posts;checks.append('server_remaining_source_product_and_carrier_preflight_before_journal');f.close()
  browser.close()
 result=dict(status='PASS',checks=checks,evidence='RENDERED_CHROMIUM_MOCKED_HTTP',native_mutations=False,physical_hardware=False)
 (OUT/'browser-report.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()









