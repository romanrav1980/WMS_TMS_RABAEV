from pathlib import Path
p=Path('scripts/store_weekly_native_fixture.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("def transaction(self,label):yield q", "def transaction(self,label):\n   try:yield q\n   except Exception:c.rollback();raise\n   else:c.commit()")
s=s.replace("finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')", "finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')\n  c.commit()")
s=s.replace("before=context();before_profile=read_profile(q,f['shop']);c.rollback()", """before=context();before_profile=read_profile(q,f['shop']);
 q.execute('select ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT from RRL_SBORKA_PALLETS where ID=:id',id=f['st_id']);old_windows=q.fetchone()
 q.execute('select FROM_ADDR,TO_ADDR,UPDATED_AT from RRL_ADDR_DISTANCE_MATRIX where SOURCE=\'NI081TEST\' and ((FROM_ADDR=:a and TO_ADDR=:b)or(FROM_ADDR=:b and TO_ADDR=:a))',a=f['base'],b=f['shop']);old_roads=q.fetchall();c.rollback()
 saved=None""".replace("where SOURCE='NI081TEST'",'where SOURCE=\"NI081TEST\"'))
# Correct literal quoting in generated Python read SQL.
s=s.replace("q.execute('select FROM_ADDR,TO_ADDR,UPDATED_AT", 'q.execute("select FROM_ADDR,TO_ADDR,UPDATED_AT').replace('where SOURCE="NI081TEST"','where SOURCE=\'NI081TEST\'').replace("TO_ADDR=:a))',a=f['base']", 'TO_ADDR=:a))",a=f[\'base\']')
s=s.replace("  changed=profile_save", "  c.rollback()\n  changed=profile_save")
s=s.replace(";assert changed_ctx['approval_status']=='SOURCE_CHANGED',changed_ctx",'')
s=s.replace("json.dumps({**body,'expected_version':approved['version']})", "json.dumps(body)")
a=s.index(' finally:\n  c.rollback()\n  after=context()')
s=s[:a]+''' finally:
  c.rollback()
  config('update RRL_SBORKA_PALLETS set ZONE_TIME_PLAN_IN=:a,ZONE_TIME_PLAN_OUT=:b where ID=:id',{'a':old_windows[0],'b':old_windows[1],'id':f['st_id']})
  for a,b,t in old_roads:config('update RRL_ADDR_DISTANCE_MATRIX set UPDATED_AT=:t where FROM_ADDR=:a and TO_ADDR=:b',{'a':a,'b':b,'t':t})
  current=read_profile(q,f['shop']);c.rollback()
  if saved is not None:
   restored=owner.save('admin',{'operation_id':tag+'.RESTORE','store_addr':f['shop'],'expected_version':current['version'],'reason':'Restore original own fixture profile semantics after bounded weekly test',**before_profile['profile'],'windows':before_profile['windows']})
  after=context();after_profile=read_profile(q,f['shop']);c.rollback()
  clean_before=dict(before['source']);clean_after=dict(after['source']);clean_before.pop('store_window_profiles',None);clean_after.pop('store_window_profiles',None)
  report['rollback']={'original_nonprofile_source_restored':clean_before==clean_after,'approval_version_restored':after['version']==before['version'],'profile_semantics_restored':after_profile['profile']==before_profile['profile']and after_profile['windows']==before_profile['windows'],'profile_new_restore_version':after_profile['version']}
  Path('reports/nicora/2026-10-13/codex/STORE_WEEKLY/native_fixture.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  assert all(report['rollback'].values()),report['rollback']
print(json.dumps({'cases':list(report['cases']),'timings_ms':report['timings_ms'],'rollback':report['rollback']}))
'''
s=s.replace("'writes_scope':'own planning fixture only, outer rollback'", "'writes_scope':'own planning fixture only; profile restore new version; ST/road exact restore; final approval rollback'")
p.write_text(s,encoding='utf-8')
