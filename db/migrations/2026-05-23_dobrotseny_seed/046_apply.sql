-- =============================================================================
-- Migration 046 — Тестовые данные «Добра Цен»: склады, ячейки, артикулы
-- =============================================================================
-- Создаёт три распределительных склада сети «Добра Цен» (Пермь / Екатеринбург / Тюмень),
-- 12 000 ячеек единой камеры на каждый склад (60 проходов × 20 позиций × 10 уровней),
-- ~1 350 артикулов продуктов питания и бытовой химии.
--
-- IDs складов: 9201–9203 (не пересекаются с MES-тестом 9101–9104)
-- Idempotent: MERGE — безопасно повторно применять.
-- =============================================================================

prompt [seed 046] Добра Цен — склады, ячейки, артикулы - apply

DECLARE
  -- ── Вспомогательные процедуры ────────────────────────────────────────────

  PROCEDURE upsert_ware(
    p_id     NUMBER,
    p_name   VARCHAR2,
    p_prefix VARCHAR2,
    p_order  NUMBER
  ) IS
  BEGIN
    MERGE INTO RRL_WARES d
    USING (
      SELECT p_id     ID,
             SUBSTR(p_name, 1, 50) NAME,
             p_prefix PREFIX,
             p_order  ORD2
        FROM dual
    ) s ON (d.ID = s.ID)
    WHEN MATCHED THEN UPDATE SET
      d.NAME   = s.NAME,
      d.PREFIX = s.PREFIX,
      d.ORD2   = s.ORD2
    WHEN NOT MATCHED THEN INSERT (
      ID, NAME, OVERFLOW_CELL_NAME, PREFIX,
      FAKE_ROWS, FAKE_ART,
      BLOCK_IF_NO_PROOVE, VERIFY_VYCHERK, ALLOW_HALF_VYCHERK, ORD2
    ) VALUES (
      s.ID, s.NAME, 'OVERFLOW', s.PREFIX,
      0, 'ДЦ-МОЛ-0001',
      0, 0, 1, s.ORD2
    );
  END;

  PROCEDURE upsert_cell(
    p_cell    VARCHAR2,
    p_ware_id NUMBER,
    p_x       NUMBER,
    p_y       NUMBER,
    p_z       NUMBER
  ) IS
  BEGIN
    MERGE INTO RRL_CELLS d
    USING (
      SELECT p_cell    CELL,
             p_ware_id WARE_ID,
             p_x X, p_y Y, p_z Z
        FROM dual
    ) s ON (d.CELL = s.CELL)
    WHEN MATCHED THEN UPDATE SET
      d.WARE_ID              = s.WARE_ID,
      d.X                    = s.X,
      d.Y                    = s.Y,
      d.Z                    = s.Z,
      d.LAST_TIME_OF_UPDATE  = SYSDATE
    WHEN NOT MATCHED THEN INSERT (
      CELL, WARE_ID, X, Y, Z,
      OTBOR, BLOCKED_FOR_REMAINS,
      BLOCKED_FOR_POPOLNENIE, BLOCKED_FOR_ACCEPT,
      IS_SYSTEM, LAST_TIME_OF_UPDATE,
      LIMIT_WEIGHT, LIMIT_HEIGHT
    ) VALUES (
      s.CELL, s.WARE_ID, s.X, s.Y, s.Z,
      0, 0, 0, 0,
      0, SYSDATE,
      5000, 2500
    );
  END;

  -- ── Переменные ────────────────────────────────────────────────────────────

  v_ware_prefix  VARCHAR2(3);
  v_ware_id      NUMBER;
  v_cell         VARCHAR2(30);
  v_artcode      VARCHAR2(40);
  v_art_global   NUMBER := 0;   -- глобальный счётчик артикула (для ячейки)
  v_barcode      VARCHAR2(13);
  v_cell_home    VARCHAR2(30);
  v_aisle        NUMBER;
  v_bay          NUMBER;

  -- Категории артикулов: (префикс, название_base, кол-во, ед_изм, срок_хранения_дней)
  TYPE t_cat IS RECORD (
    pref VARCHAR2(5),
    nm   VARCHAR2(60),
    cnt  NUMBER,
    ut   VARCHAR2(5),
    sd   NUMBER
  );
  TYPE t_cats IS TABLE OF t_cat;

  v_cats t_cats := t_cats(
    t_cat('МОЛ', 'Молочный продукт',           200, 'PCS', 14  ),
    t_cat('МЯС', 'Мясной продукт',              150, 'KG',  7   ),
    t_cat('РЫБ', 'Рыбный продукт',              100, 'KG',  5   ),
    t_cat('БАК', 'Бакалея',                     200, 'PCS', 365 ),
    t_cat('КНС', 'Консервы',                    150, 'PCS', 1095),
    t_cat('ХЛБ', 'Хлебобулочное изделие',       100, 'PCS', 3   ),
    t_cat('НАП', 'Напиток',                     150, 'PCS', 180 ),
    t_cat('КОД', 'Кондитерское изделие',        100, 'PCS', 90  ),
    t_cat('ЗАМ', 'Замороженный продукт',        100, 'KG',  180 ),
    t_cat('ХИМ', 'Бытовая химия и гигиена',    100, 'PCS', 730 )
  );

BEGIN
  -- ──────────────────────────────────────────────────────────────────────────
  -- 1. СКЛАДЫ
  -- ──────────────────────────────────────────────────────────────────────────
  upsert_ware(9201, 'ДЦ-Пермь (Добра Цен)',         'ДЦП', 201);
  upsert_ware(9202, 'ДЦ-Екатеринбург (Добра Цен)',  'ДЦЕ', 202);
  upsert_ware(9203, 'ДЦ-Тюмень (Добра Цен)',        'ДЦТ', 203);

  UPDATE RRL_WARES SET
    FLAG_FINISHED_GOODS     = 1,
    FLAG_RAW_MATERIAL       = 0,
    FLAG_PRODUCTION         = 0,
    FLAG_PRODUCTION_BUFFER  = 0,
    MES_ENABLED             = 0,
    DEFAULT_RECEIVE_CELL    = 'ДЦП-001-01-1',
    DEFAULT_ISSUE_CELL      = 'ДЦП-001-01-1',
    WARE_COMMENT = 'Тестовый склад Добра Цен, г. Пермь. Единая камера, ~12 000 ячеек. Seed: доброцен.'
  WHERE ID = 9201;

  UPDATE RRL_WARES SET
    FLAG_FINISHED_GOODS     = 1,
    FLAG_RAW_MATERIAL       = 0,
    FLAG_PRODUCTION         = 0,
    FLAG_PRODUCTION_BUFFER  = 0,
    MES_ENABLED             = 0,
    DEFAULT_RECEIVE_CELL    = 'ДЦЕ-001-01-1',
    DEFAULT_ISSUE_CELL      = 'ДЦЕ-001-01-1',
    WARE_COMMENT = 'Тестовый склад Добра Цен, г. Екатеринбург. Единая камера, ~12 000 ячеек. Seed: доброцен.'
  WHERE ID = 9202;

  UPDATE RRL_WARES SET
    FLAG_FINISHED_GOODS     = 1,
    FLAG_RAW_MATERIAL       = 0,
    FLAG_PRODUCTION         = 0,
    FLAG_PRODUCTION_BUFFER  = 0,
    MES_ENABLED             = 0,
    DEFAULT_RECEIVE_CELL    = 'ДЦТ-001-01-1',
    DEFAULT_ISSUE_CELL      = 'ДЦТ-001-01-1',
    WARE_COMMENT = 'Тестовый склад Добра Цен, г. Тюмень. Единая камера, ~12 000 ячеек. Seed: доброцен.'
  WHERE ID = 9203;

  -- ──────────────────────────────────────────────────────────────────────────
  -- 2. ЯЧЕЙКИ — 12 000 на каждый склад
  --    60 проходов × 20 позиций × 10 уровней = 12 000 ячеек
  --    Имя: {PREFIX}-{003}-{02}-{1}
  -- ──────────────────────────────────────────────────────────────────────────
  FOR w_idx IN 1..3 LOOP
    v_ware_id     := 9200 + w_idx;
    v_ware_prefix := CASE w_idx WHEN 1 THEN 'ДЦП' WHEN 2 THEN 'ДЦЕ' ELSE 'ДЦТ' END;

    FOR aisle IN 1..60 LOOP
      FOR bay IN 1..20 LOOP
        FOR lvl IN 1..10 LOOP
          v_cell := v_ware_prefix
                 || '-' || LPAD(aisle, 3, '0')
                 || '-' || LPAD(bay,   2, '0')
                 || '-' || lvl;
          upsert_cell(v_cell, v_ware_id, aisle, bay, lvl);
        END LOOP;
      END LOOP;
    END LOOP;
  END LOOP;

  -- ──────────────────────────────────────────────────────────────────────────
  -- 3. АРТИКУЛЫ — ~1 350 позиций, 10 категорий
  --    Код: ДЦ-{КАТ}-{0001}
  --    Домашняя ячейка — систематически из ДЦП (склад 9201)
  -- ──────────────────────────────────────────────────────────────────────────
  FOR i IN 1..v_cats.COUNT LOOP
    FOR j IN 1..v_cats(i).cnt LOOP
      v_art_global := v_art_global + 1;
      v_artcode    := 'ДЦ-' || v_cats(i).pref || '-' || LPAD(j, 4, '0');
      v_barcode    := LPAD(9000000000 + v_art_global, 13, '0');

      -- Домашняя ячейка: циклически по проходам/позициям уровень 1
      v_aisle    := MOD(v_art_global - 1, 60) + 1;
      v_bay      := MOD(TRUNC((v_art_global - 1) / 60), 20) + 1;
      v_cell_home := 'ДЦП-' || LPAD(v_aisle, 3, '0') || '-' || LPAD(v_bay, 2, '0') || '-1';

      MERGE INTO RRL_ARTICULS d
      USING (
        SELECT v_artcode             ACTICUL,
               v_cats(i).nm || ' '
               || LPAD(j, 4, '0')   NAME,
               v_cats(i).ut         UNIT_TYPE,
               v_cell_home          CELL,
               v_cats(i).sd         BESTBEFOREDAYS,
               v_barcode            BARCODE
          FROM dual
      ) s ON (d.ACTICUL = s.ACTICUL)
      WHEN MATCHED THEN UPDATE SET
        d.NAME           = s.NAME,
        d.UNIT_TYPE      = s.UNIT_TYPE,
        d.CELL           = s.CELL,
        d.BESTBEFOREDAYS = s.BESTBEFOREDAYS
      WHEN NOT MATCHED THEN INSERT (
        ACTICUL, NORMA_UKLADKI, CELL, NAME, UNIT_TYPE, BARCODE_SHT,
        WEIGHT_OF_KOR, COUNT_IN_ROW, ROWS_IN_PAL, COUNT_SHT_IN_KOR,
        PALLET_MULTIPLE, CARTON_WEIGHT, ETAJ_LIMIT, BESTBEFOREDAYS,
        ABC_GROUP, XYZ_GROUP
      ) VALUES (
        s.ACTICUL, 1, s.CELL, s.NAME, s.UNIT_TYPE, s.BARCODE,
        ROUND(0.3 + MOD(v_art_global, 15) * 0.15, 2),  -- вес короба 0.3–2.4 кг
        CASE v_cats(i).ut WHEN 'KG' THEN 6  ELSE 12 END,
        CASE v_cats(i).ut WHEN 'KG' THEN 4  ELSE 5  END,
        CASE v_cats(i).ut WHEN 'KG' THEN 1  ELSE 6  END,
        1, 0, 100, s.BESTBEFOREDAYS,
        CASE MOD(v_art_global, 3) WHEN 0 THEN 'A' WHEN 1 THEN 'B' ELSE 'C' END,
        CASE MOD(v_art_global, 3) WHEN 0 THEN 'X' WHEN 1 THEN 'Y' ELSE 'Z' END
      );
    END LOOP;
  END LOOP;

  COMMIT;
  DBMS_OUTPUT.PUT_LINE('046 done: склады 9201-9203, ячейки ~36 000, артикулы ~1 350');
END;
/

prompt [seed 046] Добра Цен — склады, ячейки, артикулы - done
