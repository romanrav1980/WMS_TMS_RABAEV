prompt [10] ARTICULS compatibility package

create or replace package ARTICULS is
  function ei(articul1 varchar2) return varchar2;
  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ) return int;
  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int;
  function eans(art1 varchar2) return varchar2;
end ARTICULS;
/

create or replace package body ARTICULS is
  function ei(articul1 varchar2) return varchar2 is
    type_w1 int;
  begin
    select art.type_w into type_w1
      from rrl_articuls art
     where art.acticul = articul1;

    if type_w1 in (0, 7) then
      return 'шт';
    elsif type_w1 in (8, 1, 6, 5, 2, 3) then
      return 'кг';
    else
      return 'шт';
    end if;
  exception
    when no_data_found then
      return 'шт';
  end;

  function UPDATE_MOD(
    ID1             INTEGER,
    ARTICUL1        VARCHAR2,
    NAME1           VARCHAR2,
    SHT_IN_KOR1     NUMBER,
    SHT_WEIGHT1     NUMBER,
    KARTON_WEIGHT1  NUMBER,
    DELETED1        INTEGER,
    SHK_SHT1        VARCHAR2,
    SHK_KOR1        VARCHAR2,
    X               NUMBER,
    Y               NUMBER,
    Z               NUMBER,
    BRT_KOR         NUMBER
  ) return int
  is
    BRT_KOR2 number;
    ID2 int;
  begin
    if BRT_KOR is null or BRT_KOR <= 0 then
      BRT_KOR2 := nvl(KARTON_WEIGHT1, 0) + nvl(SHT_WEIGHT1, 0) * nvl(SHT_IN_KOR1, 0);
    else
      BRT_KOR2 := BRT_KOR;
    end if;

    if ID1 > 0 then
      update RRL_ARTICUL_MODS
         set ARTICUL           = ARTICUL1,
             NAME              = NAME1,
             SHT_IN_KOR        = SHT_IN_KOR1,
             SHT_WEIGHT        = SHT_WEIGHT1,
             KARTON_WEIGHT     = KARTON_WEIGHT1,
             DELETED           = DELETED1,
             SHK_SHT           = SHK_SHT1,
             SHK_KOR           = SHK_KOR1,
             DIMK_X            = X,
             DIMK_Y            = Y,
             DIMK_Z            = Z,
             BRT_WEIGHT_OF_KOR = BRT_KOR2
       where ID = ID1;
      return ID1;
    end if;

    insert into RRL_ARTICUL_MODS (
      ID,
      ARTICUL,
      NAME,
      SHT_IN_KOR,
      SHT_WEIGHT,
      KARTON_WEIGHT,
      DELETED,
      SHK_SHT,
      SHK_KOR,
      DIMK_X,
      DIMK_Y,
      DIMK_Z,
      BRT_WEIGHT_OF_KOR
    ) values (
      MODS_SEQ.NEXTVAL,
      ARTICUL1,
      NAME1,
      SHT_IN_KOR1,
      SHT_WEIGHT1,
      KARTON_WEIGHT1,
      DELETED1,
      SHK_SHT1,
      SHK_KOR1,
      X,
      Y,
      Z,
      BRT_KOR2
    );

    select MODS_SEQ.currval into ID2 from dual;
    return ID2;
  end;

  function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int is
    new_event_id int;
  begin
    if new_cell is null or current_cell is null then
      return -1;
    end if;

    for rm1 in (
      select rm.remain, rm.uid_poleta
        from rrl_remains rm,
             rrl_pallets pts
       where rm.cell = current_cell
         and pts.uid_pallet = rm.uid_poleta
         and pts.articul = articul1
    ) loop
      select RRL_EVENT_ID_SQ.nextval into new_event_id from dual;
      insert into RRL_EVENTS (
        ID_EVENT,
        CELL_FROM,
        CELL_TO,
        DATE_EVENT,
        COUNT_EVENT,
        TYPE_EVENT,
        UID_POLETA,
        USER_ID
      ) values (
        new_event_id,
        current_cell,
        new_cell,
        systimestamp,
        rm1.remain,
        2,
        rm1.uid_poleta,
        iser_id1
      );
    end loop;

    return 1;
  end;

  function eans(art1 varchar2) return varchar2 is
    tmp1 varchar2(4000);
  begin
    begin
      select art.barcode_sht into tmp1
        from rrl_articuls art
       where art.acticul = art1;
    exception
      when no_data_found then
        tmp1 := null;
    end;

    for r in (
      select shk_sht
        from rrl_articul_mods
       where articul = art1
         and deleted = 0
         and shk_sht is not null
    ) loop
      if tmp1 is null then
        tmp1 := r.shk_sht;
      else
        tmp1 := tmp1 || ';' || r.shk_sht;
      end if;
    end loop;

    return tmp1;
  end;
end ARTICULS;
/
