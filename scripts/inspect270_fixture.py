exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for label,sql in [
 ("vehicle","select ID,NUM,TR_TYPE,MAX_WEIGHT_KG,PALLETS,WORKING_NOW,BLOCKED from RRL_TR_VEHICLE where ID=10059"),
 ("pending","select ID,ST_NUMBER,WARE_ID,CONDITION,TRANSTASK_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=33541 order by ID"),
 ("article","select a.ACTICUL,a.NAME,a.BARCODE_SHT,a.COUNT_SHT_IN_KOR,a.BRUTTO_WEIGHT_OF_KOR,a.DIMKOR_X*a.DIMKOR_Y*a.DIMKOR_Z,a.TYPE_W,a.CELL from RRL_ARTICULS a where a.ACTICUL='QPOOL2e9b6614d9'"),
 ("add_args","select OBJECT_NAME,ARGUMENT_NAME,POSITION,DATA_TYPE from USER_ARGUMENTS where OBJECT_NAME in('RRL_TT_ADD','RRL_SBORKA_PALLETS_ADD2','RRL_SBORKA_PALLET_ROWS_ADD4')and PACKAGE_NAME is null order by OBJECT_NAME,SEQUENCE")]:
  q.execute(sql);print(label,json.dumps(q.fetchall(),default=str,ensure_ascii=True))
