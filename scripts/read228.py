exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select b.ST_ID,b.ST_IDENTIFIER,b.FINAL_ADDRESS,p.ADDR,p.ST_NUMBER,p.TRANSTASK_ID from RRL_INTERWARE_ONWARD_BIND b join RRL_SBORKA_PALLETS p on p.ID=b.ST_ID where b.OPERATION_ID='IW228.ONWARD:13508027ed'");print(q.fetchall())
 q.execute("select v.ID,v.TR_TYPE,v.GIDROBORT,v.MAX_WEIGHT_KG,v.PALLETS from RRL_TR_VEHICLE v where v.ID=(select VEHICLE_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID='IW225.LOAD:13508027ed')");print(q.fetchall())
 q.execute("select ADDR,TRANSPORT_TYPE,STOL,MAX_VEHICLE_TONS from RRL_ADDR where ADDR='Own full-pallet ST'");print(q.fetchall())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_RULES'and TYPE='PACKAGE BODY'and LINE between 25 and 39 order by LINE");print(''.join(r[0]for r in q.fetchall()))
