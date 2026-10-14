exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select s.CUSTOMER_ORDER_ID,s.RAW_XML,c.WARE_ID,m.STORE_CODE,cal.UTC_OFFSET_MINUTES
 from RRL_SAP_STORE_ORDER s join RRL_CUSTOMER_ORDER c on c.CUSTOMER_ORDER_ID=s.CUSTOMER_ORDER_ID
 join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID
 join RRL_SAP_STORE_CALENDAR cal on cal.WARE_ID=c.WARE_ID and cal.CUSTOMER_STORE_MAP_ID=m.CUSTOMER_STORE_MAP_ID
 where m.ACTIVE=1 and m.CREATED_AT<sysdate-8
 order by s.CUSTOMER_ORDER_ID fetch first 1 rows only""");row=q.fetchone();assert row,"No original old-enough map sourcebook"
 Path("tmp/source264_fixture.json").write_text(json.dumps({"source_order":row[0],"raw_xml":row[1].read(),"ware":row[2],"store":row[3],"offset":row[4]},ensure_ascii=True),encoding="utf-8")
 print("Original_source264",row[0],"Ware",row[2],"UTCOffset",row[4])
