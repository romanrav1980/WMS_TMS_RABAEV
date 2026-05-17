prompt [seed 2026-05-17-012] WMS/MES test warehouses - apply

declare
  type t_item is record (
    articul varchar2(40),
    name varchar2(255),
    unit_type varchar2(20),
    qty number,
    cell varchar2(20),
    shelf_life_days number,
    pallet_qty number
  );
  type t_items is table of t_item;

  v_items t_items := t_items(
    t_item('RM-MEAT-BEEF-FROZ-01', 'Говядина замороженная блочная 20 кг', 'KG', 1200, 'RM-A01-01', 180, 200),
    t_item('RM-MEAT-BEEF-TRIM-02', 'Обрезь говяжья замороженная', 'KG', 900, 'RM-A01-02', 180, 150),
    t_item('RM-MEAT-CHICK-FIL-03', 'Куриное филе замороженное', 'KG', 1500, 'RM-A01-03', 180, 250),
    t_item('RM-MEAT-CHICK-MDM-04', 'ММО куриное замороженное', 'KG', 1100, 'RM-A01-04', 120, 220),
    t_item('RM-MEAT-TURKEY-05', 'Индейка замороженная', 'KG', 800, 'RM-A01-05', 180, 160),
    t_item('RM-MEAT-LAMB-06', 'Баранина замороженная', 'KG', 600, 'RM-A02-01', 180, 120),
    t_item('RM-MEAT-PORK-07', 'Свинина замороженная', 'KG', 700, 'RM-A02-02', 180, 140),
    t_item('RM-MEAT-LIVER-BEEF-08', 'Печень говяжья замороженная', 'KG', 500, 'RM-A02-03', 120, 100),
    t_item('RM-MEAT-HEART-BEEF-09', 'Сердце говяжье замороженное', 'KG', 450, 'RM-A02-04', 120, 90),
    t_item('RM-MEAT-FISH-SALM-10', 'Рыба лососевая замороженная', 'KG', 650, 'RM-A02-05', 120, 130),
    t_item('RM-MEAT-FISH-WHITE-11', 'Рыба белая замороженная', 'KG', 720, 'RM-A03-01', 120, 144),
    t_item('RM-MEAT-DUCK-12', 'Утка замороженная', 'KG', 530, 'RM-A03-02', 180, 106),
    t_item('RM-FAT-CHICKEN-13', 'Жир куриный замороженный', 'KG', 400, 'RM-A03-03', 120, 80),
    t_item('RM-FAT-BEEF-14', 'Жир говяжий замороженный', 'KG', 350, 'RM-A03-04', 120, 70),
    t_item('RM-BROTH-FROZ-15', 'Бульон мясной замороженный', 'KG', 300, 'RM-A03-05', 90, 60),
    t_item('RM-PACK-PAUCH-85-16', 'Пакет пауч 85 г', 'PCS', 50000, 'RM-B01-01', 720, 10000),
    t_item('RM-PACK-PAUCH-100-17', 'Пакет пауч 100 г', 'PCS', 45000, 'RM-B01-02', 720, 9000),
    t_item('RM-PACK-CAN-340-18', 'Банка жестяная 340 г', 'PCS', 22000, 'RM-B01-03', 720, 4400),
    t_item('RM-PACK-CAN-415-19', 'Банка жестяная 415 г', 'PCS', 18000, 'RM-B01-04', 720, 3600),
    t_item('RM-PACK-LID-20', 'Крышка консервная', 'PCS', 25000, 'RM-B01-05', 720, 5000),
    t_item('RM-PACK-LABEL-21', 'Этикетка кормовая универсальная', 'PCS', 60000, 'RM-B02-01', 720, 12000),
    t_item('RM-PACK-BOX-S-22', 'Короб гофро малый', 'PCS', 9000, 'RM-B02-02', 720, 1800),
    t_item('RM-PACK-BOX-M-23', 'Короб гофро средний', 'PCS', 8000, 'RM-B02-03', 720, 1600),
    t_item('RM-PACK-STRETCH-24', 'Пленка стрейч паллетная', 'KG', 240, 'RM-B02-04', 720, 48),
    t_item('RM-PACK-PALLET-25', 'Поддон деревянный EUR', 'PCS', 600, 'RM-B02-05', 720, 120),
    t_item('RM-ADD-VIT-MIX-26', 'Витаминно-минеральная смесь', 'KG', 180, 'RM-C01-01', 365, 36),
    t_item('RM-ADD-TAURINE-27', 'Таурин кормовой', 'KG', 90, 'RM-C01-02', 365, 18),
    t_item('RM-ADD-FIBER-28', 'Клетчатка кормовая', 'KG', 260, 'RM-C01-03', 365, 52),
    t_item('RM-ADD-SAUCE-29', 'Соус желирующий кормовой', 'KG', 500, 'RM-C01-04', 180, 100),
    t_item('RM-ADD-SALT-30', 'Соль пищевая кормовая', 'KG', 300, 'RM-C01-05', 720, 60)
  );

  procedure upsert_ware(p_id number, p_name varchar2, p_prefix varchar2, p_order number) is
  begin
    merge into RRL_WARES d
    using (
      select p_id ID,
             substr(p_name, 1, 50) NAME,
             p_prefix PREFIX,
             p_order ORD2
        from dual
    ) s
    on (d.ID = s.ID)
    when matched then update set
      d.NAME = s.NAME,
      d.PREFIX = s.PREFIX,
      d.OVERFLOW_CELL_NAME = 'OVERFLOW',
      d.ORD2 = s.ORD2,
      d.MES_ENABLED = 1
    when not matched then insert (
      ID, NAME, OVERFLOW_CELL_NAME, PREFIX, FAKE_ROWS, FAKE_ART,
      BLOCK_IF_NO_PROOVE, VERIFY_VYCHERK, ALLOW_HALF_VYCHERK, ORD2
    ) values (
      s.ID, s.NAME, 'OVERFLOW', s.PREFIX, 0, 'Z0001',
      0, 0, 1, s.ORD2
    );
  end;

  procedure upsert_cell(
    p_cell varchar2,
    p_ware_id number,
    p_x number,
    p_y number,
    p_z number,
    p_system number default 0
  ) is
  begin
    merge into RRL_CELLS d
    using (
      select p_cell CELL,
             p_ware_id WARE_ID,
             p_x X,
             p_y Y,
             p_z Z,
             p_system IS_SYSTEM
        from dual
    ) s
    on (d.CELL = s.CELL)
    when matched then update set
      d.WARE_ID = s.WARE_ID,
      d.X = s.X,
      d.Y = s.Y,
      d.Z = s.Z,
      d.OTBOR = 0,
      d.BLOCKED_FOR_REMAINS = 0,
      d.BLOCKED_FOR_POPOLNENIE = 0,
      d.BLOCKED_FOR_ACCEPT = 0,
      d.IS_SYSTEM = s.IS_SYSTEM,
      d.LAST_TIME_OF_UPDATE = sysdate
    when not matched then insert (
      CELL, WARE_ID, X, Y, Z, OTBOR, BLOCKED_FOR_REMAINS,
      BLOCKED_FOR_POPOLNENIE, BLOCKED_FOR_ACCEPT, IS_SYSTEM,
      LAST_TIME_OF_UPDATE, LIMIT_WEIGHT, LIMIT_HEIGHT
    ) values (
      s.CELL, s.WARE_ID, s.X, s.Y, s.Z, 0, 0,
      0, 0, s.IS_SYSTEM, sysdate, 100000, 2500
    );
  end;

  procedure upsert_articul(p_item t_item) is
  begin
    merge into RRL_ARTICULS d
    using (
      select p_item.articul ACTICUL,
             p_item.name NAME,
             p_item.unit_type UNIT_TYPE,
             p_item.cell CELL,
             p_item.shelf_life_days BESTBEFOREDAYS
        from dual
    ) s
    on (d.ACTICUL = s.ACTICUL)
    when matched then update set
      d.NAME = s.NAME,
      d.UNIT_TYPE = s.UNIT_TYPE,
      d.CELL = s.CELL,
      d.BESTBEFOREDAYS = s.BESTBEFOREDAYS,
      d.BARCODE_SHT = nvl(d.BARCODE_SHT, '777')
    when not matched then insert (
      ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
      WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
      PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS,
      ABC_GROUP, XYZ_GROUP
    ) values (
      s.ACTICUL, 1, s.CELL, s.NAME, s.UNIT_TYPE, '777',
      1, 10, 5, 1, 1, 0, 100, s.BESTBEFOREDAYS, 'B', 'Y'
    );
  end;

  procedure seed_pallet(p_item t_item, p_idx number) is
    v_uid varchar2(200);
    v_event_id number;
  begin
    v_uid := 'SEED-RM-' || lpad(p_idx, 2, '0') || '-' || p_item.articul;

    merge into RRL_PALLETS d
    using (
      select v_uid UID_PALLET,
             p_item.articul ARTICUL,
             p_item.pallet_qty UNIT_COUNT,
             trunc(sysdate) CREATION_DATE,
             trunc(sysdate) + p_item.shelf_life_days EXPIRY_DATE
        from dual
    ) s
    on (d.UID_PALLET = s.UID_PALLET)
    when matched then update set
      d.ARTICUL = s.ARTICUL,
      d.UNIT_COUNT = s.UNIT_COUNT,
      d.CREATION_DATE = s.CREATION_DATE,
      d.PRODUCED_DATE = s.CREATION_DATE,
      d.EXPIRY_DATE = s.EXPIRY_DATE,
      d.QUALITY_STATUS = 'RELEASED'
    when not matched then insert (
      UID_PALLET, ARTICUL, CREATION_DATE, PRODUCED_DATE, EXPIRY_DATE,
      UNIT_COUNT, PRIHOD_NAKLAD_ID, PRINTED, KLADOVSHIK, QUALITY_STATUS
    ) values (
      s.UID_PALLET, s.ARTICUL, s.CREATION_DATE, s.CREATION_DATE, s.EXPIRY_DATE,
      s.UNIT_COUNT, 0, 0, 'SEED', 'RELEASED'
    );

    select RRL_EVENT_ID_SQ.nextval into v_event_id from dual;

    insert into RRL_EVENTS (
      ID_EVENT, CELL_FROM, CELL_TO, DATE_EVENT, COUNT_EVENT,
      TYPE_EVENT, UID_POLETA, USER_ID
    ) values (
      v_event_id, 'SEED', p_item.cell, sysdate, p_item.pallet_qty,
      1, v_uid, 'MESSEED'
    );
  end;
begin
  upsert_ware(9101, 'TEST RAW MATERIAL', 'TRM', 10);
  upsert_ware(9102, 'TEST PRODUCTION', 'TPR', 20);
  upsert_ware(9103, 'TEST PRODUCTION BUFFER', 'TBF', 30);
  upsert_ware(9104, 'TEST FINISHED GOODS', 'TFG', 40);

  update RRL_WARES
     set MES_ENABLED = 1,
         FLAG_RAW_MATERIAL = 1,
         FLAG_PRODUCTION = 0,
         FLAG_PRODUCTION_BUFFER = 0,
         FLAG_FINISHED_GOODS = 0,
         DEFAULT_RECEIVE_CELL = 'RM-A01-01',
         DEFAULT_ISSUE_CELL = 'RM-A01-01',
         WARE_COMMENT = 'Тестовый склад сырья: мясо, упаковка, добавки'
   where ID = 9101;

  update RRL_WARES
     set MES_ENABLED = 1,
         FLAG_RAW_MATERIAL = 0,
         FLAG_PRODUCTION = 1,
         FLAG_PRODUCTION_BUFFER = 0,
         FLAG_FINISHED_GOODS = 0,
         DEFAULT_RECEIVE_CELL = 'MES_PROD',
         DEFAULT_ISSUE_CELL = 'MES_PROD',
         WARE_COMMENT = 'Тестовая производственная зона для выдачи и списания сырья'
   where ID = 9102;

  update RRL_WARES
     set MES_ENABLED = 1,
         FLAG_RAW_MATERIAL = 0,
         FLAG_PRODUCTION = 0,
         FLAG_PRODUCTION_BUFFER = 1,
         FLAG_FINISHED_GOODS = 0,
         DEFAULT_RECEIVE_CELL = 'MES_FG',
         DEFAULT_ISSUE_CELL = 'MES_FG',
         WARE_COMMENT = 'Буфер сразу после выпуска до размещения на склад готовой продукции'
   where ID = 9103;

  update RRL_WARES
     set MES_ENABLED = 1,
         FLAG_RAW_MATERIAL = 0,
         FLAG_PRODUCTION = 0,
         FLAG_PRODUCTION_BUFFER = 0,
         FLAG_FINISHED_GOODS = 1,
         DEFAULT_RECEIVE_CELL = 'FG-A01-01',
         DEFAULT_ISSUE_CELL = 'FG-A01-01',
         WARE_COMMENT = 'Стеллажный склад готовой продукции'
   where ID = 9104;

  for i in 1 .. 5 loop
    upsert_cell('RM-A01-0' || i, 9101, 1, i, 1);
    upsert_cell('RM-A02-0' || i, 9101, 2, i, 1);
    upsert_cell('RM-A03-0' || i, 9101, 3, i, 1);
    upsert_cell('RM-B01-0' || i, 9101, 4, i, 1);
    upsert_cell('RM-B02-0' || i, 9101, 5, i, 1);
    upsert_cell('RM-C01-0' || i, 9101, 6, i, 1);
  end loop;

  upsert_cell('MES_PROD', 9102, 1, 1, 1, 1);
  upsert_cell('MES_QA', 9102, 1, 2, 1, 1);
  upsert_cell('MES_REWORK', 9102, 1, 3, 1, 1);

  upsert_cell('MES_FG', 9103, 1, 1, 1, 1);
  upsert_cell('BUF_QA', 9103, 1, 2, 1, 1);
  upsert_cell('BUF_HOLD', 9103, 1, 3, 1, 1);

  for i in 1 .. 10 loop
    upsert_cell('FG-A01-' || lpad(i, 2, '0'), 9104, 1, i, 1);
    upsert_cell('FG-A02-' || lpad(i, 2, '0'), 9104, 2, i, 1);
  end loop;

  delete from RRL_REMAINS
   where UID_POLETA like 'SEED-RM-%';

  delete from RRL_EVENTS
   where USER_ID = 'MESSEED'
     and UID_POLETA like 'SEED-RM-%';

  for i in 1 .. v_items.count loop
    upsert_articul(v_items(i));
    seed_pallet(v_items(i), i);
  end loop;

  commit;
end;
/

prompt [seed 2026-05-17-012] WMS/MES test warehouses - done
