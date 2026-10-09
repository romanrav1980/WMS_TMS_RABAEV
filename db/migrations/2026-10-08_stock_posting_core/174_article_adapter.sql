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
  ,p_actor varchar2 default null) return int;
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
      return unistr('\0421\20ac\0421\201a');
    elsif type_w1 in (8, 1, 6, 5, 2, 3) then
      return unistr('\0420\0454\0420\0456');
    else
      return unistr('\0421\20ac\0421\201a');
    end if;
  exception
    when no_data_found then
      return unistr('\0421\20ac\0421\201a');
  end;
function UPDATE_MOD(ID1             INTEGER,
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
    BRT_KOR         NUMBER,p_actor varchar2 default null) return int is
 v_state varchar2(20);v_id number;v_article varchar2(160);v_brutto number;v_n number;
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' and p_actor is null then return ARTICULS_SP_OLD.UPDATE_MOD(ID1,ARTICUL1,NAME1,SHT_IN_KOR1,SHT_WEIGHT1,KARTON_WEIGHT1,DELETED1,SHK_SHT1,SHK_KOR1,X,Y,Z,BRT_KOR);end if;
 if ARTICUL1 is null or NAME1 is null or SHT_IN_KOR1 is null or SHT_IN_KOR1<1
  or SHT_IN_KOR1!=trunc(SHT_IN_KOR1) or SHT_IN_KOR1>1000000000
  or nvl(SHT_WEIGHT1,0)<0 or nvl(KARTON_WEIGHT1,0)<0 or nvl(BRT_KOR,0)<0
  or nvl(X,0)<0 or nvl(Y,0)<0 or nvl(Z,0)<0 or DELETED1 is null or DELETED1 not in(0,1) then
  raise_application_error(-20887,'ARTICLE_PACK_FACTS_INVALID');
 end if;
 RRL_STOCK_CONFIG_API.begin_change(p_actor,'warehouse_settings_edit');
 select count(*) into v_n from RRL_ARTICULS where ACTICUL=ARTICUL1;
 if v_n!=1 then raise_application_error(-20887,'ARTICLE_NOT_FOUND');end if;
 if nvl(ID1,0)>0 then
  select ARTICUL into v_article from RRL_ARTICUL_MODS where ID=ID1 for update;
  if v_article!=ARTICUL1 then raise_application_error(-20887,'ARTICLE_MOD_IDENTITY_CONFLICT');end if;
  -- Existing pallets keep their immutable packaging factor and dimensions.
  update RRL_ARTICUL_MODS set DELETED=1 where ID=ID1;
 end if;
 v_brutto:=case when nvl(BRT_KOR,0)>0 then BRT_KOR else nvl(KARTON_WEIGHT1,0)+nvl(SHT_WEIGHT1,0)*SHT_IN_KOR1 end;
 select MODS_SEQ.nextval into v_id from dual;
 insert into RRL_ARTICUL_MODS(ID,ARTICUL,NAME,SHT_IN_KOR,SHT_WEIGHT,KARTON_WEIGHT,DELETED,SHK_SHT,SHK_KOR,DIMK_X,DIMK_Y,DIMK_Z,BRT_WEIGHT_OF_KOR)
 values(v_id,ARTICUL1,NAME1,SHT_IN_KOR1,SHT_WEIGHT1,KARTON_WEIGHT1,DELETED1,SHK_SHT1,SHK_KOR1,X,Y,Z,v_brutto);
 RRL_STOCK_CONFIG_API.end_change;
 return v_id;
exception when others then RRL_STOCK_CONFIG_API.end_change;raise;
end;
function event_on_change_picking_cell(articul1 varchar2, new_cell varchar2, current_cell varchar2, iser_id1 varchar2) return int is
begin
 if articul1 is null or new_cell is null or current_cell is null or iser_id1 is null then
  raise_application_error(-20886,'ARTICLE_MOVE_FACTS_REQUIRED');
 end if;
 raise_application_error(-20886,'ARTICLE_CELL_CHANGE_REQUIRES_PHYSICAL_MOVE_TASK: use existing warehouse tasks');
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
