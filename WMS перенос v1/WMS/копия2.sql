------------------------------------------------
-- Export file for user RABAEV                --
-- Created by rrabaev on 25.07.2011, 21:08:01 --
------------------------------------------------

spool копия2.log

prompt
prompt Creating table INVENTORY_LINE_PALLET_AUDIT
prompt ==========================================
prompt
create table rabaev.INVENTORY_LINE_PALLET_AUDIT
(
  уид          VARCHAR2(25 CHAR) not null,
  кол          INTEGER default 0,
  palletid     VARCHAR2(25 CHAR) not null,
  датасоздания DATE,
  user_id      VARCHAR2(50 CHAR),
  method       VARCHAR2(20 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table LOT_AUDIT
prompt ========================
prompt
create table rabaev.LOT_AUDIT
(
  sscc      VARCHAR2(25 CHAR) not null,
  condition VARCHAR2(25 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.LOT_AUDIT
  add constraint LOT_AUDIT_PK primary key (SSCC)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table LOT_AUDIT_ERROR_LINES
prompt ====================================
prompt
create table rabaev.LOT_AUDIT_ERROR_LINES
(
  sscc          VARCHAR2(25 CHAR) not null,
  condition     VARCHAR2(15 CHAR),
  unit_count    NUMBER default 0 not null,
  uid1          VARCHAR2(12 CHAR),
  ean           VARCHAR2(25 CHAR),
  time_of_audit DATE,
  plan_count    NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.LOT_AUDIT_ERROR_LINES_PK on rabaev.LOT_AUDIT_ERROR_LINES (SSCC)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table ORDER_AUDIT
prompt ==========================
prompt
create table rabaev.ORDER_AUDIT
(
  order_number VARCHAR2(25 CHAR) not null,
  condition    VARCHAR2(25 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.ORDER_AUDIT_PK on rabaev.ORDER_AUDIT (ORDER_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table ORDER_AUDIT_ERROR_LINES
prompt ======================================
prompt
create table rabaev.ORDER_AUDIT_ERROR_LINES
(
  order_number  VARCHAR2(25 CHAR) not null,
  condition     VARCHAR2(15 CHAR),
  unit_count    INTEGER default 0 not null,
  uid1          VARCHAR2(12 CHAR) not null,
  ean           VARCHAR2(25 CHAR),
  time_of_audit DATE
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.ORDER_AUDIT_ERROR_LINES
  add constraint ORDER_AUDIT_LINES_PK primary key (ORDER_NUMBER, UID1)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table ORDER_MOV_HIST
prompt =============================
prompt
create table rabaev.ORDER_MOV_HIST
(
  id         INTEGER not null,
  order_uid  INTEGER not null,
  zone       NVARCHAR2(15),
  ruser      NVARCHAR2(15) not null,
  time_stamp DATE,
  last_flag  INTEGER default 1,
  usscc      VARCHAR2(50 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.ORDER_MOV_HIST
  add constraint ORDER_MOV_HIST_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table PLACE_AUDIT
prompt ==========================
prompt
create table rabaev.PLACE_AUDIT
(
  palletid  VARCHAR2(25 CHAR) not null,
  condition VARCHAR2(25 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table PLACE_AUDIT_ERROR_LINES
prompt ======================================
prompt
create table rabaev.PLACE_AUDIT_ERROR_LINES
(
  palletid   VARCHAR2(25 CHAR) not null,
  condition  VARCHAR2(15 CHAR),
  unit_count INTEGER default 0 not null,
  uid1       VARCHAR2(12 CHAR),
  ean        VARCHAR2(25 CHAR),
  ruser      NVARCHAR2(50),
  date1      DATE
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table Q1
prompt =================
prompt
create table rabaev.Q1
(
  id INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RIGHTS
prompt =====================
prompt
create table rabaev.RIGHTS
(
  right1     VARCHAR2(30),
  user_group VARCHAR2(15),
  id         INTEGER not null,
  descr      VARCHAR2(255)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RIGHTS
  add constraint RIGHTS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ADDR
prompt =======================
prompt
create table rabaev.RRL_ADDR
(
  addr           VARCHAR2(255) not null,
  napr           VARCHAR2(50),
  raion          VARCHAR2(50),
  region         VARCHAR2(250),
  ord            INTEGER default 0,
  transport_type VARCHAR2(15) default 15,
  prim1          VARCHAR2(255),
  stol           INTEGER default 0,
  dolgota        NUMBER,
  shirota        NUMBER,
  lead_time      INTEGER default 0,
  client_group   VARCHAR2(50),
  shipping_time  VARCHAR2(5) default '00:00',
  dock_default   VARCHAR2(15),
  deleted3       INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ADDR
  add constraint RRL_ADDR_PK primary key (ADDR)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ADDR_I33 on rabaev.RRL_ADDR (NAPR, RAION, REGION)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ALARMS
prompt =========================
prompt
create table rabaev.RRL_ALARMS
(
  id              INTEGER not null,
  type1           VARCHAR2(50),
  alarm_time      DATE,
  user_id         VARCHAR2(50),
  comment1        VARCHAR2(1024),
  send_begin      INTEGER default 0,
  send_ended      INTEGER default 0,
  ware_id         INTEGER,
  articul         VARCHAR2(50),
  cell            VARCHAR2(50),
  pallet_id       VARCHAR2(50),
  time_send_ended DATE
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ALARMS
  add constraint RRL_ALARMS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ARTICUL_MODS
prompt ===============================
prompt
create table rabaev.RRL_ARTICUL_MODS
(
  id            INTEGER not null,
  articul       VARCHAR2(15),
  name          VARCHAR2(50),
  sht_in_kor    NUMBER,
  sht_weight    NUMBER,
  karton_weight NUMBER,
  deleted       INTEGER,
  shk_sht       VARCHAR2(50),
  shk_kor       VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ARTICUL_MODS
  add constraint RRL_ARTICUL_MODS_ID primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.ART on rabaev.RRL_ARTICUL_MODS (ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ARTICUL_MODS_I5 on rabaev.RRL_ARTICUL_MODS (DELETED)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ARTICULS
prompt ===========================
prompt
create table rabaev.RRL_ARTICULS
(
  acticul          VARCHAR2(15 CHAR) not null,
  norma_ukladki    NUMBER not null,
  cell             VARCHAR2(50 CHAR),
  name             VARCHAR2(255 CHAR),
  unit_type        VARCHAR2(20 CHAR),
  barcode_sht      VARCHAR2(128 CHAR) default 777 not null,
  barcode_kor      VARCHAR2(128 CHAR),
  barcode_bl       VARCHAR2(128 CHAR),
  weight_of_kor    NUMBER,
  count_in_row     INTEGER,
  rows_in_pal      INTEGER,
  count_sht_in_kor NUMBER,
  count_sht_in_bl  NUMBER default 1,
  pallet_multiple  NUMBER default 1,
  carton_weight    NUMBER default 0,
  etaj_limit       INTEGER default 100,
  bestbeforedays   INTEGER default 360,
  ssp              NUMBER default 0,
  abc_group        VARCHAR2(1),
  xyz_group        VARCHAR2(1),
  order_of_comp    INTEGER default 0,
  rcecomplect      INTEGER default 0,
  floating_weight  INTEGER default 0,
  type_w           INTEGER default 0,
  weight_of_sht    NUMBER default 0,
  round_to         INTEGER default 2,
  def_perc         NUMBER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on column rabaev.RRL_ARTICULS.etaj_limit
  is 'Выше данного этажа не размещать';
alter table rabaev.RRL_ARTICULS
  add constraint RRL_ARTICULS_PK primary key (ACTICUL)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.PALLET_MULTIPLE_I on rabaev.RRL_ARTICULS (PALLET_MULTIPLE)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ARTICULS_BARCODE_SHT on rabaev.RRL_ARTICULS (BARCODE_SHT)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ARTICULS_I4 on rabaev.RRL_ARTICULS (CELL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_BILL_COMPANY
prompt ===============================
prompt
create table rabaev.RRL_BILL_COMPANY
(
  companyname   VARCHAR2(30) not null,
  addr          VARCHAR2(255),
  deleted       INTEGER default 0,
  pos           INTEGER,
  color         VARCHAR2(50),
  special_price INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_BILL_COMPANY
  add constraint RRL_BILL_COMPANY_PK primary key (COMPANYNAME)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_BILLING
prompt ==========================
prompt
create table rabaev.RRL_BILLING
(
  id         INTEGER not null,
  user_id    VARCHAR2(50),
  ue         NUMBER,
  timeof     DATE,
  operation  VARCHAR2(50),
  prim       VARCHAR2(255),
  pallet_uid VARCHAR2(50),
  deleted    INTEGER,
  cell_from  VARCHAR2(50),
  cell_to    VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_BILLING
  add constraint RRL_BILLING_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_BILLING_I1 on rabaev.RRL_BILLING (USER_ID, TIMEOF, OPERATION, PALLET_UID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_BILLING_NASTR_INTMOV
prompt =======================================
prompt
create table rabaev.RRL_BILLING_NASTR_INTMOV
(
  expedit_group_to   VARCHAR2(20),
  user_group         VARCHAR2(20),
  ue                 NUMBER default 0,
  expedit_group_from VARCHAR2(20)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_BILL_ORDERS
prompt ==============================
prompt
create table rabaev.RRL_BILL_ORDERS
(
  id          INTEGER not null,
  num         VARCHAR2(15),
  company     VARCHAR2(30),
  dateoforder DATE,
  datefrom    DATE,
  dateto      DATE,
  closed      INTEGER default 0,
  summ        NUMBER default 0,
  payed       INTEGER default 0,
  num_plat    VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_BILL_ORDERS
  add constraint RRL_BILL_ORDERS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_BILL_ORDERS_I4 on rabaev.RRL_BILL_ORDERS (NUM, COMPANY, DATEOFORDER, DATEFROM, DATETO)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_CELLS
prompt ========================
prompt
create table rabaev.RRL_CELLS
(
  cell                   VARCHAR2(15 CHAR) not null,
  otbor                  INTEGER default 0,
  blocked_for_remains    INTEGER default 0,
  blocked_for_popolnenie INTEGER default 0,
  uid_poleta_for_block   VARCHAR2(50 CHAR),
  time_for_block         DATE,
  x                      INTEGER default 10000 not null,
  y                      INTEGER default 10000 not null,
  z                      INTEGER default 10000 not null,
  blocked_for_accept     INTEGER default 0,
  ware_id                INTEGER default 1,
  is_system              INTEGER default 0,
  expedition_group       VARCHAR2(15),
  last_time_of_update    DATE,
  limit_weight           NUMBER default 10000,
  limit_height           NUMBER default 10000,
  y_visota               NUMBER,
  cell_weight            NUMBER,
  cell_height            NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on column rabaev.RRL_CELLS.limit_weight
  is 'Ограничения на вес товара в ячейке';
comment on column rabaev.RRL_CELLS.limit_height
  is 'Ограничения на высоту паллета';
comment on column rabaev.RRL_CELLS.y_visota
  is 'Высота над полом в метрах';
alter table rabaev.RRL_CELLS
  add constraint RRL_CELLS_PK primary key (CELL)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_CELLS_EXP on rabaev.RRL_CELLS (EXPEDITION_GROUP)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_CELLS_I7 on rabaev.RRL_CELLS (UID_POLETA_FOR_BLOCK, TIME_FOR_BLOCK)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_CELLS_I8 on rabaev.RRL_CELLS (X, Y, Z, IS_SYSTEM, Y_VISOTA)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_CELLS_I9 on rabaev.RRL_CELLS (OTBOR, BLOCKED_FOR_REMAINS, BLOCKED_FOR_POPOLNENIE, BLOCKED_FOR_ACCEPT)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_CELLS_WARE_ID on rabaev.RRL_CELLS (WARE_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_CELLS_CONDITIONS_MAPPING
prompt ===========================================
prompt
create table rabaev.RRL_CELLS_CONDITIONS_MAPPING
(
  xfrom            INTEGER,
  yfrom            INTEGER,
  zfrom            INTEGER,
  xto              INTEGER,
  yto              INTEGER,
  zto              INTEGER,
  compl_order_from INTEGER,
  compl_order_to   INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_COMPL_SEQ
prompt ============================
prompt
create table rabaev.RRL_COMPL_SEQ
(
  articul   VARCHAR2(50) not null,
  ware_id   INTEGER not null,
  seq       INTEGER not null,
  seq_group INTEGER not null
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_COMPL_SEQ_I1 on rabaev.RRL_COMPL_SEQ (ARTICUL, WARE_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_COMPL_SEQ_I2 on rabaev.RRL_COMPL_SEQ (SEQ_GROUP)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_COMPL_SEQ_I3 on rabaev.RRL_COMPL_SEQ (SEQ)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_CROSS_DOCKING_ZONES
prompt ======================================
prompt
create table rabaev.RRL_CROSS_DOCKING_ZONES
(
  id                   INTEGER not null,
  cell                 VARCHAR2(50),
  articul              VARCHAR2(50),
  condition_from_count NUMBER,
  condition_to_count   NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_CROSS_DOCKING_ZONES
  add constraint RRL_CROSS_DOCKING_ZONES_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ERROR_LOG
prompt ============================
prompt
create table rabaev.RRL_ERROR_LOG
(
  error   VARCHAR2(1024),
  datet   DATE,
  user_id VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_EVENTS
prompt =========================
prompt
create table rabaev.RRL_EVENTS
(
  id_event       NUMBER not null,
  cell_from      VARCHAR2(20),
  cell_to        VARCHAR2(20),
  date_event     DATE not null,
  date_of_order  DATE,
  count_event    NUMBER,
  type_event     NUMBER(38) not null,
  uid_poleta     VARCHAR2(50),
  user_id        VARCHAR2(50) not null,
  prihod_nakl_id INTEGER default 0,
  othod_nakl_id  INTEGER default 0,
  pallet_row_id  INTEGER,
  packet1        INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_EVENTS
  add constraint RRL_EVENTS_PK primary key (ID_EVENT)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.PALLET_ROW_ID_I8 on rabaev.RRL_EVENTS (PALLET_ROW_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_EVENTS_DATE_EVENT on rabaev.RRL_EVENTS (DATE_EVENT, UID_POLETA)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_EVENTS_I8 on rabaev.RRL_EVENTS (PACKET1)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_HISTORY_NOTES
prompt ================================
prompt
create table rabaev.RRL_HISTORY_NOTES
(
  id        INTEGER not null,
  user_id   VARCHAR2(50),
  addr_to   VARCHAR2(50),
  addr_from VARCHAR2(50),
  mess      VARCHAR2(1024),
  puid      VARCHAR2(100),
  count1    NUMBER,
  eventdate DATE,
  mess2     VARCHAR2(1024)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_HISTORY_NOTES
  add constraint RRL_HISTORY_NOTES_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_INVENTARIZ_LINES
prompt ===================================
prompt
create table rabaev.RRL_INVENTARIZ_LINES
(
  id_of_invent INTEGER not null,
  id_line      INTEGER not null,
  cell         VARCHAR2(50 CHAR) not null,
  pallet_id    VARCHAR2(50 CHAR) not null,
  count1       NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_INVENTARIZ_LINES
  add constraint RRL_INVENTARIZ_LINES_PK primary key (ID_LINE)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_INVETARIZ
prompt ============================
prompt
create table rabaev.RRL_INVETARIZ
(
  id      INTEGER not null,
  date_of DATE not null,
  type1   INTEGER default 1 not null
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_INVETARIZ
  add constraint RRL_INVETARIZ_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ORDER_PALLET_ROWS
prompt ====================================
prompt
create table rabaev.RRL_ORDER_PALLET_ROWS
(
  id                    INTEGER not null,
  order_id              INTEGER not null,
  articul               VARCHAR2(15) not null,
  shortname             VARCHAR2(255),
  ei                    VARCHAR2(3),
  order_weight          NUMBER,
  quantity              NUMBER not null,
  sortfield             INTEGER,
  ware_id               INTEGER not null,
  pack_count            INTEGER,
  original_quantity     NUMBER default 0,
  original_order_weight NUMBER default 0,
  condition             INTEGER,
  taresize              NUMBER,
  tareweight            NUMBER,
  version_d             INTEGER,
  pall_numb             INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ORDER_PALLET_ROWS
  add constraint RRL_ORDER_PALLET_ROWS_I1 primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ORDER_PALLET_ROWS_I2 on rabaev.RRL_ORDER_PALLET_ROWS (ORDER_ID, ARTICUL, PALL_NUMB, VERSION_D)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ORDER_ROWS
prompt =============================
prompt
create table rabaev.RRL_ORDER_ROWS
(
  id                    INTEGER not null,
  order_id              INTEGER not null,
  articul               VARCHAR2(15) not null,
  shortname             VARCHAR2(255),
  ei                    VARCHAR2(3),
  order_weight          NUMBER,
  quantity              NUMBER not null,
  sortfield             INTEGER,
  ware_id               INTEGER not null,
  pack_count            INTEGER,
  original_quantity     NUMBER default 0,
  original_order_weight NUMBER default 0,
  condition             INTEGER,
  taresize              NUMBER,
  tareweight            NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ORDER_ROWS
  add constraint RRL_ORDER_ROWS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ORDER_ROWS_I1 on rabaev.RRL_ORDER_ROWS (ARTICUL, ORDER_ID, WARE_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ORDERS
prompt =========================
prompt
create table rabaev.RRL_ORDERS
(
  id          INTEGER not null,
  ord_number  VARCHAR2(50) not null,
  create_date DATE not null,
  ware_id     INTEGER not null,
  addr        VARCHAR2(255),
  state       VARCHAR2(50),
  orddate     DATE,
  user_id     VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_ORDERS
  add constraint RRL_ORDERS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_ORDERS_I1 on rabaev.RRL_ORDERS (CREATE_DATE, ORD_NUMBER, WARE_ID, ADDR, STATE, USER_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_ORDERS_UI8 on rabaev.RRL_ORDERS (ORD_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_ORDERS_PALL_VERSIONS
prompt =======================================
prompt
create global temporary table rabaev.RRL_ORDERS_PALL_VERSIONS
(
  version_id        INTEGER not null,
  ord_number        VARCHAR2(50) not null,
  maxmass           NUMBER,
  maxvol            NUMBER,
  count_of_pall     INTEGER,
  volume_of_max_pal NUMBER,
  volume_of_min_pal NUMBER
)
on commit delete rows;

prompt
prompt Creating table RRL_OTHOD_NAKLAD
prompt ===============================
prompt
create table rabaev.RRL_OTHOD_NAKLAD
(
  id                  INTEGER not null,
  nakladname          VARCHAR2(50 CHAR) not null,
  mag_no              VARCHAR2(50 CHAR) not null,
  nakladdate          DATE not null,
  creationdate        DATE not null,
  planneddeliverydate DATE,
  condition           INTEGER default 0,
  summ                NUMBER default 0,
  ware_id             INTEGER default 1
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_OTHOD_NAKLAD
  add constraint RRL_OTHOD_NAKLAD_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_OTHOD_NAKLAD_I1 on rabaev.RRL_OTHOD_NAKLAD (CREATIONDATE)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_OTHOD_NAKLAD_U9 on rabaev.RRL_OTHOD_NAKLAD (NAKLADNAME)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_OTHOD_NAKLAD_ROWS
prompt ====================================
prompt
create table rabaev.RRL_OTHOD_NAKLAD_ROWS
(
  id        INTEGER not null,
  id_naklad INTEGER not null,
  articul   VARCHAR2(15 CHAR) not null,
  count1    NUMBER not null,
  price     NUMBER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_OTHOD_NAKLAD_ROWS
  add constraint RRL_OTHOD_NAKLAD_ROWS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_OTHOD_NAKLAD_ROWS_A on rabaev.RRL_OTHOD_NAKLAD_ROWS (ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_OTHOD_NAKLAD_ROWS_ART on rabaev.RRL_OTHOD_NAKLAD_ROWS (ARTICUL, ID_NAKLAD)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_PALLETS
prompt ==========================
prompt
create table rabaev.RRL_PALLETS
(
  uid_pallet       VARCHAR2(50 CHAR) not null,
  articul          VARCHAR2(15 CHAR),
  creation_date    DATE,
  expiry_date      DATE,
  unit_count       NUMBER,
  price            NUMBER,
  prihod_naklad_id INTEGER not null,
  printed          INTEGER default 0,
  kladovshik       VARCHAR2(15),
  produced_date    DATE,
  mod_id           INTEGER,
  weight_brutto    NUMBER,
  weight_tn        NUMBER,
  defect_perc      NUMBER default 0,
  count_kor        INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on column rabaev.RRL_PALLETS.weight_tn
  is 'Вес паллета';
comment on column rabaev.RRL_PALLETS.count_kor
  is 'Количество коробок при оприходовании.';
alter table rabaev.RRL_PALLETS
  add constraint RRL_PALLETS_PK primary key (UID_PALLET)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PALLETS_MI on rabaev.RRL_PALLETS (CREATION_DATE, EXPIRY_DATE, ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PALLETS_NAKLAD on rabaev.RRL_PALLETS (PRIHOD_NAKLAD_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_PRIHOD_NAKLAD
prompt ================================
prompt
create table rabaev.RRL_PRIHOD_NAKLAD
(
  naklad_number    VARCHAR2(50 CHAR),
  date_of_naklad   DATE,
  date_of_accept   DATE,
  postavshik_name  VARCHAR2(50 CHAR),
  sm_naklad_number VARCHAR2(50 CHAR) not null,
  condition        INTEGER default 0,
  id               INTEGER,
  ware_id          INTEGER default 1,
  zakaz_number     VARCHAR2(20),
  vechile_number   VARCHAR2(20),
  voditel_name     VARCHAR2(255),
  temperature      NUMBER,
  user_id          VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_PRIHOD_NAKLAD
  add constraint RRL_PRIHOD_NAKLAD_PK primary key (SM_NAKLAD_NUMBER);
create unique index rabaev.RRL_PRIHOD_NAKLAD_ID on rabaev.RRL_PRIHOD_NAKLAD (ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_PRIHOD_NAKLAD_I2 on rabaev.RRL_PRIHOD_NAKLAD (SM_NAKLAD_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PRIHOD_NAKLAD_I8 on rabaev.RRL_PRIHOD_NAKLAD (ZAKAZ_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PRIHOD_NAKLAD_1 on rabaev.RRL_PRIHOD_NAKLAD (DATE_OF_NAKLAD)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PRIHOD_NAKLAD_4 on rabaev.RRL_PRIHOD_NAKLAD (NAKLAD_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_PRIHOD_NAKLAD_ROWS
prompt =====================================
prompt
create table rabaev.RRL_PRIHOD_NAKLAD_ROWS
(
  ordid         INTEGER,
  articul       VARCHAR2(15 CHAR),
  expiry_date   DATE,
  id            INTEGER not null,
  count1        NUMBER default 0,
  price         NUMBER default 0,
  invent_cell   VARCHAR2(15),
  kolpal        NUMBER,
  srok_godnosti INTEGER,
  mod_id        INTEGER,
  defect_perc   NUMBER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_PRIHOD_NAKLAD_ROWS
  add constraint RRL_PRIHOD_NAKLAD_ROWS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_PRIHOD_NAKLAD_ROWS_A on rabaev.RRL_PRIHOD_NAKLAD_ROWS (ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_PRIHOD_NAKLAD_ROWS_ART on rabaev.RRL_PRIHOD_NAKLAD_ROWS (ARTICUL, ORDID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_PRIHOD_NAKLAD_ROWS_ID2 on rabaev.RRL_PRIHOD_NAKLAD_ROWS (ORDID, ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_PRINTFORMS
prompt =============================
prompt
create table rabaev.RRL_PRINTFORMS
(
  id      VARCHAR2(100) not null,
  content CLOB
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_PRINTFORMS
  add constraint RRL_PRINTFORMS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_REMAINS
prompt ==========================
prompt
create table rabaev.RRL_REMAINS
(
  cell                VARCHAR2(20),
  uid_poleta          VARCHAR2(50),
  remain              NUMBER,
  othod_nakl_id       INTEGER default 0,
  time_of_last_update DATE
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_REMAINS_IND on rabaev.RRL_REMAINS (CELL, UID_POLETA)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_REVISION_ROW
prompt ===============================
prompt
create table rabaev.RRL_REVISION_ROW
(
  id          INTEGER not null,
  revision_id INTEGER not null,
  cell        VARCHAR2(50) not null,
  remark1     VARCHAR2(1024),
  count1      NUMBER,
  rev_date    DATE,
  count_kor   NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_REVISION_ROW
  add constraint RRL_REVISION_ROW_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_REVISION_ROW_I1 on rabaev.RRL_REVISION_ROW (REVISION_ID, CELL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_REVIZION
prompt ===========================
prompt
create table rabaev.RRL_REVIZION
(
  id          INTEGER not null,
  ware_id     INTEGER not null,
  create_date DATE not null,
  condition   INTEGER default 0,
  user_id     VARCHAR2(50) not null
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_REVIZION
  add constraint RRL_REVIZION_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_REVIZION_I on rabaev.RRL_REVIZION (WARE_ID, CONDITION, USER_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SBORKA_PALLET_ROWS
prompt =====================================
prompt
create table rabaev.RRL_SBORKA_PALLET_ROWS
(
  id                      INTEGER not null,
  pallet_uid              VARCHAR2(50),
  articul                 VARCHAR2(15),
  shortname               VARCHAR2(255),
  shtrihkod               VARCHAR2(4000),
  ei                      VARCHAR2(3),
  tareweight              NUMBER,
  order_weight            NUMBER,
  taresize                NUMBER,
  quantity                NUMBER,
  sortfield               INTEGER,
  auction                 VARCHAR2(255),
  docid                   VARCHAR2(15),
  ware_id                 INTEGER,
  path                    VARCHAR2(50),
  pack_count              INTEGER,
  original_quantity       NUMBER default 0,
  original_order_weight   NUMBER default 0,
  time_of_checking        DATE,
  current_mod_id          INTEGER,
  selected                INTEGER,
  vycherk_user_id         VARCHAR2(50),
  prihod_pallet_uid       VARCHAR2(50),
  sobrano                 NUMBER,
  expiry_date             DATE,
  prihod_pallet_uid_count INTEGER default 0,
  condition               INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_SBORKA_PALLET_ROWS
  add constraint RRL_SBORKA_PALLET_ROWS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLET_ROWS_I1 on rabaev.RRL_SBORKA_PALLET_ROWS (PALLET_UID, ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLET_ROWS_I9 on rabaev.RRL_SBORKA_PALLET_ROWS (WARE_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLET_ROWS_PPU on rabaev.RRL_SBORKA_PALLET_ROWS (PRIHOD_PALLET_UID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SBORKA_PALLETS
prompt =================================
prompt
create table rabaev.RRL_SBORKA_PALLETS
(
  id                 INTEGER not null,
  st_number          VARCHAR2(50),
  create_date        DATE,
  ware_id            INTEGER,
  pallet_number      INTEGER,
  pallet_uid         VARCHAR2(100),
  addr               VARCHAR2(255),
  state              VARCHAR2(50),
  stdate             DATE,
  naklad_number      VARCHAR2(50),
  transtask_id       INTEGER,
  rows_number        INTEGER default 0,
  napr               VARCHAR2(255),
  original_st_number VARCHAR2(50),
  wood_weight        NUMBER default 0,
  prooved            INTEGER default 0,
  trial_weight       NUMBER default 0,
  zone               VARCHAR2(50),
  user_id            VARCHAR2(50),
  ord                INTEGER default 0,
  sborshik           VARCHAR2(50),
  kladovshik         VARCHAR2(15),
  prooved_by_scan    INTEGER default 0,
  prim               VARCHAR2(1024),
  count_of_errors    INTEGER default 0,
  vesovshik          VARCHAR2(55),
  tt_oplata          NUMBER default 0,
  condition          INTEGER default 0,
  count_of_prints    INTEGER default 0,
  zone_time_plan_in  TIMESTAMP(0),
  zone_time_plan_out TIMESTAMP(0),
  ip_addr            VARCHAR2(50),
  count_of_prints2   INTEGER default 0,
  summary_task_id    INTEGER,
  count_of_prints3   INTEGER default 0,
  user_id_last_upd   VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_SBORKA_PALLETS
  add constraint RRL_SBORKA_PALLETS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_I2 on rabaev.RRL_SBORKA_PALLETS (ST_NUMBER, PALLET_NUMBER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_SBORKA_PALLETS_I5 on rabaev.RRL_SBORKA_PALLETS (PALLET_UID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_I7 on rabaev.RRL_SBORKA_PALLETS (STATE)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_I88 on rabaev.RRL_SBORKA_PALLETS (SBORSHIK)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_I9 on rabaev.RRL_SBORKA_PALLETS (TRANSTASK_ID, STDATE, CREATE_DATE, WARE_ID, ORD)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_I_99 on rabaev.RRL_SBORKA_PALLETS (ADDR)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_SB_I on rabaev.RRL_SBORKA_PALLETS (SUMMARY_TASK_ID, IP_ADDR, CONDITION, PROOVED)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_ZONE on rabaev.RRL_SBORKA_PALLETS (ZONE)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_ZONE_IN on rabaev.RRL_SBORKA_PALLETS (ZONE_TIME_PLAN_IN, ZONE_TIME_PLAN_OUT)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SBORKA_PALLETS_COND
prompt ======================================
prompt
create table rabaev.RRL_SBORKA_PALLETS_COND
(
  cond       VARCHAR2(25) not null,
  done       INTEGER default 0,
  sendt      INTEGER default 1,
  in_process INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_SBORKA_PALLETS_COND
  add constraint RRL_SBORKA_PALLETS_COND_PK primary key (COND)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SBORKA_PALLETS_HISTORY
prompt =========================================
prompt
create table rabaev.RRL_SBORKA_PALLETS_HISTORY
(
  id         INTEGER,
  pallet_uid VARCHAR2(50),
  user_id    VARCHAR2(50),
  zone       VARCHAR2(50),
  event      VARCHAR2(50),
  time1      DATE,
  weight     NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALLETS_HISTORY_I1 on rabaev.RRL_SBORKA_PALLETS_HISTORY (ID, PALLET_UID, EVENT)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SBORKA_PALL_ROWS_PARTS
prompt =========================================
prompt
create table rabaev.RRL_SBORKA_PALL_ROWS_PARTS
(
  id          INTEGER not null,
  pallet_uid  VARCHAR2(50),
  count       NUMBER,
  articul     VARCHAR2(50),
  expiry_date DATE
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_SBORKA_PALL_ROWS_PARTS
  add constraint RRL_SBORKA_PALL_ROWS_PARTSPK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_SBORKA_PALL_ROWS_PARTSI1 on rabaev.RRL_SBORKA_PALL_ROWS_PARTS (PALLET_UID, ARTICUL)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SUMMARY_PICK_LIST
prompt ====================================
prompt
create table rabaev.RRL_SUMMARY_PICK_LIST
(
  id         INTEGER not null,
  createdate DATE,
  condition  INTEGER default 0,
  ware_id    INTEGER not null
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_SUMMARY_PICK_LIST
  add constraint RRL_SUMMARY_PICK_LIST_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_SUMMARY_PICK_LIST_ROWS
prompt =========================================
prompt
create table rabaev.RRL_SUMMARY_PICK_LIST_ROWS
(
  id                INTEGER not null,
  articul           VARCHAR2(50) not null,
  spl_id            INTEGER not null,
  quantity          NUMBER default 0,
  quantity_complete NUMBER default 0,
  condition         INTEGER default 0,
  quantity_planned  NUMBER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on table rabaev.RRL_SUMMARY_PICK_LIST_ROWS
  is 'таблица строк суммарных сборочных листов';
comment on column rabaev.RRL_SUMMARY_PICK_LIST_ROWS.spl_id
  is 'ИД ССЛ';
comment on column rabaev.RRL_SUMMARY_PICK_LIST_ROWS.quantity
  is 'Количество нужно';
comment on column rabaev.RRL_SUMMARY_PICK_LIST_ROWS.quantity_complete
  is 'Количество обеспечено';
comment on column rabaev.RRL_SUMMARY_PICK_LIST_ROWS.condition
  is 'Состояний 0 - спланировано 1-не полностью спланировано 2-полностью обеспечено и закрыто';
comment on column rabaev.RRL_SUMMARY_PICK_LIST_ROWS.quantity_planned
  is 'Количество спланировано WT';
alter table rabaev.RRL_SUMMARY_PICK_LIST_ROWS
  add constraint RRL_SUMMARY_PICK_LIST_ROWS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TRANSPORT_PRICE
prompt ==================================
prompt
create table rabaev.RRL_TRANSPORT_PRICE
(
  id              INTEGER not null,
  price_name      VARCHAR2(1024) not null,
  price           NUMBER(10,2) not null,
  company         VARCHAR2(255),
  range1          NUMBER,
  price_for_hours NUMBER default 0,
  type_tr         VARCHAR2(15),
  price_folder    INTEGER default 0,
  price_for_addr  NUMBER default 0,
  norm_hours      NUMBER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TRANSPORT_PRICE
  add constraint RRL_TRANSPORT_PRICE_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_PRICE_I3 on rabaev.RRL_TRANSPORT_PRICE (PRICE_NAME, COMPANY)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TRANSPORT_TASK
prompt =================================
prompt
create table rabaev.RRL_TRANSPORT_TASK
(
  id                    INTEGER not null,
  createdate            DATE,
  transport             VARCHAR2(50),
  transtype             VARCHAR2(10),
  routetype             VARCHAR2(100),
  condition             VARCHAR2(25) default 'Спланирован',
  transp_zone           VARCHAR2(15),
  wave                  VARCHAR2(15),
  shipment_date         DATE,
  planned_delivery_date DATE,
  voditel_id            INTEGER,
  primechanie           VARCHAR2(1024),
  deleted               INTEGER default 0,
  dock                  VARCHAR2(50),
  price                 NUMBER,
  hours                 NUMBER,
  range1                NUMBER,
  temp_region           VARCHAR2(1024),
  pay_order_id          INTEGER default 0,
  temp_weight           NUMBER,
  user_id               VARCHAR2(50),
  pay_region            VARCHAR2(1024),
  addr_premio           INTEGER,
  shipment_time         DATE,
  dock_rezerv_time_from TIMESTAMP(0),
  dock_rezerv_time_to   TIMESTAMP(0)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TRANSPORT_TASK
  add constraint RRL_TRANSPORT_TASK_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_TASK on rabaev.RRL_TRANSPORT_TASK (CREATEDATE, SHIPMENT_DATE, DELETED, PAY_ORDER_ID, VODITEL_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_TASK_DOCK on rabaev.RRL_TRANSPORT_TASK (DOCK)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_TASK_DOCK_RESERV on rabaev.RRL_TRANSPORT_TASK (DOCK_REZERV_TIME_FROM, DOCK_REZERV_TIME_TO)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_TASK_USER on rabaev.RRL_TRANSPORT_TASK (USER_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TRANSPORT_TASK_HISTORY
prompt =========================================
prompt
create table rabaev.RRL_TRANSPORT_TASK_HISTORY
(
  id            INTEGER not null,
  ttask_id      INTEGER,
  user_id       VARCHAR2(50),
  transtype     VARCHAR2(20),
  transport     VARCHAR2(50),
  routetype     VARCHAR2(100),
  shipment_time DATE,
  voditel_id    INTEGER,
  primechanie   VARCHAR2(1024),
  dock          VARCHAR2(50),
  shipment_date DATE,
  operation     VARCHAR2(20),
  event_time    TIMESTAMP(0),
  st_number     VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TRANSPORT_TASK_HISTORY
  add constraint RRL_TRANSPORT_TASK_HISTORY_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TRANSPORT_TASK_HISTORY_I1 on rabaev.RRL_TRANSPORT_TASK_HISTORY (TTASK_ID, USER_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TRANSPORT_TYPE
prompt =================================
prompt
create table rabaev.RRL_TRANSPORT_TYPE
(
  transporttype VARCHAR2(25) not null,
  ref           INTEGER,
  norma_pallet  INTEGER,
  norma_weight  NUMBER,
  ord           INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TRANSPORT_TYPE
  add constraint RRL_TRANSPORT_TYPE_PK primary key (TRANSPORTTYPE)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TR_VEHICLE
prompt =============================
prompt
create table rabaev.RRL_TR_VEHICLE
(
  id          INTEGER not null,
  num         VARCHAR2(50),
  tr_type     VARCHAR2(15),
  marka       VARCHAR2(50),
  ref_rejim   VARCHAR2(50) default 'без',
  working_now INTEGER default 1,
  pallets     INTEGER,
  blocked     INTEGER default 0,
  gidrobort   INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TR_VEHICLE
  add constraint RRL_TR_VEHICLE_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create unique index rabaev.RRL_TR_VEHICLE_I on rabaev.RRL_TR_VEHICLE (NUM)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TR_VODITEL
prompt =============================
prompt
create table rabaev.RRL_TR_VODITEL
(
  id             INTEGER not null,
  f              VARCHAR2(50),
  i              VARCHAR2(50),
  o              VARCHAR2(50),
  deleted        INTEGER default 0,
  sobstvennyy    INTEGER default 0,
  veh_id         INTEGER,
  passport       VARCHAR2(255),
  doverennost_ot VARCHAR2(50),
  transport_num  VARCHAR2(50),
  addr           VARCHAR2(255),
  tel            VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TR_VODITEL
  add constraint RRL_TR_VODITEL_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TT_BILL_PRICE_KM
prompt ===================================
prompt
create table rabaev.RRL_TT_BILL_PRICE_KM
(
  tt      VARCHAR2(15),
  km_from INTEGER,
  km_to   INTEGER,
  price   INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TT_DOCK
prompt ==========================
prompt
create table rabaev.RRL_TT_DOCK
(
  dock            VARCHAR2(15) not null,
  ware_id         INTEGER,
  ord             INTEGER,
  dock_is_blocked INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TT_DOCK
  add constraint RRL_TT_DOCK_PK primary key (DOCK)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TT_LOAD_TASK
prompt ===============================
prompt
create table rabaev.RRL_TT_LOAD_TASK
(
  tt_id     INTEGER,
  dock      VARCHAR2(50),
  load_from DATE,
  load_to   DATE,
  ware_id   INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TT_PATH
prompt ==========================
prompt
create table rabaev.RRL_TT_PATH
(
  path1           VARCHAR2(1024) not null,
  range1          NUMBER,
  normative_hours NUMBER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TT_PATH
  add constraint RRL_TT_PATH_PK primary key (PATH1)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_TT_ZONES
prompt ===========================
prompt
create table rabaev.RRL_TT_ZONES
(
  zone     VARCHAR2(20),
  sub_zone VARCHAR2(25) not null,
  dock     VARCHAR2(15),
  x        NUMBER default 1000,
  y        NUMBER default 1000
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_TT_ZONES
  add constraint RRL_TT_ZONES_PK primary key (SUB_ZONE)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_TT_ZONES_XY on rabaev.RRL_TT_ZONES (X, Y)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_VERSIONS
prompt ===========================
prompt
create table rabaev.RRL_VERSIONS
(
  version VARCHAR2(150) not null,
  allow   INTEGER default 1
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_VERSIONS
  add constraint RRL_VERSIONS_PK primary key (VERSION)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_WARE_DISTR_TIME_PARAM
prompt ========================================
prompt
create table rabaev.RRL_WARE_DISTR_TIME_PARAM
(
  ware_id        VARCHAR2(50),
  time_perc_from NUMBER,
  time_perc_to   NUMBER,
  distr_perc     NUMBER,
  client_group   VARCHAR2(50)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on table rabaev.RRL_WARE_DISTR_TIME_PARAM
  is 'Параметры допустимых сроков дистрибуции в зависимости от склада, группы магазинов.';

prompt
prompt Creating table RRL_WARES
prompt ========================
prompt
create table rabaev.RRL_WARES
(
  id                            INTEGER,
  name                          VARCHAR2(50),
  overflow_cell_name            VARCHAR2(50) default 'OVERFLOW',
  prefix                        VARCHAR2(3),
  fake_rows                     INTEGER default 0,
  fake_art                      VARCHAR2(25) default 'Z0001',
  block_if_no_proove            INTEGER default 0,
  verify_vycherk                INTEGER default 0,
  write_both_expiryandbest      INTEGER default 0,
  spis_if_hran_no_empty         VARCHAR2(10),
  allow_half_vycherk            INTEGER default 1,
  spis_otbor_on_scan_opall      INTEGER default 0,
  spis_otbor_on_wproove_opall   INTEGER default 0,
  time_coeff                    NUMBER default 0.33,
  xyz_xcov                      NUMBER default 0.1,
  xyz_ycov                      NUMBER default 0.5,
  abc_a                         NUMBER default 0.8,
  abc_b                         NUMBER default 0.10,
  abc_xyz_time_edges_in_days    NUMBER(30),
  verify_vycherk_in_otbor       INTEGER default 0,
  print_expiry_date_op          INTEGER default 0,
  count_of_prints               INTEGER default 10000,
  weight_limit_warning          INTEGER default 0,
  weight_limit_stop             INTEGER default 0,
  parent_ware_id                INTEGER,
  ord2                          INTEGER,
  condition_print               INTEGER default 0,
  condition_close               INTEGER default 0,
  cntrl_brtto_weght_agnst_count INTEGER default 0,
  fasovka_needed                INTEGER default 0,
  count_weight_autorecalc       INTEGER default 0,
  type_w                        INTEGER default 0,
  direct_accept_to_cell         INTEGER default 0,
  partia_needed                 INTEGER default 0,
  zone_needed                   INTEGER default 0,
  fcontrol_fifo                 INTEGER default 1,
  verify_vycherk_in_other_wares INTEGER default 1,
  auto_plan_dock                INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
comment on column rabaev.RRL_WARES.spis_if_hran_no_empty
  is 'Имя ячейки, куда списать товар, когда идет размещение в непустую ячейку';
comment on column rabaev.RRL_WARES.xyz_xcov
  is 'Коэффциент ковариации Х. по умолчанию 0,1';
comment on column rabaev.RRL_WARES.xyz_ycov
  is 'Коэффициент ковариации Y. По умолчанию = 0.5';
comment on column rabaev.RRL_WARES.condition_print
  is 'Печать разрешена, если статус накладной в бух-базе больше либо равен установленного значения';
comment on column rabaev.RRL_WARES.condition_close
  is 'Закрытие разрешено, если статус накладной в бух-базе больше либо равен установленного значения';

prompt
prompt Creating table RRL_WARE_TRACKS
prompt ==============================
prompt
create table rabaev.RRL_WARE_TRACKS
(
  wtrack  VARCHAR2(50) not null,
  speedx  NUMBER default 1 not null,
  zlimit  NUMBER default 2,
  speedz  NUMBER default 0.5 not null,
  speedy  NUMBER default 1 not null,
  ware_id INTEGER default 3
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_WARE_TRACKS
  add constraint RRL_WARE_TRACKS_PK primary key (WTRACK)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RRL_WT
prompt =====================
prompt
create table rabaev.RRL_WT
(
  id              INTEGER not null,
  type1           VARCHAR2(5),
  puid            VARCHAR2(50),
  from1           VARCHAR2(50),
  to1             VARCHAR2(50),
  count1          NUMBER,
  plan_start_time DATE,
  plan_end_time   DATE,
  fact_start_time DATE,
  fact_end_time   DATE,
  worker          VARCHAR2(50),
  condtion        INTEGER default 0,
  parent_id       INTEGER,
  order1          INTEGER,
  articul         VARCHAR2(50),
  flag_last_pal   INTEGER default 0,
  flag_partial    INTEGER default 0
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RRL_WT
  add constraint RRL_WT_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_WT_I1 on rabaev.RRL_WT (CONDTION, WORKER)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_WT_I2 on rabaev.RRL_WT (TYPE1)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_WT_I5 on rabaev.RRL_WT (PUID, FROM1, TO1)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_WT_I7 on rabaev.RRL_WT (PLAN_START_TIME, PLAN_END_TIME, FACT_START_TIME, FACT_END_TIME)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
create index rabaev.RRL_WT_I8 on rabaev.RRL_WT (PARENT_ID)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table RUSERS
prompt =====================
prompt
create table rabaev.RUSERS
(
  id                          NVARCHAR2(50) not null,
  name                        NVARCHAR2(255),
  pravo_inventory_edit        INTEGER default 0,
  pravo_check_order           INTEGER default 0,
  pravo_light_inventory_check INTEGER default 0,
  deleted                     INTEGER default 0,
  pravo_razvoz_zayavok        INTEGER default 0,
  wmsuser_id                  VARCHAR2(5),
  pravo_ean_product_change    INTEGER default 0,
  pravo_karshik               INTEGER default 0,
  ware_id                     INTEGER default 1,
  pass                        VARCHAR2(50),
  pravo_admin_login           INTEGER,
  smfilepath                  VARCHAR2(1024),
  ip_server_print             VARCHAR2(50),
  user_group                  VARCHAR2(15),
  smena                       VARCHAR2(5)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.RUSERS
  add constraint RUSERS_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table SFERA_EAN
prompt ========================
prompt
create table rabaev.SFERA_EAN
(
  tmc_uid     VARCHAR2(50 CHAR) not null,
  ean_sht     VARCHAR2(20 CHAR),
  ean_bl      VARCHAR2(20 CHAR),
  ean_kor     VARCHAR2(20 CHAR),
  manualenter CHAR(1 CHAR) default 'Y',
  sht_in_bl   INTEGER not null,
  bl_in_kor   INTEGER not null,
  уид         INTEGER,
  name        VARCHAR2(255 CHAR)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating table TMP_ORDERS_PALL_VERSIONS
prompt =======================================
prompt
create global temporary table rabaev.TMP_ORDERS_PALL_VERSIONS
(
  version_id        INTEGER not null,
  ord_number        VARCHAR2(50) not null,
  maxmass           NUMBER,
  maxvol            NUMBER,
  count_of_pall     INTEGER,
  volume_of_max_pal NUMBER,
  volume_of_min_pal NUMBER
)
on commit delete rows;

prompt
prompt Creating table TMP_PALLET_ROWS
prompt ==============================
prompt
create global temporary table rabaev.TMP_PALLET_ROWS
(
  vers         INTEGER,
  order_id     INTEGER not null,
  articul      VARCHAR2(15) not null,
  ei           VARCHAR2(3),
  order_weight NUMBER,
  quantity     NUMBER not null,
  sortfield    INTEGER,
  pack_count   INTEGER,
  taresize     NUMBER,
  tareweight   NUMBER
)
on commit delete rows;

prompt
prompt Creating table USER_GROUP
prompt =========================
prompt
create table rabaev.USER_GROUP
(
  id   VARCHAR2(15) not null,
  name VARCHAR2(255)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
alter table rabaev.USER_GROUP
  add constraint USER_GROUP_PK primary key (ID)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

prompt
prompt Creating sequence MODS_SEQ
prompt ==========================
prompt
create sequence rabaev.MODS_SEQ
minvalue 0
maxvalue 999999999999999999999999999
start with 964
increment by 1
nocache;

prompt
prompt Creating sequence ORDER_MOV_HIST_ID
prompt ===================================
prompt
create sequence rabaev.ORDER_MOV_HIST_ID
minvalue 1
maxvalue 999999999999999999
start with 78
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_BILLING_SEQ
prompt =================================
prompt
create sequence rabaev.RRL_BILLING_SEQ
minvalue 0
maxvalue 999999999999999999999999999
start with 133
increment by 1
nocache;

prompt
prompt Creating sequence RRL_BILL_ORDERS_SEQ
prompt =====================================
prompt
create sequence rabaev.RRL_BILL_ORDERS_SEQ
minvalue 0
maxvalue 999999999999999999999999999
start with 32
increment by 1
nocache;

prompt
prompt Creating sequence RRL_CROSS_DOCKING_ZONES_SQ
prompt ============================================
prompt
create sequence rabaev.RRL_CROSS_DOCKING_ZONES_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 2
increment by 1
nocache;

prompt
prompt Creating sequence RRL_EVENT_ID_SQ
prompt =================================
prompt
create sequence rabaev.RRL_EVENT_ID_SQ
minvalue 5
maxvalue 999999999999999999999
start with 13608735
increment by 2
nocache
cycle;

prompt
prompt Creating sequence RRL_HISTORY_NOTE_SQ
prompt =====================================
prompt
create sequence rabaev.RRL_HISTORY_NOTE_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 51350
increment by 1
nocache;

prompt
prompt Creating sequence RRL_ORDER_PALLET_ROWS_SQ
prompt ==========================================
prompt
create sequence rabaev.RRL_ORDER_PALLET_ROWS_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 0
increment by 1
nocache;

prompt
prompt Creating sequence RRL_ORDER_ROW_SEQ
prompt ===================================
prompt
create sequence rabaev.RRL_ORDER_ROW_SEQ
minvalue 1
maxvalue 99999999999999999999999
start with 109280
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_ORDER_ROWS_SQ
prompt ===================================
prompt
create sequence rabaev.RRL_ORDER_ROWS_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 0
increment by 1
nocache;

prompt
prompt Creating sequence RRL_ORDERS_SQ
prompt ===============================
prompt
create sequence rabaev.RRL_ORDERS_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 9
increment by 1
nocache;

prompt
prompt Creating sequence RRL_PRIHOD_NAKLAD_ROWS_SQ
prompt ===========================================
prompt
create sequence rabaev.RRL_PRIHOD_NAKLAD_ROWS_SQ
minvalue 1
maxvalue 999999999999999999999999999
start with 748778
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_PRIHOD_NAKLAD_SQ
prompt ======================================
prompt
create sequence rabaev.RRL_PRIHOD_NAKLAD_SQ
minvalue 1
maxvalue 9999999999999999
start with 32776
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_PRIH_ORD_ID
prompt =================================
prompt
create sequence rabaev.RRL_PRIH_ORD_ID
minvalue 1
maxvalue 99999999999999999999999
start with 44177
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_REVISION_ROW_SQ
prompt =====================================
prompt
create sequence rabaev.RRL_REVISION_ROW_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 500
increment by 1
nocache;

prompt
prompt Creating sequence RRL_REVISION_SQ
prompt =================================
prompt
create sequence rabaev.RRL_REVISION_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 5
increment by 1
nocache;

prompt
prompt Creating sequence RRL_SBORKA_PALLET_ROWS_SQ
prompt ===========================================
prompt
create sequence rabaev.RRL_SBORKA_PALLET_ROWS_SQ
minvalue 1
maxvalue 99999999999999999999
start with 21232964
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_SBORKA_PALLETS_HISTSQ
prompt ===========================================
prompt
create sequence rabaev.RRL_SBORKA_PALLETS_HISTSQ
minvalue 1
maxvalue 9999999999999999
start with 1082187
increment by 1
nocache;

prompt
prompt Creating sequence RRL_SBORKA_PALLETS_SQ
prompt =======================================
prompt
create sequence rabaev.RRL_SBORKA_PALLETS_SQ
minvalue 0
maxvalue 99999999999999999999
start with 890543
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_SBORKA_PALL_ROWS_PARTSSQ
prompt ==============================================
prompt
create sequence rabaev.RRL_SBORKA_PALL_ROWS_PARTSSQ
minvalue 0
maxvalue 999999999999999999999999999
start with 23096
increment by 1
nocache;

prompt
prompt Creating sequence RRL_SUMMARY_PICK_LIST_ROWS_SQ
prompt ===============================================
prompt
create sequence rabaev.RRL_SUMMARY_PICK_LIST_ROWS_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 5149
increment by 1
nocache;

prompt
prompt Creating sequence RRL_SUMMARY_PICK_LIST_SQ
prompt ==========================================
prompt
create sequence rabaev.RRL_SUMMARY_PICK_LIST_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 53
increment by 1
nocache;

prompt
prompt Creating sequence RRL_TRANSPORT_PRICE_ID
prompt ========================================
prompt
create sequence rabaev.RRL_TRANSPORT_PRICE_ID
minvalue 1
maxvalue 999999999999999999999999999
start with 21202
increment by 1
nocache;

prompt
prompt Creating sequence RRL_TRANSPORT_TASK_HISTORY_SQ
prompt ===============================================
prompt
create sequence rabaev.RRL_TRANSPORT_TASK_HISTORY_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 152618
increment by 1
nocache;

prompt
prompt Creating sequence RRL_TRANSPORT_TASK_SQ
prompt =======================================
prompt
create sequence rabaev.RRL_TRANSPORT_TASK_SQ
minvalue 1
maxvalue 999999999999999999999
start with 46323
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_TR_VEHICLE_SQ
prompt ===================================
prompt
create sequence rabaev.RRL_TR_VEHICLE_SQ
minvalue 1
maxvalue 99999999999999
start with 1819
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_TR_VODITEL_SQ
prompt ===================================
prompt
create sequence rabaev.RRL_TR_VODITEL_SQ
minvalue 1
maxvalue 999999999999999
start with 2379
increment by 1
nocache
cycle;

prompt
prompt Creating sequence RRL_WT_SQ
prompt ===========================
prompt
create sequence rabaev.RRL_WT_SQ
minvalue 0
maxvalue 999999999999999999999999999
start with 5316
increment by 1
nocache;

prompt
prompt Creating sequence SFERA_EAN_ID
prompt ==============================
prompt
create sequence rabaev.SFERA_EAN_ID
minvalue 1
maxvalue 999999999999999999999999999
start with 92231
increment by 1
nocache
cycle;

prompt
prompt Creating view Z1
prompt ================
prompt
create or replace view rabaev.z1 as
select distinct 
ADDR , 
NAPR
from
RRL_SBORKA_PALLETS;

prompt
prompt Creating package COMPL
prompt ======================
prompt
create or replace package rabaev.compl is

  -- Author  : RRABAEV
  -- Created : 29.05.2011 15:39:59
  -- Purpose : Комплектация и сборка товара, деление на паллеты
  


  -- Public function and procedure declarations
  function update_seq( articul1 varchar2 , ware_id1 int , SQ1 int, SQGROUP int ) return int;
  function show_sq( articul1  varchar2 , ware_id1 int ) return int ;
  function show_sq_gr( articul1 varchar2 , ware_id1  int ) return int ;
  function divide_st_bypal( stn varchar2 , ware_id1  int ) return int ;
  function create_order_from_spallets( st_numb varchar2 , user_id1 varchar2 ) return int ;
function path( articul1 varchar2 ,  sborka_pallet_uid  varchar2 ) return varchar2 ;

  
end compl;
/

prompt
prompt Creating package DOCK_PLANNING
prompt ==============================
prompt
create or replace package rabaev.DOCK_PLANNING is

   function IS_AUTO_PLAN_DOCK(  TT_ID int) return int ;
     
   
end DOCK_PLANNING;
/

prompt
prompt Creating package GOODS_TO_PICK
prompt ==============================
prompt
CREATE OR REPLACE PACKAGE rabaev.GOODS_TO_PICK is

id1 int;
tmp int;

function delete_wtasks( summary_task_id1 int ) return int ;
 function add_summary_task( ware_id1 int)  return int ;
 function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int;
 function add_pallet_2_summary_task2(  PUID varchar2   ) return int;
 function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number;
 function get_opened_summary_task(ware_id1 int) return int;
function create_wtasks( summary_task_id1 int ) return int;
function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int ;






END GOODS_TO_PICK;
/

prompt
prompt Creating package REVIZION
prompt =========================
prompt
create or replace package rabaev.REVIZION is

  -- Author  : RRABAEV
  -- Created : 15.06.2011 10:04:49
  -- Purpose : ревизии
  

function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int , 
  count2 number , user_id3 varchar2 ) return varchar2 ;


end REVIZION;
/

prompt
prompt Creating function ADD_HISTORY_NOTE
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_HISTORY_NOTE (

  USER_ID1    VARCHAR2,
  ADDR_TO1    VARCHAR2,
  ADDR_FROM1  VARCHAR2,
  MESS1       VARCHAR2,
  PUID1       VARCHAR2,
  COUNT12     NUMBER
  
) return int
IS
ID1 int;

BEGIN
select RRL_HISTORY_NOTE_SQ.NEXTVAL into ID1 from dual;

    INSERT INTO RABAEV.RRL_HISTORY_NOTES (
  ID         ,
  USER_ID   ,
  ADDR_TO   ,
  ADDR_FROM ,
  MESS    ,
  PUID    ,
  COUNT1  , EVENTDATE
      
  ) VALUES (
          ID1,
  USER_ID1    ,
  ADDR_TO1    ,
  ADDR_FROM1  ,
  MESS1       ,
  PUID1       ,
  COUNT12  , SYSTIMESTAMP
    
    );
    
   -- SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID1;
END  ADD_HISTORY_NOTE;
/

prompt
prompt Creating function ADD_RRL_OTHOD_NAKLAD
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_OTHOD_NAKLAD(
  NAKLADNAME1           VARCHAR2      ,
  MAG_NO1               VARCHAR2      ,
  NAKLADDATE1           DATE          ,
  CREATIONDATE1         DATE          ,
  PLANNEDDELIVERYDATE1  DATE ,
  ware_id1  int

)
 RETURN INT 
 
 IS

    tmpVar int;
    nnn varchar2(50);

BEGIN
   tmpVar := 0;
   
   begin
    select ID into tmpVar from  RABAEV.RRL_OTHOD_NAKLAD  where NAKLADNAME=  NAKLADNAME1 ;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
       
            SELECT RABAEV.RRL_PRIHOD_NAKLAD_SQ.NEXTVAL INTO tmpVar FROM DUAL;
   
            INSERT INTO RABAEV.RRL_OTHOD_NAKLAD (
              ID,
              NAKLADNAME   ,
              MAG_NO       ,
              NAKLADDATE   ,
              CREATIONDATE ,
              PLANNEDDELIVERYDATE ,
              ware_id
            ) VALUES (
                  tmpVar , 
                  NAKLADNAME1   ,
                  MAG_NO1       ,
                  NAKLADDATE1   ,
                  CREATIONDATE1 ,
                  PLANNEDDELIVERYDATE1 ,
                  ware_id1
            );
           return tmpVar;
       end;
     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
   

    
commit;

   
   RETURN tmpVar;
   
   
 
       
END ADD_RRL_OTHOD_NAKLAD;
/

prompt
prompt Creating function ADD_RRL_OTHOD_NAKLAD_ROWS
prompt ===========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_OTHOD_NAKLAD_ROWS(
ID_ROW1 int ,
    ID_NAKLAD1           int      ,
    ARTICUL1 varchar,
    COUNT2  number
)
 RETURN INT 
 IS
 
tmpVar int;
ID_ROW2 int;
cond1 int;

BEGIN
   tmpVar := 0;
   ID_ROW2:=0;
   
   select CONDITION into cond1  from RABAEV.RRL_OTHOD_NAKLAD where ID=ID_NAKLAD1 ;

    if(cond1>=2 ) then
        return 0;
    end if;  
       


    begin

        select  ID into ID_ROW2  from  RABAEV.RRL_OTHOD_NAKLAD_ROWS where ARTICUL=ARTICUL1  and ID_NAKLAD=ID_NAKLAD1 ;
    exception
        WHEN NO_DATA_FOUND THEN
            ID_ROW2:=0;
            
    end;




    if( ID_ROW2=0 ) then
    
      SELECT RABAEV.RRL_PRIHOD_NAKLAD_ROWS_SQ.NEXTVAL INTO tmpVar FROM DUAL;
      INSERT INTO RABAEV.RRL_OTHOD_NAKLAD_ROWS (
          ID,
          ID_NAKLAD   ,
          ARTICUL ,
          COUNT1      
      ) VALUES (
              tmpVar , 
              ID_NAKLAD1   ,
              ARTICUL1 ,
              COUNT2    
      );

    else

        update RABAEV.RRL_OTHOD_NAKLAD_ROWS set ARTICUL=ARTICUL1 , COUNT1=COUNT2 where ID= ID_ROW2;

    end if;

   RETURN tmpVar;
    
END ADD_RRL_OTHOD_NAKLAD_ROWS;
/

prompt
prompt Creating function ADD_RRL_PRIH_NAKLAD
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_PRIH_NAKLAD (

    NAKLAD_NUMBER varchar2,
    DATE_OF_NAKLAD date,
    DATE_OF_ACCEPT date,
    POSTAVSHIK_NAME varchar2,
    SM_NAKLAD_NUMBER varchar2 ,
    ware_id1 int
) return int
IS
ID int;

BEGIN
    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD (
      ID,
    NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER , 
    ware_id
      
  ) VALUES (
          RABAEV.RRL_PRIH_ORD_ID.NEXTVAL,
           NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER ,
    ware_id1
    
    );
    
    SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD;
/

prompt
prompt Creating function ADD_RRL_PRIH_NAKLAD_ROW
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_PRIH_NAKLAD_ROW (
    NAKLAD_ID int,
    articul string,
    expiury_date date ,
    count1 NUMBER ,
    price Number
) return int
IS
ID int;

BEGIN

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
    ORDID ,
    ARTICUL ,
    EXPIRY_DATE,
    count1 ,
    price ,
    ID  
  ) VALUES (
    NAKLAD_ID ,
    articul , 
    expiury_date ,
    count1 ,
    price ,
    RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD_ROW;
/

prompt
prompt Creating function ADD_RRL_PRIH_NAKLAD_ROW2
prompt ==========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_PRIH_NAKLAD_ROW2 (
    NAKLAD_ID int,
    articul1 varchar2,
    expiury_date date ,
    count1 NUMBER ,
    price Number , 
    kolpal1 Number , 
    srok_godnosti1 int
) return int
IS
ID int;

BEGIN


delete from  RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ORDID=NAKLAD_ID and ARTICUL=articul1  ;

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
    ORDID ,
    ARTICUL ,
    EXPIRY_DATE,
    count1 ,
    price ,
    ID  ,
    kolpal ,
    srok_godnosti
  ) VALUES (
    NAKLAD_ID ,
    articul1 , 
    expiury_date ,
    count1 ,
    price ,
    RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL ,
    kolpal1 ,
    srok_godnosti1
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO ID FROM DUAL;

    return ID;
END  ADD_RRL_PRIH_NAKLAD_ROW2;
/

prompt
prompt Creating function ADD_RRL_PRIH_NAKLAD2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_PRIH_NAKLAD2 (

    NAKLAD_NUMBER varchar2,
    DATE_OF_NAKLAD date,
    DATE_OF_ACCEPT date,
    POSTAVSHIK_NAME varchar2,
    SM_NAKLAD_NUMBER varchar2 ,
    ZAKAZ_NUMBER1 varchar2,
    ware_id1 int
) return int
IS
ID int;

BEGIN
    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD (
      ID,
    NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER , 
    ZAKAZ_NUMBER ,
    ware_id
      
  ) VALUES (
          RABAEV.RRL_PRIH_ORD_ID.NEXTVAL,
           NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER ,
    ZAKAZ_NUMBER1 ,
    ware_id1
    
    );
    
    SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD2;
/

prompt
prompt Creating function ADD_RRL_TR_VEHICLE
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_TR_VEHICLE(
  ID1 int ,
  NUM1 varchar2 , 
  TR_TYPE1 varchar2 , 
  MARKA1  varchar2 ,
  REF_REJIM1 varchar2 ,
  WORKOINGNOW int ,
  PALLETS1 int , 
  LOPATA int

)
 RETURN INT 
 
 IS

    tmpVar int;
    nnn varchar2(50);

BEGIN
   tmpVar := 0;
   
   begin
   
    select ID into tmpVar from  RABAEV.RRL_TR_VEHICLE  where ID=  ID1 ;
    
    update  RABAEV.RRL_TR_VEHICLE set     NUM =  NUM1      ,
                  TR_TYPE =  TR_TYPE1  ,
                  MARKA  = MARKA1    ,
                  REF_REJIM = REF_REJIM1 , WORKING_NOW = WORKOINGNOW , PALLETS= PALLETS1 , GIDROBORT = LOPATA where  ID=  ID1 ;
    return tmpVar;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
       
            INSERT INTO RABAEV.RRL_TR_VEHICLE (

                  NUM        ,
                  TR_TYPE    ,
                  MARKA      ,
                  REF_REJIM  ,
                  WORKING_NOW  , 
                  PALLETS , 
                  GIDROBORT
                  
              ) VALUES (
                  NUM1        ,
                  TR_TYPE1    ,
                  MARKA1      ,
                  REF_REJIM1  ,
                  WORKOINGNOW ,
                  PALLETS1 , 
                  LOPATA
            );
            
            SELECT RABAEV.RRL_TR_VEHICLE_SQ.CURRVAL INTO tmpVar FROM DUAL;
           return tmpVar;
       end;

     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
   

    
commit;

   
   RETURN tmpVar;
   
   
 
       
END ADD_RRL_TR_VEHICLE;
/

prompt
prompt Creating function ADD_RRL_VOD
prompt =============================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_RRL_VOD(
 ID1              INTEGER   ,
  F1               VARCHAR2 ,
  I1               VARCHAR2 ,
  O1               VARCHAR2 ,
  DELETED1         INTEGER  ,
  SOBSTVENNYY1     INTEGER  ,
  PASSPORT1        VARCHAR2 ,
  DOVERENNOST_OT1  VARCHAR2 ,
  TRANSPORT_NUM1   VARCHAR2 ,
  ADDR1            VARCHAR2 ,
  TEL1             VARCHAR2

)
 RETURN INT 
 
 IS
    tmpVar int;
BEGIN
   tmpVar := 0;
   
   begin
   
    select ID into tmpVar from  RABAEV.RRL_TR_VODITEL  where ID=  ID1 ;
    
    update  RABAEV.RRL_TR_VODITEL 
    set 
      F=F1                ,
      I=I1                ,
      O=O1                ,
      DELETED=DELETED1           ,
      SOBSTVENNYY=SOBSTVENNYY1       ,
      PASSPORT=PASSPORT1         ,
      DOVERENNOST_OT=DOVERENNOST_OT1   ,
      TRANSPORT_NUM=TRANSPORT_NUM1    ,
      ADDR=ADDR1             ,
      TEL=TEL1   
        where ID=ID1;
                            
    return tmpVar;
   
   exception
       WHEN NO_DATA_FOUND THEN
       begin 
            SELECT RABAEV.RRL_TR_VODITEL_SQ.NextVal INTO tmpVar FROM DUAL;
            insert into  RABAEV.RRL_TR_VODITEL 
            (
                  ID                 ,
                  F                ,
                  I                ,
                  O                ,
                  DELETED           ,
                  SOBSTVENNYY       ,
                  PASSPORT         ,
                  DOVERENNOST_OT   ,
                  TRANSPORT_NUM    ,
                  ADDR             ,
                  TEL             
            )
            values 
            (
                  tmpVar                 ,
                  F1                ,
                  I1                ,
                  O1                ,
                  DELETED1           ,
                  SOBSTVENNYY1       ,
                  PASSPORT1         ,
                  DOVERENNOST_OT1   ,
                  TRANSPORT_NUM1    ,
                  ADDR1             ,
                  TEL1  
            );
            
           return tmpVar;
       end;

     WHEN OTHERS THEN
           return -1;
       RAISE;
   
   end;
       
commit;
   RETURN tmpVar;  
END ADD_RRL_VOD;
/

prompt
prompt Creating function ADD_SFERA_EAN2
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ADD_SFERA_EAN2 (

    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
) return int
IS
row_uid int;

BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    return row_uid;
END  ADD_SFERA_EAN2;
/

prompt
prompt Creating function CALC_TIMESTAMP_DIFF_IN_SECONDS
prompt ================================================
prompt
create or replace function rabaev.CALC_TIMESTAMP_DIFF_IN_SECONDS (ts1 in timestamp, ts2 in timestamp)
           return number is total_secs number;
           diff interval day(9) to second(6);
       begin
       
       diff := ts2 - ts1;
       
       total_secs := abs(extract(second from diff) + extract(minute from diff)*60 + 
        extract(hour from diff)*60*60 +
        extract(day from diff)*24*60*60
        );
        
       return total_secs;
    end CALC_TIMESTAMP_DIFF_IN_SECONDS;
/

prompt
prompt Creating function DELETE_RRL_PRIH_NAKLAD_ROW
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.DELETE_RRL_PRIH_NAKLAD_ROW (
    ROW_ID1 int
) return varchar2
IS
order_id2 int;
cond1 int;

BEGIN

select r.ORDID into order_id2 from RABAEV.RRL_PRIHOD_NAKLAD_ROWS r where ID= ROW_ID1;

select r2.CONDITION into cond1 from RABAEV.RRL_PRIHOD_NAKLAD r2 where ID  = order_id2 ;

DBMS_OUTPUT.put_line(  'DELETE_RRL_PRIH_NAKLAD_ROW' );

    if cond1 = 0 then
        delete from RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ID= ROW_ID1;
        commit;
    else
        return concat( 'naklad is closed' , order_id2 );
    end if;


    return 'ok';
END  DELETE_RRL_PRIH_NAKLAD_ROW;
/

prompt
prompt Creating function FTIME_SHIPPING_PLAN
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.ftime_shipping_plan(
STDATE date ,
SHIPPING_TIME varchar2 
 )
 RETURN date
 --По дате создания накладной и плановому времени отгрузки возвращает плановое время-дата отгрузки
 IS 
 ret date;
 STDATE1 date;
 h_hours int;


BEGIN



    STDATE1:=STDATE;
    h_hours:=0;
    ret := STDATE;
    -- ЕСЛИ КОЛИЧЕСТВО ЧАСОВ > 12 , то  День отгрузки  = STDATE + 2 
    -- ЕСЛИ КОЛИЧЕСТВО ЧАСОВ <= 12 , то  День отгрузки  = STDATE + 1 
    
    if(   to_number( substr( SHIPPING_TIME  , 0 ,2 ) ) > 20 ) then 
        STDATE1:=  STDATE ;

    else
        STDATE1:=STDATE+1;

    end if;
    
    ret := to_date( concat ( to_char( STDATE1 ) , concat( ' ' , SHIPPING_TIME ) ) , 'dd.mm.yy HH24:MI'   ) ;
    
    
    
    
    
    return ret;

exception when others then return STDATE;



END ftime_shipping_plan;
/

prompt
prompt Creating function INT2BOOL
prompt ==========================
prompt
CREATE OR REPLACE FUNCTION rabaev.int2bool(
par int
 )
 RETURN varchar2 
 IS 
 

BEGIN
    

if( par<=0 ) then

   RETURN 'false';
   
end if;

return 'true';

END int2bool;
/

prompt
prompt Creating function ISIF
prompt ======================
prompt
CREATE OR REPLACE FUNCTION rabaev.isif(
par1 int ,
par2 int 
 )
 RETURN int 
 IS 
 

BEGIN
    

if( par1 is null ) then
   RETURN 0;   
end if;
if( par2 is null ) then
   RETURN 0;   
end if;

if( par1 = par2 ) then
   RETURN 1;   
end if;

return 0;

END isif;
/

prompt
prompt Creating function MIN2
prompt ======================
prompt
CREATE OR REPLACE FUNCTION rabaev.min2(
par1 number ,
par2 number
 )
 RETURN number 
 IS 
 
BEGIN
    if( par1 > par2  ) then
       RETURN par2;
       else
       RETURN par1;
          
    end if;
return 0;
END min2;
/

prompt
prompt Creating function OBJ2NUMBER
prompt ============================
prompt
CREATE OR REPLACE FUNCTION rabaev.obj2number(
par1 number 
 )
 RETURN number 
 IS 
 

BEGIN
    
    if( par1 is null ) then
       RETURN 0;   
    end if;
    return par1;
    
exception
    when others then
    return 0;
END obj2number;
/

prompt
prompt Creating function RRL_ABC_CALCULATE
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ABC_CALCULATE( ware_id1 int  )
    RETURN int IS 
    tmpVar varchar2(255);
    ABC_A1 number;
    ABC_B1 number;
    ABC_XYZ_TIME_EDGES_IN_DAYS1 Numeric;
    Date1 Date;
    Date2 Date;
    
    sum_q number;
    sum_w number;
    sum_s number;
    
    h_sum number;
    
    cursor articul_q
    is 
    select ARTICUL , sum( QUANTITY )  Q
        from RABAEV.RRL_SBORKA_PALLET_ROWS  R ,RABAEV.RRL_SBORKA_PALLETS PP  where ( R.PALLET_UID = PP.PALLET_UID ) 
        and ( PP.CREATE_DATE >= Date1 ) and ( PP.CREATE_DATE <= Date2 ) and ( PP.WARE_ID =  ware_id1 ) 
        group by ARTICUL order by sum( QUANTITY ) DESC  ;

    
BEGIN
-- ФУНКЦИЯ ФОРМИРУЕТ ABC АНАЛИЗ ТОВАРА НА СКЛАДЕ

    Date1:=systimestamp;
    Date2:=systimestamp;

    select  ww.ABC_A , ww.ABC_B, ww.ABC_XYZ_TIME_EDGES_IN_DAYS into ABC_A1 , ABC_B1 , ABC_XYZ_TIME_EDGES_IN_DAYS1 
      from rrl_wares ww where ww.ID = ware_id1; 
     
    Date1:=systimestamp  -    ABC_XYZ_TIME_EDGES_IN_DAYS1 ;
    --DBMS_OUTPUT.put_line(  Date1 );
    --DBMS_OUTPUT.put_line(  Date2 );

    select sum( QUANTITY ) , sum(ORDER_WEIGHT) , sum( R.TARESIZE * ( R.PACK_COUNT ) )   
    into sum_q , sum_w , sum_s
    from RABAEV.RRL_SBORKA_PALLET_ROWS  R ,RABAEV.RRL_SBORKA_PALLETS PP  where ( R.PALLET_UID = PP.PALLET_UID ) 
    and ( PP.CREATE_DATE >= Date1 ) and ( PP.CREATE_DATE <= Date2 ) and ( PP.WARE_ID =  ware_id1 ) ;

    h_sum:=0;
    
    for  art_q in articul_q  loop
      --DBMS_OUTPUT.put_line( h_sum );
        h_sum:=h_sum+art_q.Q;
        update rrl_articuls set SSP= round (art_q.Q/ABC_XYZ_TIME_EDGES_IN_DAYS1 , 0 ) where ACTICUL = art_q.ARTICUL;
        if( ( h_sum / sum_q)>ABC_A1+ ABC_B1  ) then
         --  ГРУППА С
         update rrl_articuls set ABC_GROUP='C' where ACTICUL = art_q.ARTICUL;
         
        else
        
            if( ( h_sum / sum_q)>ABC_A1    ) then
             --  ГРУППА B
                update rrl_articuls set ABC_GROUP='B' where ACTICUL = art_q.ARTICUL;
            else 
            -- ГРУППА С 
                update rrl_articuls set ABC_GROUP='A' where ACTICUL = art_q.ARTICUL;
            end if;
            
        end if;
        --DBMS_OUTPUT.put_line(   art_q.ARTICUL );
    end loop;
  
 --DBMS_OUTPUT.put_line(   'конец' );
 
    RETURN 1;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_ABC_CALCULATE;
/

prompt
prompt Creating function RRL_ACCEPT_ORDER
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ACCEPT_ORDER ( order_id int )

RETURN NUMBER 
IS
tmpVar NUMBER;

cursor dddd is
   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
   
BEGIN
   tmpVar := 0;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   
 
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
   
   
   
              
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       NULL;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ACCEPT_ORDER;
/

prompt
prompt Creating function RRL_ACCEPT_ORDER2_3
prompt =====================================
prompt
create or replace function rabaev.RRL_ACCEPT_ORDER2_3 (
 order_id int ,
 user_id1 varchar2
 ) return int
is
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;
infin int;
DEFECT_PERC1 NUMBER ; 
MOD_ID1 int;

cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU , RRL_PRIHOD_NAKLAD_ROWS.DEFECT_PERC , RRL_PRIHOD_NAKLAD_ROWS.MOD_ID  
  
   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN

infin:=0;   
   DBMS_OUTPUT.put_line( 'flag 1'); 
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return 0;
   end if;
   
   DBMS_OUTPUT.put_line( 'flag 2'); 
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
    if(infin>1000) then  return 0; end if;
 
    DEFECT_PERC1:=articul_row.DEFECT_PERC ;
    MOD_ID1:= articul_row.MOD_ID ;
 
 infin:=infin+1;
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 

    while tmpVar>0 loop
          begin
        
        if(infin>1000) then  return 0; end if;
        infin:=infin+1;
    
        if( articul_row_NORMA_UKLADKI<=0 ) then
            DBMS_OUTPUT.put_line( 'null' );
            return 0;
        end if;
        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
         
            
                DBMS_OUTPUT.put_line( tmp_uid_pallet);  
    
             --delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             --delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID , kladovshik  , DEFECT_PERC , MOD_ID ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              systimestamp  , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id , user_id1 , DEFECT_PERC1 , MOD_ID1   );
              -- 
              
              
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  


--commit;

return 0;

exception 
when no_data_found then null;
when others then  RAISE;

end  RRL_ACCEPT_ORDER2_3;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

prompt
prompt Creating function RRL_ADD_INV_LINE
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ADD_INV_LINE
(

    CELL5         varchar2 , 
    articul5      varchar2 ,
    COUNT15        number ,
    date_of_expire5  date ,
    PRICE5  number ,
    inventory_id  int , 
    iser_id5 varchar2

)
 RETURN varchar2 IS
tmpVar varchar2(150);
tmp_uid_pallet varchar2(150);
new_event_id int ;

BEGIN

   tmpVar := '';
   -- СОЗДАЕМ НОВЫЙ ПАЛЛЕТ С АРТИКУЛОМ И СРОКОМ ГОДНОСТИ
   
  tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul5) ,'_G' ) , inventory_id ) , '_' ) , CELL5 )  ;
   
 /*
  begin 
  
    select UID_PALLET into tmpVar from RABAEV.RRL_PALLETS  where  UID_PALLET = tmp_uid_pallet ;


  exception
  
  WHEN NO_DATA_FOUND THEN
      */
        insert into RABAEV.RRL_PALLETS
          (
              UID_PALLET        ,
              ARTICUL           ,
              CREATION_DATE     ,
              EXPIRY_DATE       ,
              UNIT_COUNT        ,
              PRICE             ,
              PRIHOD_NAKLAD_ID  )  values 
          (
              tmp_uid_pallet , 
              articul5,
              SYSTIMESTAMP ,
              date_of_expire5 ,
              COUNT15 ,
              PRICE5 , 
              -1* inventory_id
          )  ;
  
  --end;




   -- ЗАПИСЫВАЕМ ЕГО КОЛИЧЕСТВо В ЯЧЕЙКУ
   
    SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( 
                      new_event_id ,
                      'INVENT',
                      cell5,
                      SYSTIMESTAMP , 
                      COUNT15 ,
                      1,
                      tmp_uid_pallet ,
                      iser_id5 ,
                      ( -1* inventory_id )
                      ) ;
    
   
   -- ***************************************************
   
   
   RETURN tmpVar;
  
       
END RRL_ADD_INV_LINE;
/

prompt
prompt Creating function RRL_ADD_TT_2_BILLINGORDER
prompt ===========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ADD_TT_2_BILLINGORDER(
bill_id int ,
tt_id int ,
act int -- 0 Удалить 1  Добавить
)

RETURN varchar2 IS 

tmpVar varchar2(255);
temp_company1 varchar2(255);
is_closed int;
temp_comp2 varchar2(255);
sum_of number;

BEGIN
   tmpVar := 'OK';
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.

    select ORDE.CLOSED , ORDE.COMPANY into is_closed , temp_company1 from RABAEV.RRL_BILL_ORDERS ORDE where ORDE.ID = bill_id ;
    if ( is_closed>0 ) then
    return 'Счет на оплату закрыт.';
    end if;
   
   -- Проверяем, что компания счета совпадает с компанией рейса.
 
   begin
   select VOD.DOVERENNOST_OT , PRICE into temp_comp2 , sum_of from  RABAEV.RRL_TRANSPORT_TASK T , RRL_TR_VODITEL VOD where 
     VOD.ID = T.VODITEL_ID and T.ID = tt_id and VOD.DOVERENNOST_OT = temp_company1  ;
   exception when no_data_found then return 'Компания Рейса не равна компании счета';
    when others then null;
   end;
   
   -- Проверяем, что рейс рассчитан (сумма не нулевая)
   if(sum_of<=0) then
   return 'Сумма рейса не рассчитана';
   end if;
   
   if(act=1) then
       -- Иначе добавляем рейс ко счету.   
       update  RABAEV.RRL_TRANSPORT_TASK  TT set PAY_ORDER_ID = bill_id where TT.ID=tt_id;
   else
       
       update  RABAEV.RRL_TRANSPORT_TASK  TT set PAY_ORDER_ID = null where TT.ID=tt_id;
  
   end if;
   
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'Нет такого счета или рейса';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ADD_TT_2_BILLINGORDER;
/

prompt
prompt Creating function RRL_AUTH
prompt ==========================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_AUTH
(
    login varchar2 , 
    pass1 varchar2
)
 RETURN int
  IS
tmpVar int;


BEGIN


           return -1;
select  ware_id into tmpVar  from RABAEV.RUSERS where ID = login and  PASS = pass1 and  DELETED=0 and PRAVO_ADMIN_LOGIN=1;




   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_AUTH;
/

prompt
prompt Creating function RRL_AUTH2
prompt ===========================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_AUTH2
(
    login varchar2 , 
    pass1 varchar2 ,
    version1 varchar2 
    
)
 RETURN int
  IS
tmpVar int;

BEGIN

begin
select V.ALLOW into tmpVar  from RABAEV.RRL_VERSIONS V where V.VERSION = version1 and V.ALLOW=1;
EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -3;
     WHEN OTHERS THEN
           return -4;
       RAISE;
   
end;

select  ware_id into tmpVar  from RABAEV.RUSERS where ID = login and  PASS = pass1 and  DELETED=0 and PRAVO_ADMIN_LOGIN=1;
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_AUTH2;
/

prompt
prompt Creating function RRL_BILL_ADD_TTBILL
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_BILL_ADD_TTBILL
(
   ID1 int,
   NUM1 varchar2,
   COMPANY1 varchar2,
   DATEOFORDER1 Date,
   DATEFROM1  Date,
   DATETO1  Date ,
   NUM_PLAT1 varchar2
  
   
)
 RETURN int IS
temp_is_closed int;
 aaa int;
                                                              
BEGIN

 
aaa:=0;





 if( ID1>0 ) then
 
 
     select closed into temp_is_closed from RRL_BILL_ORDERS where ID = ID1;
    
    if(temp_is_closed=1) then 
        return ID1;
    end if;
 
 
 -- Обновление?
    update RABAEV.RRL_BILL_ORDERS  set    
      NUM   =NUM1,
      COMPANY   =COMPANY1,
      DATEOFORDER  =DATEOFORDER1,
      DATEFROM     =DATEFROM1,
      DATETO       =DATETO1 ,          
    NUM_PLAT=NUM_PLAT1
    where ID=ID1 ;
 
 
  return ID1;
 
 
 else 
 

   select RRL_BILL_ORDERS_SEQ.NextVal into aaa from dual;
 
 insert into RABAEV.RRL_BILL_ORDERS ( 
  NUM   ,
      COMPANY   ,
      DATEOFORDER  ,
      DATEFROM     ,
      DATETO       ,
      ID , NUM_PLAT
 ) 
 values 
 ( 
    NUM1 , COMPANY1 , DATEOFORDER1 , DATEFROM1 , DATETO1 , aaa , NUM_PLAT1
  );
 
    return aaa;
 
 end if;

 

   RETURN 0;
 
END  RRL_BILL_ADD_TTBILL;
/

prompt
prompt Creating function RRL_BILLINGORDER_SUM
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_BILLINGORDER_sum(
bill_id int 
)

RETURN varchar2 IS 

temp1 number;
BEGIN
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
   select sum( TT.PRICE ) into temp1 from RRL_TRANSPORT_TASK TT where TT.PAY_ORDER_ID = bill_id;

   RETURN temp1;
END RRL_BILLINGORDER_sum;
/

prompt
prompt Creating function RRL_CARTON_WEIGHT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CARTON_WEIGHT (
    ART varchar2  ,
    count1 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
kart number;
BEGIN

ret:=0;
select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
--ret2:=ttt*count1;
--return ret2;
select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;


return ttt*kart;

exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;

END  RRL_CARTON_WEIGHT;
/

prompt
prompt Creating function RRL_CARTON_WEIGHT2
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CARTON_WEIGHT2
(
    ART varchar2  ,
    count1 int ,
    CURRENT_MOD_ID2 int
) return number
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
kart number;
BEGIN


-- если не указан номер МОДа, то действуем по обычной схеме

if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
    
    
    ret:=0;
    select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
    select  ( count1/ A.COUNT_SHT_IN_KOR   ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
    return round( ttt*kart , 2 );
    
else

    begin        

        select ( MS.KARTON_WEIGHT/ 1000 ) ,    ( count1/  MS.SHT_IN_KOR )    into kart , ttt
        from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
        
        return round( ttt*kart , 2) ;
        
    exception
       when NO_DATA_FOUND then 
        
        ret:=0;
        select ( CARTON_WEIGHT / 1000 ) into kart from RRL_ARTICULS A where  A.ACTICUL=ART;
        select  ( count1/ A.COUNT_SHT_IN_KOR  ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
        return round( ttt*kart , 2);
        when others then 
        return 0;
    
    end;
    
end if;


exception
when NO_DATA_FOUND then


    return 0;
    when others then 
    return 0;

END  RRL_CARTON_WEIGHT2;
/

prompt
prompt Creating function RRL_CLEAR_OTBOR_CELL
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLEAR_OTBOR_CELL(
    CELL1 varchar2 ,
    user_id1 varchar2
)
 RETURN varchar2 IS

tmpVar varchar2(250);
iii int;
otbor1 int;
first1 int;
new_event_uid int;
cursor rests is 
select UID_POLETA , REMAIN from(
select rm.UID_POLETA , rm.REMAIN from rrl_remains rm , rrl_pallets pp where rm.UID_POLETA=pp.UID_PALLET and rm.CELL=CELL1 order by pp.EXPIRY_DATE desc
)  ;

BEGIN

begin
first1:=1;
select otbor into otbor1 from rrl_cells where  cell=CELL1;
    exception when no_data_found  then return 'Такой ячейки нет';
end;

if( otbor1<>1  ) then 
    return 'Ячейка не является ячейкой отбора';
end if;

-- Для всех паллет из ячейки отбора , кроме паллета с самым большим сроком годности, спысываем остаток.
for rest in rests loop
DBMS_OUTPUT.put_line(  'flag1' );
    if( first1<>1 ) then
    
     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
     
        insert into rrl_events ( date_event ,  id_event ,  CELL_FROM   ,
          CELL_TO     ,
          COUNT_EVENT  ,
          TYPE_EVENT   ,
          UID_POLETA   ,
          USER_ID   ) values ( SYSTIMESTAMP , new_event_uid ,  cell1 , 'none' , rest.REMAIN , 3 , rest.UID_POLETA , user_id1 );
DBMS_OUTPUT.put_line(  'flag2' );

    end if;
    first1:=0;
DBMS_OUTPUT.put_line(  'flag3' );

end loop;



    
RETURN 'ok';

exception when no_data_found then return 'нет данных';
--when others then return 'ошибка2';

END  RRL_CLEAR_OTBOR_CELL;
/

prompt
prompt Creating function RRL_CLEAR_OTHOD_NAKLAD2
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLEAR_OTHOD_NAKLAD2(
    ID_NAKLAD1           int 
)
 RETURN INT 
 IS
 
tmpVar int;
cond1 int;

BEGIN
   tmpVar := 0;
   
   select CONDITION into cond1  from RABAEV.RRL_OTHOD_NAKLAD where ID=ID_NAKLAD1 ;

    if(cond1>=2 ) then
        return 0;
    end if;  

    begin
        delete from  RABAEV.RRL_OTHOD_NAKLAD_ROWS where  ID_NAKLAD=ID_NAKLAD1 ;  
    end;

commit;

   RETURN tmpVar;
    
END RRL_CLEAR_OTHOD_NAKLAD2;
/

prompt
prompt Creating function RRL_CLEAR_PRIH_NAKLAD_ROWS
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLEAR_PRIH_NAKLAD_ROWS (
    NAKLAD_ID int
) return int
IS
ID2 int;

BEGIN

    select condition into ID2 from RABAEV.RRL_PRIHOD_NAKLAD where ID = NAKLAD_ID;
    
    if ID2=0 then
        delete from RABAEV.RRL_PRIHOD_NAKLAD_ROWS where ORDID = NAKLAD_ID ;
        return 1;
    end if;
    
    return 0;
END  RRL_CLEAR_PRIH_NAKLAD_ROWS;
/

prompt
prompt Creating function RRL_CLOSE_BILLINGORDER
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLOSE_BILLINGORDER(
bill_id int ,
act int -- 0 ОТкрыть 1  Закрыть
)

RETURN varchar2 IS 

tmpVar varchar2(255);
temp_company1 varchar2(255);
is_payed int;
temp_comp2 varchar2(255);

BEGIN
   tmpVar := 'OK';
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
if(act=0) then
    select ORDE.PAYED   into  is_payed    from RABAEV.RRL_BILL_ORDERS ORDE where ORDE.ID = bill_id ;
    if ( is_payed>0 ) then
    return 'Счет на оплату уже был оплачен.';
    end if;
   
end if;

  update RABAEV.RRL_BILL_ORDERS set closed=act    where ID = bill_id ;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'Нет такого счета или рейса';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_CLOSE_BILLINGORDER;
/

prompt
prompt Creating function RRL_CLOSE_OTHOD_NAKLAD
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLOSE_OTHOD_NAKLAD
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    naklad_num int ,
    iser_id21 varchar2 
)
 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);


cursor rowss is 
select * from RABAEV.RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD = naklad_num ;

--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS left join RABAEV.RRL_PALLETS on 
    RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET  
    where RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  order by RRL_PALLETS.EXPIRY_DATE  ; 


BEGIN

EXPEDITION_CELL:= concat( 'EX_' , naklad_num );
DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar from RABAEV.RRL_OTHOD_NAKLAD where ID = naklad_num;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;

/*
При закрытии отгрузочной накладной:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


for naklad_row in rowss loop

tmpVar:=0;
kolvo_otbora:=naklad_row.COUNT1;


    DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА НАКЛАДНОЙ!' );
   DBMS_OUTPUT.put_line(  naklad_row.ARTICUL );

    select CELL into  current_cell from  RABAEV.RRL_ARTICULS 
    where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;
    
    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );
    DBMS_OUTPUT.put_line(  current_cell );
    

    for  ddd8 in rests_in_cell loop
-- REMAIN
    
        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );
        DBMS_OUTPUT.put_line(   ddd8.REMAIN );
        DBMS_OUTPUT.put_line(   ddd8.EXPIRY_DATE );
        DBMS_OUTPUT.put_line(   ddd8.UID_POLETA );
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  
          
        
        if(kolvo_otbora>0) then
/*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
        
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла  
*/          
            if(kolvo_otbora <= ddd8.REMAIN )  then
                -- UID_POLETA
                
                
                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                    kolvo_otbora:=0;
                else
                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id,
                      current_cell, 
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      ddd8.REMAIN ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                      
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
                
            end if;      

   
        end if;
    end loop;


         DBMS_OUTPUT.put_line(  '  почти конец ' );   
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  

--если Количество_отбора > 0 
--    Делаем проводку из ячейки 'excess' на отгрузочную накладную
--Количество_отбора  = 0
--конец если
if(kolvo_otbora >0 )  then
                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      'EXCESS',
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                     concat( 'EXCESS_' , naklad_row.ARTICUL ) ,
                      iser_id21 ,
                      naklad_num
                      ) ;
kolvo_otbora:=0;
end if;

   DBMS_OUTPUT.put_line(  '  почти конец ' );   

end loop;

update  RABAEV.RRL_OTHOD_NAKLAD set condition = 2  where ID = naklad_num;
   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   


commit;

   RETURN 'ok';
END RRL_CLOSE_OTHOD_NAKLAD;
/

prompt
prompt Creating function RRL_CLOSE_OTHOD_PALLET
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_CLOSE_OTHOD_PALLET
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    PALLET_ID1 varchar2 ,
    iser_id21 varchar2 
)

 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);
PALLET_ROW_ID1 int;


-- Курсор со строками паллета, для которых не выбрана партия .
cursor rowss is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 and PRIHOD_PALLET_UID is null ;

-- Курсор со строками паллета, для которых  выбрана партия .
cursor rowss2 is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 and not( PRIHOD_PALLET_UID is null );


--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS , RABAEV.RRL_PALLETS  
     
    where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and
     RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  
     order by RRL_PALLETS.EXPIRY_DATE  ; 

BEGIN

DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar from RABAEV.RRL_SBORKA_PALLETs where PALLET_UID = PALLET_ID1;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;


for naklad_row2 in rowss2 loop


    PALLET_ROW_ID1:= naklad_row2.ID;
    kolvo_otbora:=naklad_row2.QUANTITY;
    select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row2.ARTICUL ; 
    SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      3,
                      naklad_row2.PRIHOD_PALLET_UID ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
    DBMS_OUTPUT.put_line( concat( concat( naklad_row2.ARTICUL , ' списание для определенной партии ' ) ,naklad_row2.PRIHOD_PALLET_UID ) );
    
end loop;

/*
При закрытии отгрузочной паллеты:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на строку паллета в количестве Количество_отбора  
                Количество_отбора  =0 
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


for naklad_row in rowss loop

PALLET_ROW_ID1:= naklad_row.ID;
tmpVar:=0;
kolvo_otbora:=naklad_row.QUANTITY;

   DBMS_OUTPUT.put_line(  concat( 'НОВАЯ СТРОКА ПАЛЛЕТЫ ОТГРУЗКИ!' , naklad_row.ARTICUL ) );
   select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ; 
   DBMS_OUTPUT.put_line( concat( 'ЯЧЕЙКА ОТБОРА=' , current_cell ) );

 

    for  ddd8 in rests_in_cell loop  -- ЦИКЛ ПО ОСТАТКАМ В ЯЧЕЙКЕ ОТБОРА 
    
        update RABAEV.RRL_SBORKA_PALLET_ROWS set PRIHOD_PALLET_UID = ddd8.UID_POLETA where ID = naklad_row.ID ; 
        update RABAEV.RRL_SBORKA_PALLET_ROWS set EXPIRY_DATE = ddd8.EXPIRY_DATE where ID = naklad_row.ID ; 
        
        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );
        DBMS_OUTPUT.put_line(  ddd8.REMAIN );
        DBMS_OUTPUT.put_line(  ddd8.EXPIRY_DATE );
        DBMS_OUTPUT.put_line(  ddd8.UID_POLETA );
        DBMS_OUTPUT.put_line(  '  количество отбора1= ' );     
        DBMS_OUTPUT.put_line(  kolvo_otbora );  
          
        
        if(kolvo_otbora>0) then
/*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если
        конец цикла  
*/          
            DBMS_OUTPUT.put_line(  CONCAT( 'REMAIN = ' , to_char( ddd8.REMAIN ) ) );
            if(kolvo_otbora <= ddd8.REMAIN )  then
               
                
                
                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      3,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
                    kolvo_otbora:=0;
                else
                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id,
                      current_cell, 
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      ddd8.REMAIN ,
                      3,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
                      
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
                
            end if;      

   
        end if;
    end loop;


         DBMS_OUTPUT.put_line(  '  почти конец ' );   
         DBMS_OUTPUT.put_line(  '  количество отбора2= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  

--если Количество_отбора > 0 
--    Делаем проводку из ячейки 'excess' на отгрузочную накладную
--Количество_отбора  = 0
--конец если
if(kolvo_otbora >0 )  then
                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          PALLET_ROW_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      'MINUS',
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      3,
                      'MINUS'   ,
                      iser_id21 ,
                      PALLET_ROW_ID1
                      ) ;
kolvo_otbora:=0;
end if;

   DBMS_OUTPUT.put_line(  '  почти конец ' );   

end loop;

update   RABAEV.RRL_SBORKA_PALLETs  set condition = 2  where   PALLET_UID = PALLET_ID1;




   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   
   RETURN 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_CLOSE_OTHOD_PALLET;
/

prompt
prompt Creating function RRL_COPY_PALLET_ROW2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_COPY_PALLET_ROW2(
    row_id2 int ,
    count1  number , 
    PALLET_UID_NEW    VARCHAR2 
 )
 
 RETURN int 
 IS 
 
 ID1 int;
  PALLET_UID1    VARCHAR2(255) ;
  ARTICUL1       VARCHAR2(255) ;
  SHORTNAME1     VARCHAR2(1255) ;
  SHTRIHKOD1     VARCHAR2(255) ;
  EI1            VARCHAR2(255) ;
  TAREWEIGHT1    NUMBER;
  PATH1          VARCHAR2(1255) ;
  ORDER_WEIGHT1  NUMBER;
  TARESIZE1      NUMBER;
 QUANTITY1       NUMBER;
  SORTFIELD1     INTEGER;
  AUCTION1       VARCHAR2(255);
  DOCID1         VARCHAR2(255) ;
  ORIGINAL_QUANTITY1 number;
   ORIGINAL_ORDER_WEIGHT1 number;
  ware_id1 int ;
  PACK_COUNT1 int;
 

BEGIN
  
if( count1<=0) then 
    return 0;
end if;

--------------------------------------------------------------------------------------------
 

      select  PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT  into 
              
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1 ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 , 
              ORIGINAL_QUANTITY1 ,
              ORIGINAL_ORDER_WEIGHT1     
              from RABAEV.RRL_SBORKA_PALLET_ROWS where ID= row_id2 ;



SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID_NEW    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              (count1* ORIGINAL_ORDER_WEIGHT1/ORIGINAL_QUANTITY1 )  ,
              TARESIZE1      ,
              count1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              ORIGINAL_QUANTITY1,
              ORIGINAL_ORDER_WEIGHT1
            );

 
   
--update   RABAEV.RRL_SBORKA_PALLET_ROWS set QUANTITY = QUANTITY - count1 where ID = row_id2  ; 
--------------------------------------------------------------------------------------------

   RETURN ID1;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_COPY_PALLET_ROW2;
/

prompt
prompt Creating function RRL_COUNT_KOR
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_COUNT_KOR (
    ART varchar2  ,
    count1 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
BEGIN

ret:=0;
--select CARTON_WEIGHT into ttt from RRL_ARTICULS A where  A.ACTICUL=ART;
--ret2:=ttt*count1;
--return ret2;
select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;


return ttt;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
END  RRL_COUNT_KOR;
/

prompt
prompt Creating function RRL_COUNT_KOR2
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_COUNT_KOR2 (
    ART varchar2  ,
    count1 int ,
     CURRENT_MOD_ID2 int
) return int
-- КОЛИЧЕСТВО КОРОБОК 
IS
ttt number;
ret int;
ret2 number;
BEGIN




    if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
        

            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
        
    else    

                select    round ( count1/  MS.SHT_IN_KOR ,0 )    into  ttt
                from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
                
                return ttt;
                
           
    end if;

-- =============================================================================

return ttt;
exception
when NO_DATA_FOUND then
            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
    when others then 
    return 0;
END  RRL_COUNT_KOR2;
/

prompt
prompt Creating function RRL_COUNT_KOR3
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_COUNT_KOR3 (
    ART varchar2  ,
    count1 int ,
    pallet_uid1 varchar2
) return int
-- Определение количества коробок на основании прихода. 
IS
ttt number;
ret int;
ret2 number;
CURRENT_MOD_ID2 int;
BEGIN

begin
    
    select pal.MOD_ID into  CURRENT_MOD_ID2 from rrl_pallets pal where pal.UID_PALLET=  pallet_uid1  ;
    
    
    
exception
when NO_DATA_FOUND then 
CURRENT_MOD_ID2:=0;
when others then 
CURRENT_MOD_ID2:=0;
end;


    if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
        

            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
        
    else    

                select    round ( count1/  MS.SHT_IN_KOR ,0 )    into  ttt
                from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
                
                return ttt;
                
           
    end if;

-- =============================================================================

return ttt;
exception
when NO_DATA_FOUND then
            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
    when others then 
    return 0;
END  RRL_COUNT_KOR3;
/

prompt
prompt Creating function RRL_COUNT_KOR4
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_COUNT_KOR4 (
    count1 int ,
    pallet_uid1 varchar2
) return int
-- Определение количества коробок на основании прихода. 
IS
ART varchar2(255)  ;
ttt number;
ret int;
ret2 number;
CURRENT_MOD_ID2 int;
BEGIN

begin
    
    select pal.MOD_ID , pal.ARTICUL into  CURRENT_MOD_ID2 , ART  from rrl_pallets pal where pal.UID_PALLET=  pallet_uid1  ;
    
    
    
exception
when NO_DATA_FOUND then 
CURRENT_MOD_ID2:=0;
return 0;
when others then 
CURRENT_MOD_ID2:=0;
return 0;
end;


    if ( (  CURRENT_MOD_ID2 is null ) or (CURRENT_MOD_ID2=0) )  then
        

            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
        
    else    

                select    round ( count1/  MS.SHT_IN_KOR ,0 )    into  ttt
                from RRL_ARTICUL_MODS MS where  ( ( MS.ID = CURRENT_MOD_ID2 ) and ( MS.ARTICUL = ART ) ) ;
                
                return ttt;
                
           
    end if;

-- =============================================================================

return ttt;
exception
when NO_DATA_FOUND then
            select round ( count1/ A.COUNT_SHT_IN_KOR ,0 ) into ttt from RRL_ARTICULS A where  A.ACTICUL=ART and A.COUNT_SHT_IN_KOR>0;
            return ttt;
    when others then 
    return 0;
END  RRL_COUNT_KOR4;
/

prompt
prompt Creating function RRL_DAY_DISTRIBUTE_ENDS
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_DAY_DISTRIBUTE_ENDS
(
    articul1 varchar2 ,
    exp_date1 date 
  
)
 RETURN Date IS
-- Возвращает 1, если товар уже нельзя распределять.

tmpVar varchar(1250);
days_left interval day(5) TO SECOND;
days_left1 number;
days_best_before number;
perc1 number ;
perc2 int;
final_day     Date;                                                                          
             ware_id1 int ;                                                                    
BEGIN


ware_id1:=3;

begin 
-- По артикулу определяем склад
    select  rrl_cells.WARE_ID into ware_id1 from rrl_articuls , rrl_cells where rrl_cells.CELL = rrl_articuls.CELL and rrl_articuls.acticul = articul1 ;
exception   
            when no_data_found then null;
            when others then null;
end;


    tmpVar := '';
    select rrl_articuls.BESTBEFOREDAYS into days_best_before from rrl_articuls where acticul =  articul1                  ;
    days_left :=    (  exp_date1 - SYSTIMESTAMP ) ;
    days_left1:= extract( day from ( days_left  ) )  ;
    

 DBMS_OUTPUT.put_line( concat( 'ware_id =' , ware_id1 ) );
     
-- Пробуем найти настройки срока годности в таблице RABAEV.RRL_WARE_DISTR_TIME_PARAM

begin 



select PP.DISTR_PERC into perc1 from     RABAEV.RRL_WARE_DISTR_TIME_PARAM PP where 
    PP.WARE_ID = ware_id1 and ( days_best_before<=PP.TIME_PERC_TO ) and ( days_best_before > PP.TIME_PERC_FROM ) and ROWNUM<=1;
exception when no_data_found then perc1:=33.33;
    
end ;
    


 DBMS_OUTPUT.put_line( 'exp_date1 =' );
 DBMS_OUTPUT.put_line( exp_date1  );


 DBMS_OUTPUT.put_line( 'days_best_before =' );
 DBMS_OUTPUT.put_line( days_best_before  );

 DBMS_OUTPUT.put_line( 'days_left1 =' );
 DBMS_OUTPUT.put_line( days_left1  );

 DBMS_OUTPUT.put_line( 'perc1=' );
 DBMS_OUTPUT.put_line( perc1 );
 DBMS_OUTPUT.put_line( '--------------------' );

final_day  := exp_date1 -    ( days_best_before*( perc1)/100 );


   RETURN final_day ;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  null ;
     WHEN OTHERS THEN
       RETURN null;
       
END  RRL_DAY_DISTRIBUTE_ENDS;
/

prompt
prompt Creating function RRL_DELETE_CELL
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_DELETE_CELL(
cell4 varchar2 
)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_REMAINS C where C.CELL=cell4;
        
        
        
        
        
    exception
    when NO_DATA_FOUND THEN
            delete from RABAEV.RRL_CELLS   where CELL=cell4 and IS_SYSTEM<>1 ;
                
            WHEN OTHERS THEN
                   null;
    end;


 RETURN 1;
   
  
END RRL_DELETE_CELL;
/

prompt
prompt Creating function RRL_DELETE_OPALLET
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_DELETE_OPALLET(
    PALLET_ID1 varchar2 
)
 RETURN varchar2 IS

tmpVar varchar2(250);
iii int;

BEGIN

    select count(ID) into iii from RRL_SBORKA_PALLET_ROWS R where R.PALLET_UID = PALLET_ID1;
    if(iii>0) then
        return 'not_empty';
    else
        delete from  RRL_SBORKA_PALLETS where PALLET_UID = PALLET_ID1 ;
    end if;
    
RETURN 'ok';
END RRL_DELETE_OPALLET;
/

prompt
prompt Creating function RRL_DELETE_ST
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_DELETE_ST(
ST_NUMBER1 varchar2 
)
 RETURN varchar2 IS
tmpVar varchar2(250);

cursor pallets is select PALLET_UID from RRL_SBORKA_PALLETS where ST_NUMBER  like concat( ST_NUMBER1 , '%' ) ;--and ( ( TRANSTASK_ID=0 )  or ( TRANSTASK_ID is null ) ) 


BEGIN




for roww in pallets loop

   DBMS_OUTPUT.put_line(   roww.PALLET_UID  );
   delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID= roww.PALLET_UID ;
        
end loop;


delete from  RRL_SBORKA_PALLETS where ST_NUMBER like concat( ST_NUMBER1 , '%' ) ; -- and ( ( TRANSTASK_ID=0 )  or ( TRANSTASK_ID is null ) ) ;

 RETURN 'ok';
   
  
END RRL_DELETE_ST;
/

prompt
prompt Creating function RRL_GET_CELL_REMAIN
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_CELL_REMAIN( cell_id varchar2 )
 RETURN NUMBER IS 
tmpVar NUMBER;
BEGIN
   tmpVar := 0;
   select sum( REMAIN ) into tmpVar from RRL_REMAINS where CELL = cell_id group by CELL;
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_CELL_REMAIN;
/

prompt
prompt Creating function RRL_GET_MOD_INFO
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_MOD_INFO( mod_id int )
 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := '';
   
   select  NAME  into tmpVar from RRL_ARTICUL_MODS where ID = mod_id  ;
   
   if(tmpVar is null) then
   tmpVar:='';
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '-';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_MOD_INFO;
/

prompt
prompt Creating function RRL_GET_PAL_INFOTEXT
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_PAL_INFOTEXT(
    PALLET_UID1 varchar2  
) return varchar2
IS
 
addr1 varchar2(50);
prooved1 int;
prooved_by_scan1 int;
zone1 varchar2(200);
trans1 varchar2(200) ;
dock1 varchar2(200);
wave1 varchar2(200); 
ret varchar2(2024);

BEGIN

ret:='';
select P1.ADDR , P1.PROOVED , P1.PROOVED_BY_SCAN ,  TT1.DOCK , P1.ZONE , TT1.TRANSPORT , TT1.WAVE
into  addr1 , prooved1 , prooved_by_scan1 , dock1 , zone1 , trans1 ,  wave1 
  from  RABAEV.RRL_SBORKA_PALLETS  P1 , RRL_TRANSPORT_TASK TT1  where  P1.TRANSTASK_ID = TT1.ID (+) and  PALLET_UID=PALLET_UID1  ; 


ret := concat(  concat( ret , 'ЗОНА:' ) , zone1 ); 
ret := concat(  concat( ret , ' ВРЕМЯ:' ) , wave1 ); 
ret := concat(  concat( ret , ' ДОК:' ) , dock1 ); 
ret := concat(  concat( ret , ' ТРАН:' ) , trans1 ); 

--ret := concat(  concat( ret , '   АДРЕС=' ) , addr1 );




return  ret;
exception
when NO_DATA_FOUND then
    return '';
    when others then 
    return '';
    
END  RRL_GET_PAL_INFOTEXT;
/

prompt
prompt Creating function RRL_GET_PALLET_CHECK_TIMES
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_PALLET_CHECK_TIMES( puid varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor dddd is
select to_char(time1 , 'dd.mm.yyyy HH24:MI:SS' ) time2, weight , user_id from RRL_SBORKA_PALLETS_HISTORY where ( PALLET_UID = puid ) and event='WEIGHT_CHECK' ;


BEGIN
   tmpVar := '';
   
   for f in dddd loop
        
    tmpVar:=concat(concat(Concat(concat(tmpVar  , concat( f.time2 , concat( ' = ' ,  f.weight ))) , 'u='  ) , f.user_id ) , ' ;');
   
   end loop;
   

   --select Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) )  into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   if(tmpVar is null) then
   tmpVar:='НЕ ПРОВЕРЯЛСЯ';
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ПРОВЕРЯЛСЯ';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return tmpVar;
       RAISE;
END RRL_GET_PALLET_CHECK_TIMES;
/

prompt
prompt Creating function RRL_GET_PALLET_ROWS_COUNT
prompt ===========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_PALLET_ROWS_COUNT( puid varchar2 )
 RETURN int IS 

ret int;


BEGIN

select count(ID) into ret from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = puid; 
   
   RETURN ret;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       return 0;
       RAISE;
END RRL_GET_PALLET_ROWS_COUNT;
/

prompt
prompt Creating function RRL_GET_SBORKA_PALLET_TIME
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_SBORKA_PALLET_TIME
 ( puid varchar2 )
 RETURN DATE  IS 
 tmp date;
BEGIN

 tmp:=null;
 
 select min(TIME1) into tmp from RRL_SBORKA_PALLETS_HISTORY where  PALLET_UID=puid;
 
 
 
RETURN tmp;

EXCEPTION
  WHEN NO_DATA_FOUND THEN
       RETURN null;
  WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN null;
END RRL_GET_SBORKA_PALLET_TIME;
/

prompt
prompt Creating function RRL_GET_ST_CHECK_TIMES
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_ST_CHECK_TIMES( st_id varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor dddd is
select to_char( max(time1) , 'dd.mm.yyyy HH24:MI:SS')   time2 ,  H.user_id  from RRL_SBORKA_PALLETS_HISTORY H , RRL_SBORKA_PALLETS P
        where ( H.PALLET_UID=P.PALLET_UID )   and  ( P.ST_NUMBER like concat( '%' , concat( st_id , '%' ) ) ) and event='WEIGHT_CHECK'
        group by   H.user_id
         ;


BEGIN
   tmpVar := '';
   
   for f in dddd loop
        
    tmpVar:=concat(concat(tmpVar  , concat( f.time2 , concat( ' = ' ,  f.user_id  ))) , ' ;');
   
   end loop;
   

   --select Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) )  into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   if(tmpVar is null) then
   tmpVar:='НЕ ПРОВЕРЯЛСЯ';
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ПРОВЕРЯЛСЯ';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return tmpVar;
       RAISE;
END RRL_GET_ST_CHECK_TIMES;
/

prompt
prompt Creating function RRL_GET_ST_IS_SCANNED
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_ST_IS_SCANNED( st_number1 varchar2 )
 RETURN number IS 
tmpVar number;
itogo number ;
ret number ;
BEGIN
--   tmpVar := '';
   
   select count( PAL.PROOVED_BY_SCAN ) into tmpVar from RRL_SBORKA_PALLETS PAL where PAL.ST_NUMBER = st_number1 and  PAL.PROOVED_BY_SCAN=1 ;   
   select count( PAL.PROOVED_BY_SCAN ) into itogo from RRL_SBORKA_PALLETS PAL where PAL.ST_NUMBER = st_number1  ;   
   ret:= round( 100*tmpVar/itogo ,0 ) ;
   RETURN ret ;
   
   EXCEPTION 
     WHEN NO_DATA_FOUND THEN 
       RETURN 0; 
     WHEN OTHERS THEN 
       -- Consider logging the error and then re-raise 
       RAISE; 
END RRL_GET_ST_IS_SCANNED;
/

prompt
prompt Creating function RRL_GET_TT_INFO
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_TT_INFO( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := 'пусто';
   
   select 
   concat(
   Concat( Concat( Concat ( concat( TRANSTYPE , concat( ' [' , TRANSPORT ) ) , concat( '] ' , to_char(SHIPMENT_DATE) )  ) , '-' ) , to_char( tt_id) ) ,  
   concat( ' D=', DOCK )
   )
   into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;
   
   
   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'пусто';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_INFO;
/

prompt
prompt Creating function RRL_GET_TT_PRICE_ID
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_TT_PRICE_ID
 ( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

cursor ss is
select DISTINCT upper(ADDR1.REGION) REGION , upper(ADDR1.RAION) RAION  from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id
order by upper(ADDR1.REGION) , upper(ADDR1.RAION) ;

BEGIN
   tmpVar := '[]';
   
   select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tmpVar from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
   
   for s in ss  loop
   
    tmpVar:= Concat( Concat( concat( concat( tmpVar , upper( trim( s.REGION) ) )  , '-') , upper( trim(s.RAION) )) , ';' ) ;
   
   end loop;
 
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'no_transp_task';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_PRICE_ID;
/

prompt
prompt Creating function RRL_GET_TT_PRICE_ID2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_TT_PRICE_ID2
 ( tt_id int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);

--  

cursor ss is
select DISTINCT upper(ADDR1.REGION) REGION    from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id
order by upper(ADDR1.REGION)   ;

BEGIN
   tmpVar := '[]';
   
   select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tmpVar from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
   
   for s in ss  loop
   
    tmpVar:= Concat(  concat( tmpVar ,   s.REGION    ) , ';' ) ;
   
   end loop;
 
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'no_transp_task';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_TT_PRICE_ID2;
/

prompt
prompt Creating function RRL_TT_ADDR_COUNT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ADDR_COUNT( TTID int )
 RETURN int IS 
    tmpVar int;
BEGIN

select count( distinct RRL_SBORKA_PALLETS.ADDR  ) into tmpVar
from RABAEV.RRL_SBORKA_PALLETS,  RABAEV.RRL_ADDR  
where TRANSTASK_ID=TTID   ;
   
if(tmpVar=0 ) then 
return 0;
end if;

   RETURN tmpVar-1;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 0;
       RAISE;
END RRL_TT_ADDR_COUNT;
/

prompt
prompt Creating function RRL_GET_TT_PRICE
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_TT_PRICE
 ( tt_id int )
 RETURN number IS 
price_id1 varchar2(1024);
company_name varchar2(255);
price1 number;
price_hours number;
hours1 number;
tr_type1 varchar(15);
PRICE_FOR_ADDR1 number;
special_price1 int; -- Рассчет Строго по специальному прайсу
address_premio  int;
BEGIN
price1:=0;
price_hours:=0;
hours1:=0;
special_price1:=0;
address_premio :=0;
tr_type1 := '[]';
select concat( '[' , concat(  TTT.TRANSTYPE , ']' ) ) into  tr_type1 from RRL_TRANSPORT_TASK TTT where ID = tt_id  ;
  

   
   DBMS_OUTPUT.put_line(  tr_type1 ); 
   price_id1 :=  RRL_GET_TT_PRICE_ID( tt_id )  ;
   DBMS_OUTPUT.put_line(  price_id1 ); 
   company_name:='';
   -- Определяем  КОМПАНИЮ 
   begin 
   DBMS_OUTPUT.put_line(  'flag1' ); 
    select   VOD.DOVERENNOST_OT , RRL_TT.HOURS into company_name , hours1  from RRL_TRANSPORT_TASK RRL_TT , RRL_TR_VODITEL VOD
        where   RRL_TT.VODITEL_ID = VOD.ID and RRL_TT.ID = tt_id ;
        -- По собственному транспорту биллинг не ведем
        DBMS_OUTPUT.put_line(  'flag2' ); 
        DBMS_OUTPUT.put_line( concat( 'КОМПАНИЯ=' , company_name ) );
        --if( company_name='МОНЕТКА' ) then 
        --return 0;
        --end if;
        
         select CC.SPECIAL_PRICE into special_price1 from RABAEV.RRL_BILL_COMPANY CC where CC.COMPANYNAME =  company_name ;
        
   exception 
     WHEN NO_DATA_FOUND THEN 
     DBMS_OUTPUT.put_line(  'Не найден водитель, либо рейс. '  );
      return 0;
      wHEN OTHERS THEN  DBMS_OUTPUT.put_line(  ' Неизвестная ошибка '  ); return 0;
   end;
   
   DBMS_OUTPUT.put_line(  company_name  ); 

   if( company_name='' ) then 
   return 0;
   end if;
      
      DBMS_OUTPUT.put_line( 'flag 4' );
      
   begin
   -- СНАЧАЛА ПРОБУЕМ НАЙТИ ПРАЙС СООТВЕТСТВУЮЩИЙ  РАЙОНУ+СОМПАНИИ
    DBMS_OUTPUT.put_line( 'flag 7' );
       
     select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR into price1 , price_hours , PRICE_FOR_ADDR1 from RABAEV.RRL_TRANSPORT_PRICE PR 
     where PR.PRICE_NAME=price_id1 and PR.COMPANY=company_name and rownum<=1 ;
     
     address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))     where ID = tt_id  ;     
     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
           
           
   exception 
        WHEN NO_DATA_FOUND THEN
        begin
        
            DBMS_OUTPUT.put_line( 'flag 3' );
        
            -- ЗАТЕМ ПРОСТО РАЙОНУ 
            select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR  into price1 , price_hours, PRICE_FOR_ADDR1 from RRL_TRANSPORT_PRICE PR 
            where PR.PRICE_NAME=price_id1 and ( PR.COMPANY is null or PR.COMPANY=''  ) and special_price1=0 and rownum<=1 ;
            DBMS_OUTPUT.put_line( price1 );   
            DBMS_OUTPUT.put_line( price1 + hours1 * price_hours );  
            
            address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
            update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
            return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
            
             
        exception
            WHEN NO_DATA_FOUND THEN
            begin
            price_id1 :=  RRL_GET_TT_PRICE_ID2( tt_id )  ;
               DBMS_OUTPUT.put_line(  price_id1 );
             -- ЗАТЕМ РЕГИОНУ+КОМПАНИИ 
                select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR   into price1 , price_hours , PRICE_FOR_ADDR1 
                from RRL_TRANSPORT_PRICE PR where PR.PRICE_NAME=price_id1 and PR.COMPANY=company_name  and rownum<=1  ;
                
                
                address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
                update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                
             -- ЗАТЕМ ПРОСТО РЕГИОНУ.
             exception 
             WHEN NO_DATA_FOUND THEN
                begin
                    select  PR.PRICE , PR.PRICE_FOR_HOURS , PR.PRICE_FOR_ADDR   into price1 , price_hours , PRICE_FOR_ADDR1 
                    from RRL_TRANSPORT_PRICE PR where PR.PRICE_NAME=price_id1 and ( PR.COMPANY is null or PR.COMPANY='' ) and special_price1=0
                     and rownum<=1 ;
                  
                     address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
                     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                   
                exception
                WHEN NO_DATA_FOUND THEN
                    --  ТЕПЕРЬ БЕЖИМ ПО СПИСКУ РЕГИОНОВ МАРШРУТА и ПОЛУЧАЕМ МАКСИМАЛЬНУЮ ЦЕНУ ИЗ СПИСКА.
                    
                    begin 
                    DBMS_OUTPUT.put_line( 'flag -1' );
                    select  max( PR.PRICE) , max( PR.PRICE_FOR_HOURS), max( PR.PRICE_FOR_ADDR )  into price1 , price_hours ,  PRICE_FOR_ADDR1  
                    from  RRL_TRANSPORT_PRICE PR ,  (
                    select DISTINCT  Concat (Concat( tr_type1 , upper(ADDR1.REGION) ) , ';')  REGION   from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  
                    where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id ) REG 
                    where PR.PRICE_NAME=REG.REGION and PR.COMPANY=company_name having count(PR.PRICE)>=1
                     ;
                     
                    address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)  )) ;
                    update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))   where ID = tt_id  ;     
                    return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                    
                    exception 
                        WHEN NO_DATA_FOUND THEN
                        begin
                        
                                DBMS_OUTPUT.put_line( 'flag 1' );
                                
                                select  max( PR.PRICE) , max( PR.PRICE_FOR_HOURS) , max( PR.PRICE_FOR_ADDR )  into price1 , price_hours ,  PRICE_FOR_ADDR1   from  RRL_TRANSPORT_PRICE PR ,  (
                                select DISTINCT  Concat (Concat( tr_type1 , upper(ADDR1.REGION) ) , ';')  REGION   from RRL_SBORKA_PALLETS PPP , RRL_ADDR ADDR1  
                                where PPP.ADDR=ADDR1.ADDR and PPP.TRANSTASK_ID = tt_id ) REG 
                                where PR.PRICE_NAME=REG.REGION and ( PR.COMPANY is null or PR.COMPANY='' ) and special_price1=0
                                 having count(PR.PRICE)>=1 ;
                                  
                               address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)  )) ;
                                update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO =((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id)+1 ))    where ID = tt_id  ;     
                                return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
                                
                                exception
                                WHEN NO_DATA_FOUND THEN return 0;
                        end;
                        when others then return 0;
                    end;
                    
                    return 0;
                  when others then return 0;  
                    
                end;
             
            end;
        end;
   end;
      
   
   address_premio:= ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )) ;
     update  RRL_TRANSPORT_TASK set PAY_REGION=price_id1 , ADDR_PREMIO = ((obj2number( PRICE_FOR_ADDR1 ))*( RRL_TT_ADDR_COUNT(tt_id) )+1)     where ID = tt_id  ;     
     return price1 + obj2number(hours1) * obj2number(price_hours)+address_premio    ;
     

   RETURN 0;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN -1;
END RRL_GET_TT_PRICE;
/

prompt
prompt Creating function RRL_GET_USER_INFO
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GET_USER_INFO( USER_ID1 varchar2 )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := '';
  

select Name into tmpVar from RABAEV.RUSERS where  ID = USER_ID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_USER_INFO;
/

prompt
prompt Creating function RRL_PRIEMPALLET_HEIGHT
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIEMPALLET_HEIGHT( pallet_uid varchar2 , count_of number )
 RETURN number IS 
WEIGHT1 number;
itogo int;
sobrano int;
count_of1 number; 
-- Процедура возвращает нормативную высоту паллета. Если не указывается количество, для подсчета берется нормативная норма укладки.

BEGIN

    count_of1 :=count_of ;
    WEIGHT1:= 0;

    if( count_of =0 ) then
        select   (ART.NORMA_UKLADKI  /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
        from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
        RETURN WEIGHT1;    
    end if;

    select   (count_of /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
    from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
    RETURN WEIGHT1;   
    
    
     EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PRIEMPALLET_HEIGHT;
/

prompt
prompt Creating function RRL_PRIEMPALLET_WEIGHT
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIEMPALLET_WEIGHT( pallet_uid varchar2 , count_of number )
 RETURN number IS 
WEIGHT1 number;
itogo int;
sobrano int;
count_of1 number; 
-- Процедура возвращает нормативный вес паллета. Если не указывается количество, для подсчета берется нормативная норма укладки.

BEGIN

    count_of1 :=count_of ;
    WEIGHT1:= 0;

    if( count_of =0 ) then
        select   (ART.NORMA_UKLADKI  /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
        from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
        RETURN WEIGHT1;    
    end if;

    select   (count_of /  (   ART.COUNT_SHT_IN_KOR )) *  ART.WEIGHT_OF_KOR   into WEIGHT1
    from  RABAEV.RRL_PALLETS PAL , RABAEV.RRL_ARTICULS ART where PAL.ARTICUL = ART.ACTICUL ;
    RETURN WEIGHT1;   
    
    
     EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PRIEMPALLET_WEIGHT;
/

prompt
prompt Creating function RRL_GIVE_DESTINATION_CELL2
prompt ============================================
prompt
create or replace function rabaev.RRL_GIVE_DESTINATION_CELL2 (
-- ДАННАЯ ПРОЦЕДУРА ПРЕДЛАГАЕТ ЯЧЕЙКУ ДЛЯ РАЗМЕЩЕНИЯ. ЕСЛИ ТОВАР РАЗМЕЩЕН, УКАЗЫВАЕТ КУДА.
 pallet_uid varchar2 , 
 ware_id1 int
 
 ) return varchar2
is


cell_destination  varchar2(50) ;
tmpVar NUMBER;
PX int; 
PY int;
PZ int;
etaj_limit1 int;
m_RRL_TIME_FOR_RESERV int;
error_name  varchar2(250) ;
articul3  varchar2(250) ;
pallet_weight1 number;
pallet_height1 number;
debug_mode int;
 
cursor ddd is 
select cell from RRL_CELLS where UID_POLETA_FOR_BLOCK = pallet_uid and TIME_FOR_BLOCK >=    SYSTIMESTAMP  ;

cursor pallet_row is 
select * from RRL_PALLETS where UID_PALLET = pallet_uid    ;


cursor cell_for_pick is
select c1.*  from RABAEV.RRL_CELLS c1, RABAEV.RRL_ARTICULS , RABAEV.RRL_PALLETS   where
    RRL_ARTICULS.CELL = C1.CELL and RRL_PALLETS.ARTICUL= RRL_ARTICULS.ACTICUL
    and RRL_PALLETS.UID_PALLET = pallet_uid 
    and (     (( UID_POLETA_FOR_BLOCK is null ) or ( TIME_FOR_BLOCK < SYSTIMESTAMP ))  );


BEGIN

--m_RRL_TIME_FOR_RESERV:=RRL_TIME_FOR_RESERV();
debug_mode:=1;
etaj_limit1:=100;
articul3:='';
pallet_weight1:=RRL_PRIEMPALLET_WEIGHT(pallet_uid  , 0 );
pallet_height1:=RRL_PRIEMPALLET_HEIGHT(pallet_uid  , 0 );

begin

select RRL_PALLETS.ARTICUL into articul3 from RRL_PALLETS where RRL_PALLETS.UID_PALLET = pallet_uid ;
select etaj_limit into etaj_limit1  from rrl_articuls where acticul = articul3;

exception

    WHEN NO_DATA_FOUND THEN
       null;
    WHEN OTHERS THEN
       null;

end;



    if(debug_mode=1) then
        DBMS_OUTPUT.put_line( ' Hello 1 ');
    end if;


error_name:='';
cell_destination:='NONE';
-- Если существует паллето-место, куда указан резерв на данный паллет 
-- (и время ожидания не истекло), выбирается первое паллето-место. 
for fff in  ddd loop
    cell_destination:=fff.cell;
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана ячейка, назначенная раннее ');
            end if;
    return cell_destination;
end loop;

begin
-- ЕСЛИ ДАННЫЙ ПАЛЛЕТ ИМЕЕТ ОСТАТКИ В ЗОНЕ ХРАНЕНИЯ, ВЫДАЕМ ЭТОТ CELL 
    select C.CELL into cell_destination from RABAEV.RRL_REMAINS R , RABAEV.RRL_CELLS C 
        where R.CELL=C.CELL and R.UID_POLETA=pallet_uid 
        and R.REMAIN>0 and C.BLOCKED_FOR_REMAINS=0 and C.BLOCKED_FOR_POPOLNENIE=0 ;

    return cell_destination;
exception
        WHEN NO_DATA_FOUND THEN
        cell_destination:='NONE1';
         WHEN OTHERS THEN
         cell_destination:='NONE2';
end;

--Иначе, выбирается ячеека отбора для данного артикула  , если она с нулевыми (или меньшими)
-- остатками, и на которую нет действующего резерва другого паллета.
for cell_for_pick1 in cell_for_pick loop

PX:=cell_for_pick1.X;
PY:=cell_for_pick1.Y;
PZ:=cell_for_pick1.Z;



--  select sum(REMAIN) into tmpVar from RRL_REMAINS where cell = cell_for_pick1.cell group by cell ;

tmpVar:=RRL_GET_CELL_REMAIN( cell_for_pick1.cell);
    -- определяем остатки в ячейке отбора 

    if( ( (tmpVar) is null) or (tmpVar=0)  ) then
    
        cell_destination:=cell_for_pick1.cell;
        -- ФИКСИРУЕМ РЕЗЕРВ В ТАБЛИЦЕ ЯЧЕЕК 
        update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
        where RRL_CELLS.CELL = cell_for_pick1.cell ;
        
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана свободная ячейка пикинга ');
            end if;
        
        return cell_destination;
    
    end if;
   
end loop;



--Если свободной ячейки отбора нет, среди всех ячеек хранения отбираем свободную 
--не зарезервированную ячейку с наименьшим весом, чтобы не нарушалось ограничение этажа. Вес определяется как расстояние 
--от ячейки отбора данного паллета. 
--Если такой ячейки нет, помещаем паллет в зону переполнения.
--ВЕС: пусть X - ячейки по горизонтали Y - вертикаль  Z  - параллельные ряды.   
-- расстояние между 2-мя ячейками = abs( X1 - X2 ) + 2* abs(Y1-Y2) + 20 * abs(Z1-Z2)




    begin

        select CELL into cell_destination from 
        RRL_CELLS where (BLOCKED_FOR_ACCEPT=0) and (OTBOR=0) and ( ( TIME_FOR_BLOCK is null ) or (TIME_FOR_BLOCK <=    SYSTIMESTAMP )) 
        and RRL_GET_CELL_REMAIN(CELL)=0  and ROWNUM <=1   and ware_id=ware_id1 and Y<=etaj_limit1  and   pallet_weight1<= LIMIT_WEIGHT
        and pallet_height1<=LIMIT_HEIGHT
        order by 4*abs(PX-X)+abs(PY-Y)+40*abs(PZ-Z) , LIMIT_HEIGHT ;
        
        -- фиксируем наш выбор на 12 минут.
        --update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '12' minute
        --where RRL_CELLS.CELL = cell_destination ;

            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Найдена свободная ячейка хранения ');
            end if;

        
    EXCEPTION
         WHEN NO_DATA_FOUND THEN
            cell_destination:='OVERFLOW';
         WHEN OTHERS THEN
            cell_destination:='OVERFLOW2';
    end;



if( (cell_destination<>'OVERFLOW' ) and (cell_destination<>'OVERFLOW2' )  ) then
   update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
   where RRL_CELLS.CELL = cell_destination ;

end if;

   
    if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Результат зафиксирован ');
    end if;  
     

return cell_destination;

end;
/

prompt
prompt Creating function RRL_GIVE_KARSH_STAT_INFO
prompt ==========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_KARSH_STAT_INFO(
user_id1 varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   tmpVar := 'пусто';
   
   
   
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'пусто';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GIVE_KARSH_STAT_INFO;
/

prompt
prompt Creating function RRL_GIVE_NEXT_CELL
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_NEXT_CELL
(
    cell1 varchar2
)
 RETURN varchar2
  IS
tmpVar varchar2(50);
Y1 int ;
X1 int;
Z1 int ;
ware_id1 int ;

BEGIN

select  ware_id ,Y , X , Z into  ware_id1 , Y1 , X1 ,Z1 from RABAEV.RRL_CELLS where CELL = cell1 and BLOCKED_FOR_REMAINS=0 ;

select cell into tmpVar  from
 (select cell 
 from RABAEV.RRL_CELLS where  Z=Z1 and Y=Y1 and X>X1 and ware_id=ware_id1
  order by X )  where  ROWNUM <=1  ;



   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return 'no next';
     WHEN OTHERS THEN
           return 'err66';
       RAISE;
END RRL_GIVE_NEXT_CELL;
/

prompt
prompt Creating function RRL_SBORKA_PALLETS_ADD2
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLETS_ADD2 (
    ST_NUMBER1   varchar2,
    ADDR1 varchar2,
    PALLET_NUMBER1 INTEGER ,
    PALLET_UID1     VARCHAR2 ,
    STATE1    VARCHAR2 ,
    STDATE1 Date ,
    NAPR1 varchar2 ,
    USER_ID1 varchar2 ,
    ware_id1 int
) return int
IS

    ID1 int;
    DONE1 int;
    COND1 varchar2(255) ;

BEGIN


select ID into ID1 from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_UID1 ;
begin

    select R.STATE into COND1 from RABAEV.RRL_SBORKA_PALLETS R  where PALLET_UID = PALLET_UID1 ;
    select IN_PROCESS  into DONE1 from RABAEV.RRL_SBORKA_PALLETS_COND where COND=COND1;
    
    if ( DONE1=1)  then 
        return ID1;
    end if;
    
    delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID1;
    
    exception
    when NO_DATA_FOUND then
    NULL;
end;

delete from  RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_UID1 ;

update RRL_SBORKA_PALLETS set  STATE = STATE1 , NAPR = NAPR1 where  PALLET_UID = PALLET_UID1 ;


return ID1;
exception
    when NO_DATA_FOUND then
    begin
        INSERT INTO RABAEV.RRL_SBORKA_PALLETS (
              ADDR ,  
              ST_NUMBER      ,
              WARE_ID        ,
              PALLET_NUMBER  ,
              PALLET_UID     ,
              STATE ,
              NAPR ,
              STDATE , 
               USER_ID

      ) VALUES (
                ADDR1 ,
              ST_NUMBER1      ,
              WARE_ID1        ,
              PALLET_NUMBER1  ,
              PALLET_UID1     ,
              STATE1 ,
              NAPR1 ,
              STDATE1 ,
               USER_ID1
        
        );
        
        SELECT RRL_SBORKA_PALLETS_SQ.CURRVAL INTO ID1 FROM DUAL;
    return ID1;
    end;
    
END  RRL_SBORKA_PALLETS_ADD2 ;
/

prompt
prompt Creating function RRL_GIVE_NEXT_OPALLET_NUMBER
prompt ==============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_NEXT_OPALLET_NUMBER
(
    PREV_PALLET_ID  varchar2 ,
    USER_ID1        varchar2
 )
RETURN varchar2 IS 

    tmpVar varchar2(50);
    ret int;
    ADDR1 varchar2(255) ;
    PALLET_NUMBER1 int;
    PALLET_UID1     VARCHAR2 (100);
    STATE1    VARCHAR2(100) ;
    STDATE1 Date;
    ware_id1 int;
    NAPR1 varchar2(255);
    id2 int;
BEGIN


ret:=0;
select PP.ST_NUMBER , ADDR , STATE , STDATE , ware_id , NAPR into tmpVar , ADDR1 , STATE1 , STDATE1 , ware_id1 , NAPR1 
  from RRL_SBORKA_PALLETS PP where PP.PALLET_UID=PREV_PALLET_ID;
select (max(PALLET_NUMBER )+1) into  PALLET_NUMBER1  from RRL_SBORKA_PALLETS PP where  PP.ST_NUMBER = tmpVar ;

PALLET_UID1:= Concat( 'OP_' , Concat( Concat( tmpVar , '_'  ) ,  PALLET_NUMBER1  ) );


id2 := RABAEV.RRL_SBORKA_PALLETS_ADD2 (
    tmpVar,
    ADDR1 ,
    PALLET_NUMBER1  ,
    PALLET_UID1      ,
    STATE1     ,
    STDATE1  ,
    NAPR1  ,
    USER_ID1  ,
    ware_id1 );




RETURN PALLET_UID1;



   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GIVE_NEXT_OPALLET_NUMBER;
/

prompt
prompt Creating function RRL_GIVE_POPOLNENIE2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_POPOLNENIE2
(
    PIKING_CELL varchar2 ,
    ware_id1 int   
)
RETURN varchar2 IS
articul1 varchar(50);
tmpVar  varchar(950);
id_pal  varchar(50);


cursor rrrr is     select CELL , UID_POLETA into tmpVar , id_pal from (
        select RRL_REMAINS.CELL , RRL_REMAINS.UID_POLETA 
        from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , 
        RABAEV.RRL_CELLS    
         where ARTICUL=articul1       
         and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
         and RRL_CELLS.CELL = RRL_REMAINS.CELL
         and RRL_REMAINS.REMAIN>0 and RRL_REMAINS.CELL<>PIKING_CELL
         and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1 
         
         and RRL_CELLS.OTBOR =0 
         
 --        and RRL_CELLS.WARE_ID = ware_id1
         order by EXPIRY_DATE ) 
     where  ROWNUM<=1  ;



BEGIN
-- по заданной ячейке отбора вычисляем артикул и 
-- выдаем паллет данного артикула с наименьшим сроком годноти, стоящий ближе всего
    begin  
      select  ACTICUL into articul1 from RABAEV.RRL_ARTICULS 
            where CELL=PIKING_CELL;
     EXCEPTION
         WHEN NO_DATA_FOUND THEN
         
           -- **************************************************************
         
         begin 
             
              select ARTICUL into articul1   from (
                select RRL_PALLETS.ARTICUL  
                from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS   
                 where   RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
                 and RRL_REMAINS.REMAIN>0  
                 and RRL_REMAINS.CELL = PIKING_CELL
                 
                ) 
                
             where  ROWNUM=1  ;
             EXCEPTION
         WHEN NO_DATA_FOUND THEN
           return 'not a picking cell';
         WHEN OTHERS THEN
           return 'error5';
         end;
         
         
           -- **************************************************************
         
          -- return 'no a picking cell';
         WHEN OTHERS THEN
           return 'error4';
    end;
    
/*
    select CELL , UID_POLETA into tmpVar , id_pal from (
        select RRL_REMAINS.CELL , RRL_REMAINS.UID_POLETA 
        from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , 
        RABAEV.RRL_CELLS    
         where ARTICUL=articul1       
         and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA
         and RRL_CELLS.CELL = RRL_REMAINS.CELL
         and RRL_REMAINS.REMAIN>0 and RRL_REMAINS.CELL<>PIKING_CELL
         and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1 
         
         and RRL_CELLS.OTBOR =0 
         
         and RRL_CELLS.WARE_ID = ware_id1
         order by EXPIRY_DATE ) 
     where  ROWNUM=1  ;
     */
     
     for ddd in rrrr loop
        tmpVar :=    concat( concat( tmpVar , ddd.CELL ) , ' '   ) ;      
     end loop;

     
     

RETURN tmpVar;

   --RETURN concat(tmpVar , concat( ' = ','id_pal')  ) ;

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       return 'no pallet';
     WHEN OTHERS THEN
       return 'error7';  
END RRL_GIVE_POPOLNENIE2 ;
/

prompt
prompt Creating function RRL_GIVE_PREVIOUS_CELL
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_PREVIOUS_CELL
(
    cell1 varchar2
)

 RETURN varchar2
  IS
tmpVar varchar2(50);
Y1 int ;
X1 int;
Z1 int ;
ware_id1 int ;

BEGIN

select  ware_id ,Y , X , Z into  ware_id1 , Y1 , X1 ,Z1 from RABAEV.RRL_CELLS where CELL = cell1 and BLOCKED_FOR_REMAINS=0 ;

select cell into tmpVar  from
 (select cell 
 from RABAEV.RRL_CELLS where  Z=Z1 and Y=Y1 and X<X1 and ware_id=ware_id1
  order by X DESC )  where  ROWNUM <=1  ;



   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return 'no prev';
     WHEN OTHERS THEN
           return 'err66';
       RAISE;
       
END RRL_GIVE_PREVIOUS_CELL;
/

prompt
prompt Creating function RRL_GIVE_TERMINAL_TASK
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_TERMINAL_TASK( USER_ID1_ varchar2 )
RETURN varchar2 
IS 
    tmp varchar2(255);
BEGIN
 tmp:='';
 -- НАХОДИМ ЗАДАЧУ ДЛЯ ДАННОГО ЮЗЕРА 

select PALLET_UID into tmp from ( 
    select PP.PALLET_UID   from RABAEV.RRL_SBORKA_PALLETS  PP
    where ( SBORSHIK =  USER_ID1_ )
      and ( PROOVED_BY_SCAN=0 and PROOVED=0 ) order by PP.STDATE DESC , PP.ADDR , PP.ORD  

) where rownum=1 ;

      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values ( tmp , USER_ID1_ , 'VESOV' , 'GIVE_TERMINAL_TASK' , 0  );

   RETURN  tmp;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN '';
END RRL_GIVE_TERMINAL_TASK;
/

prompt
prompt Creating function RRL_GIVE_TERMINAL_TASK2
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_GIVE_TERMINAL_TASK2(
    USER_ID1 varchar2 ,
    ip_addr1 varchar2
 )
RETURN varchar2 
IS 
    tmp varchar2(255);
BEGIN
 tmp:='';
 -- НАХОДИМ ЗАДАЧУ ДЛЯ ДАННОГО ЮЗЕРА 

select PALLET_UID into tmp from ( 
    select PP.PALLET_UID   from RABAEV.RRL_SBORKA_PALLETS  PP
    where ( SBORSHIK =  USER_ID1 )
    and ( (ip_addr is null ) or (ip_addr='') or (ip_addr=ip_addr1) )
      and ( PROOVED_BY_SCAN=0 and PROOVED=0 ) order by PP.STDATE DESC , PP.ADDR , PP.ORD  
) where rownum=1 ;

      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values ( tmp , USER_ID1 , ip_addr1 , 'GIVE_TERMINAL_TASK' , 0  );


update RABAEV.RRL_SBORKA_PALLETS set ip_addr=ip_addr1 where PALLET_UID = tmp;

   RETURN  tmp;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN '';
END RRL_GIVE_TERMINAL_TASK2;
/

prompt
prompt Creating function RRL_HAS_WRIGHT
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )
    RETURN int IS 
    tmpVar varchar2(255);
    
BEGIN

begin

--return 1;
select id into tmpVar from rusers where id=user_id and USER_GROUP='GLOBAL_ADMIN';
return 1;

exception
 WHEN NO_DATA_FOUND THEN
    null;
end;


select USER_GROUP into tmpVar from (
    select  RUSERS.USER_GROUP  from RUSERS , RABAEV.RIGHTS where 
            RUSERS.ID=user_id and RIGHTS.USER_GROUP=RUSERS.USER_GROUP
             and RIGHT1= wright_name  ) where ROWNUM=1  ;

   
    RETURN 1;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_HAS_WRIGHT;
/

prompt
prompt Creating function RRL_INFO_CELL_RESTS
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INFO_CELL_RESTS
(
    cell1 varchar2 
)

 RETURN varchar2 IS
tmpVar varchar(1250);

cursor rrrr is select   remain , uid_poleta , rrl_pallets.ARTICUL , rrl_pallets.EXPIRY_DATE  from rrl_remains , rrl_pallets   where rrl_remains.cell = cell1 
 and rrl_remains.UID_POLETA= rrl_pallets.UID_PALLET  
  ;
                                                                                
                                                                                
BEGIN
tmpVar := '';
                    
for ddd in rrrr loop

    tmpVar := concat( concat( concat( concat( tmpVar , concat( '[', ddd.ARTICUL )  ) , '-' ) , to_char( ddd.remain )  ) , ' ' ) ;
    tmpVar :=concat( '' , concat(  concat ( tmpVar  ,  to_char(  ddd.EXPIRY_DATE  , 'dd.mm.yyyy ' )    ) , '] ' ) ) ;

--tmpVar :=    concat( tmpVar , pallet_id )    ;
                                                                    
end loop;


   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  'no rest';
     WHEN OTHERS THEN
       RETURN 'слишком много значений';
END  RRL_INFO_CELL_RESTS;
/

prompt
prompt Creating function RRL_INFO_PALLET_RESTS
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INFO_PALLET_RESTS
(
    pallet_id varchar2 
)

 RETURN varchar2 IS
tmpVar varchar(250);

cursor rrrr is select cell , remain from rrl_remains where uid_poleta=pallet_id   and cell not like 'EX%' ;
                                                                                
                                                                                
BEGIN
tmpVar := '';
                    
for ddd in rrrr loop

tmpVar := concat( concat( concat( concat( tmpVar , ddd.Cell ) , '=' ) , to_char( ddd.remain )  ) , '; ' ) ;

--tmpVar :=    concat( tmpVar , pallet_id )    ;
                                                                    
end loop;


   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  'no rest';
     WHEN OTHERS THEN
       RETURN 'error';
END  RRL_INFO_PALLET_RESTS;
/

prompt
prompt Creating function RRL_INTERNAL_MOVE2
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INTERNAL_MOVE2(
pallet_id varchar2 , 
cell_to varchar2 ,
count1 number ,
user_id1 varchar2
)

RETURN varchar2

IS
count2 number;
tmpVar NUMBER;
art1 varchar2(50) ;
is_otbor int;
remain_in_cell_to number;
checks_passed int;
cell_from1 varchar2(50);
cell_next varchar2(50);
debug_mode int;
new_event_uid int;

prihod_cond int;
cursor rrr is select * from RRL_REMAINS where CELL = cell_to;

BEGIN
    
prihod_cond:=0;
count2:=count1;
   debug_mode:=0;
   tmpVar := 0;
   is_otbor:=0;
   remain_in_cell_to:=0;
   checks_passed:=0;
   cell_from1:='NONE';




 -- ЕСЛИ списание на НЕДОСТАЧУ
if  ( pallet_id='NO_PALLET' ) then

    begin
        for fgr in rrr  loop
        --
             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );

        --
        end loop;
     exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL;
    
    end;

    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
    RETURN CONCAT('ok_' ,  cell_next );
end if;


-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?
begin
    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;

    if( (prihod_cond=1) or (prihod_cond=0) ) then
        return 'NAKLAD_NE_ZAKRYTA';
    end if;

   exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL; 
    
end;




    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА
    

    select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;
  -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;



        if(count2=0) then
            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
        end if;

    exception
        WHEN NO_DATA_FOUND THEN
        
        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   
        UID_POLETA=pallet_id and cell=cell_to;
         
            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
            RETURN CONCAT('ok_' ,  cell_next );
        

         WHEN OTHERS THEN
            begin
            
                    begin
                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА
                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where
                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;
                    exception
                
                        WHEN NO_DATA_FOUND THEN
                            return 'pallet byl otgruzen';
                        WHEN OTHERS THEN null;
                        --    return 'other pallet3';
                    end;

                         
                    if(count2=0) then
                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
                    end if;
                    


                    
            exception
            
                WHEN NO_DATA_FOUND THEN
                    return 'other pallet1';
                WHEN OTHERS THEN
                    return 'other pallet2';
            end;
         
            
    end;
    

if( cell_to=cell_from1 ) then 
    return 'cell_to=cell_from1';
end if;   
    

    if(count2=0) then
        return 'count2=0';
    end if;

begin
    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 
    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 
    select OTBOR into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;
exception
         WHEN NO_DATA_FOUND THEN
           return 'no_pallet_cell_to';
         WHEN OTHERS THEN
           return 'other pallet1';
end;


if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then

    begin
        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;
    exception
             WHEN NO_DATA_FOUND THEN
               remain_in_cell_to:=0;
             WHEN OTHERS THEN
               remain_in_cell_to:=0;
    end;

    if remain_in_cell_to is null then
    remain_in_cell_to:=0;
    end if;

    if(remain_in_cell_to<=0)  then
        checks_passed:=1;
    else
    return 'cell_not_empty';    
    end if;

else
    checks_passed:=1;
end if;

        
    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 
    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event
    -- type_event = 2 , UID_POLETA , USER_ID

    if( checks_passed=0 ) then
     return 'fault';
    end if;
    

  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
 TYPE_EVENT , UID_POLETA , USER_ID ) values
( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );

-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ

commit;

cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);


   RETURN CONCAT('ok_' ,  cell_next );
      
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       return 'err1';
     WHEN OTHERS THEN
       return 'err2';
END RRL_INTERNAL_MOVE2;
/

prompt
prompt Creating function RRL_INTERNAL_MOVE3
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INTERNAL_MOVE3(
pallet_id varchar2 , 
cell_to varchar2 ,
count1 number ,
user_id1 varchar2
)
-- ПРОЦЕДУРА ВНУТРЕННЕГО ПЕРЕМЕЩЕНИЯ 
-- ЕСЛИ ПЕРЕМЕЩЕНИЕ ИДЕТ В ЯЧЕЙКУ ОТБОРА, ТО КОНТРОЛИРУЕТСЯ 
--  - ЯВЛЯЕТСЯ ЛИ ДАННАЯ ЯЧЕЙКА РОДНОЙ ДЛЯ ДАННОГО ТОВАРА 

RETURN varchar2

IS
count2 number;
tmpVar NUMBER;
tmpVar2 varchar(250);
art1 varchar2(50) ;
is_otbor int;
remain_in_cell_to number;
checks_passed int;
cell_from1 varchar2(50);
cell_next varchar2(150);
dummy1 varchar(500);
dummy2 varchar(500);

articul1 varchar2(250);
cell_otbora_for_pallet varchar2(50);
ware_id_to int;
debug_mode int;
new_event_uid int;
SPIS_IF_HRAN_NO_EMPTY1 varchar(100);
data_spisania Date ;
alternative_puid varchar2(400);
alternative_cell varchar2(400);
alternative_date date;
rret varchar2(500);
helv varchar2(500);

flag_control_fifo int;

user_group1 varchar2(500);
weight_limit_warning1 int;
WEIGHT_LIMIT_STOP1 int;
weight_of_cell_to number;
PRIEMPALLET_WEIGHT1 number;
prihod_cond int;
cursor rrr is select * from RRL_REMAINS where CELL = cell_to;
cursor rrr2 is select * from  RABAEV.RRL_REMAINS  where CELL=cell_to ;

BEGIN
    

begin
    select rusers.USER_GROUP into user_group1 from rusers where rusers.ID=user_group1 ;
exception 
        when no_data_found then null;
        when others then null;
end;



    begin -- ФИКСИРУЕМ ВРЕМЯ ПОСЛЕДНЕГО ДОСТУПА К ЯЧЕЙКЕ        
        update rrl_cells set LAST_TIME_OF_UPDATE= SYSTIMESTAMP where CELL=cell_to;
    exception        
        when no_data_found then null;
        when others then null;
    end;


select ware_id into ware_id_to from RABAEV.rrl_cells CC where CC.cell =  cell_to;
articul1:=null;

 select   FCONTROL_FIFO into flag_control_fifo from RRL_WARES where id=ware_id_to ;


DBMS_OUTPUT.put_line( 'Начало' );

if( pallet_id<>'NO_PALLET' ) then

    begin
        select PA.ARTICUL into articul1 from  RABAEV.RRL_PALLETS  PA where PA.UID_PALLET=pallet_id;
    exception
    when no_data_found then 
        helv:= Concat( 'отсутствует паллет ' , concat( pallet_id , concat( ' ячейка=' , cell_to) ) ) ; 
        insert into rrl_error_log ( error , datet  ,user_id ) values ( helv , systimestamp , user_id1 ) ;
        DBMS_OUTPUT.put_line( 'ошибка 0 типа' );
        return 'Pallet Udalen. I2';
    when others then 
        DBMS_OUTPUT.put_line( 'ошибка 1 типа' );
    end;

end if;

DBMS_OUTPUT.put_line( articul1 );

DBMS_OUTPUT.put_line( 'Флаг1' );


   prihod_cond:=0;
   count2:=count1;
   debug_mode:=0;
   tmpVar := 0;
   is_otbor:=0;
   remain_in_cell_to:=0;
   checks_passed:=0;
   cell_from1:='NONE';
   weight_limit_warning1:=0; -- Настройка - предупреждать - ли в случае превышения веса
   PRIEMPALLET_WEIGHT1 := 0; -- Вес перемещаемого товара
   WEIGHT_LIMIT_STOP1 := 0;



 -- ЕСЛИ списание на НЕДОСТАЧУ
if  ( pallet_id='NO_PALLET' ) then

    begin
        for fgr in rrr  loop
        --
             SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
            ( new_event_uid , 'INVENT'  , fgr.CELL , SYSTIMESTAMP , fgr.REMAIN , 2 , fgr.UID_POLETA , user_id1  );

        --
        end loop;
     exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL;
    
    end;

    cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
    RETURN CONCAT('ok_' ,  cell_next );
end if;


-- ОПРЕДЕЛЯЕМ - НЕ НАХОДИТСЯ ЛИ НАКЛАДНАЯ ДАННОГО ПАЛЛЕТА В ЧЕРНОВИКЕ?

begin
    select N.CONDITION into prihod_cond from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_PRIHOD_NAKLAD N   where  PP.PRIHOD_NAKLAD_ID = N.ID  and PP.UID_PALLET = pallet_id;

    if( (prihod_cond=1) or (prihod_cond=0) ) then
        return 'NAKLAD_NE_ZAKRYTA';
    end if;

   exception
        WHEN NO_DATA_FOUND THEN
                    NULL;
         WHEN OTHERS THEN
                    NULL; 
    
end;




    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА
    

        select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;
        -- select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id  group by cell ;



        if(count2=0) then
            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
        end if;

    exception
        WHEN NO_DATA_FOUND THEN
        
        update RABAEV.RRL_REMAINS RRR set RRR.TIME_OF_LAST_UPDATE = SYSTIMESTAMP where   
        UID_POLETA=pallet_id and cell=cell_to;
         
            cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);
            RETURN CONCAT('ok_' ,  cell_next );
        

         WHEN OTHERS THEN
            begin
            
                    begin
                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА
                    
                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where
                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;
                         
                    exception
                
                        WHEN NO_DATA_FOUND THEN
                        
                            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'net stolko tovara',  pallet_id ,  count1  ) ;
                            return 'net stolko tovara';
                            
                        WHEN OTHERS THEN
                           null ; -- return 'other pallet3';
                    end;

                         
                    if(count2=0) then
                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
                    end if;
                    


                    
            exception
            
                WHEN NO_DATA_FOUND THEN
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet1',  pallet_id ,  count1  ) ;
                    return 'other pallet1';
                WHEN OTHERS THEN
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'other pallet2',  pallet_id ,  count1  ) ;
                    return 'other pallet2';
            end;
         
            
    end;
    

DBMS_OUTPUT.put_line( 'FLAG 8' );

if( cell_to=cell_from1 ) then 
    return 'ok_';
end if;   
    

if(count2=0) then
    return 'ok_count2=0';
end if;





begin
    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 
    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 
    select OTBOR  into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;
exception
         WHEN NO_DATA_FOUND THEN
         
           return 'no_pallet_cell_to';
         WHEN OTHERS THEN
           return 'other pallet1';
end;





if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then

PRIEMPALLET_WEIGHT1 := RRL_PRIEMPALLET_WEIGHT( pallet_id , count1 );
-- Если перемещение идет не в ячейку отбора, проверяем параметры веса ячейки.  если вес не допустим -
-- тогда предупреждение или отказ (в зависимости от настроек склада ячейки, куда перемещается товар)                 
    -- Находим ограничения по весу для данной ячейки.
    begin
    
        select weight_limit_warning , cells.LIMIT_WEIGHT , WEIGHT_LIMIT_STOP into weight_limit_warning1 , weight_of_cell_to , WEIGHT_LIMIT_STOP1 from rrl_wares ww , rrl_cells cells 
            where cells.CELL = cell_to and cells.WARE_ID= ww.ID ;
            -- ЕСЛИ ВКЛЮЧЕНА НАСТРОЙКА СРАВНЕНИЯ ВЕСА И ПРЕДУПРЕЖДЕНИЯ О ВЕСЕ.
            if (  weight_limit_warning1 = 1 ) then  -- СРАВНИВАЕМ ВЕС ПАЛЛЕТА С ЛИМИТАМИ ПО ДАННОЙ ЯЧЕЙКЕ 
               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then
                 dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'weight_limit_warning',  pallet_id ,  count1  ) ;
               end if;
            end if;

            if (  WEIGHT_LIMIT_STOP1 = 1 ) then  
               if(weight_of_cell_to > PRIEMPALLET_WEIGHT1 )then
                return 'LIMIT_VESA';
               end if;
            end if;

            
        exception
        WHEN NO_DATA_FOUND THEN null;
        WHEN OTHERS THEN null;
        
    end; 



-- ЕСЛИ перемещение идет не в назначенную ячейку - сообщение об ошибке  карщика.      




    begin
        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;
    exception
             WHEN NO_DATA_FOUND THEN
               remain_in_cell_to:=0;
             WHEN OTHERS THEN
               remain_in_cell_to:=0;
    end;

    if remain_in_cell_to is null then
    remain_in_cell_to:=0;
    end if;

    if(remain_in_cell_to<=0)  then
        checks_passed:=1;
    else
        -- ЕСЛИ ДЛЯ ДАННОЙ ЯЧЕЙКИ  УЖЕ ЕСТЬ ОСТАТОК ЧЕГО -ТО 
     -- если для данного склкда указана опция - списывать паллеты на недостачу, то списываем все в соотв. ячейку.
        select SPIS_IF_HRAN_NO_EMPTY into SPIS_IF_HRAN_NO_EMPTY1  from rrl_wares where rrl_wares.id = ware_id_to;
        
        if( (not ( SPIS_IF_HRAN_NO_EMPTY1 is null ) ) or (SPIS_IF_HRAN_NO_EMPTY1 <>'')  ) then
        
           
                checks_passed:=1;
                
                 for fgr2 in rrr2  loop
                    
                     tmpVar2:=RABAEV.RRL_INTERNAL_MOVE2(
                     fgr2.UID_POLETA  , 
                     SPIS_IF_HRAN_NO_EMPTY1  ,
                     fgr2.REMAIN ,
                     user_id1 
                        );

                end loop;
                
           
        
        end if;
        
        
        if(checks_passed=0) then
            dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'cell_not_empty',  pallet_id ,  count1  ) ;
            return 'cell_not_empty';
        end if;
        
    end if;

else

DBMS_OUTPUT.put_line( 'спуск в отбор' );

    if cell_to<>'MEZONIN' then
        begin
            -- НЕ ДАЕМ СТАВИТЬ ТОВАР В ЛЕВЫЙ ОТБОР
                select AR.CELL , PP.EXPIRY_DATE  into  cell_otbora_for_pallet , data_spisania
                from RABAEV.RRL_PALLETS  PP , RABAEV.RRL_ARTICULS AR   
                where   PP.UID_PALLET = pallet_id and AR.ACTICUL=PP.ARTICUL ;
                
                if( cell_otbora_for_pallet<>cell_to ) then
                    DBMS_OUTPUT.put_line( concat( cell_otbora_for_pallet , concat( '#' , cell_to ) ) );
                    dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'OTBOR_DRUGOGO_ARTICULA',  pallet_id ,  count1  ) ;
                    return 'OTBOR_DRUGOGO_ARTICULA';
                end if;
                
                
                -- Проверяем нарушение принципа FEFO 
                -- ИЩЕМ ПАЛЛЕТ ЭТОГО ТОВАРА В ХРАНЕНИИ ХУДШИМ СРОКОМ 
                -- data_spisania 
                DBMS_OUTPUT.put_line( concat('Флаг2' , articul1 ) );
                if not ( articul1  is null ) then
                DBMS_OUTPUT.put_line( 'ffff4' );
                    if  (1=1) then 
                    
                        alternative_puid :='';
                        alternative_cell :='';
                        alternative_date:=null;
                        begin
                        DBMS_OUTPUT.put_line( 'Флаг3' );
                            select UID_PALLET , CELL , EXPIRY_DATE  into alternative_puid , alternative_cell , alternative_date  from  (
                            select  PA.UID_PALLET , REMA.CELL , PA.EXPIRY_DATE  from RABAEV.RRL_REMAINS REMA , RABAEV.RRL_PALLETS  PA , RRL_CELLS CE  where 
                            REMA.UID_POLETA= PA.UID_PALLET and REMA.CELL=CE.CELL and PA.ARTICUL=articul1  and PA.EXPIRY_DATE<data_spisania  and CE.BLOCKED_FOR_REMAINS<>1 and CE.OTBOR<>1 order by PA.EXPIRY_DATE 
                            ) where rownum<=1  ; 
                            DBMS_OUTPUT.put_line( 'Флаг4' );
                            dummy2:=to_char( data_spisania, 'DD-MM-YYYY'  );
                            dummy1:= concat(concat(to_char( alternative_date, 'DD-MM-YYYY' ) , ' # ') , dummy2 ) ;
                            
                          --  rret :=concat( concat( concat( concat( Concat('SMOTRI SROK:' ,   alternative_cell) , ' ' ) , alternative_puid ) , ' srok=') , to_char( alternative_date, 'DD-MM-YYYY' ) ); 
                            rret := concat(concat( concat(Concat('SMOTRI SROK:' ,   alternative_cell) , ' [') , dummy1 ) ,  ']' )  ; 
                           dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  rret ,  pallet_id ,  count1  ) ;
                           DBMS_OUTPUT.put_line( 'Флаг5' );
                           if(flag_control_fifo =1) then
                                return rret;
                           end if;
                           
                      exception
                            WHEN NO_DATA_FOUND THEN  null;
                            WHEN OTHERS THEN  null; 
                        end;
                    end if;
                end if;
             
        exception
                 WHEN NO_DATA_FOUND THEN
                     return 'no_articul';
                 WHEN OTHERS THEN
                  null;
        end;

    end if;

    checks_passed:=1;
end if;

        
    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 
    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event
    -- type_event = 2 , UID_POLETA , USER_ID

    if( checks_passed=0 ) then
     return 'fault';
    end if;
    

  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
 TYPE_EVENT , UID_POLETA , USER_ID ) values
( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );

-- ОПРЕДЕЛЯЕМ ЯЧЕЙКУ, СЛЕДУЮЩУЮ ЗА ТЕКУЩЕЙ

commit;

cell_next:=RABAEV.RRL_GIVE_NEXT_CELL(CELL_TO);


   RETURN CONCAT('ok_' ,  cell_next );
      
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
          dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '', concat( 'RRL_INTERNAL_MOVE3:err1 ' , cell_to ) ,  pallet_id ,  count1  ) ;
                 
       return 'err1';
     WHEN OTHERS THEN
     dummy1:=ADD_HISTORY_NOTE (  user_id1,  cell_to     ,  '',  'RRL_INTERNAL_MOVE3:err2' ,  pallet_id ,  count1  ) ;
       return 'err2';
END RRL_INTERNAL_MOVE3;
/

prompt
prompt Creating function RRL_INV_CREATE_LINE
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INV_CREATE_LINE
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
BEGIN
price:=1;
NAKLAD_ID:=1796;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );

    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает строчку в плане инвентаризации ( константа ), делая ссылку на адрес.
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

delete from RRL_PRIHOD_NAKLAD_ROWS where INVENT_CELL=cell1 ;

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
        ORDID ,
        ARTICUL ,
        EXPIRY_DATE,
        count1 ,
        price ,
        ID  ,
        INVENT_CELL 
  ) VALUES (
        NAKLAD_ID ,
        articul1 , 
        expiury_date ,
        count1 ,
        price ,
        RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL ,
        cell1
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO id1 FROM DUAL;

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);

 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ


   
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE;
/

prompt
prompt Creating function RRL_INV_CREATE_LINE2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INV_CREATE_LINE2
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=1796;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;

--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end
--==================================================================

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE2;
/

prompt
prompt Creating function RRL_INV_CREATE_LINE3
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INV_CREATE_LINE3
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int
)
    RETURN varchar2 IS 
    price Number;
    expiury_date date ;
    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;
expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА

DBMS_OUTPUT.put_line(  pallet_name );
begin
insert into RABAEV.RRL_PALLETS
(
  UID_PALLET       ,
  ARTICUL           ,
  CREATION_DATE     ,
  EXPIRY_DATE       ,
  UNIT_COUNT        ,
  PRICE             ,
  PRIHOD_NAKLAD_ID  
)values
(
    pallet_name , 
    articul1 ,
    sysdate ,
    expiury_date ,
    count1 , 
    1,
    NAKLAD_ID
);
exception
when others then null;
end;

--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'KLAD_VOSTRIKOV' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end
--==================================================================

commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'ERR1';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 'ERR2';
END RRL_INV_CREATE_LINE3;
/

prompt
prompt Creating function RRL_INV_CREATE_LINE4
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_INV_CREATE_LINE4
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER ,
    UID_DOC int,
    expiury_date date 
)
    RETURN varchar2 IS 
    price Number;

    next_cell varchar2(255);
    tmp_cell varchar2(255);
    articul1 varchar2(255);
    NAKLAD_ID int;
    id1 int ;
    event_id int;
    pallet_name varchar2(255);
    help2 varchar2(255);
    help3 int;
BEGIN
price:=1;
NAKLAD_ID:=UID_DOC;
--expiury_date :=  to_date( '01.06.2010' , 'dd.mm.yyyy' );




    begin 
        select cell into tmp_cell from rrl_cells where cell=cell1;
    exception
            when NO_DATA_FOUND THEN
            return 'NO_CELL';
    end;


    begin 
        select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where BARCODE_SHT=shk_art or BARCODE_KOR =shk_art or  BARCODE_BL=shk_art ;
       
        
    exception
            when NO_DATA_FOUND THEN
            begin       
                select ACTICUL into articul1 from RABAEV.RRL_ARTICULS where ACTICUL like  concat( '%' , articul_part ) ;
            exception
                when NO_DATA_FOUND THEN
                return 'NO_ARTICUL';
                WHEN OTHERS THEN
                return 'MORE_ARTICUL';
            end;
    end;


begin



pallet_name:= Concat( Concat( Concat('P_' , articul1 ) , '_G2_') , tmp_cell);
pallet_name:=replace(pallet_name , 'Т' ,'T' );


DBMS_OUTPUT.put_line(  pallet_name );
--  ПРОЦЕДУРА ИНВЕНТАРИЗАЦИИ ПРИ ВНЕДРЕНИИ: 
-- Создает паллет, делает проводку на остатки
-- ВОЗВРАЩАЕТ НОМЕР СЛЕДУЮЩЕЙ ЯЧЕЙКИ ВСЕГДА
begin 
-- Проверяем наличие такого артикула 
select ARTICUL into help2 from RABAEV.RRL_PALLETS where UID_PALLET=pallet_name;
update RABAEV.RRL_PALLETS set PRIHOD_NAKLAD_ID=NAKLAD_ID where UID_PALLET=pallet_name;
DBMS_OUTPUT.put_line( 'Паллет найден' );
exception when no_data_found then

        begin
        insert into RABAEV.RRL_PALLETS
        (
          UID_PALLET       ,
          ARTICUL           ,
          CREATION_DATE     ,
          EXPIRY_DATE       ,
          UNIT_COUNT        ,
          PRICE             ,
          PRIHOD_NAKLAD_ID  
        )values
        (
            pallet_name , 
            articul1 ,
            sysdate ,
            expiury_date ,
            count1 , 
            1,
            NAKLAD_ID
        );
        exception
        when no_data_found then -- null; 
            return 'ERR39';
        end;

end;


begin 

null;


begin

delete from rrl_remains rr where   rr.cell=tmp_cell  ;

exception
  when others then null;
end;

end;
--============ ТЕПЕРЬ ФИКСИРУЕМ ОСТАТКИ ===============================
 select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        
 insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          tmp_cell ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          'R' ,
          NAKLAD_ID 
            );
exception
when others then
return 'ERR3';

end;
--==================================================================

--commit;
next_cell:=RRL_GIVE_NEXT_CELL(cell1);
 -- ТЕПЕРЬ ИЩЕМ СЛЕДУЮЩУЮ ЯЧЕЙКУ, ВЫДАЕМ ЕЕ
    RETURN next_cell;
--    EXCEPTION
--     WHEN NO_DATA_FOUND THEN   RETURN 'ERR1';
 --    WHEN OTHERS THEN RETURN 'ERR2';
       
END RRL_INV_CREATE_LINE4;
/

prompt
prompt Creating function RRL_IS_PALLET_LIKE_FAKE
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_is_PALLET_like_fake( puid varchar2 )
 RETURN int IS 
tmpVar int;

BEGIN
   tmpVar := 0;
   select count( distinct WEIGHT ) into tmpVar from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' group by PALLET_UID  ;
if(  tmpVar>2) then
 tmpVar:=1;
   else
 tmpVar:=0;
end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 1;
       RAISE;
END RRL_is_PALLET_like_fake;
/

prompt
prompt Creating function RRL_SKLADNAME_BY_ID
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SKLADNAME_BY_ID( ids int )
 RETURN varchar2  IS 
tmpVar varchar2(50);


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select NAME into tmpVar from RABAEV.RRL_WARES W  
     where W.ID = ids  ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'НЕ ИЗВЕСТНЫЙ СКЛАД';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SKLADNAME_BY_ID;
/

prompt
prompt Creating function RRL_IS_PALLET_STRICTLY_FAKE
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_is_PALLET_strictly_fake( puid varchar2 )
-- ФУНКЦИЯ ПРЕДСКАЗЫВАЕТ КРИВЫЕ ПОДДОНЫ
 RETURN int IS 
tmpVar int;
tmp2 varchar2(255);
BEGIN
   
   -- если паллет с мезонина или сухого склада , и не прошел весовой контроль
   -- и взвешивался  1 раз, либо интервал между взвешиваниями менее 15 минут, поддон считаем ложным.
begin

   select P.PALLET_UID into tmp2 from RRL_SBORKA_PALLETS P  
   where  ( RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'АЛКО'  )) and (  PROOVED=0 )
   and ( P.PALLET_UID = puid ) ;
  -- сколько раз взвешиваля поддон
 
    begin
       -- and ( count( distinct WEIGHT ) =1 )
       -- если поддон взвешивался 1 раз и времени прошло более 15 минут having ( (max(TIME1)  - min(TIME1))*24*60 >10  ) 
       
        select count(  WEIGHT )   into tmpVar 
            from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and (event='WEIGHT_CHECK')  
            group by PALLET_UID having  ( ( sysdate  - min(TIME1)  )*24*60 >=15 )  ;
            
            if( tmpVar=1 ) then 
            return 1;
            end if;
            
        exception 
            when no_data_found then   return 1;
            when others then null;   
    end;


   begin
        select (max(TIME1)  - min(TIME1))*24*60   into tmpVar 
        from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' 
        group by PALLET_UID  having ( (max(TIME1)  - min(TIME1))*24*60 >15  )  ;
        return 0;
        exception
        when no_data_found then null;
        when others then return 3; 
    end;
    
    
       begin
        select (max(TIME1)  - min(TIME1))*24*60   into tmpVar 
        from RRL_SBORKA_PALLETS_HISTORY where PALLET_UID = puid  and event='WEIGHT_CHECK' 
        group by PALLET_UID  having ( (max(TIME1)  - min(TIME1))*24*60 >5  )  ;
        return 4;
        exception
        when no_data_found then return 2;
        when others then return 3; 
    end;
    
    return 0;
exception 
when no_data_found then
    return 0;    
end;

   tmpVar := 0;
   RETURN tmpVar;
END RRL_is_PALLET_strictly_fake;
/

prompt
prompt Creating function RRL_MAY_DELETE
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_MAY_DELETE ( ST_N varchar2 )
 RETURN varchar2 IS 
tmpVar varchar2(6);
t2 int;

BEGIN

 --return 'yes';
 
 select count( P.ID ) into t2 from RRL_SBORKA_PALLETS P where P.ST_NUMBER=ST_N and ( P.TRANSTASK_ID>0 or P.PROOVED=1 or P.PROOVED_BY_SCAN=1 );  

 if(t2>0) then 
    return  'no';
 end if;
 
   tmpVar := 'no';

select IN_PROCESS into tmpVar from ( select CC.IN_PROCESS    
     from RABAEV.RRL_SBORKA_PALLETS PP , RABAEV.RRL_SBORKA_PALLETS_COND CC
     where  PP.ST_NUMBER=ST_N  and PP.STATE = CC.COND  and  CC.IN_PROCESS =1 ) where ROWNUM<=1 ; 


     if(tmpVar=1) then
        return 'no';
     else
        return 'yes';
     end if;
     
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'yes';
     WHEN OTHERS THEN
       RAISE;
END RRL_MAY_DELETE;
/

prompt
prompt Creating function RRL_MAY_DISTRIBUTE
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_MAY_DISTRIBUTE
(
    articul1 varchar2 ,
    exp_date1 date
)
 RETURN int IS
-- Возвращает 1, если товар уже нельзя распределять.

tmpVar varchar(1250);
days_left interval day(5) TO SECOND;
days_left1 number;
days_best_before number;
perc1 number ;
perc2 int;
ware_id1 int;                                                                                
                  
day_of_distr_end date;
                                                              
BEGIN



day_of_distr_end := RRL_DAY_DISTRIBUTE_ENDS( articul1 , exp_date1   );
if( day_of_distr_end is null ) then 
-- Товар протух 
    return 0;
else 
    
    if( day_of_distr_end> SYSTIMESTAMP  ) then
        return 1;
    end if;
    
end if;



   RETURN 0;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  1 ;
     WHEN OTHERS THEN
       RETURN 1;
END  RRL_MAY_DISTRIBUTE;
/

prompt
prompt Creating function RRL_OP_WEIGHT
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_OP_WEIGHT( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;


BEGIN
   tmpVar := 0;
select sum(  R.ORDER_WEIGHT )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    R.PALLET_UID = PALLET_UID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_OP_WEIGHT;
/

prompt
prompt Creating function RRL_OP_WEIGHT2
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_OP_WEIGHT2( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;
-- ВЕС ПАЛЛЕТА С УЧЕТОМ ВЕСА ТАРЫ для УКАЗАННОЙ ФАСОВКИ ТОВАРА

BEGIN
   tmpVar := 0;
select sum(  R.ORDER_WEIGHT + RRL_CARTON_WEIGHT2( R.ARTICUL , R.QUANTITY , R.CURRENT_MOD_ID )  )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    R.PALLET_UID = PALLET_UID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_OP_WEIGHT2;
/

prompt
prompt Creating function RRL_OTHOD_PALLET_PODBOR_PARTII
prompt ================================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_OTHOD_PALLET_PODBOR_PARTII
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    PALLET_ID1 varchar2 
)

 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);
PALLET_ROW_ID1 int;
count_of_PUID int;
new_part_id int;
vychet number;
all_found int;
mod_id4 int;
articul_for varchar2(255);

-- Курсор со строками паллета, для которых не выбрана партия .
cursor rowss is 
select * from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_ID1 and QUANTITY>0 and PRIHOD_PALLET_UID is null ;

--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
    
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE , RRL_PALLETS.ARTICUL
  from RABAEV.RRL_REMAINS , RABAEV.RRL_PALLETS  
    where RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and
     RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  and RRL_PALLETS.ARTICUL = articul_for
     order by RRL_PALLETS.EXPIRY_DATE  ; 
    
BEGIN

all_found:=1;
DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar   from RABAEV.RRL_SBORKA_PALLETs where PALLET_UID = PALLET_ID1;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;

/*
При закрытии отгрузочной паллеты:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на строку паллета в количестве Количество_отбора  
                Количество_отбора  =0 
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


count_of_PUID := 0;
new_part_id:=0;

for naklad_row in rowss loop

count_of_PUID :=0 ;
PALLET_ROW_ID1:= naklad_row.ID;
tmpVar:=0;
kolvo_otbora:=naklad_row.QUANTITY;
   articul_for := naklad_row.ARTICUL ;
    
   DBMS_OUTPUT.put_line(  concat( 'НОВАЯ СТРОКА ПАЛЛЕТЫ ОТГРУЗКИ!' , naklad_row.ARTICUL ) );
   select CELL into  current_cell from  RABAEV.RRL_ARTICULS  where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ; 
 
   DBMS_OUTPUT.put_line( concat( 'ЯЧЕЙКА ОТБОРА=' , current_cell ) );
    
    for  ddd8 in rests_in_cell loop  -- ЦИКЛ ПО ОСТАТКАМ В ЯЧЕЙКЕ ОТБОРА 
        
          
        
        if(kolvo_otbora>0) then
            
        DBMS_OUTPUT.put_line( concat( concat( '  НОВАЯ СТРОКА ОСТАТКОВ кол-во=' , to_char( ddd8.REMAIN  )   ) , concat ( ddd8.UID_POLETA , concat( ' Дата '  , to_char( ddd8.EXPIRY_DATE  ) ) ) ) );
        DBMS_OUTPUT.put_line(  concat( '  количество отбора1= ' , to_char(kolvo_otbora ) ) );     
        
        
            count_of_PUID :=count_of_PUID +1;
            
            /*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если
        конец цикла  
            */ 
                     
            DBMS_OUTPUT.put_line(  CONCAT( 'REMAIN = ' , to_char( ddd8.REMAIN ) ) );
            if(kolvo_otbora <= ddd8.REMAIN )  then
               -- ЕСЛИ ОСТАТОК КОЛИЧЕСТВА ОТБОРА МЕНЬШЕ ЛИБО РАВЕН ПАРТИИ В ЯЧЕЙКЕ . 
                   vychet := kolvo_otbora;
                   kolvo_otbora:=0;
            else
                    vychet:=ddd8.REMAIN; 
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
            end if;      

             DBMS_OUTPUT.put_line( concat( 'count_of_PUID=' , count_of_PUID ));
            if(  count_of_PUID =1 ) then -- Назначение ПАРТИИ 
                      
            ---уке
            --mod_id4 
              select  PPP.MOD_ID into  mod_id4  from RRL_PALLETS PPP where PPP.UID_PALLET= ddd8.UID_POLETA  ;
                      
                        update RABAEV.RRL_SBORKA_PALLET_ROWS set 
                        CURRENT_MOD_ID  = mod_id4  ,
                        PRIHOD_PALLET_UID = ddd8.UID_POLETA , 
                         PRIHOD_PALLET_UID_COUNT = count_of_PUID ,
                         EXPIRY_DATE = ddd8.EXPIRY_DATE where ID = naklad_row.ID ; 
                         
                         delete from  RABAEV.RRL_SBORKA_PALL_ROWS_PARTS  where PALLET_UID=ddd8.UID_POLETA and ARTICUL=ddd8.ARTICUL ; 
                         
            else 
                      
                        SELECT RABAEV.RRL_SBORKA_PALL_ROWS_PARTSSQ.NEXTVAL INTO new_part_id FROM dual;
                        
                            insert into  RABAEV.RRL_SBORKA_PALL_ROWS_PARTS   
                            ( ID ,  PALLET_UID , COUNT , ARTICUL ,  EXPIRY_DATE ) values 
                            ( new_part_id ,ddd8.UID_POLETA , kolvo_otbora , ddd8.ARTICUL , ddd8.EXPIRY_DATE   );
                      
                        update RABAEV.RRL_SBORKA_PALLET_ROWS set 
                        PRIHOD_PALLET_UID_COUNT = count_of_PUID 
                        where ID = naklad_row.ID ;
                      
            end if; -- Назначение ПАРТИИ 

        end if;
    end loop;

         DBMS_OUTPUT.put_line(  '  закончено распределение остатков ' );   
         DBMS_OUTPUT.put_line( concat( concat( '  осталось распределеить= ' , to_char( kolvo_otbora ) ) , concat( ' из первоначальных ' , naklad_row.QUANTITY ) ) );     
 
 
    if (kolvo_otbora >0 )  then
--        update RABAEV.RRL_SBORKA_PALLET_ROWS    set  condition=2 where ID = naklad_row.ID ;
        kolvo_otbora:=0;
        all_found:=0;
    else
        null;
  --      update RABAEV.RRL_SBORKA_PALLET_ROWS    set  condition=3 where ID = naklad_row.ID ;
    end if;
    
   DBMS_OUTPUT.put_line(  '  почти конец ' );   
end loop;
    
    
    if(all_found=0) then
        return 'Не все партии найдены';
    end if;
    
    
   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   
   RETURN 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_OTHOD_PALLET_PODBOR_PARTII;
/

prompt
prompt Creating function RRL_PAL_KOR_COUNT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PAL_KOR_COUNT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum(  RRL_COUNT_KOR2( ARTICUL , QUANTITY ,  CURRENT_MOD_ID  )     )  into tmpVar
 from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 




   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_KOR_COUNT;
/

prompt
prompt Creating function RRL_PALLET_HAS_MODS
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PALLET_HAS_MODS(
    PALLET_UID1  varchar2 
 )
 
 RETURN int IS 
tmpVar number;
BEGIN

   tmpVar := 0;
  

select count(  MODS.ID )  into tmpVar 
from   RABAEV.RRL_SBORKA_PALLET_ROWS R , RRL_ARTICUL_MODS MODS
     where    PALLET_UID =   PALLET_UID1  and R.ARTICUL = MODS.ARTICUL and R.CURRENT_MOD_ID = MODS.ID and MODS.DELETED<>1 ; 


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PALLET_HAS_MODS;
/

prompt
prompt Creating function RRL_PALLET_WEIGHT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PALLET_WEIGHT(PALID varchar2  )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN

select sum(  R.ORDER_WEIGHT )  into tmpVar from  RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  R.PALLET_UID   = PALID    ;
 
   RETURN tmpVar;

 
 
 
   

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PALLET_WEIGHT;
/

prompt
prompt Creating function RRL_PALLET_WEIGHT_SET
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PALLET_WEIGHT_SET(
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int IS 
    tmpVar number;
    pogr number;
    IDD1 int;
    SPIS_OTBOR_ON_SCAN_OPALL1 int;
    vhelp2 varchar2(255);
BEGIN

 
if( TO_NUMBER(TRIAL_WEIGHT1)>0 ) then
    update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TO_NUMBER( TRIAL_WEIGHT1 ), VESOVSHIK = user_id1  
    where PALLET_UID=PALLET_UID1;
end if;

if ( (WOOD_WEIGHT1)>0) then
    update RABAEV.RRL_SBORKA_PALLETS set   WOOD_WEIGHT = TO_NUMBER( WOOD_WEIGHT1 ) , VESOVSHIK = user_id1  
    where PALLET_UID=PALLET_UID1;
end if;

return '1';
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '0';
     WHEN OTHERS THEN
     return '-1';
       -- Consider logging the error and then re-raise
      
END RRL_PALLET_WEIGHT_SET;
/

prompt
prompt Creating function RRL_PALLET_WEIGHT2
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PALLET_WEIGHT2(
    PALLET_UID1  varchar2 
 )
 
 RETURN number IS 
tmpVar number;
BEGIN

   tmpVar := 0;
   
select sum(  R.ORDER_WEIGHT + RRL_CARTON_WEIGHT2( ARTICUL , QUANTITY , CURRENT_MOD_ID )  )  into tmpVar from   RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where    PALLET_UID =   PALLET_UID1  ; 




-- RRL_CARTON_WEIGHT( ARTICUL , QUANTITY ) 



   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PALLET_WEIGHT2;
/

prompt
prompt Creating function RRL_PAL_ROW_COUNT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PAL_ROW_COUNT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select count( R.ID  )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_ROW_COUNT;
/

prompt
prompt Creating function RRL_PAL_VOLUME
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PAL_VOLUME( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID   ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_VOLUME;
/

prompt
prompt Creating function RRL_PAL_WEIGHT
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PAL_WEIGHT( PALID varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select sum(  R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.PALLET_UID   = PALID and P.PALLET_UID =  R.PALLET_UID   ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_PAL_WEIGHT;
/

prompt
prompt Creating function RRL_PAY_BILLINGORDER
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PAY_BILLINGORDER(
bill_id int ,
act int -- 0 ОТкрыть 1  Закрыть
)

RETURN varchar2 IS 



BEGIN
   
   -- Если данный рейс принадлежит уже закрытому счету, то возвращаем ошибку.
    if(act=1) then
       
      update RABAEV.RRL_BILL_ORDERS set payed=1    where ID = bill_id ;
       
    end if;


   RETURN 'OK';

END RRL_PAY_BILLINGORDER;
/

prompt
prompt Creating function RRL_PRIHOD_MAY_STORNO
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHOD_MAY_STORNO(
    order_id1  int 
 )
 
 RETURN int IS 
tmpVar number;
BEGIN
-- Проверяем - все-ли паллеты данного прихода находятся в ячейке IN_DOCK

   tmpVar := 0;  

   SELECT count(PP.UID_PALLET) into tmpVar
      FROM RRL_PALLETS PP , RRL_REMAINS REMAINS  where PRIHOD_NAKLAD_ID= order_id1 
    and PP.UID_PALLET = REMAINS.UID_POLETA and REMAINS.CELL<>'IN_DOCK'     ;

if( tmpVar=0 ) then 

    return 1;

else

    return 0;

end if;

   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_PRIHOD_MAY_STORNO;
/

prompt
prompt Creating function RRL_PRIHODPALLET_CALC_COUNT
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHODPALLET_CALC_COUNT(
PALLET_UID1 varchar2 , 
weight1 number ,
option1 int  -- 1= дан вес товара  2=вест товара без картона  
 )
 -- Вычисление  количества товара на основании веса данного паллета 
 -- на основании модификации
 -- 
 
 RETURN number IS 

tmpVar number;
articul_id1 varchar2(255) ;
FASOVKA_ID int ;
wsht number; 
kwsht number ;

BEGIN




select PAL.ARTICUL , PAL.MOD_ID into articul_id1 , FASOVKA_ID  from  RABAEV.RRL_PALLETS PAL where PAL.UID_PALLET=PALLET_UID1 ;
select MD.SHT_WEIGHT , MD.KARTON_WEIGHT into wsht , kwsht  from RRL_ARTICUL_MODS MD where MD.ARTICUL= articul_id1;

if(wsht=0) then 
return 0;
 end if;

if(option1=1) then
    tmpVar :=weight1 / ( wsht + kwsht) ; 
    RETURN tmpVar;
end if;
 
if(option1=2) then
    if(wsht - kwsht=0) then return 0;  end if;
    tmpVar := weight1/ (wsht  )  ; 
    RETURN tmpVar;
end if;
 

       RETURN 0;
       
       
EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
       
END RRL_PRIHODPALLET_CALC_COUNT;
/

prompt
prompt Creating function RRL_PRIHODPALLET_CALC_WEIGHT
prompt ==============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHODPALLET_CALC_WEIGHT(
PALLET_UID1 varchar2 , 
COUNT1 number ,
option1 int  -- 1= вес товара  2=вест товара без картона  3= вес картона
 )
 -- Вычисление веса количества товара данного паллета 
 -- на основании модификации
 -- 
 
 RETURN number IS 

tmpVar number;
articul_id1 varchar2(255) ;
FASOVKA_ID int ;
wsht number; 
kwsht number ;

BEGIN


select PAL.ARTICUL , PAL.MOD_ID into articul_id1 , FASOVKA_ID  from  RABAEV.RRL_PALLETS PAL where PAL.UID_PALLET=PALLET_UID1 ;

select MD.SHT_WEIGHT , MD.KARTON_WEIGHT into wsht , kwsht  from RRL_ARTICUL_MODS MD where MD.ARTICUL= articul_id1;

DBMS_OUTPUT.put_line(  'flag1' );

if(option1=1) then
DBMS_OUTPUT.put_line(  'flag2' );
DBMS_OUTPUT.put_line(  (wsht +kwsht) *COUNT1  );

    tmpVar := ( wsht + kwsht )*COUNT1 ; 
    RETURN tmpVar;
end if;
 
if(option1=2) then
    tmpVar := (wsht  )*COUNT1 ; 
    RETURN tmpVar;
end if;
 
if(option1=3) then
    tmpVar := (  kwsht )*COUNT1 ; 
    RETURN tmpVar;
end if;
 
   return 0;

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
END RRL_PRIHODPALLET_CALC_WEIGHT;
/

prompt
prompt Creating function RRL_PRIHODPALLET_CHANGE
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHODPALLET_CHANGE(
 PALLET_UID1 varchar2 , 
 art varchar2 ,
 UNIT_COUNT1  number ,
 DEFECT_PERC1  number ,
 COUNT_KOR1 int ,
 WEIGHT_BRUTTO1 number ,
 WEIGHT_TN1 number ,
 MOD_ID1 int 

  ) 


RETURN varchar2 IS 

 type_w1 int;
 tmpVar number;
 UNIT_COUNT2  number ;
 DEFECT_PERC2  number ;
 COUNT_KOR2 int ;
 WEIGHT_BRUTTO2 number ;
 WEIGHT_TN2 number ;
 MOD_ID2 int ;
 WEIGHT_OF_KOR2 number;
 WEIGHT_OF_SHT5 number;
 round5 int;
BEGIN

 WEIGHT_OF_SHT5:=0;
 UNIT_COUNT2  := UNIT_COUNT1;
 DEFECT_PERC2  := DEFECT_PERC1;
 COUNT_KOR2 := COUNT_KOR1;
 WEIGHT_BRUTTO2 := WEIGHT_BRUTTO1;
 WEIGHT_TN2 := WEIGHT_TN1;
 MOD_ID2 := MOD_ID1;
 if( DEFECT_PERC2 is null) then
    DEFECT_PERC2:=0;
 end if;
 

    select type_w ,round_to into type_w1 , round5  from RRL_ARTICULS where ACTICUL = art;

    if(type_w1=0) then
    
        DEFECT_PERC2:=0;
        begin 
            select  round( UNIT_COUNT2 / AA.COUNT_SHT_IN_KOR ,2 ) into COUNT_KOR2 from RRL_ARTICULS AA where acticul=art;
            select   CARTON_WEIGHT/1000 ,  WEIGHT_OF_SHT into  WEIGHT_OF_KOR2 ,  WEIGHT_OF_SHT5 from RRL_ARTICULS AA where acticul=art;
            if WEIGHT_OF_KOR2 is null then 
            return 'Исправьте Логопараметры: Укажите вес коробки1' ; 
            end if;
            
            if WEIGHT_OF_KOR2 =0 then 
            return 'Исправьте Логопараметры:Укажите вес коробки2' ; 
            end if;
            
            WEIGHT_BRUTTO2:= WEIGHT_OF_KOR2 *COUNT_KOR2+WEIGHT_TN2+ WEIGHT_OF_SHT5*UNIT_COUNT2;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'артикул не найден';
            WHEN OTHERS THEN
            RETURN 'Исправьте Логопараметры: укажите количество штук в коробке' ;
        end;
        MOD_ID2 := 0;
        
        
    end if;



    if(type_w1=1) then
        DEFECT_PERC2:=0;
        
         begin 
            select  round( UNIT_COUNT2 / AA.SHT_IN_KOR ,2 ) , (AA.KARTON_WEIGHT+AA.SHT_WEIGHT*AA.SHT_IN_KOR )   
            into COUNT_KOR2 , WEIGHT_OF_KOR2 from RRL_ARTICUL_MODS AA where ID=MOD_ID2;
 
            if WEIGHT_OF_KOR2 is null then 
            return 'Исправьте Логопараметры: Укажите вес коробки и штуки' ; 
            end if;
            WEIGHT_BRUTTO2 := WEIGHT_OF_KOR2 *COUNT_KOR2+WEIGHT_TN2;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'Исправьте Логопараметры: фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end;
         
    end if;



    if(type_w1=2) then
        --UNIT_COUNT2:=  (WEIGHT_BRUTTO2-WEIGHT_TN2) * ((100-DEFECT_PERC2)/100 );
        
        
        begin 
        
         select    (WEIGHT_BRUTTO2-WEIGHT_TN2-AA.KARTON_WEIGHT*COUNT_KOR2) * ((100-DEFECT_PERC2)/100 )    
            into UNIT_COUNT2   from RRL_ARTICUL_MODS AA where ID=MOD_ID2;
        
            select   (AA.KARTON_WEIGHT+AA.SHT_WEIGHT* AA.SHT_IN_KOR )   
            into WEIGHT_OF_KOR2 from RRL_ARTICUL_MODS AA where ID=MOD_ID2;
 
            if WEIGHT_OF_KOR2 is null then 
            return 'Исправьте Логопараметры: Укажите вес коробки и штуки, вложенность' ; 
            end if;
            
            if WEIGHT_OF_KOR2 =0 then 
            return 'Исправьте Логопараметры: Укажите вес коробки и штуки , вложенность' ; 
            end if;
            
           COUNT_KOR2 := (WEIGHT_BRUTTO2-WEIGHT_TN2)/WEIGHT_OF_KOR2;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end; 
        
    end if;

    if(type_w1=3) then
         begin 
        
         select    (WEIGHT_BRUTTO2-WEIGHT_TN2-AA.KARTON_WEIGHT*COUNT_KOR2) * ((100-DEFECT_PERC2)/100 )    
            into UNIT_COUNT2   from RRL_ARTICUL_MODS AA where ID=MOD_ID2;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end; 
    end if;


    if(type_w1=5) then
    
    
        begin 
            select    (WEIGHT_BRUTTO2-WEIGHT_TN2-AA.KARTON_WEIGHT*COUNT_KOR2) * ((100-DEFECT_PERC2)/100 )    
            into UNIT_COUNT2   from RRL_ARTICUL_MODS AA where ID=MOD_ID2;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'Исправьте Логопараметры: фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end;
    
    
        --UNIT_COUNT2:=  (WEIGHT_BRUTTO2-WEIGHT_TN2) * ((100-DEFECT_PERC2)/100 );
       
    end if;


    if(type_w1=6) then
    
            begin 
            select    (WEIGHT_BRUTTO2-WEIGHT_TN2-AA.KARTON_WEIGHT*COUNT_KOR2) * ((100-DEFECT_PERC2)/100 )    
            into UNIT_COUNT2   from RRL_ARTICUL_MODS AA where ID=MOD_ID2;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'Исправьте Логопараметры: фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end;
        
       -- UNIT_COUNT2:=  (WEIGHT_BRUTTO2-WEIGHT_TN2) * ((100-DEFECT_PERC2)/100 );
    end if;




    if(type_w1=7 ) then
    
            begin 
            select    ( AA.SHT_IN_KOR * COUNT_KOR2)   
            into UNIT_COUNT2   from RRL_ARTICUL_MODS AA where ID=MOD_ID2;

        EXCEPTION
            WHEN NO_DATA_FOUND THEN
            RETURN  'Исправьте Логопараметры: фасовка не найдена';
            WHEN OTHERS THEN
            RETURN  'Исправьте Логопараметры: укажите количество штук в фасовке'  ;
        end;
        DEFECT_PERC2:=0;
       -- UNIT_COUNT2:=  (WEIGHT_BRUTTO2-WEIGHT_TN2) * ((100-DEFECT_PERC2)/100 );
    end if;



update RRL_PALLETS set 
 UNIT_COUNT  = round( UNIT_COUNT2 , round5) ,
 DEFECT_PERC  = DEFECT_PERC2 ,
 COUNT_KOR = COUNT_KOR2 ,
 WEIGHT_BRUTTO = WEIGHT_BRUTTO2 ,
 WEIGHT_TN = WEIGHT_TN2 ,
 MOD_ID = MOD_ID2 
where UID_PALLET = PALLET_UID1;


       RETURN 'OK';
       
EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 1;
     WHEN OTHERS THEN
       RETURN 2;
       
END RRL_PRIHODPALLET_CHANGE;
/

prompt
prompt Creating function RRL_PRIHODPALLET_CHANGE_COUNT
prompt ===============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHODPALLET_CHANGE_COUNT(
PALLET_UID1 varchar2 , 
count1 number  ,
change_weight int -- менять ли вес?
 ) 
 -- Изменение количества в паллете. 
RETURN number IS 

tmpVar number;
articul_id1 varchar2(255) ;
FASOVKA_ID int ;
cond1 int ;
PRIHOD_ID int;
new_count_for_prihod number ;
ware_id1 int;
COUNT_WEIGHT_AUTORECALC1 int;
new_w number;
floating_weight1 int;
DEFECT_PERC1  number;
BEGIN
new_w:=0;
new_count_for_prihod :=0;
PRIHOD_ID :=0;


select PAL.ARTICUL , PAL.MOD_ID ,  PAL.PRIHOD_NAKLAD_ID , PAL.DEFECT_PERC  into articul_id1 , FASOVKA_ID  , PRIHOD_ID , DEFECT_PERC1 
from  RABAEV.RRL_PALLETS PAL where PAL.UID_PALLET=PALLET_UID1 ;

select ware_id , CONDITION into ware_id1 , cond1 from RABAEV.RRL_PRIHOD_NAKLAD where ID =  PRIHOD_ID ;

select COUNT_WEIGHT_AUTORECALC into COUNT_WEIGHT_AUTORECALC1 from RRL_WARES where id=ware_id1;
select floating_weight into floating_weight1 from RRL_ARTICULS where acticul = articul_id1 ;
if( floating_weight1=1) then
     COUNT_WEIGHT_AUTORECALC1:=0;
end if;


if( cond1=2 ) then
return 0; -- Накладная закрыта, изменения запрещены.
end if;
 


update RABAEV.RRL_PALLETS set UNIT_COUNT = count1 where  UID_PALLET = PALLET_UID1;
-- обновляем накладную
select sum(unit_count) into new_count_for_prihod from  RABAEV.RRL_PALLETS 
    where PRIHOD_NAKLAD_ID =  PRIHOD_ID and ARTICUL=articul_id1 ;

if( new_count_for_prihod>0 ) then
    update RABAEV.RRL_PRIHOD_NAKLAD_ROWS set COUNT1=new_count_for_prihod where ORDID = PRIHOD_ID and ARTICUL =articul_id1 ;
end if;


if(change_weight=1) then

    if(COUNT_WEIGHT_AUTORECALC1=1) then 
    -- Обновляем вес 
        
        new_w:=RRL_PRIHODPALLET_CALC_WEIGHT( PALLET_UID1 ,  count1 , 1 );  
        
        update RABAEV.RRL_PALLETS set WEIGHT_BRUTTO= obj2number( WEIGHT_TN ) + new_w*(100+DEFECT_PERC1)/100  where  UID_PALLET = PALLET_UID1;
        select WEIGHT_BRUTTO  into new_w from  RABAEV.RRL_PALLETS where  UID_PALLET = PALLET_UID1;
        return new_w;    
    end if;
end if;

       RETURN 0;
       
EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
       
END RRL_PRIHODPALLET_CHANGE_COUNT;
/

prompt
prompt Creating function RRL_PRIHODPALLET_CHANGE_WEIGHT
prompt ================================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHODPALLET_CHANGE_WEIGHT(
PALLET_UID1 varchar2 , 
weight_brutto1 number  ,
change_count int -- менять ли вес?
 ) 
 -- Изменение веса в паллета. 
RETURN number IS 

tmpVar number;
articul_id1 varchar2(255) ;
FASOVKA_ID int ;
cond1 int ;
PRIHOD_ID int;
new_count_for_prihod number ;
ware_id1 int;
COUNT_WEIGHT_AUTORECALC1 int;
new_w number;
new_count int;
floating_weight1 int;
DEFECT_PERC1 number;

BEGIN
new_w:=0;
new_count_for_prihod :=0;
PRIHOD_ID :=0;
new_count:=0;

select PAL.ARTICUL , PAL.MOD_ID ,  PAL.PRIHOD_NAKLAD_ID , PAL.DEFECT_PERC  into articul_id1 , FASOVKA_ID  , PRIHOD_ID , DEFECT_PERC1
from  RABAEV.RRL_PALLETS PAL where PAL.UID_PALLET=PALLET_UID1 ;

select ware_id , CONDITION into ware_id1 , cond1 from RABAEV.RRL_PRIHOD_NAKLAD where ID =  PRIHOD_ID ;
select COUNT_WEIGHT_AUTORECALC into COUNT_WEIGHT_AUTORECALC1 from RRL_WARES where id=ware_id1;
select floating_weight into floating_weight1 from RRL_ARTICULS where acticul = articul_id1 ;
if( floating_weight1=1) then
     COUNT_WEIGHT_AUTORECALC1:=0;
end if;


if( cond1=2 ) then
return 0; -- Накладная закрыта, изменения запрещены.
end if;
 
update RABAEV.RRL_PALLETS set WEIGHT_BRUTTO = weight_brutto1 where  UID_PALLET = PALLET_UID1;

DBMS_OUTPUT.put_line( 'Начало' );

if(change_count=1) then

    if(COUNT_WEIGHT_AUTORECALC1=1) then 
        
        
        select ( obj2number(WEIGHT_BRUTTO) - obj2number( WEIGHT_TN ) )  into new_w from  RABAEV.RRL_PALLETS where  UID_PALLET = PALLET_UID1;
        DBMS_OUTPUT.put_line( 'flag2' );
        DBMS_OUTPUT.put_line( concat ( ' Вес товара в паллете=' , to_char( new_w ) ) );

        
        if ((new_w>0) and (FASOVKA_ID>0)) then
            --Минус процент брака, минус вес картона. 
            DBMS_OUTPUT.put_line( concat ( ' FASOVKA_ID=' , to_char(FASOVKA_ID) ) );
            DBMS_OUTPUT.put_line( concat ( ' DEFECT_PERC1=' , to_char(DEFECT_PERC1) ) );
            
            select round( ( (new_w* (100 - DEFECT_PERC1 ))) /(100*( MD.SHT_WEIGHT + MD.KARTON_WEIGHT)) , 0 ) into new_count from RRl_ARTICUL_MODS MD where MD.ID = FASOVKA_ID ;
            DBMS_OUTPUT.put_line( concat ( ' количество в паллете=' , to_char(FASOVKA_ID) ) );
            DBMS_OUTPUT.put_line( 'flag3' );
            return new_count;
        end if;
        
        return new_w;    
    end if;
end if;

       RETURN 0;
       
EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RETURN 0;
       
END RRL_PRIHODPALLET_CHANGE_WEIGHT;
/

prompt
prompt Creating function RRL_PRIHOD_VERIFY
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_PRIHOD_VERIFY(
 prihod_id1 int 
  ) 
-- Процедура проверки прихода на корректность 

RETURN varchar2 IS 

cursor rr is
select 
PAL.UID_PALLET ,
PAL.ARTICUL ,
PAL.UNIT_COUNT ,
PAL.COUNT_KOR ,
PAL.WEIGHT_BRUTTO ,
PAL.WEIGHT_TN ,
PAL.MOD_ID ,
ART.TYPE_W
from RRL_PALLETS PAL , RRL_ARTICULS ART where PAL.PRIHOD_NAKLAD_ID = prihod_id1 and ART.ACTICUL = PAL.ARTICUL ; 

BEGIN

for r in rr loop
    if( r.UNIT_COUNT<=0 ) then
        return concat('Количество должно быть больше 0:' , r.UID_PALLET ) ;
    end if;

    if( r.UNIT_COUNT<=0 ) then
        return concat('Количество коробок должно быть больше 0:' , r.UID_PALLET ) ;
    end if;
    
    
    if( r.type_w =2 or  r.type_w =3 or  r.type_w =5 or r.type_w =6   ) then
    
        if(  r.WEIGHT_BRUTTO is null ) then
            return concat('Вес паллета должен быть больше 0:' , r.UID_PALLET ) ;
        end if;
        
        if(  r.WEIGHT_TN is null ) then
            return concat('Вес поддона должен быть больше 0:' , r.UID_PALLET ) ;
        end if;
        
        if( r.WEIGHT_BRUTTO > 1500 or r.WEIGHT_BRUTTO<=r.WEIGHT_TN  ) then
            return concat('Вес паллета должен быть больше 0 и меньше 1500:' , r.UID_PALLET ) ;
        end if;
        
        if( r.WEIGHT_TN > 30 or r.WEIGHT_TN<9  ) then
            return concat('Вес поддона должен быть больше 9 и меньше 30:' , r.UID_PALLET ) ;
        end if;
        
    end if;
    
    
    if  ( r.MOD_ID is null ) or ( r.MOD_ID =0 ) then 
      if( r.type_w =1 or  r.type_w =2 or  r.type_w =3 or  r.type_w =6   or  r.type_w =5  ) then
       return concat('Укажите фасовку:' , r.UID_PALLET ) ;
      end if;
    end if;
    
end loop;


       RETURN 'OK';
       
EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'NO_DATA_FOUND';
     WHEN OTHERS THEN
       RETURN 'OTHERS';
       
END RRL_PRIHOD_VERIFY;
/

prompt
prompt Creating function RRL_REVIZION_CELL
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_REVIZION_CELL

(
    CELL1 varchar2 ,
    count1 number ,
    user_id1 varchar2
) return varchar2
 -- ПРОВЕДЕНИЕ ИНВЕНТАРИЗАЦИИ ДЛЯ ЯЧЕЙКИ в штуках. БЕЗ УЧЕТА СРОКОВ ГОДНОСТИ И ПАРТИЙ. 
 -- процедура выбирает в ячейке партии в порядке  сроков годности (спуска их  вниз, )     
 -- и оставляет партии с самым свежим сроком. 
 -- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Списать с ячейки претензий с последней партией , находящейся  в ячейке отбора
 --  иначе 
 --     Породить алерт 
 --     Потребовать разбирательства специалиста по качеству, то есть списания  с указанием партии (это другая процедура) 
 --     возврат ошибки
 --конец если    
 --      
 -- возврат ок.    
 
is

cursor rema is select rm.REMAIN , rm.UID_POLETA from rrl_remains rm  where rm.CELL=CELL1 and   rm.REMAIN>0 
order by  rm.TIME_OF_LAST_UPDATE desc;

tmp varchar2(255);
to_spis number;
ostatok number;
begin
ostatok:=count1;

for  rr in rema  loop

    if(ostatok>=rr.REMAIN) then
    -- все ок.  
        null;
    
    else -- Если остаток спиания меньше остатка в ячейке, то  данная партия в количестве [rr.REMAIN-ostatok] 
         -- списывается в недостачу. если ostatok<0 , то списывается вся партия . 
        
        if(rr.REMAIN<ostatok) then
            to_spis:=rr.REMAIN;
        else
            to_spis:=rr.REMAIN-ostatok ;
        end if;
        
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
        rr.UID_POLETA , 
        'INVENT' ,
        to_spis ,
        user_id1 );
        
        
    end if;
    
ostatok:=ostatok- rr.REMAIN;
end loop;

-- если ostatok > 0  , то в ячейке не хватает  партий, их надо найти или спросить.
-- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Списать с ячейки претензий с последней партией , находящейся  в ячейке отбора
-- если ostatok < 0 , то в ячейке зафиксирована недостача в количестве ostatok.  возвращаем ок.

if( ostatok > 0  ) then 
null;
-- Вываливаемся с ошибкой, либо берем остатки из ячейки недостач - последние упавшие. 
    return 'neok';
else 
 -- Порождаем сообщение о недостаче. 
    return 'ok';
end if;


return 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_REVIZION_CELL;
/

prompt
prompt Creating function RRL_REVIZION_CELL_KOR
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_REVIZION_CELL_KOR
(
    CELL1 varchar2 ,
    count_kor2 varchar2 ,
    user_id1 varchar2
) return varchar2

 -- ПРОВЕДЕНИЕ ИНВЕНТАРИЗАЦИИ ДЛЯ ЯЧЕЙКИ в штуках. БЕЗ УЧЕТА СРОКОВ ГОДНОСТИ И ПАРТИЙ. 
 -- процедура выбирает в ячейке партии в порядке  сроков годности (спуска их  вниз, )     
 -- и оставляет партии с самым свежим сроком. 
 -- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Списать с ячейки претензий с последней партией , находящейся  в ячейке отбора
 --  иначе 
 --     Породить алерт 
 --     Потребовать разбирательства специалиста по качеству, то есть списания  с указанием партии (это другая процедура) 
 --     возврат ошибки
 --конец если    
 -- возврат ок.    
 
is

articul1 varchar2(50);


cursor rema_in_p  is 
select rm.REMAIN as RM1 , RABAEV.RRL_COUNT_KOR3( pal.ARTICUL ,  rm.REMAIN , rm.UID_POLETA ) kk , 
rm.UID_POLETA 
from rrl_remains rm , rrl_pallets pal 
where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
  and    pal.ARTICUL=articul1  and rm.REMAIN>0
order by    pal.EXPIRY_DATE asc;


cursor rema is select rm.REMAIN as RM1 , RABAEV.RRL_COUNT_KOR3( pal.ARTICUL ,  rm.REMAIN , rm.UID_POLETA ) kk , rm.UID_POLETA 
from rrl_remains rm , rrl_pallets pal 
where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
  and  rm.REMAIN  >0 
order by pal.EXPIRY_DATE desc;


count_kor1 int ;
tmp varchar2(255);
to_spis number;
ostatok number;
nedostacha number;
is_otbor1 int;
last_pal_uid varchar2(50);

new_event_uid int;
ostatok2 number;

begin
ostatok2:=0;
last_pal_uid:='';
is_otbor1:=0;
nedostacha:=0;
count_kor1:= to_number( count_kor2 ) ;
ostatok:=count_kor1;
-- Проверяем, что данная ячейка является ячейкой отбора. Если не так - уходим с ошибкой.

    begin
        select ccc.OTBOR  into is_otbor1  from rrl_cells ccc where cell=cell1; 
       -- DBMS_OUTPUT.put_line('flag 1');
        select  acticul into articul1 from rrl_articuls where cell = CELL1;
    exception 
        when no_data_found then  return 'НЕТ ЯЧЕЙКИ ОТБОРА';
        when others then return 'ошибка RRL_REVIZION_CELL_KOR';
    end;



if( is_otbor1=0 ) then
    return 'НЕ ОТБОР';
end if;

for  rr in rema  loop  -- ПО Всем партиям ячейки отбора , упорядоченных по СГ ,  Проверяем- что вошло, а что нет.

DBMS_OUTPUT.put_line( concat( concat('ячейка, Паллет = ' ,  rr.UID_POLETA) , concat( ' кол-во=' , rr.kk ) ) );

    if(rr.kk=0 ) then
    DBMS_OUTPUT.put_line( concat('нулевое кол-во коробок для ' ,  rr.UID_POLETA) );
        return concat('нулевое к-во коробок для ' ,  rr.UID_POLETA);
    end if;

    if(ostatok>=rr.kk) then
    -- все ок.  
      null;
    else 
        last_pal_uid := rr.UID_POLETA ;
        if(rr.kk<=ostatok) then -- если ostatok<0 , то списывается вся партия . 
            to_spis:=rr.RM1;
            DBMS_OUTPUT.put_line( concat( 'FL1 to_spis=' , to_spis ) );

        else -- Если остаток спиания меньше остатка в ячейке, то  данная партия в количестве [rr.REMAIN-ostatok] списывается в недостачу. 
            to_spis:= (rr.kk-ostatok)*floor(  ( rr.rm1/rr.kk )  );  -- rr.rm1 - (rr.rm1*ostatok)/rr.kk ; -- ;
            DBMS_OUTPUT.put_line( concat( concat( 'FL2 rr.kk=' , to_char(rr.kk) )  , concat( ' rr.rm1/rr.kk=' , to_char(rr.rm1/rr.kk) ) ) );
            DBMS_OUTPUT.put_line( concat( 'FL3 ostatok=' , ostatok ) );

        end if; -- ВЛОЖЕННОСТЬ В КОРОБКУ = обязательно целое число!!!! 
        
        nedostacha:= nedostacha + to_spis;
        DBMS_OUTPUT.put_line( concat( concat('списываем в недостачу ' , rr.UID_POLETA )   , concat( ' кол=' , to_char(to_spis) ) ) );
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
        rr.UID_POLETA , 
        'INVENT_P' ,
        to_spis ,
        user_id1 );
        
        
    end if;
    
    if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
        last_pal_uid := rr.UID_POLETA ;
    end if;
    
  ostatok:=ostatok- rr.kk;
if(ostatok<0) then
    ostatok:=0;
end if;

end loop; -- ПО Всем партиям ячейки отбора , упорядоченных по СГ ,  Проверяем- что вошло, а что нет.


-- если ostatok > 0  , то в ячейке не хватает  партий, их надо найти или спросить.
-- Если количество  превышает, указанное по учету, на величину менее 100 штук то  , 
 --     Пока остаток не скомпенсирован, по всем партиям ячейки INVENT_P 
 --     Списать с ячейки излишков в ячейку, количество = min ( остаток , остаток в ячейке  )
 
 -- если ostatok < 0 , то в ячейке зафиксирована недостача в количестве ostatok. она списана уже на  INVENT_P возвращаем ок.
 -- иначе 
 -- Если после этого оказалось, что не хватает товара для восполнения излишка, берем последнюю партию в ячейке отбора. 
 -- 



if( ostatok > 0  ) then 

    DBMS_OUTPUT.put_line ( concat( 'излишки есть кол=' , to_char(ostatok) ) );
    ostatok2:=ostatok;
    -- НОВОЕ 
    -- зафиксирован излишек, данный излишек нужно переслать из INVENT_P в текущую ячейку. 
    
    for  rr in rema_in_p  loop
        
        if ( ostatok2>0 ) then 
        
        
          if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
                last_pal_uid := rr.UID_POLETA ;
          end if;
        
          if(rr.kk<=ostatok2) then 
          DBMS_OUTPUT.put_line ( 'flag 1 ');
            to_spis:=rr.RM1;
          else 
          DBMS_OUTPUT.put_line ( concat( concat( 'flag 2   ostatok2=' , to_char(ostatok2) ) , concat( '    rr.kk= ' , to_char(rr.kk) ) ));
             to_spis:= (ostatok2)*floor(  ( rr.rm1/rr.kk )  );  
          end if;
        
            DBMS_OUTPUT.put_line ( concat( concat( 'INVENT_P => ' , concat( cell1 , ' кол=' )  )   ,to_number(  to_spis )  ));
            DBMS_OUTPUT.put_line ( concat( ' паллет =' , rr.UID_POLETA  ));
            
            SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
            insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
                TYPE_EVENT , UID_POLETA , USER_ID ) values
                ( new_event_uid ,  cell1  , 'INVENT_P' , SYSTIMESTAMP , to_spis , 2 , rr.UID_POLETA , user_id1  );
            
            ostatok2:=ostatok2-rr.kk;
            
        end if;
        
    end loop;  
    

    -- Вываливаемся с ошибкой, либо 
    -- если по складу действует настройка пополнения излишков из недостач, то ищем паллет, попавший в недостачу не позднее 2 дней от текущей даты
    -- иначе весь излишек проводим   
    -- если он есть, то делаем проводку из него на ячейку 
    
    if ostatok2>0 then  -- ЕСЛИ КОЛИЧЕСТВА В ЯЧЕЙКЕ INVENT_P не достаточно 


        -- 
        if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_POLETA  into last_pal_uid from(  
                    select  rm.UID_POLETA 
                    from rrl_remains rm , rrl_pallets pal 
                    where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
                      and  rm.REMAIN  >0 and pal.ARTICUL=articul1 
                    order by sign( rm.REMAIN)  asc ,  pal.EXPIRY_DATE desc ) where rownum=1  ; 
            exception 
                    when no_data_found then  null ;
                    when others then null;
            end;
        end if;


        if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_POLETA  into last_pal_uid from(  
                    select  rm.UID_POLETA 
                    from rrl_remains rm , rrl_pallets pal 
                    where rm.CELL=cell1 and pal.UID_PALLET=rm.UID_POLETA
                      and  rm.REMAIN  >0 and pal.ARTICUL=articul1 
                    order by  pal.EXPIRY_DATE desc ) where rownum=1  ; 
            exception 
                    when no_data_found then  null ;
                    when others then null;
            end;
        end if;
        


      if (( last_pal_uid is null ) or ( last_pal_uid='' )) then
            begin 
                    select UID_PALLET into last_pal_uid from(  
                    select pal.UID_PALLET from rrl_pallets pal where pal.ARTICUL=articul1 order by Expiry_date desc ) 
                    where rownum=1 ; 
            exception 
                    when no_data_found then  return 'ИЗЛИШКИ НЕ РАСП';
            end;
      end if;

      
        to_spis:=round(  ostatok* 10000/RABAEV.RRL_COUNT_KOR3 ( articul1  ,10000 , last_pal_uid ),0 ) ; 
        DBMS_OUTPUT.put_line ( concat( concat( 'Недостача покрыта не вся!!! Партия= ' , last_pal_uid  ) , concat( ' списываем=' , to_char(to_spis) )  ) );
        SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
        insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
             TYPE_EVENT , UID_POLETA , USER_ID ) values
             ( new_event_uid ,  cell1  , 'INVENT_P' , SYSTIMESTAMP , to_spis , 2 , last_pal_uid , user_id1  );
             
    end if;  -- ЕСЛИ КОЛИЧЕСТВА В ЯЧЕЙКЕ INVENT_P не достаточно 
 
 
    return  concat ( 'ИЗЛИШКИ ' ,  concat( to_char(ostatok) , ' кор' ) );
else 

if(ostatok <> 0) then
    return  concat( 'СПИСАНО ' , to_char(ostatok) ) ;
end if;
--return 'СОВПАЛО';
DBMS_OUTPUT.put_line('излишков нет');
 -- Порождаем сообщение о недостаче. 
    return concat( 'НЕДОСТАЧА ' , concat( to_char(nedostacha) , ' шт' )  ) ;
end if;


return 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_REVIZION_CELL_KOR;
/

prompt
prompt Creating function RRL_SBORKA_CELL
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_CELL(
articul1 varchar2 ,
ware_id int , 
count1 number ,
addr1 varchar2
 )
RETURN varchar2
 IS 
-- ФУНКЦИЯ ВОЗВРАЩАЕТ ЯЧЕЙКУ ОТБОРА ДЛЯ АРТИКУЛА, в зависимости от склада , количества и адреса. 
ret1 varchar2(255);
BEGIN
    
    select aa.CELL into ret1 from rrl_articuls aa where aa.ACTICUL = articul1 ;
    
    
    
    return ret1;
exception
when no_data_found then return '';
    when others then
    return '';
END RRL_SBORKA_CELL;
/

prompt
prompt Creating function RRL_SBORKA_PALLET_ROWS_ADD
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLET_ROWS_ADD (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int

) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD ;
/

prompt
prompt Creating function RRL_SBORKA_PALLET_ROWS_ADD2
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLET_ROWS_ADD2 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int

) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD ;
/

prompt
prompt Creating function RRL_SBORKA_PALLET_ROWS_ADD3
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLET_ROWS_ADD3 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int , 
  PACK_COUNT1 int


) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD3 ;
/

prompt
prompt Creating function RRL_SBORKA_PALLET_ROWS_ADD4
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLET_ROWS_ADD4 (

  PALLET_UID1    VARCHAR2 ,
  ARTICUL1       VARCHAR2 ,
  SHORTNAME1     VARCHAR2 ,
  SHTRIHKOD1     VARCHAR2 ,
  EI1            VARCHAR2 ,
  TAREWEIGHT1    NUMBER,
  PATH1 VARCHAR2 ,
  ORDER_WEIGHT1  NUMBER,
  TARESIZE1      NUMBER,
  QUANTITY1      NUMBER,
  SORTFIELD1     INTEGER,
  AUCTION1       VARCHAR2,
  DOCID1         VARCHAR2 ,
  ware_id1 int , 
  PACK_COUNT1 int


) return int
IS
ID1 int;
BEGIN

    select ID into ID1 from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;

return ID1;
exception

    when NO_DATA_FOUND then
    begin
        SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    end;
    
    when others then 
    begin
    
     delete from RRL_SBORKA_PALLET_ROWS where ((PALLET_UID = PALLET_UID1) and (ARTICUL=ARTICUL1) ) ;
    
            SELECT RRL_SBORKA_PALLET_ROWS_SQ.Nextval INTO ID1 FROM DUAL;

            INSERT INTO RABAEV.RRL_SBORKA_PALLET_ROWS
            (
            ID , 
              PALLET_UID    ,
              ARTICUL       ,
              SHORTNAME     ,
              SHTRIHKOD     ,
              EI            ,
              TAREWEIGHT    ,
              PATH ,
              ORDER_WEIGHT  ,
              TARESIZE      ,
              QUANTITY      ,
              SORTFIELD     ,
              AUCTION       ,
              DOCID         , 
              ware_id ,
              PACK_COUNT , 
              ORIGINAL_QUANTITY ,
              ORIGINAL_ORDER_WEIGHT
            )  values (
            ID1 ,
              PALLET_UID1    ,
              ARTICUL1       ,
              SHORTNAME1     ,
              SHTRIHKOD1     ,
              EI1            ,
              TAREWEIGHT1    ,
              PATH1          ,
              ORDER_WEIGHT1  ,
              TARESIZE1      ,
              QUANTITY1      ,
              SORTFIELD1     ,
              AUCTION1       ,
              DOCID1         , 
              ware_id1 ,
              PACK_COUNT1 ,
              QUANTITY1 ,
              ORDER_WEIGHT1 
            );

    return ID1;
    
    end;
    
END  RRL_SBORKA_PALLET_ROWS_ADD4 ;
/

prompt
prompt Creating function RRL_SBORKA_PALLETS_ADD
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PALLETS_ADD (
    ST_NUMBER1   varchar2,
    ADDR1 varchar2,
    PALLET_NUMBER1 INTEGER ,
    PALLET_UID1     VARCHAR2 ,
    STATE1    VARCHAR2 ,
    STDATE1 Date ,
    NAPR1 varchar2 ,
    ware_id1 int
) return int
IS

    ID1 int;
    DONE1 int;
    COND1 varchar2(255) ;

BEGIN


select ID into ID1 from RRL_SBORKA_PALLETS where PALLET_UID = PALLET_UID1 ;
begin

    select R.STATE into COND1 from RABAEV.RRL_SBORKA_PALLETS R  where PALLET_UID = PALLET_UID1 ;
    select IN_PROCESS  into DONE1 from RABAEV.RRL_SBORKA_PALLETS_COND where COND=COND1;
    
    if ( DONE1=1)  then 
        return ID1;
    end if;
    
    delete from RRL_SBORKA_PALLET_ROWS where PALLET_UID=PALLET_UID1;
    
    exception
    when NO_DATA_FOUND then
    NULL;
end;

delete from  RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = PALLET_UID1 ;

update RRL_SBORKA_PALLETS set  STATE = STATE1 , NAPR = NAPR1 where  PALLET_UID = PALLET_UID1 ;


return ID1;
exception
    when NO_DATA_FOUND then
    begin
        INSERT INTO RABAEV.RRL_SBORKA_PALLETS (
              ADDR ,  
              ST_NUMBER      ,
              WARE_ID        ,
              PALLET_NUMBER  ,
              PALLET_UID     ,
              STATE ,
              NAPR ,
              STDATE

      ) VALUES (
                ADDR1 ,
              ST_NUMBER1      ,
              WARE_ID1        ,
              PALLET_NUMBER1  ,
              PALLET_UID1     ,
              STATE1 ,
              NAPR1 ,
              STDATE1
        
        );
        
        SELECT RRL_SBORKA_PALLETS_SQ.CURRVAL INTO ID1 FROM DUAL;
    return ID1;
    end;
    
END  RRL_SBORKA_PALLETS_ADD ;
/

prompt
prompt Creating function RRL_SBORKA_PLANNINGTIME
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SBORKA_PLANNINGTIME( pall_id1 varchar2 )
 RETURN Date IS 
tmpVar Date;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := null;
  

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN null;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SBORKA_PLANNINGTIME;
/

prompt
prompt Creating function RRL_SET_KLADOVSHIK
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_KLADOVSHIK(
    PALLET_UID1 varchar2  ,
    KLADOVSHIK1 varchar2
) return int
 
IS
ttt number;
 
BEGIN

 
update RABAEV.RRL_SBORKA_PALLETS set KLADOVSHIK=KLADOVSHIK1 where PALLET_UID=PALLET_UID1  ; 


return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_KLADOVSHIK;
/

prompt
prompt Creating function RRL_SET_SBORKA_ZONE
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_SBORKA_ZONE(
    PALLET_UID1 varchar2  ,
    ZONE1 varchar2 ,
    user_id1 varchar2
) return int
IS
ttt number;
money1 number;
exp_group varchar2(20);
exp_cell varchar2(20);
prov1 int;

BEGIN
 

-- ЗАПОМИНАЕМ ЗОНУ, ИЗ КОТОРОЙ ПЕРЕМЕЩАЛСЯ ПАЛЛЕТ.
  select  ZONE into exp_cell  from  RABAEV.RRL_SBORKA_PALLETS  where PALLET_UID=PALLET_UID1  ; 
    
    if ( (exp_cell is null) or ( exp_cell='' ) ) then
        
        exp_group:='ZERO';
    else
    
        begin
            select  RRL_CELLS.EXPEDITION_GROUP into exp_group from RRL_CELLS where RRL_CELLS.CELL = exp_cell ;
        exception
            when NO_DATA_FOUND then
                exp_group:='ZERO';
            when OTHERS then
                exp_group:='ZERO';
        end;
        
    end if;


    if ( (exp_group is null) or ( exp_group='' ) ) then
        exp_group:='ZERO';
    end if;



  update RABAEV.RRL_SBORKA_PALLETS set ZONE=ZONE1   where PALLET_UID=PALLET_UID1  ; 
     
  
  insert into  RABAEV.RRL_SBORKA_PALLETS_HISTORY 
  (
    PALLET_UID ,
    USER_ID ,
    ZONE,
    EVENT,
    TIME1
  ) values (
    PALLET_UID1 ,
    user_id1 ,
    ZONE1 , 
    'INTERNAL_MOVE' ,
    SYSTIMESTAMP 
  );
  

  -- ТЕПЕРЬ БИЛЛИНГ: 
  -- ОПЛАТА ЗА БИЛЛИНГ БЕРЕТСЯ ИСХОДЯ ИЗ  [ГРУППЫ ЦЕЛЕВОЙ ЯЧЕЙКИ ЗОНЫ ОТГРУЗКИ ]  И  [ГРУППЫ ПОЛЬЗОВАТЕЛЯ ]   

begin 
    money1:=0;
    
-- СНАЧАЛА ПОЙМЕМ В КАКОЙ ГРУППЕ ЯЧЕЕК ЭКСПЕДИЦИИ НАХОДИТСЯ СОБРАННЫЙ ПАЛЛЕТ



    select min(RRL_BILLING_NASTR_INTMOV.UE) into money1 from RUSERS , RRL_CELLS , RRL_BILLING_NASTR_INTMOV
    where RUSERS.ID = user_id1 and RRL_CELLS.CELL = ZONE1 and
    RRL_BILLING_NASTR_INTMOV.EXPEDIT_GROUP_TO = RRL_CELLS.EXPEDITION_GROUP and
    RRL_BILLING_NASTR_INTMOV.USER_GROUP= RUSERS.USER_GROUP  and
    RRL_BILLING_NASTR_INTMOV.EXPEDIT_GROUP_FROM = exp_group ;

prov1:=0;
select count(PALLET_UID ) into prov1 from RRL_BILLING where CELL_TO=ZONE1 and OPERATION='INT_MOVE'  and   PALLET_UID =  PALLET_UID1 ;

      
if ( ( money1>0 ) and (prov1=0) ) then -- ПИШЕМ В ТАБЛИЦУ БИЛЛИНГА

-- Проверка = если есть записи биллинга с той-же CELL_TO , то писать в биллинг не будем. 



insert into RRL_BILLING 
(
     ID           ,
      USER_ID     ,
      UE          ,
      TIMEOF      ,
      OPERATION   ,
      PRIM        ,
      PALLET_UID  
       , CELL_FROM , CELL_TO
) values
(
    RRL_BILLING_SEQ.NEXTVAL ,
    user_id1 , 
    money1 ,
    systimestamp ,
    'INT_MOVE' ,
    '' , 
    PALLET_UID1  , exp_cell , ZONE1
    
) ;





end if;

exception

       when NO_DATA_FOUND then 
           return 0;
        when others then 
           return 0;

end ;

  
return 0;    
END  RRL_SET_SBORKA_ZONE;
/

prompt
prompt Creating function RRL_SET_SBORSHIK
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_SBORSHIK(
    PALLET_UID1 varchar2  ,
    SBORSHIK1 varchar2
) return int
 
IS
ttt number;
 
BEGIN

 
update RABAEV.RRL_SBORKA_PALLETS set SBORSHIK=SBORSHIK1 where PALLET_UID=PALLET_UID1  ; 


return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SBORSHIK;
/

prompt
prompt Creating function RRL_SET_SCAN_PROOVE
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_SCAN_PROOVE(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2
) return int
 
IS
ttt number;
  SPIS_OTBOR_ON_SCAN_OPALL1 int;
  vhelp2 varchar2(255);
  
BEGIN


    if count_of_errors1=0 then
     update RABAEV.RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ; 
     
     DBMS_OUTPUT.put_line(  'flag1' );
     --  СПИСЫВАЕМ ТОВАР ИЗ ЯЧЕЕК ОТБОРА. настройка= SPIS_OTBOR_ON_SCAN_OPALL
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
     DBMS_OUTPUT.put_line(  'flag2' );

           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    '' );
                DBMS_OUTPUT.put_line(  'flag3' );

         end if;
     -- СПИСАНИЕ ОСТАТКОВ ИЗ ОТБОРА   
          
     
    else
     update RABAEV.RRL_SBORKA_PALLETS set  prim=prim1 , COUNT_OF_ERRORS=count_of_errors1  where PALLET_UID=PALLET_UID1  ; 
    end if;
    

return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SCAN_PROOVE;
/

prompt
prompt Creating function RRL_SET_SCAN_PROOVE2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_SCAN_PROOVE2(
    PALLET_UID1 varchar2  ,
    count_of_errors1 int ,
    prim1 varchar2 , 
    SBORSHIK1  VARCHAR2,
    KLADOVSHIK1 VARCHAR2
) return int
 
IS
vhelp2 varchar2(255);
ttt number;
 SPIS_OTBOR_ON_SCAN_OPALL1 int;
BEGIN


    if count_of_errors1=0 then
    
     update RABAEV.RRL_SBORKA_PALLETS set    PROOVED_BY_SCAN=1 , prim=prim1   where PALLET_UID=PALLET_UID1  ;
     --  СПИСЫВАЕМ ТОВАР ИЗ ЯЧЕЕК ОТБОРА. настройка= SPIS_OTBOR_ON_SCAN_OPALL
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    KLADOVSHIK1 );
         end if;
     -- СПИСАНИЕ ОСТАТКОВ ИЗ ОТБОРА   
          
    else
     update RABAEV.RRL_SBORKA_PALLETS set   prim=prim1 , COUNT_OF_ERRORS=count_of_errors1  where PALLET_UID=PALLET_UID1  ; 
    end if;
    
    if (not(SBORSHIK1 is null)) then
     update RABAEV.RRL_SBORKA_PALLETS set  SBORSHIK=SBORSHIK1   where PALLET_UID=PALLET_UID1  ; 
    end if;
    
    if (not(KLADOVSHIK1 is null)) then
     update RABAEV.RRL_SBORKA_PALLETS set  KLADOVSHIK=KLADOVSHIK1   where PALLET_UID=PALLET_UID1  ; 
    end if;

return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_SCAN_PROOVE2;
/

prompt
prompt Creating function RRL_SET_TRANSPORT_PRICE
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_TRANSPORT_PRICE(
    PRICE_NAME1 varchar2  ,
    PATH_NAME1 varchar2 ,
    PRICE2 number , 
    kilometers1 number,
    price_hours1 number,
    PRICE2_ADDR number ,
    hours_normative1 number ,
    
    COMPANY2 VARCHAR2
) return int
 
IS
ttt number;
PRICE1 number; 
ID1 int;
path3 varchar2(1024) ;
COMPANY3 varchar(255);

BEGIN

    if( COMPANY2 is null ) then 
        COMPANY3 := '';
    else
        COMPANY3 := COMPANY2;
    end if;

 
DBMS_OUTPUT.put_line(  'begin funct' );

    begin
        
        select path1 into path3 from rrl_tt_path where path1=PATH_NAME1 ; 
        update rrl_tt_path set  path1 = path_name1 , range1 = kilometers1 , NORMATIVE_HOURS = hours_normative1  where  path1=PATH_NAME1  ;
        
    exception when no_data_found then 
        insert into rrl_tt_path  ( path1 , range1 ,  NORMATIVE_HOURS  ) values ( PATH_NAME1 , kilometers1 ,  hours_normative1 );
        when others then null;
    end;






select ID into ID1 from RRL_TRANSPORT_PRICE PR where  PRICE_NAME = PRICE_NAME1 and COMPANY=COMPANY3 ; 

update RRL_TRANSPORT_PRICE set  PRICE = PRICE2 , RANGE1=kilometers1 , PRICE_FOR_HOURS=price_hours1 , PRICE_FOR_ADDR =  PRICE2_ADDR , 
NORM_HOURS = hours_normative1
    where  ID = ID1 ;       
   --   PRICE_NAME = PRICE_NAME1 and ( (COMPANY=COMPANY2) 
   --   or ( ((COMPANY2='') or (COMPANY2 is null)) and ((COMPANY='') or (COMPANY is null))  ) ) ; 

DBMS_OUTPUT.put_line(  'update' );



return 0;
exception
when NO_DATA_FOUND then


    SELECT RRL_TRANSPORT_PRICE_ID.Nextval INTO ID1 FROM DUAL;
    
    insert into RRL_TRANSPORT_PRICE (ID , PRICE_NAME , PRICE ,RANGE1 , COMPANY , PRICE_FOR_HOURS , PRICE_FOR_ADDR , NORM_HOURS ) values 
    ( ID1 ,PRICE_NAME1 , PRICE2 , kilometers1 , COMPANY2 , price_hours1 , PRICE2_ADDR ,  hours_normative1 ) ;
DBMS_OUTPUT.put_line(  'insert' );

    return ID1;
    when others then 
    return -1;
    
END  RRL_SET_TRANSPORT_PRICE;
/

prompt
prompt Creating function RRL_SET_TT_LOAD_TASK
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SET_TT_LOAD_TASK(
    TT_ID1 int  ,
    ZONE varchar2 , 
    time_from timestamp ,
    time_to timestamp ,
    ware_id1 int
) return int
 
IS
ttt number;
 
BEGIN
 
 
--  select from RRL_TT_LOAD_TASK TTT where TTT.WARE_ID=ware_id1 and TTT.TT_ID = TT_ID1 ; 


return 0;
exception
when NO_DATA_FOUND then
    return 0;
    when others then 
    return 0;
    
END  RRL_SET_TT_LOAD_TASK;
/

prompt
prompt Creating function RRL_SFERA_EAN_EAN_BL
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_sfera_ean_EAN_BL
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_BL into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_BL;
/

prompt
prompt Creating function RRL_SFERA_EAN_EAN_KOR
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_sfera_ean_EAN_KOR
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_KOR into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_KOR;
/

prompt
prompt Creating function RRL_SFERA_EAN_EAN_SHT
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_sfera_ean_EAN_SHT
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_SHT into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_SHT;
/

prompt
prompt Creating function RRL_SHOW_PRICE
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SHOW_PRICE( tt_id int )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
   
   select    price
   into tmpVar from RRL_TRANSPORT_TASK where ID = tt_id  ;

   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_SHOW_PRICE;
/

prompt
prompt Creating function RRL_ST_ROW_COUNT
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ST_ROW_COUNT( ST varchar2 )
 RETURN number IS 
tmpVar number;
BEGIN
   tmpVar := 0;
  
select count( R.ID  )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  P.ST_NUMBER   = ST and P.PALLET_UID =  R.PALLET_UID and R.QUANTITY>0  ;
 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_ST_ROW_COUNT;
/

prompt
prompt Creating function RRL_ST_UNIQPCOUNT
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ST_UNIQPCOUNT( ST varchar2 )
 RETURN int IS 
tmpVar number;
itogo int;
sobrano int;
 -- ВОЗВРАЩАЕТ КОЛИЧЕСТВО ПАЛЛЕТ, СОДЕРЖАЩИХ САХАР
BEGIN

   itogo := 0;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
--select  count(DISTINCT R.PALLET_UID)  into itogo from   RRL_SBORKA_PALLET_ROWS R , RRL_ARTICULS  A 
--   where   (  R.PALLET_UID = ST ) and ( R.ARTICUL=A.ACTICUL ) and ( A.PALLET_MULTIPLE<>1 ) ;

select  count(DISTINCT R.PALLET_UID)  into itogo from   RRL_SBORKA_PALLET_ROWS R  
   where   (  R.PALLET_UID = ST ) and  ( R.ARTICUL in ( 'Т0000008795' , 'Т0000127793' , 'Т0000127794'   ) );


   RETURN itogo+1;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
        RETURN -2;
END RRL_ST_UNIQPCOUNT;
/

prompt
prompt Creating function RRL_ST_VERYFY_PERC
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ST_VERYFY_PERC( ST varchar2 )
 RETURN int IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
 --  return 0;
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  ST_NUMBER  = ST;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where   ST_NUMBER  = ST and ( PROOVED=1 or  PROOVED_BY_SCAN=1 );

    if(itogo=0) then
        return 0;
    end if;


tmpVar:= sobrano *100/ itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
        RETURN -2;
END RRL_ST_VERYFY_PERC;
/

prompt
prompt Creating function RRL_ST_VOLUME
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ST_VOLUME( stnumber1 varchar2 )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where p.ST_NUMBER=stnumber1 and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ST_VOLUME;
/

prompt
prompt Creating function RRL_ST_WEIGHT
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_ST_WEIGHT( stnumber1 varchar2 )
 RETURN number IS 
tmpVar number;

BEGIN
   tmpVar := 0;
  
select sum( R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where p.ST_NUMBER=stnumber1 and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ST_WEIGHT;
/

prompt
prompt Creating function RRL_SUGAR_HAS
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SUGAR_HAS( ART varchar2 )
return int
is
BEGIN

    if( ART= 'Т0000008795' ) then 
        return 1;
    end if;


    if( ART= 'Т0000127793' ) then 
        return 1;
    end if;

    if( ART= 'Т0000127794' ) then 
        return 1;
    end if;

return 0;


END RRL_SUGAR_HAS;
/

prompt
prompt Creating function RRL_SYNC_ADDR
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_SYNC_ADDR (
dummy int
)
RETURN INT
is
tmpVar INT;
 

cursor dddd is 
  ( SELECT DISTINCT rrl_sborka_pallets.addr, rrl_sborka_pallets.napr  FROM rrl_sborka_pallets left join RRL_ADDR on rrl_sborka_pallets.ADDR = RRL_ADDR.ADDR(+) where RRL_ADDR.ADDR is null );
   
  begin 
  
  tmpVar:=0;
    for addr_row in dddd loop
        tmpVar:=tmpVar+1;
        INSERT INTO RRL_ADDR (  addr, napr   ) VALUES (  addr_row.addr, addr_row.napr  ) ;
    end loop;


RETURN tmpVar ;
   END RRL_SYNC_ADDR;
/

prompt
prompt Creating function RRL_TIME_FOR_RESERV
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TIME_FOR_RESERV RETURN int IS

BEGIN
   RETURN 12;
END RRL_TIME_FOR_RESERV;
/

prompt
prompt Creating function RRL_TOVAR_TYPE
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TOVAR_TYPE( ART varchar2 , ware_id1  int  )
 RETURN int IS 
 -- Функция возвращает тип товара ( Весовой, точный Весовой, Штучный  )
 -- в зависимости от склада, артикула.
 -- 0 = Штука 
 -- 1= Весовой точный 
 -- 2 = Весовой плавающий 
 
tmpVar int;
BEGIN
   tmpVar := 0;
--  select type_w into tmpVar from rrl_wares where id= ware_id1 ;
  select type_w into tmpVar from rrl_articuls where acticul= art ;

 
   RETURN tmpVar;
  
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_TOVAR_TYPE;
/

prompt
prompt Creating function RRL_TRANPORT_TASK_HISTORY_ADD
prompt ===============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRANPORT_TASK_HISTORY_ADD (
 TT_ID int, 
 TRANSTYPE1 varchar2, 
 TRANSPORT1 varchar2, 
 ROUTETYPE1 varchar2, 
 WAVE1 varchar2, 
 SHIPMENT_DATE1 date, 
 VODITEL_ID1 int, 
 PRIMECHANIE1 varchar2,
 DOCK1 varchar2,
 user_id1 varchar2 ,
 OPERATION1 varchar2
 )
 RETURN varchar2 
 IS 
 next_hist_id  int;
begin

 SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;

 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , TRANSTYPE  ,  TRANSPORT   , ROUTETYPE   , SHIPMENT_TIME   ,
        SHIPMENT_DATE , VODITEL_ID  , PRIMECHANIE , DOCK , user_id , OPERATION , event_time ) values 
        ( next_hist_id , TT_ID , TRANSTYPE1 , TRANSPORT1 , ROUTETYPE1 , WAVE1 , SHIPMENT_DATE1 , 
        VODITEL_ID1 , PRIMECHANIE1 ,DOCK1 ,user_id1 , OPERATION1 , systimestamp ) ;
 
 return 'ok';
 
 END RRL_TRANPORT_TASK_HISTORY_ADD ;
/

prompt
prompt Creating function RRL_TRASPORT_TASK_ADD
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRASPORT_TASK_ADD (
    TRANSTYPE1    VARCHAR2 ,
    SHIPMENT_DATE1 DATE , 
    user_id1 varchar2
) return int
IS
ID1 int;
next_hist_id int;
BEGIN

    SELECT RRL_TRANSPORT_TASK_SQ.Nextval INTO ID1 FROM DUAL;

    insert into    RRL_TRANSPORT_TASK
    (
        ID ,
        CREATEDATE , 
        TRANSTYPE ,
        SHIPMENT_DATE
    ) values (
        ID1 ,
        SYSDATE ,
        TRANSTYPE1 ,
        SHIPMENT_DATE1 
    )    ; 
    
     SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;
 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , user_id , OPERATION , event_time ) values
 ( next_hist_id ,ID1 , user_id1 , 'CREATE' , systimestamp );
    
    return ID1;

END  RRL_TRASPORT_TASK_ADD ;
/

prompt
prompt Creating function RRL_TRASPORT_TASK_UPDATE
prompt ==========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRASPORT_TASK_UPDATE (
    TT_ID    int ,
    TRANSTYPE1 varchar2 , 
    TRANSPORT1 varchar2 ,
    ROUTETYPE1 varchar2 ,
    WAVE1 varchar2 ,
    SHIPMENT_DATE1 DATE , 
    VODITEL_ID1   INTEGER ,
    PRIMECHANIE1 varchar2 ,
    DOCK1 varchar2 , 
    user_id1 varchar2
    
) return int
IS
ID1 int;
BEGIN

   

    update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 , WAVE = WAVE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    return  TT_ID ;

END  RRL_TRASPORT_TASK_UPDATE ;
/

prompt
prompt Creating function RRL_TRASPORT_TASK_UPDATE2
prompt ===========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRASPORT_TASK_UPDATE2 (
    TT_ID    int ,
    TRANSTYPE1 varchar2 , 
    TRANSPORT1 varchar2 ,
    ROUTETYPE1 varchar2 ,
    WAVE1 Date ,
    SHIPMENT_DATE1 DATE , 
    VODITEL_ID1   INTEGER ,
    PRIMECHANIE1 varchar2 ,
    DOCK1 varchar2 , 
    user_id1 varchar2
    
) return int
IS
ID1 int;
next_hist_id int;
BEGIN



 SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;

   if( not WAVE1 is null ) then 

        update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 , SHIPMENT_TIME = WAVE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    else

        update RRL_TRANSPORT_TASK set   TRANSTYPE= TRANSTYPE1 ,  TRANSPORT = TRANSPORT1 , ROUTETYPE = ROUTETYPE1 ,
        SHIPMENT_DATE=SHIPMENT_DATE1 , VODITEL_ID = VODITEL_ID1 , PRIMECHANIE=PRIMECHANIE1 , DOCK=DOCK1 , user_id=user_id1  where  ID =  TT_ID  ; 
    
    end if;
    
 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , TRANSTYPE  ,  TRANSPORT   , ROUTETYPE   , SHIPMENT_TIME   ,
        SHIPMENT_DATE , VODITEL_ID  , PRIMECHANIE , DOCK , user_id , OPERATION , event_time ) values 
        ( next_hist_id , TT_ID , TRANSTYPE1 , TRANSPORT1 , ROUTETYPE1 , WAVE1 , SHIPMENT_DATE1 , 
        VODITEL_ID1 , PRIMECHANIE1 ,DOCK1 ,user_id1 , 'UPDATE' , systimestamp ) ; 
    
    return  TT_ID ;

END  RRL_TRASPORT_TASK_UPDATE2 ;
/

prompt
prompt Creating function RRL_TT_POGRESHNOST
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_POGRESHNOST( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN

   tmpVar := 3;


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
       
END RRL_TT_POGRESHNOST;
/

prompt
prompt Creating function RRL_TRIAL_BY_WEIGHT
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRIAL_BY_WEIGHT(
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int IS 
    tmpVar number;
    pogr number;
    IDD1 int;
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);



--


update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT(PALLET_UID1)  )<pogr ) then
       
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = 'ПроверенВесами' where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = 'Выдан в сборку' where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;       
END RRL_TRIAL_BY_WEIGHT;
/

prompt
prompt Creating function RRL_TRIAL_BY_WEIGHT2
prompt ======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TRIAL_BY_WEIGHT2(
    PALLET_UID1  varchar2 ,
    TRIAL_WEIGHT1 varchar2 ,
    WOOD_WEIGHT1 varchar2 ,
    user_id1 varchar2
)
 RETURN int IS 
    tmpVar number;
    pogr number;
    IDD1 int;
    SPIS_OTBOR_ON_SCAN_OPALL1 int;
    vhelp2 varchar2(255);
BEGIN


select ID into IDD1 from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID=PALLET_UID1;

   tmpVar := 0;
   pogr:=RRL_TT_POGRESHNOST(IDD1);



--


update RABAEV.RRL_SBORKA_PALLETS set TRIAL_WEIGHT = TRIAL_WEIGHT1 ,  WOOD_WEIGHT = WOOD_WEIGHT1 , VESOVSHIK = user_id1  where PALLET_UID=PALLET_UID1;

    if (abs( TRIAL_WEIGHT1-WOOD_WEIGHT1 - RRL_PALLET_WEIGHT2(PALLET_UID1)  )<pogr ) then
       
        -- СПИСАНИЕ ОСТАТКОВ 
        select WW.SPIS_OTBOR_ON_SCAN_OPALL into SPIS_OTBOR_ON_SCAN_OPALL1 from RRL_SBORKA_PALLETS PP ,  RRL_WARES WW where PP.WARE_ID=WW.ID and PP.PALLET_UID=PALLET_UID1;
         if( SPIS_OTBOR_ON_SCAN_OPALL1=1 ) then 
           vhelp2:= RABAEV.RRL_CLOSE_OTHOD_PALLET(    PALLET_UID1  ,    user_id1 );
         end if;
        -- СПИСАНИЕ ОСТАТКОВ 
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=1 , STATE = 'ПроверенВесами' where PALLET_UID=PALLET_UID1;
        
        insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
            values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        return 1;
        
      else
      
      insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT , WEIGHT)
        values (PALLET_UID1 , user_id1 , 'VESOV' , 'WEIGHT_CHECK' , TRIAL_WEIGHT1  );

        
        update RABAEV.RRL_SBORKA_PALLETS set PROOVED=0 , STATE = 'Выдан в сборку' where PALLET_UID=PALLET_UID1;
        return 0;
        
    end if;
    


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;       
END RRL_TRIAL_BY_WEIGHT2;
/

prompt
prompt Creating function RRL_TT_REGIONS
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_REGIONS( TTID int )
 RETURN varchar2 IS 
tmpVar varchar2(1024);
tmpVar2 varchar2(1024);
cursor ttu is
select distinct REGION from RABAEV.RRL_SBORKA_PALLETS,  RABAEV.RRL_ADDR  where TRANSTASK_ID=TTID and  RRL_SBORKA_PALLETS.ADDR =RRL_ADDR.ADDR ;


BEGIN

   select  TEMP_REGION  into tmpVar2 from RRL_TRANSPORT_TASK where ID = TTID ;
   if( not ( tmpVar2  is null )) 
    then
    --   DBMS_OUTPUT.put_line(  'ffff' );
     return tmpVar2 ;
   end if;
   

for ttq in ttu loop
tmpVar := concat( tmpVar ,concat( ' ' ,  concat( ttq.REGION , '; '  )));
end loop;
   

--update RABAEV.RRL_TRANSPORT_TASK set TEMP_REGION = tmpVar where ID = TTID ;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 'err2';
       RAISE;
END RRL_TT_REGIONS;
/

prompt
prompt Creating function RRL_TT_ADD_PALL
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ADD_PALL(
    TT_ID int ,
    ST_NUMBER1 varchar2  ,
    user_id1 varchar2
)
 RETURN varchar2 IS 
tmpVar varchar2(1024);
tmpVar2 varchar2(1024);

next_hist_id int;
max_tt_int int;
BEGIN
max_tt_int:=0;
tmpVar:='';

    if( TT_ID>0)then 
        update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID =  TT_ID  where ST_NUMBER= ST_NUMBER1;
         SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;
 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , user_id , OPERATION , event_time , ST_NUMBER ) values
 ( next_hist_id ,TT_ID , user_id1 , 'CREATE' , systimestamp , ST_NUMBER1 );
        
    else
        
        select max(TRANSTASK_ID) into max_tt_int from  RABAEV.RRL_SBORKA_PALLETS  where ST_NUMBER= ST_NUMBER1;
        
        update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID =  null where ST_NUMBER= ST_NUMBER1;
        
         SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;
        insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , user_id , OPERATION , event_time , ST_NUMBER ) values
         ( next_hist_id  , max_tt_int , user_id1 , 'CREATE' , systimestamp , ST_NUMBER1 );
 
    end if;


    tmpVar:=RABAEV.RRL_TT_REGIONS( TT_ID  );
    
update RABAEV.RRL_TRANSPORT_TASK set TEMP_REGION = tmpVar where ID = TT_ID ;    
    
    
    
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 'err2';
       RAISE;
END RRL_TT_ADD_PALL;
/

prompt
prompt Creating function RRL_TT_BILL_RECALC_PRICE
prompt ==========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_BILL_RECALC_PRICE
(
    login varchar2 
)
 RETURN int
  IS
  
  
tmpVar int;

cursor mainloop is
select
  PR.ID              ,  PR.PRICE_NAME      ,
  PR.PRICE           ,  PR.COMPANY         ,
  PR.RANGE1          ,  PR.PRICE_FOR_HOURS ,
  PR.TYPE_TR , 
  km.PRICE* PR.RANGE1 ppp
 from 
RABAEV.RRL_TRANSPORT_PRICE PR , RABAEV.RRL_TT_BILL_PRICE_KM KM  
where  PRICE_NAME like  concat( concat( '' , KM.TT ) , '%' )
and PR.RANGE1 >  KM.KM_FROM and  PR.RANGE1 <= KM.KM_TO and PR.PRICE_FOR_HOURS=0
and price_folder=0 and PR.PRICE_FOLDER=0 ;


BEGIN



    for ml in mainloop loop
            
            update RRL_TRANSPORT_PRICE set PRICE = ml.ppp where ID = ml.ID;
    
        
        
    end loop;

           return -1;




   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_TT_BILL_RECALC_PRICE;
/

prompt
prompt Creating function RRL_TT_DROP
prompt =============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_DROP( IDTT int , user_id1 varchar2 )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;
next_hist_id int;
BEGIN

tmpVar := 1;
  
update RABAEV.RRL_SBORKA_PALLETS set TRANSTASK_ID = null where  TRANSTASK_ID  = IDTT;
update RRL_TRANSPORT_TASK set  DELETED=1 where ID = IDTT;

 SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;
 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , user_id , OPERATION , event_time ) values
 ( next_hist_id ,IDTT , user_id1 , 'DELETE' , systimestamp );
 
 
commit;
RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_TT_DROP;
/

prompt
prompt Creating function RRL_TT_DROP2
prompt ==============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_DROP2( IDTT int , user_id1 varchar2 )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;
next_hist_id int;
BEGIN

tmpVar := 1;
  
update RABAEV.RRL_SBORKA_PALLETS set TRANSTASK_ID = null where  TRANSTASK_ID  = IDTT;
update RRL_TRANSPORT_TASK set  DELETED=1 where ID = IDTT;

 SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;
 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , user_id ) values
 ( next_hist_id ,IDTT , user_id1 );
 
 
commit;
RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       RAISE;
END RRL_TT_DROP2;
/

prompt
prompt Creating function RRL_TT_PALLETS
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_PALLETS( IDTT int )
 RETURN number IS 
tmpVar int;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
 --    RETURN tmpVar;
-- сначала запросим общее количество паллет
select count(  P.PALLET_UID )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P 
     where  TRANSTASK_ID  = IDTT  ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_PALLETS;
/

prompt
prompt Creating function RRL_TT_ZONE_EMPTY
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ZONE_EMPTY
(  
  time1      timestamp, 
  SUB_ZONE1  VARCHAR2
)
-- ПРОцедура дает количество паллет, находящихся в данной зоне в данный момент времени
RETURN number IS

count_of_pal int;
 
BEGIN

--return 0;

count_of_pal:=0;
select count( PAL.PALLET_UID ) into count_of_pal 
    from RABAEV.RRL_SBORKA_PALLETS PAL where   ZONE_TIME_PLAN_IN <= time1 and
    time1<= ZONE_TIME_PLAN_OUT and ZONE = SUB_ZONE1 ;


if( count_of_pal >0 ) then 
    return count_of_pal;
else
    return 0;
end if;


   RETURN 1;
exception

    when no_data_found then 
       RETURN 1;
    when others then return 1;

END  RRL_TT_ZONE_EMPTY;
/

prompt
prompt Creating function RRL_TT_ZONE_DISTANCE_TO_DOCK
prompt ==============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ZONE_DISTANCE_TO_DOCK
-- МЕРА РАССТОЯНИЯ ОТ ДОКА (ЗОНЫ) до ЯЧЕЙКИ ОТГРУЗОЧНОЙ. 
-- Необходима для определения 
-- Мера близости ( место  , зона дока ) = ( расстояние по оси У ) + (растояние по оси Х)* (длину ряда)
-- Измеряется как расстояние До первой ячейки данной подзоны (ячейки с расстоянием = 1). если таковой нет, 	то не измеряем вообща
(  
  ZONE1      VARCHAR2, 
  SUB_ZONE1  VARCHAR2
)
 RETURN number IS
 ZONE_OF_CELL varchar2(255);
 X1 number;
 Y1 number;
 X_MAX number;
 Y_MAX number;
 X_MIN number;
 distance number;
 
BEGIN

distance:=0;
-- Если ячейка находится на той-же оси, что и ZONE1 , то расстояние = Y , иначе 
-- Расстояние =  100*( расстояние между ЗОНАМи по оси Х )  + ( расстояние от ячейки  до конца ряда ( т.е. последней ячейки в ряде.) )

select ZONE , X,Y  into ZONE_OF_CELL , X1 , Y1  from RRL_TT_ZONES where SUB_ZONE = SUB_ZONE1 ;
if ( ZONE_OF_CELL = ZONE1 ) then 
    return Y1;
else

    -- Находим параметры зоны, в которой находится ячейка - максимальная удаленность ячеек в зоне , и параметр X (максимальный)
    select max( X ) , max(Y)  into X_MAX , Y_MAX   from RRL_TT_ZONES where  ZONE = ZONE_OF_CELL ;
    -- Находим параметры зоны , с которой идет сравнение -  параметр  X 
    select min( X )  into X_MIN   from RRL_TT_ZONES where  ZONE = ZONE1 ;

-- Расстояние =  100*( расстояние между ЗОНАМи по оси Х )  + ( расстояние от ячейки  до конца ряда ( т.е. последней ячейки в ряде.) )
distance:= 1000*(  abs(X_MAX-X_MIN) ) + abs( Y_MAX-Y1 )  ;
return distance;
end if;


   RETURN 10000;
exception

    when no_data_found then 
       RETURN 100000;
    when others then return 1000000;

END  RRL_TT_ZONE_DISTANCE_TO_DOCK;
/

prompt
prompt Creating function RRL_TT_ZONE_FIND_EMPTY_PLACE
prompt ==============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ZONE_FIND_EMPTY_PLACE
(  
  time1      timestamp, 
  ZONE1  VARCHAR2
)
-- Написать процедуру поиска первого свободного места для ворот (зоны) в данное время. F(Время , Зона   )
-- Ищется как ближайший не занятое паллето-место к зоне, имеющее расстояние не более 1 от зоны , иначе возвращается место OVERFLOW. 

RETURN varchar2 IS

X_min int;
RES_SUBZONE varchar2(255);
RES_DIST number;

begin 


DBMS_OUTPUT.put_line( concat( concat( ' --------------- RRL_TT_ZONE_FIND_EMPTY_PLACE (' , ZONE1  ) , ');' ));


-- Для данной зоны находим минимум по оси Х  
select min(X) into X_min from  RRL_TT_ZONES ZZ where ZZ.ZONE=ZONE1 ; 


-- по всем ячейкам, отстоящим не более чем на 1 позицию по оси Х   находим незанятую ячейку на данное время, 
-- имеющую минимальное расстояние до начала зоны  
select SUB_ZONE , DIST into RES_SUBZONE , RES_DIST  from
 (
    select
    SUB_ZONE , 
    RRL_TT_ZONE_DISTANCE_TO_DOCK(  ZONE1 , SUB_ZONE ) DIST
     from  RRL_TT_ZONES ZZ  where 
        abs( X-X_min) <=1 and 
        (RRL_TT_ZONE_EMPTY( time1 , ZZ.SUB_ZONE  )=0) /* Количество паллет допустимое в ячейке */ 
    order by RRL_TT_ZONE_DISTANCE_TO_DOCK(  ZONE1 , SUB_ZONE )
) where ROWNUM=1
    ;


   RETURN RES_SUBZONE;
exception

    when no_data_found then  RETURN 'ERR1';
    when others then return 'ERR2';

END  RRL_TT_ZONE_FIND_EMPTY_PLACE;
/

prompt
prompt Creating function RRL_TT_PLAN_PALL_ZONES
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_PLAN_PALL_ZONES
(  
  TT  int , 
  ZONE1 varchar2 , -- Зона 
  time1 timestamp , -- Время плановой отгрузки товара 
  replain int ,
  MAIN_WARE_ID int
)


-- Процедура назначения плановых мест для паллетт маршрута. (фиксации занятости )
-- Паллеты маршрута упорядочиваются по: Адресу (согласно планирования логистов) , весу.
    
-- Для каждой паллеты из маршрута определяется свободное место, и фиксируется на 
-- время от ( начала плановой отгрузки товара - 30 минут ) до ( начала плановой отгрузки товара + 30 минут )


RETURN int IS


    cursor aaa is 
    select SP.PALLET_UID , ZONE from RRL_SBORKA_PALLETS SP , RRL_ADDR ADR , RRL_WARES WAR 
    where  SP.WARE_ID = WAR.ID  and WAR.PARENT_WARE_ID=MAIN_WARE_ID and  SP.TRANSTASK_ID = TT and SP.ADDR = ADR.ADDR 
    order by SP.ORD ,  SP.ADDR  , WAR.ORD2 ,  RRL_PAL_WEIGHT( SP.PALLET_UID ) desc ; 

    cell1 varchar2(255) ; 
  time1_ timestamp;
  time2 timestamp;
  time3 timestamp;
ye int;
begin 

--select year( time1_ ) into ye from dual;

time1_:=time1;
if( ( time1_ )< to_date( '01-01-2000' ) ) then
time1_:= systimestamp ;
end if;


if ( replain=1 ) then 
    
    update RRL_SBORKA_PALLETS  set 
        ZONE=null , 
        ZONE_TIME_PLAN_IN   = null   ,
        ZONE_TIME_PLAN_OUT = null 
    where  TRANSTASK_ID = TT ;
    
end if;
time2 := time1_ - 1/24;
time3 := time1_ + 1/24;

-- НАЗНАЧЕНИЕ ЗАНЯТОСТИ ДОКА 
update RRL_TRANSPORT_TASK set DOCK = concat( concat( DOCK ,  ZONE1 ) , ';') , 
DOCK_REZERV_TIME_FROM  = time1_ ,
DOCK_REZERV_TIME_TO = time3
 where ID = TT ;

begin 
    delete from RRL_TT_LOAD_TASK where DOCK = ZONE1 and LOAD_FROM  <= time1_ and
    LOAD_TO >= time3;
exception
    when no_data_found then null;
    when others then null;
end;

insert into RABAEV.RRL_TT_LOAD_TASK (  TT_ID  ,DOCK ,LOAD_FROM , LOAD_TO , WARE_ID ) values 
    ( TT , ZONE1 , time1_ , time3 , MAIN_WARE_ID );





-- НАЗНАЧЕНИЕ ЗАНЯТОСТИ ДОКА



for aa in aaa loop
-- Для каждой паллеты из маршрута определяется свободное место, и фиксируется на 
-- время от ( начала плановой отгрузки товара - 30 минут ) до ( начала плановой отгрузки товара + 30 минут )
    
    cell1 := RRL_TT_ZONE_FIND_EMPTY_PLACE(  time1_  ,  ZONE1  );
    update RRL_SBORKA_PALLETS set  
        ZONE=cell1 , 
        ZONE_TIME_PLAN_IN   = time2   ,
        ZONE_TIME_PLAN_OUT = time3 
    where PALLET_UID = aa.PALLET_UID ;
    
    DBMS_OUTPUT.put_line(  concat( '              Зафиксировано место для паллета ' ,  aa.PALLET_UID )  );
    DBMS_OUTPUT.put_line( concat( '               ячейка ' , cell1 )  ) ;  
        
    DBMS_OUTPUT.put_line( time2 );
    DBMS_OUTPUT.put_line( time3 );

end loop;

   RETURN 0;
exception

    when no_data_found then 
    DBMS_OUTPUT.put_line( 'no_data_found' ) ;
     RETURN 0;
    when others then
    DBMS_OUTPUT.put_line( 'others' ) ;
     return 0;

END  RRL_TT_PLAN_PALL_ZONES;
/

prompt
prompt Creating function RRL_TT_ZONE_IS_EMPTY_DOCK
prompt ===========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ZONE_IS_EMPTY_DOCK
(  
    DOCK1 varchar2 , -- ПОДЗОНА  ( например  13L )  
    time1      timestamp 
)

--  процедура оценивает занятость дока на текущий момент времени. ( Ищет занятые подзоны , смотрим по рейсам ) 
--  Возвращает количество минут после последней спланированной  отгрузки. 
--  Или 0, если док на данное время занят или заняты все его подзоны. 

RETURN number IS
cursor subzones is
 select distinct ZONE from  RABAEV.RRL_TT_ZONES where DOCK=DOCK1 ; 

    max_time timestamp;
    id1 int;
    ret int;
    count_of_pallets  int;
    exist_subzone_with_0_palls int;
    min_palls_in_subzones int;
begin 

    count_of_pallets:=0;
    ret:=0;
    exist_subzone_with_0_palls:=0;
    min_palls_in_subzones:=1000;
    
    DBMS_OUTPUT.put_line( concat( ' Док= ' , DOCK1 ) );
    DBMS_OUTPUT.put_line( 'time1 = ' );
    DBMS_OUTPUT.put_line( time1 );
    -- time1 
    
    begin



        -- Если данный док занят в данный участов времени, то возвращаем 0 
        --select TT.ID into id1  from RRL_TRANSPORT_TASK TT , RRL_TT_ZONES ZZ  where TT.DOCK = ZZ.ZONE and ZZ.DOCK= DOCK1 and 
        --TT.DOCK_REZERV_TIME_FROM <= time1 and  time1<=   TT.DOCK_REZERV_TIME_TO ;
        
        select LT.TT_ID into id1  from RRL_TT_LOAD_TASK LT , RRL_TT_ZONES ZZ  where LT.DOCK = ZZ.ZONE and ZZ.DOCK= DOCK1 and 
        LT.LOAD_FROM <= time1 and  time1<=   LT.LOAD_TO ;



/*        
RABAEV.RRL_TT_LOAD_TASK
(
  TT_ID      INTEGER,
  DOCK       VARCHAR2(50 BYTE),
  LOAD_FROM  DATE,
  LOAD_TO    DATE,
  WARE_ID    INTEGER
)
*/        
        

        DBMS_OUTPUT.put_line( 'Док занят' );
        RETURN 0;
        
    exception
        
        
        
      when no_data_found then
      begin
           -- Если не существует свободной подзоны на указанный период времени, то возвращаем 0 
           DBMS_OUTPUT.put_line( 'Док не занят. бежим по всем подзонам для проверки свободного места' );
           
         for subzone in subzones loop
          
              count_of_pallets := RRL_TT_ZONE_EMPTY( time1 , subzone.ZONE ); 
              -- Если количество паллет в данной подзоне = 0 , то считаем данный док свободным.
               if(count_of_pallets=0) then
                exist_subzone_with_0_palls:=1;
               end if;
               
               if( count_of_pallets < min_palls_in_subzones ) then
                min_palls_in_subzones:= count_of_pallets;
               end if;
               
               DBMS_OUTPUT.put_line( concat(  concat(  concat( 'Подзона = ' , subzone.ZONE  ) , ' количество паллет= '  ) , count_of_pallets )  );
               
         end loop;

        if( exist_subzone_with_0_palls=0 ) then 
          DBMS_OUTPUT.put_line( 'Нет пустых зон, док занят' );
            return 0; -- Если не существует не занятых зон - считаем что док занят.    
        end if;
           
           -- Ищем максиальное время занятости дока.
                select max( TT.DOCK_REZERV_TIME_TO ) into max_time from RRL_TRANSPORT_TASK TT, RRL_TT_ZONES ZZ 
                where TT.DOCK = ZZ.ZONE and ZZ.DOCK=DOCK1 and 
                TT.DOCK_REZERV_TIME_FROM <= time1 and  TT.DOCK_REZERV_TIME_TO <= time1   ;
                DBMS_OUTPUT.put_line(  'время простоя дока в минутах составляет = '  );
                if( max_time is null ) then
                DBMS_OUTPUT.put_line( 10000000 );
                    return 10000000;
                end if;
                
                 ret :=  CALC_TIMESTAMP_DIFF_IN_SECONDS( time1 , max_time )/60 ;
                
                DBMS_OUTPUT.put_line( time1 );
                DBMS_OUTPUT.put_line( max_time );
                DBMS_OUTPUT.put_line( ret );
                DBMS_OUTPUT.put_line( '!' );
                
          RETURN ret;
          
          exception
          when no_data_found then return -2;
          when others then return -3;
          
      end;
    end;



   RETURN 0;
exception

    when no_data_found then  RETURN 0;
    when others then return -1;

END  RRL_TT_ZONE_IS_EMPTY_DOCK;
/

prompt
prompt Creating function RRL_TT_ZONE_FIND_EMPTY_DOCK
prompt =============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_ZONE_FIND_EMPTY_DOCK
(  
  time1      timestamp, 
  ware_id1 int
)

-- Если номер склада пуст
-- По всем докам, доступным к отгрузке,  находим док, 
-- с максимальным расстоянием от предыдущей отгрузки, далее порядком доков.

-- Если номер склада определен, 
-- По всем докам, доступным к отгрузке, с данным номером склада,  находим док, 
-- с максимальным расстоянием от предыдущей отгрузки, далее порядком доков.

RETURN varchar2 IS

ret varchar2(255);

begin 

ret:='';

 if(ware_id1=0  ) then
 
    select DOCK into ret from (
    select DD.DOCK   from RRL_TT_DOCK DD where 
    dock_is_blocked = 0
     order by RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK( DD.DOCK , time1 ) desc , ord
) where rownum=1;
 
 else
 
        select DOCK into ret from (
        select DD.DOCK   from RRL_TT_DOCK DD 
        where DD.WARE_ID=ware_id1 and 
        dock_is_blocked=0
        order by RABAEV.RRL_TT_ZONE_IS_EMPTY_DOCK( DD.DOCK , time1 ) desc , ord
        ) where rownum=1;
 
 end if;


   RETURN ret;
exception

    when no_data_found then  RETURN 'NO_DOCK2';
    when others then return 'ERR2';

END  RRL_TT_ZONE_FIND_EMPTY_DOCK;
/

prompt
prompt Creating function RRL_TT_PLAN_DOCK
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_PLAN_DOCK
(  
  TT  int ,
  time1 timestamp
)
-- Центральная процедура находящая свободный док , фиксирующая его за маршрутом, 
RETURN int IS    

DOCK1 varchar2(255);

cursor subzones is
    select distinct ZONE from  RABAEV.RRL_TT_ZONES where DOCK=DOCK1 ; 

cursor WW_wares_id is 
select distinct PARENT_WARE_ID  from(
   select   WARE.PARENT_WARE_ID 
   from  RRL_SBORKA_PALLETS PAL , RRL_WARES WARE 
   where  
     PAL.TRANSTASK_ID = TT and 
     WARE.ID = PAL.WARE_ID 
     group by  WARE.PARENT_WARE_ID ,  WARE.ORD2 
     order by WARE.ORD2 ) ;


    replain_tt int;
    found_dock1 int;         
    found_dock varchar2(255);   
    time2 timestamp ;   
    time3 timestamp;        
    exit1 int;                  
    count1 int;                 
    ret1 int;                   
    ware_id2 int;
    count_of_pallets int;
    docks varchar(255);
    
begin 

time3:=time1;
docks:='';

-- СНАЧАЛА ОЧИЩАЕМ ПАЛЛЕТЫ МАРШРУТА ОТ СПЛАНИРОВАННЫХ ЗОН И ВРЕМЕН 

update RRL_SBORKA_PALLETS set ZONE = null ,   ZONE_TIME_PLAN_IN = null ,  ZONE_TIME_PLAN_OUT = null where TRANSTASK_ID = TT ;
update RRL_TRANSPORT_TASK set   DOCK_REZERV_TIME_FROM = null ,  DOCK_REZERV_TIME_TO = null , DOCK=null where ID=TT;
delete from RRL_TT_LOAD_TASK where TT_ID = TT ; -- ОЧИЩАЕМ ТАБЛИЦУ С ЗАДАНИЯМИ НА ПОГРУЗКУ.



replain_tt:=1;  -- Паллеты данного маршрута будем перепланировать при 1 проходе. 
DBMS_OUTPUT.put_line( 'начало процедуры RABAEV.RRL_TT_PLAN_DOCK' );
for WW_wares_id1  in  WW_wares_id loop -- ЦИКЛ ПО ВСЕМ СКЛАДАМ, ПАЛЛЕТЫ КОТОРЫХ УЧАВСТВУЮТ В МАРШРУТЕ , ПОРЯДОК СКЛАДОВ БЕРЕТСЯ ИЗ ПОЛЯ ORD2 !!! 

    DBMS_OUTPUT.put_line( 'перед' );
    DBMS_OUTPUT.put_line( concat( ' Паллеты склада: ' , to_char(WW_wares_id1.PARENT_WARE_ID ) ) );
    DBMS_OUTPUT.put_line( 'после' );

            found_dock:='';
            count1:=0;
            exit1:=0;
            time2:=time3; -- Время, на которое планируется док. 
            --    Находим док, свободный от погрузки на планируемый момент времени через процедуру RRL_TT_ZONE_FIND_EMPTY_DOCK.
            --    Если док и зона найдена, Фиксируем занятость дока и подзоны путем вызова процедур 
            --    RRL_TT_PLAN_PALL_ZONES - для зон  и маршрутов. Если свободного дока нет, 
            --    увеличиваем время на 30  минут и пробуем снова. 
            --    Если получилось, устанавливаем новое плановое время отгрузки маршрута.

            while  exit1=0 loop  -- Пока не найден док для данного склада, либо количество итерация превысило 10  
                count1:=count1+1;   
                  
                found_dock := RRL_TT_ZONE_FIND_EMPTY_DOCK( time2 , WW_wares_id1.PARENT_WARE_ID );  
                 
                DBMS_OUTPUT.put_line( concat( 'RRL_TT_ZONE_FIND_EMPTY_DOCK = ' , to_char( time2 )  ) );  
                DBMS_OUTPUT.put_line(found_dock ); 
                
                if (found_dock = 'NO_DOCK2' or found_dock = ''  ) then  
                    exit1:=0; 
                    time2:= time2 - 1/48; -- отступаем на 30 минут.
                else 
                    exit1:=1; 
                end if; 
                
                if( count1>10 ) then 
                    exit1:=1; -- Для данного склада дока не нашлось 
                    found_dock := concat( 'OF_' , to_char(WW_wares_id1.PARENT_WARE_ID) );
                    time2:=time3; -- откатываем изменение времени. 
                  --  return 0;
                end if;
                
            end loop;
            
            docks:=  found_dock ;
            --if (  (docks = '') or ( docks is null ) ) then
                 
            --else  
            --   docks:= concat(  concat( docks , ';' ) , found_dock ) ;             
            --end if;
            
            
             DBMS_OUTPUT.put_line( concat( '****Цепь найденных доков: '  , docks ) );
            
            if( time3<>time2 ) then -- Нужно изменить время начала погрузки на данном складе.
                update RRL_TRANSPORT_TASK set SHIPMENT_TIME=time2  where ID = TT ; 
            end if;
            
            
            update RRL_TRANSPORT_TASK set DOCK = docks   where ID = TT ; 
            -- Теперь для найденного дока находим свободную подзону.
            -- 
            DOCK1 :=found_dock;

        exit1:=0;
        for subzone1 in subzones loop -- По всем подзонам дока  DOCK1 
         
            if( exit1=0 ) then 
             
                count_of_pallets := RRL_TT_ZONE_EMPTY( time2 , subzone1.ZONE ); -- Получаем количество паллет, уже стоящих в зоне. 
                if count_of_pallets=0 then
                    ret1:=RRL_TT_PLAN_PALL_ZONES( TT , subzone1.ZONE , time2 , replain_tt , WW_wares_id1.PARENT_WARE_ID );
                    replain_tt:=0;
                    -- update RRL_TRANSPORT_TASK set DOCK = docks   where ID = TT ; 
                    exit1:=1; -- поиск по подзонам окончен
                    --return 1;
                    DBMS_OUTPUT.put_line( concat('          Паллеты пд данному складу и маршруту распланированы на зону: ' , subzone1.ZONE ) ) ;
                    time3:=time2;
                    else
                    DBMS_OUTPUT.put_line( concat('          НЕ НАЙДЕНО ПУСТЫХ ЯЧЕЕК В ЗОНЕ ОТГРУЗКИ НАПРОТИВ ЗОНЫ ' , subzone1.ZONE ) ) ;
                end if;
                
            end if;
            
        end loop;

        if( exit1=0 ) then
            DBMS_OUTPUT.put_line( concat('НЕ НАЙДЕНО ПУСТЫХ ЯЧЕЕК В ЗОНЕ ОТГРУЗКИ НАПРОТИВ ДОКА ' , DOCK1 ) ) ;
        end if;
        
        time3:=time2-1/48; -- Следующий склад грузится на полчаса позже 
        
end loop; -- ЦИКЛ ПО ВСЕМ СКЛАДАМ, ПАЛЛЕТЫ КОТОРЫХУЧАВСТВУЮТ В МАРШРУТЕ 

DBMS_OUTPUT.put_line( concat( 'ДОК=' , docks ) ) ;
 update RRL_TRANSPORT_TASK set DOCK = docks   where ID = TT ; 

    return 0;

exception

    when no_data_found then 
    DBMS_OUTPUT.put_line( 'no_data_found' ) ;
     RETURN 0;
    when others then
    DBMS_OUTPUT.put_line( 'others' ) ;
     return 0;

END   RRL_TT_PLAN_DOCK;
/

prompt
prompt Creating function RRL_TT_PLAN_SHIPPPING_HOUR
prompt ============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_PLAN_SHIPPPING_HOUR
( IDTT int )
RETURN timestamp 
IS 
  data_otgruzki timestamp ; 
BEGIN
 
--return systimestamp;
--DBMS_OUTPUT.put_line(  'hello1' );

    select max(  ftime_shipping_plan(  PAL.STDATE , ADR.SHIPPING_TIME ) ) into   data_otgruzki   
      from RRL_SBORKA_PALLETS PAL ,  RRL_ADDR ADR  where  TRANSTASK_ID  = IDTT  and PAL.ADDR=ADR.ADDR(+) ;
      
    DBMS_OUTPUT.put_line(  data_otgruzki );  
      
    update   RRL_TRANSPORT_TASK TT set SHIPMENT_TIME =  data_otgruzki where  TT.ID = IDTT ;


--DBMS_OUTPUT.put_line(  'hello2' );


   RETURN  data_otgruzki;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN null;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN null;
END RRL_TT_PLAN_SHIPPPING_HOUR;
/

prompt
prompt Creating function RRL_TT_POGRESHNOST2
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_POGRESHNOST2( PALLET_UID1 varchar2 )
 RETURN number IS 
tmpVar number;
count_kor number;

BEGIN



-- RRL_COUNT_KOR2( ARTICUL , QUANTITY , CURRENT_MOD_ID )
 
 
  
--select min( ( rowss.ORDER_WEIGHT / RRL_COUNT_KOR(  rowss.ARTICUL  , rowss.QUANTITY ) ) ) into tmpVar   from rrl_sborka_pallet_rows rowss 
-- where (rowss.PALLET_UID = PALLET_UID1) and (rowss.ORDER_WEIGHT > 0)  and ( RRL_COUNT_KOR(  rowss.ARTICUL  , rowss.QUANTITY )>0 ); 



   tmpVar := 3;


   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 3.5;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
       
END RRL_TT_POGRESHNOST2;
/

prompt
prompt Creating function RRL_TT_READY_PERC
prompt ===================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_READY_PERC( IDTT int )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLETS_COND C where  TRANSTASK_ID  = IDTT 
    and P.STATE = C.COND(+) and C.DONE=1;

tmpVar:= sobrano / itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_READY_PERC;
/

prompt
prompt Creating function RRL_TT_REORDER_ADR
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_REORDER_ADR( IDTT int )
 RETURN number IS 
 tmpVar number ;
 data_otgruzki date ; 
 tt int;
t3 timestamp;
-- переделать порядок для паллет , Устоновить плановое время отгрузки для маршрута.

cursor dddd is
SELECT ID , PALLET_UID  , ADDR  , ROWnum as ORD1   FROM (
select  P.ID , P.PALLET_UID  , P.ADDR  , ADR.ORD   from RABAEV.RRL_SBORKA_PALLETS  P  , RRL_ADDR ADR
     where  TRANSTASK_ID  = IDTT  and P.ADDR=ADR.ADDR(+) order by ADR.ORD ,  P.PALLET_UID  ) ;


BEGIN

   tmpVar := 0;
  
for sss in dddd loop
    update RRL_SBORKA_PALLETS set  RRL_SBORKA_PALLETS.ORD= sss.ORD1 where RRL_SBORKA_PALLETS.ID = sss.ID;
end loop;

    tmpVar :=  RRL_GET_TT_PRICE( IDTT ) ;
    update   RRL_TRANSPORT_TASK TT set PRICE = tmpVar where  TT.ID = IDTT ;
 

    t3:= RRL_TT_PLAN_SHIPPPING_HOUR( IDTT ) ;

   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RETURN 0;
END RRL_TT_REORDER_ADR;
/

prompt
prompt Creating function RRL_TT_SET_TRANSCOMMENT
prompt =========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_SET_TRANSCOMMENT (

  TRANS    VARCHAR2,
  TTID1    int

  
) return varchar2
IS
ID1 int;
LOPATA int;
count_fault_adr int;
htemp varchar2(255);

BEGIN


select TT.GIDROBORT into LOPATA  from RRL_TR_VEHICLE TT where TT.NUM = TRANS ;
if(LOPATA=1  ) then 
    return 'OK';
end if;



select count( DISTINCT AA.ADDR ) into count_fault_adr from RRL_SBORKA_PALLETS PP , RRL_ADDR AA where  ( PP.ID = TTID1 )  and ( PP.ADDR=AA.ADDR ) and  AA.STOL = 0 ;

if( count_fault_adr>0 ) then 
     htemp:= concat ( concat( 'У ' , concat( count_fault_adr , '  адреса(ов) нет подъемного стола, у машины #' ) ) ,  concat( TRANS ,  '# нет  гидроборта' ) );
     return  htemp;
end if;

return 'OK';

exception

when no_data_found then return 'Нет такого номера в базе';


END  RRL_TT_SET_TRANSCOMMENT;
/

prompt
prompt Creating function RRL_TT_SUMM
prompt =============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_SUMM( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
--select sum( R.TARESIZE )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
--     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_SUMM;
/

prompt
prompt Creating function RRL_TT_VERYFY_PERC
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_VERYFY_PERC( IDTT int )
 RETURN number IS 
tmpVar number;
itogo int;
sobrano int;

BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;

-- затем поймем, сколько из них собрано , прошло весовой контроль и размещено в зону экспедиции
select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where  TRANSTASK_ID  = IDTT and PROOVED=1;

    if(itogo=0) then
        return 0;
    end if;


tmpVar:= sobrano / itogo ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VERYFY_PERC;
/

prompt
prompt Creating function RRL_TT_VODITEL_COMPANY
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_VODITEL_COMPANY( VODITEL_ID1 int )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN

    tmpVar := '';
  
    select  DOVERENNOST_OT into tmpVar from RABAEV.RRL_TR_VODITEL VOD   where  VOD.ID = VODITEL_ID1 ;
 
    RETURN tmpVar;
   
    EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VODITEL_COMPANY;
/

prompt
prompt Creating function RRL_TT_VODITEL_INFO
prompt =====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_VODITEL_INFO( VODITEL_ID1 int )

 RETURN varchar2 IS 
tmpVar varchar2(255);
BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select concat( concat( concat( concat( F , ' ' ) , I ) , ' ' ) , O ) into tmpVar from RABAEV.RRL_TR_VODITEL where  ID = VODITEL_ID1 ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VODITEL_INFO;
/

prompt
prompt Creating function RRL_TT_VOLUME
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_VOLUME( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum( R.TARESIZE * ( R.PACK_COUNT ) )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID   ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_VOLUME;
/

prompt
prompt Creating function RRL_TT_WEIGHT
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_TT_WEIGHT( IDTT int )
 RETURN number IS 
tmpVar number;


BEGIN
   -- Возвращает процент собранных паллет 
   tmpVar := 0;
  
-- сначала запросим общее количество паллет
select sum(  R.ORDER_WEIGHT )  into tmpVar from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R 
     where  TRANSTASK_ID  = IDTT and P.PALLET_UID =  R.PALLET_UID ;

 
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_TT_WEIGHT;
/

prompt
prompt Creating function RRL_UPDATE_ARTICUL_EX
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_ARTICUL_EX(
-- ПРОЦЕДУРА ДЛЯ АВТОМАТИЧЕСКОЙ ЗАКАЧКИ ДАННЫХ ИЗ EXCEL
--Артикул    
articul4 varchar2 ,
--Наименование артикула     
name4 varchar2, 
--секция    (На самом деле идентификатор склада)    
section4 varchar2 ,
--ряд           = Z 
Z int ,
--стеллаж       = X*3
X3 int , 
--ярус          = Y
Y int ,
--место         = +X
X int ,
-- мест в ряду    
count_in_layer int ,
-- рядов в паллете    
layer_in_pall int ,
-- штук в паллете    
count_in_pal int , 
-- Ячейка отбора   
cell4 varchar ,
--Вес коробки
weight_of_kor number ,

-- Штрих-код штуки  
unit_barkode varchar,
--  Штрих-код коробки
kor_barkode varchar

)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_CELLS C where C.CELL=cell4;
    exception
            WHEN NO_DATA_FOUND THEN
                insert into RABAEV.RRL_CELLS (
                        CELL  ,
                      OTBOR    ,
                      BLOCKED_FOR_REMAINS    ,
                      BLOCKED_FOR_POPOLNENIE ,
                      X                      ,
                      Y                      ,
                      Z                      ,
                      BLOCKED_FOR_ACCEPT     ,
                      WARE_ID          
                )  
                values 
                (   
                    cell4 ,
                    1 ,
                    0 ,
                    0 ,
                    X3*3+X ,
                    Y ,
                    Z ,
                    0,
                    1
                );
            WHEN OTHERS THEN
                   null;
    end;


--return '';


--DBMS_OUTPUT.put_line( ' Hello 1 ');

    begin

        select AAA.ACTICUL into tmpVar from RABAEV.RRL_ARTICULS AAA where AAA.ACTICUL =   articul4 ;

        update RABAEV.RRL_ARTICULS set 
             NORMA_UKLADKI = count_in_pal ,
             CELL  = cell4 ,
             NAME  = name4,
             UNIT_TYPE  =  'шт'    ,
           BARCODE_SHT= unit_barkode,
              BARCODE_KOR  = kor_barkode ,
              BARCODE_BL  =  '' ,
              WEIGHT_OF_KOR = weight_of_kor,
              COUNT_IN_ROW = count_in_layer,
              ROWS_IN_PAL = layer_in_pall 
        where  ACTICUL =   articul4 ;
       
    exception
        WHEN NO_DATA_FOUND THEN
           
            insert into RABAEV.RRL_ARTICULS  (
                  ACTICUL   ,
                  NORMA_UKLADKI ,
                  CELL   ,
                  NAME   ,
                  UNIT_TYPE     ,
                  BARCODE_SHT ,
                  BARCODE_KOR    ,
                  BARCODE_BL     ,
                  WEIGHT_OF_KOR  ,
                  COUNT_IN_ROW  ,
                  ROWS_IN_PAL   
            ) values (
                articul4 ,
                count_in_pal ,
                cell4 ,
                name4 ,
                'шт' , 
                unit_barkode ,
                kor_barkode ,
                '' ,
                weight_of_kor ,
                count_in_layer  ,
                layer_in_pall 
            );
        
         WHEN OTHERS THEN
           null;
    end;
   


   
   
   RETURN '';
   
  
END RRL_UPDATE_ARTICUL_EX;
/

prompt
prompt Creating function RRL_UPDATE_CELL
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_CELL(
    cell4 varchar2 ,
    X1 int ,
    Y1 int ,
    Z1 int , 
    ware_id4 int , 
    LIMIT_WEIGHT1 number ,
    LIMIT_HEIGHT1 number ,
    Y_VISOTA1 number

)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_CELLS C where C.CELL=cell4;
        
        
        update RABAEV.RRL_CELLS set X=X1 , Y=Y1 , Z=Z1 , ware_id= ware_id4  ,
         LIMIT_WEIGHT=LIMIT_WEIGHT1 , LIMIT_HEIGHT=LIMIT_HEIGHT1 ,
         Y_VISOTA=Y_VISOTA1 
        where CELL=cell4 ;
        
        
    exception
            WHEN NO_DATA_FOUND THEN
                insert into RABAEV.RRL_CELLS (
                      CELL  ,
                      OTBOR    ,
                      BLOCKED_FOR_REMAINS    ,
                      BLOCKED_FOR_POPOLNENIE ,
                      X                      ,
                      Y                      ,
                      Z                      ,
                      BLOCKED_FOR_ACCEPT     ,
                      WARE_ID        ,
                      LIMIT_WEIGHT  , 
                      LIMIT_HEIGHT ,
                      Y_VISOTA
                )  
                values 
                (   
                    cell4 ,
                    1 ,
                    0 ,
                    0 ,
                    X1 ,
                    Y1 ,
                    Z1 ,
                    0,
                    ware_id4 ,
                    LIMIT_WEIGHT1 , 
                    LIMIT_HEIGHT1 ,
                    Y_VISOTA1
                );
            WHEN OTHERS THEN
                   null;
    end;


 RETURN 1;
   
  
END RRL_UPDATE_CELL;
/

prompt
prompt Creating function RRL_UPDATE_OTHOD_PALLET_ROWS2
prompt ===============================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_OTHOD_PALLET_ROWS2(

PALLET_UID_to varchar ,
row_id_from int 


)
 RETURN INT 
 IS
 
tmpVar int;
 
BEGIN
   tmpVar := 0;
 
   
  
      


   
   RETURN tmpVar;
    
END RRL_UPDATE_OTHOD_NAKLAD_ROWS2;
/

prompt
prompt Creating function RRL_UPDATE_PALLET_ROW
prompt =======================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_PALLET_ROW(
    articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2 
 )
 
 RETURN varchar2 
 IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;

BEGIN
    
 select  TAREWEIGHT , ORDER_WEIGHT , TARESIZE , quantity , ORIGINAL_ORDER_WEIGHT , original_quantity
 into   TAREWEIGHT1 , ORDER_WEIGHT1 , TARESIZE1 , quantity1 , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
 from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 if(quantity1=0) then
 
     if( ORIGINAL_ORDER_WEIGHT1 >0 ) then
     
      koef := count1 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1
        ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
        where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
         
        
     end if;
  
 return 'ok';
 else
    
    koef := count1 / quantity1 ;
    
 end if;
 
 

 

 
   update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1
    ,ORDER_WEIGHT= round( ORDER_WEIGHT*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
    where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   

   RETURN 'ok';
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PALLET_ROW;
/

prompt
prompt Creating function RRL_UPDATE_PALLET_ROW2
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_PALLET_ROW2(
    articul1 varchar2 ,
    pallet_uid1 varchar2 ,
    count1  number , 
    user_id1 varchar2
 )
 
 RETURN varchar2 
 IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;
count_nesobrano int;
rhelp int;

BEGIN
    count_nesobrano:=0;
 select  TAREWEIGHT , ORDER_WEIGHT , TARESIZE , quantity , ORIGINAL_ORDER_WEIGHT , original_quantity
 into   TAREWEIGHT1 , ORDER_WEIGHT1 , TARESIZE1 , quantity1 , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
 from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 if(quantity1=0) then
 
     if( ORIGINAL_ORDER_WEIGHT1 >0 ) then
     
      koef := count1 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1 , VYCHERK_USER_ID = user_id1 
        ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
        where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
         
        
     end if;
  

 else
    
    koef := count1 / quantity1 ;
       update RABAEV.RRL_SBORKA_PALLET_ROWS  set QUANTITY = count1 ,  VYCHERK_USER_ID = user_id1 
    ,ORDER_WEIGHT= round( ORDER_WEIGHT*koef , 4) -- ,  TARESIZE= round( TARESIZE*koef , 4) , TAREWEIGHT= round( TAREWEIGHT*koef , 4) , 
    where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
   
 end if;
 

 
begin
 
 select count(ID) into count_nesobrano from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ((QUANTITY<> sobrano) or (sobrano is null));
    if(count_nesobrano=0)then
        
        update RABAEV.RRL_SBORKA_PALLETs set PROOVED_BY_SCAN=1 , KLADOVSHIK=user_id1  where PALLET_UID = pallet_uid1  ;
        
        
        rhelp:=RABAEV.RRL_SET_SCAN_PROOVE2(
            PALLET_UID1    ,
            0 ,
            '' , 
            '',
            user_id1
        );
        
        RETURN 'PROOVED_BY_SCAN';
    end if;
exception WHEN NO_DATA_FOUND THEN null;
end;   
   
    RETURN 'ok';

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PALLET_ROW2;
/

prompt
prompt Creating function RRL_UPDATE_PALLET_ROW3
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_PALLET_ROW3(
    row_id1 int ,
    articul1 varchar2 ,
    pallet_uid1 varchar2 , 
    PACK_COUNT2 number , -- Количество упаковок
    QUANTITY2 number , -- Штуки
    CURRENT_MOD_ID2 int , -- Модификация 
    ORDER_WEIGHT2 number , -- Вес N штук.
    PRIHOD_PALLET_UID2 varchar2 ,-- Данные паллета прихода.
    user_id1 varchar2
 )
 
 RETURN varchar2 
 IS 
 
quantity1 number;
original_quantity1 number;
TAREWEIGHT1 number;
ORDER_WEIGHT1 number;
TARESIZE1  number;
ORIGINAL_ORDER_WEIGHT1 number ;
koef number;
count_nesobrano int;
rhelp int;
type_w1 int;
COUNT_SHT_IN_KOR1 int;
PACK_COUNT3 int; 
KARTON_WEIGHT3 number;
QUANTITY3 number;
 SHT_IN_KOR3 int;
SHT_WEIGHT3 number;
ORDER_WEIGHT3 number;
BEGIN

count_nesobrano:=0;
select art.type_w , COUNT_SHT_IN_KOR  into type_w1 , COUNT_SHT_IN_KOR1  from rrl_articuls art where art.ACTICUL= articul1; 



if( type_w1=0 ) then  -- ТИП товара = 0     
    if(COUNT_SHT_IN_KOR1= 0) or ( COUNT_SHT_IN_KOR1 is null ) then
                     return  concat( concat('Для артикула ' , articul1)  , ' не указана вложенность. Укажите вложенность.' );
    end if;

     select     ORDER_WEIGHT    , ORIGINAL_ORDER_WEIGHT , original_quantity
     into      ORDER_WEIGHT1   , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
     from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

          koef := QUANTITY2 / original_quantity1 ;
          update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
          PACK_COUNT=round(QUANTITY/COUNT_SHT_IN_KOR1 , 2 ) , 
          QUANTITY = QUANTITY2 , 
          VYCHERK_USER_ID = user_id1 
          ,ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4)  ,
          PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 
          where id = row_id1 ; --PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
     
end if;  -- ТИП товара = 0 

if( type_w1=1 ) then    -- ТИП товара = 1  
   
     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                       return  concat( concat('Для артикула ' , articul1)  , ' не указана фасовка. Укажите фасовку.' );
     end if;

     select     ORDER_WEIGHT    , ORIGINAL_ORDER_WEIGHT , original_quantity
     into      ORDER_WEIGHT1   , ORIGINAL_ORDER_WEIGHT1 , original_quantity1
     from RABAEV.RRL_SBORKA_PALLET_ROWS where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 
       
     select SHT_IN_KOR into COUNT_SHT_IN_KOR1  from rrl_articul_mods where id=CURRENT_MOD_ID2 ; 

     koef := QUANTITY2 / original_quantity1 ;
     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=round(QUANTITY/COUNT_SHT_IN_KOR1 , 2 ) , 
     QUANTITY = QUANTITY2 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= round( ORIGINAL_ORDER_WEIGHT1*koef , 4)  ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

end if;  -- ТИП товара = 1  
 

if( type_w1=2 ) then    -- ТИП товара = 2  
   
     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                        return  concat( concat('Для артикула ' , articul1)  , ' не указана фасовка. Укажите фасовку.' );
        end if;

     if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                        return  concat( concat('Для артикула ' , articul1)  , ' не указана партия. Укажите партию.' );
     end if;

    select round(  ORDER_WEIGHT2 / ( MOD_ID.KARTON_WEIGHT + MOD_ID.SHT_WEIGHT* MOD_ID.SHT_IN_KOR ) ,2 ) , MOD_ID.KARTON_WEIGHT
     into  PACK_COUNT3 , KARTON_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    select (ORDER_WEIGHT2 - PACK_COUNT3* KARTON_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT3 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

end if;  -- ТИП товара = 2  

if( type_w1=3 ) then    -- ТИП товара = 3  
   
     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                          return  concat( concat('Для артикула ' , articul1)  , ' не указана фасовка. Укажите фасовку.' );
        end if;

    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                          return  concat( concat('Для артикула ' , articul1)  , ' не указана партия. Укажите партию.' );
    end if;

    select   MOD_ID.KARTON_WEIGHT
     into    KARTON_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    select (ORDER_WEIGHT2 - PACK_COUNT2* KARTON_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

end if;  -- ТИП товара = 3   



if( type_w1=6 ) then    -- ТИП товара = 6  
   
     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
                        return  concat( concat('Для артикула ' , articul1)  , ' не указана фасовка. Укажите фасовку.' );
        end if;

    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                            return  concat( concat('Для артикула ' , articul1)  , ' не указана партия. Укажите партию.' );
    end if;

    select   MOD_ID.KARTON_WEIGHT , MOD_ID.SHT_WEIGHT 
     into    KARTON_WEIGHT3 , SHT_WEIGHT3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

    if(SHT_WEIGHT3   = 0) or ( SHT_WEIGHT3 is null ) then
            return 'Для артикула '+articul1+' не указан вес штуки в фасовке.';
        end if;
        
    select (((ORDER_WEIGHT2 - PACK_COUNT2* KARTON_WEIGHT3 ) / SHT_WEIGHT3 ) *  ( 100- obj2number(PRIHOD_PALLET.DEFECT_PERC)  ) )/100
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

end if;  -- ТИП товара = 6   







if( type_w1=7 ) then    -- ТИП товара = 7    
   
     if(CURRENT_MOD_ID2   = 0) or ( CURRENT_MOD_ID2 is null ) then
            return  concat( concat('Для артикула ' , articul1)  , ' не указана фасовка. Укажите фасовку.' );
        end if;

     if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
              return  concat( concat('Для артикула ' , articul1)  , ' не указана партия. Укажите партию.' );
     end if;

    select   MOD_ID.KARTON_WEIGHT , MOD_ID.SHT_WEIGHT , MOD_ID.SHT_IN_KOR   
     into    KARTON_WEIGHT3 , SHT_WEIGHT3 , SHT_IN_KOR3 from RRL_ARTICUL_MODS MOD_ID where ID=CURRENT_MOD_ID2 ;

     if(SHT_WEIGHT3   = 0) or ( SHT_WEIGHT3 is null ) then
            return    concat( concat('Для артикула ' , articul1)  ,' не указан вес штуки в фасовке.' );
            
     end if;
        
    if(SHT_IN_KOR3   = 0) or ( SHT_IN_KOR3 is null ) then
             return    concat( concat('Для артикула ' , articul1)  ,' не указана вложенность штуки в фасовке.' );
    end if;      
        
    begin 
        select (  PACK_COUNT2 * SHT_IN_KOR3     )   ,    PACK_COUNT2 * ( ( WEIGHT_BRUTTO - WEIGHT_TN ) / PRIHOD_PALLET.COUNT_KOR   )
        into QUANTITY3 ,   ORDER_WEIGHT3 from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;
    exception
        when no_data_found then return concat( concat( 'Приход по паллету ' , PRIHOD_PALLET_UID2 ) , ' не обнаружен' );
        when others then return  concat( concat( 'Приход по паллету ' , PRIHOD_PALLET_UID2 ) , ' не указан вес, ТН либо колич. коробок. '  );

    end;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT3 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

end if;  -- ТИП товара = 7  








if( type_w1=5 ) then    -- ТИП товара = 5  
   
begin 
    if(PRIHOD_PALLET_UID2   = '') or ( PRIHOD_PALLET_UID2 is null ) then
                          return  concat( concat('Для артикула ' , articul1)  , ' не указана партия. Укажите партию.' );
    end if;
        
    select PRIHOD_PALLET.UNIT_COUNT * (ORDER_WEIGHT2 / ( PRIHOD_PALLET.WEIGHT_BRUTTO - PRIHOD_PALLET.WEIGHT_TN )  ) 
    into QUANTITY3  from  RRL_PALLETS PRIHOD_PALLET where PRIHOD_PALLET.UID_PALLET = PRIHOD_PALLET_UID2;

     update RABAEV.RRL_SBORKA_PALLET_ROWS  set 
     PACK_COUNT=PACK_COUNT2 , 
     QUANTITY = QUANTITY3 , 
     VYCHERK_USER_ID = user_id1 ,
     ORDER_WEIGHT= ORDER_WEIGHT2 ,
     PRIHOD_PALLET_UID = PRIHOD_PALLET_UID2 , 
     CURRENT_MOD_ID = CURRENT_MOD_ID2 
      where id = row_id1 ; --where PALLET_UID = pallet_uid1  and ARTICUL=articul1 ; 

    exception 
    when no_data_found then return 'Не найдена партия';
    when others then return 'ошибка RRL_UPDATE_PALLET_ROW3';
    end;

end if;  -- ТИП товара = 6   

-- Закончили с type_w  

begin
 select count(ID) into count_nesobrano from RABAEV.RRL_SBORKA_PALLET_ROWS 
 where PALLET_UID = pallet_uid1  and ((QUANTITY<> sobrano) or (sobrano is null));
    if(count_nesobrano=0)then        
        update RABAEV.RRL_SBORKA_PALLETs set PROOVED_BY_SCAN=1 , KLADOVSHIK=user_id1  where PALLET_UID = pallet_uid1  ;
        rhelp:=RABAEV.RRL_SET_SCAN_PROOVE2(
            PALLET_UID1    ,
            0 ,
            '' , 
            '',
            user_id1
        );
        RETURN 'PROOVED_BY_SCAN';
    end if;
exception WHEN NO_DATA_FOUND THEN null;
end;   


RETURN 'ok';

   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 'не найдено';
      WHEN OTHERS THEN RAISE;
END RRL_UPDATE_PALLET_ROW3;
/

prompt
prompt Creating function RRL_UPDATE_PRICE
prompt ==================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_PRICE( tt_id int )
 RETURN number IS 
tmpVar number;
BEGIN
 tmpVar := 0;
   tmpVar := RRL_GET_TT_PRICE(  tt_id ) ;
   
   
   
   update RRL_TRANSPORT_TASK  set price=tmpVar  where ID = tt_id  ;

   
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_UPDATE_PRICE;
/

prompt
prompt Creating function RRL_UPDATE_SBORKA_PALLET_ROWS2
prompt ================================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_SBORKA_PALLET_ROWS2(

PALLET_UID_to varchar2 ,
row_id_from int 


)
 RETURN INT 
 IS
 
PALLET_UID_from varchar2(255);
tmpVar int;
articul_temp varchar(255);
row_id_upd int;
count1 number;
count2 number;
tt varchar(200);

BEGIN
   tmpVar := 0;
 
select PR.ARTICUL  ,  PR.QUANTITY   , PR.PALLET_UID  into articul_temp , count2 , PALLET_UID_from from RRL_SBORKA_PALLET_ROWS PR where PR.ID = row_id_from ;

    if( PALLET_UID_from= PALLET_UID_to ) then 
        return row_id_from;
    end if;
    

    begin
        --   СМОТРИМ В ПРЕДЫДУЩЕМ ПАЛЛЕТЕ . 
        select PR.ID , PR.QUANTITY into row_id_upd , count1  from RRL_SBORKA_PALLET_ROWS PR where PR.PALLET_UID = PALLET_UID_to and PR.ARTICUL = articul_temp  ;
        --update RRL_SBORKA_PALLET_ROWS PR  set   PR. , selected=1 where ID = row_id_from ;    
--       tt:= RRL_UPDATE_PALLET_ROW2( row_id_upd  ,    count1+count2 , 'MOVE' ); 
        tt:= RRL_UPDATE_PALLET_ROW2( articul_temp   ,  PALLET_UID_to  ,    count1+count2 , 'MOVE' ); 
        
        if( PALLET_UID_from <> PALLET_UID_to ) then 
            
            delete  from RRL_SBORKA_PALLET_ROWS   where  ID = row_id_from;
            
        end if;
        
    exception
        when no_data_found then
        -- Если в паллете, куда переностися строка нет таких артикулов.   
            update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = PALLET_UID_to , selected=1 where ID = row_id_from ;
        when others then RAISE;
          
    end;

   
   RETURN tmpVar;
    
END RRL_UPDATE_SBORKA_PALLET_ROWS2;
/

prompt
prompt Creating function RRL_UPDATE_SG
prompt ===============================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_SG
(
    articul1 varchar2 ,
   sg int
)
 RETURN int IS

 
                                                              
BEGIN


 update rrl_articuls R set R.BESTBEFOREDAYS=sg where R.ACTICUL=articul1;

   RETURN 0;
 
END  RRL_UPDATE_SG;
/

prompt
prompt Creating function RRL_UPDATE_TT_ZONE
prompt ====================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_UPDATE_TT_ZONE
(  
  ZONE1      VARCHAR2, 
  SUB_ZONE1  VARCHAR2, 
  DOCK1      VARCHAR2 ,  
  X1 number , 
  Y1 number 
)
 RETURN int IS
 tmp_var varchar2(255);

BEGIN

    select SUB_ZONE1 into  tmp_var  from RRL_TT_ZONES where SUB_ZONE  = SUB_ZONE1 ;
    update RRL_TT_ZONES set zone=zone1 , dock = dock1 , X=X1 , Y=Y1  where sub_zone = sub_zone1 ;

   RETURN 0;
exception
when no_data_found then 
    insert into RABAEV.RRL_TT_ZONES ( ZONE , SUB_ZONE , DOCK , X , Y   ) values ( ZONE1 , SUB_ZONE1 , DOCK1 , X1 , Y1 );
   RETURN 0;
END  RRL_UPDATE_TT_ZONE;
/

prompt
prompt Creating function RRL_VEHICLE_REIS_COUNT
prompt ========================================
prompt
CREATE OR REPLACE FUNCTION rabaev.RRL_VEHICLE_REIS_COUNT( NUM varchar2 , dat Date )
 RETURN int IS 
 varTMP int;
BEGIN
varTMP:=0;
select count(ID) into varTMP from RABAEV.RRL_TRANSPORT_TASK where TRANSPORT=NUM and SHIPMENT_DATE = dat;
   

   
   RETURN varTMP;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       return 0;
       RAISE;
END RRL_VEHICLE_REIS_COUNT;
/

prompt
prompt Creating function UPDATE_RRL_MOD
prompt ================================
prompt
CREATE OR REPLACE FUNCTION rabaev.UPDATE_RRL_MOD (

  ID1             INTEGER,
  ARTICUL1        VARCHAR2,
  NAME1           VARCHAR2,
  SHT_IN_KOR1     INTEGER,
  SHT_WEIGHT1     NUMBER,
  KARTON_WEIGHT1  NUMBER,
  DELETED1        INTEGER
  
) return int
IS
ID2 int;

BEGIN
  

if ID1>0 then

    update  RABAEV.RRL_ARTICUL_MODS
    set 
      ID             = ID1,
      ARTICUL        = ARTICUL1,
      NAME           = NAME1,
      SHT_IN_KOR     = SHT_IN_KOR1 ,
      SHT_WEIGHT     = SHT_WEIGHT1 ,
      KARTON_WEIGHT  = KARTON_WEIGHT1,
      DELETED        =DELETED1
    where ID=ID1;
return ID1;
else

      INSERT INTO RABAEV.RRL_ARTICUL_MODS(
          ID , 
          ARTICUL        ,
          NAME           ,
          SHT_IN_KOR     ,
          SHT_WEIGHT     ,
          KARTON_WEIGHT  ,
          DELETED        
      ) VALUES (
          RABAEV.MODS_SEQ.NEXTVAL,
          ARTICUL1      ,
          NAME1          ,
          SHT_IN_KOR1     ,
          SHT_WEIGHT1     ,
          KARTON_WEIGHT1  ,
          DELETED1                      
        );
        
    SELECT MODS_SEQ.CURRVAL INTO ID2 FROM DUAL;
    
end if;
    
    return ID2;
    
END  UPDATE_RRL_MOD;
/

prompt
prompt Creating function UPDATE_RRL_MOD2
prompt =================================
prompt
CREATE OR REPLACE FUNCTION rabaev.UPDATE_RRL_MOD2 (

  ID1             INTEGER,
  ARTICUL1        VARCHAR2,
  NAME1           VARCHAR2,
  SHT_IN_KOR1     number,
  SHT_WEIGHT1     NUMBER,
  KARTON_WEIGHT1  NUMBER,
  DELETED1        INTEGER ,
  SHK_SHT1   VARCHAR2,
  SHK_KOR1   VARCHAR2
  
) return int
IS
ID2 int;

BEGIN
  

if ID1>0 then

    update  RABAEV.RRL_ARTICUL_MODS
    set 
      ID             = ID1,
      ARTICUL        = ARTICUL1,
      NAME           = NAME1,
      SHT_IN_KOR     = SHT_IN_KOR1 ,
      SHT_WEIGHT     = SHT_WEIGHT1 ,
      KARTON_WEIGHT  = KARTON_WEIGHT1,
      DELETED        =DELETED1 , 
      SHK_SHT = SHK_SHT1 ,
      SHK_KOR = SHK_KOR1
    where ID=ID1;
return ID1;
else

      INSERT INTO RABAEV.RRL_ARTICUL_MODS(
          ID , 
          ARTICUL        ,
          NAME           ,
          SHT_IN_KOR     ,
          SHT_WEIGHT     ,
          KARTON_WEIGHT  ,
          DELETED        
      ) VALUES (
          RABAEV.MODS_SEQ.NEXTVAL,
          ARTICUL1      ,
          NAME1          ,
          SHT_IN_KOR1     ,
          SHT_WEIGHT1     ,
          KARTON_WEIGHT1  ,
          DELETED1                      
        );
        
    SELECT MODS_SEQ.CURRVAL INTO ID2 FROM DUAL;
    
end if;
    
    return ID2;
    
END  UPDATE_RRL_MOD2;
/

prompt
prompt Creating procedure ADD_SFERA_EAN
prompt ================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.ADD_SFERA_EAN (
    row_uid OUT NUMBER,
    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
)
AS
BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    
END  ADD_SFERA_EAN;
/

prompt
prompt Creating procedure RRL_ACCEPT_ORDER2
prompt ====================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.RRL_ACCEPT_ORDER2 (
 order_id int 
 )
as
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;

cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN
    
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return;
   end if;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 
 
    while tmpVar>0 loop
        begin
     
    

        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
        
             delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID   ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              articul_row.EXPIRY_DATE , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id 
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  


commit;

end;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

prompt
prompt Creating procedure RRL_ACCEPT_ORDER2_2
prompt ======================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.RRL_ACCEPT_ORDER2_2 (
 order_id int ,
 user_id1 varchar2
 )
as
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);
tmp_current_cond int;
articul_row_NORMA_UKLADKI int ;
infin int;
cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID , RRL_PRIHOD_NAKLAD_ROWS.KOLPAL CUSTOM_NU   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
BEGIN

infin:=0;   
   DBMS_OUTPUT.put_line( 'flag 1'); 
   tmp_current_cond:=0;
   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 ) or ( tmp_current_cond=1 ) then
        return;
   end if;
   
   DBMS_OUTPUT.put_line( 'flag 2'); 
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;



DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
    if(infin>1000) then  return; end if;
 
    
 
 infin:=infin+1;
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 articul_row_NORMA_UKLADKI:=articul_row.NORMA_UKLADKI;
 
 if  ((not ( articul_row.CUSTOM_NU is null )) and ( articul_row.CUSTOM_NU >0 )) then
     articul_row_NORMA_UKLADKI:=articul_row.CUSTOM_NU ;
 end if;
 

    while tmpVar>0 loop
          begin
        
        if(infin>1000) then  return; end if;
        infin:=infin+1;
    
        if( articul_row_NORMA_UKLADKI<=0 ) then
            DBMS_OUTPUT.put_line( 'null' );
            return;
        end if;
        
    
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row_NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row_NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
         
             delete from RABAEV.RRL_REMAINS where UID_POLETA=tmp_uid_pallet  ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA  =tmp_uid_pallet  ;
     
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID , kladovshik  ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              systimestamp  , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id , user_id1
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  


--commit;

end;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

prompt
prompt Creating procedure RRL_ACCEPT_ORDER3
prompt ====================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.RRL_ACCEPT_ORDER3 (
 order_id int ,
 user_id1 varchar2
 )
as
tmpVar NUMBER;
event_id int ;
dest_cell varchar2(50);
direct_accept_to_cell1 int;
direct_cell varchar2(50);

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
  
cursor rows1 is

   SELECT   ARTICUL , sum(UNIT_COUNT ) uc ,sum( UNIT_COUNT*PRICE ) sm , (sum( DEFECT_PERC*UNIT_COUNT ) / sum ( UNIT_COUNT)) dp
       FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id 
    group by ARTICUL ;
      
   
BEGIN

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=2  where ID = order_id ;
direct_accept_to_cell1:=0; 

-- dbms_output.put_line('n='||event_id);
    
    
     for  pallet_row in dddd loop
     
        select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;
        dest_cell:='IN_DOCK';
        direct_cell:=null;
        begin 
            select WAR.direct_accept_to_cell , CEL.CELL into direct_accept_to_cell1 , direct_cell 
            from RRL_ARTICULS ART , RRL_CELLS CEL , RRL_WARES WAR 
            where ART.CELL = CEL.CELL and ART.ACTICUL = pallet_row.ARTICUL and WAR.id=CEL.ware_id ;

        exception 
            when no_data_found then null;
            when others then null;
        end ;

        if not (direct_cell is null) then
            if direct_accept_to_cell1 =1 then 
                
                dest_cell:=direct_cell ;
                
            end if;
            
        end if;


         insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          dest_cell,
          pallet_row.CREATION_DATE , 
          pallet_row.CREATION_DATE , 
          pallet_row.UNIT_COUNT , 
          1 ,
          pallet_row.UID_PALLET ,
          user_id1 ,
          pallet_row.PRIHOD_NAKLAD_ID 
            );


      end loop;
  
  for  r1 in rows1 loop
    update RRL_PRIHOD_NAKLAD_ROWS  set COUNT1 = r1.uc , DEFECT_PERC = r1.dp
    where ORDID =  order_id and  ARTICUL=r1.ARTICUL ; 
    
    
  end loop;

commit;




end;
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

prompt
prompt Creating procedure RRL_OTKAT_ORDER2
prompt ===================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.RRL_OTKAT_ORDER2 (
 order_id int 
 )
as

tmp_current_cond int;
tmp_v varchar2(50);
cursor dddd is

   SELECT   UID_PALLET  from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id ;
   
BEGIN
    
   tmp_current_cond:=0;

   
   select condition into tmp_current_cond from  RABAEV.RRL_PRIHOD_NAKLAD  where ID = order_id  ;
   
   if  ( tmp_current_cond=2 )  then
        return;
   end if;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=0  where ID = order_id  ;
   
   if  ( tmp_current_cond=1 or tmp_current_cond=0 )  then
     delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   end if;


 for  articul_row in dddd loop
            tmp_v := articul_row.UID_PALLET ;
             delete from RABAEV.RRL_REMAINS where UID_POLETA= tmp_v ;
             delete from RABAEV.RRL_EVENTS where   UID_POLETA=tmp_v  ;
  end loop;



commit;

end;
/

prompt
prompt Creating procedure RRL_STORNO_ORDER3
prompt ====================================
prompt
CREATE OR REPLACE PROCEDURE rabaev.RRL_STORNO_ORDER3 (
 order_id int ,
 user_id1 varchar2
 )
as
tmpVar NUMBER;
event_id int ;

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
   
   
BEGIN

if( RRL_PRIHOD_MAY_STORNO(order_id )=0 ) then 
    return;
end if;

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=3  where ID = order_id ;
    
    
     for  pallet_row in dddd loop
     
        select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;


         insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          'IN_DOCK',
          pallet_row.CREATION_DATE , 
          pallet_row.CREATION_DATE , 
          ( (-1)*(pallet_row.UNIT_COUNT ) ) , 
          1 ,
          pallet_row.UID_PALLET ,
          user_id1 ,
          pallet_row.PRIHOD_NAKLAD_ID 
            );


      end loop;

commit;

end;
   -- По каждой паллете сделать проводку, удалив ее из зоны "ПРИЕМКИ".
/

prompt
prompt Creating package body COMPL
prompt ===========================
prompt
create or replace package body rabaev.compl is


  -- Function and procedure implementations
function update_seq( articul1 varchar2 , ware_id1 int , SQ1 int, SQGROUP int ) return int is
     d1 int;
  begin
        select     SQ.SEQ into d1
         from RABAEV.RRL_COMPL_SEQ SQ where SQ.ARTICUL=articul1 and SQ.WARE_ID= ware_id1 ; 
         update RABAEV.RRL_COMPL_SEQ  set SEQ=SQ1 , SEQ_GROUP = SQGROUP 
         where articul= articul1 and ware_id= ware_id1;
        return 1;
    EXCEPTION
      WHEN no_data_found then 
        insert into RABAEV.RRL_COMPL_SEQ  ( articul , WARE_ID , SEQ ,SEQ_GROUP )values
               (articul1 , ware_id1 , SQ1 ,SQGROUP );
               return 1;
  end;

-- Порядок сборки для артикула
function show_sq( articul1 varchar2 , ware_id1  int ) return int is
  ret1 int;
begin

    select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
    return ret1;
    exception
      when no_data_found then return 101;
    when others then 
      begin
        delete from  RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1 and rownum>1 ;
        
         select SQ.SEQ into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
         return ret1;
      end;
end;

-- ГРУППА СБОРКИ ДЛЯ АРТИКУЛА
function show_sq_gr( articul1 varchar2 , ware_id1  int ) return int is
  ret1 int;
begin

    select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
    return ret1;
    exception
      when no_data_found then return 101;
    when others then 
      begin
        delete from  RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1 and rownum>1 ;
        commit;
         select SQ.SEQ_GROUP into ret1 from RRL_COMPL_SEQ SQ where articul=articul1 and ware_id=ware_id1;
         return ret1;
      end;
end;

-- Ячейка отбора для данного артикула в данной заявке.
function path( articul1 varchar2 ,  sborka_pallet_uid  varchar2 ) return varchar2 is
  ret1 varchar2(50);
begin

select cell into ret1  from RRL_ARTICULS where acticul = articul1;
return ret1;
exception 
when no_data_found then return 'NO_ART';
when others then  return  'ERR8';
end;

-- ДЕЛЕНИЕ СТ НА ПАЛЛЕТЫ.
-- деление ст на паллеты.
-- настройки склада - Максимум 

-- берем максимальное ограничение на паллеты из настроек склада.
-- подпроцедура сделать разбиение на основе поданных настроек.
-- Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка)
-- По всем строкам  

-- если предыдущий паллет завершен, начинаем новый паллет
-- конец если
--  у= мин ( количество коробок данного артикула , необходимое для завершения паллета , заказ на данный артикул )

-- если у=0, завершаем паллет, повторяем 
--       у= мин ( количество коробок данного артикула , необходимое для завершения паллета , заказ на данный артикул )
-- конец если 
-- Конец по всем строкам
-- фиксируем версию разбиения
-- конец процедуры.
         


function divide_st_bypal( stn varchar2 , ware_id1  int ) return int is
  ret1 int;
begin
 
null;







commit ;
  return 0;
end;



-- подпроцедура сделать разбиение на основе поданных настроек( МаксимумV , МаксимумМ , номер заказа ). Возврат число
function sub_divide_pall( ord_id int ) return int is 
--  Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка) 
    cursor ORDER_ROWS is 
       select RS.ARTICUL , RS.ORDER_WEIGHT , RS.QUANTITY , RS.TARESIZE , RS.TAREWEIGHT , RS.ORIGINAL_QUANTITY , RS.Original_Order_Weight
       from RABAEV.RRL_ORDER_ROWS RS where RS.ORDER_ID = ord_id ;
begin
  
--    Берем строки заказа из таблицы RABAEV.RRL_ORDER_ROWS  (RRL_ORDERS - шапка) 
for r in order_rows loop
null;
--  Начинаем 1-й паллет;
--  По всем строкам  
--    К = количество товара в заказе
--    у=1;
--      Пока к>0 и у>0 цикл
--        у = мин ( количество коробок данного артикула необходимое для завершения паллета, заказ на данный артикул )
--        К=К-у;
--            если у=0, 
--                 завершаем паллет(версия, номер паллета);
--                 Начинаем новый паллет;
--            Иначе 
--            у коробок из заказа переносим в текущий паллет.
--                  если к=0 тогда
--                  конец если;
--            конец если;
--      конец цикла;
--  Конец по всем строкам
end loop;

--фиксируем версию разбиения
--возвращаем количество паллет.
 

  return 0;
end;




/*
CREATE TABLE RABAEV.RRL_ORDER_ROWS
(
  ID                     INTEGER,
  ORDER_ID               INTEGER                NOT NULL,
  ARTICUL                VARCHAR2(15 BYTE)      NOT NULL,
  SHORTNAME              VARCHAR2(255 BYTE),
  EI                     VARCHAR2(3 BYTE),
  ORDER_WEIGHT           NUMBER,
  QUANTITY               NUMBER                 NOT NULL,
  SORTFIELD              INTEGER,
  WARE_ID                INTEGER                NOT NULL,
  PACK_COUNT             INTEGER,
  ORIGINAL_QUANTITY      NUMBER                 DEFAULT 0,
  ORIGINAL_ORDER_WEIGHT  NUMBER                 DEFAULT 0,
  CONDITION              INTEGER
)
*/
/*
 ORD_NUMBER   VARCHAR2(50 BYTE)                NOT NULL,
  CREATE_DATE  DATE                             NOT NULL,
  WARE_ID      INTEGER                          NOT NULL,
  ADDR         VARCHAR2(255 BYTE),
  STATE        VARCHAR2(50 BYTE),
  ORDDATE      DATE,
  USER_ID  
*/
-- СОЗДАНИЕ ЗАКАЗА ИЗ СТ 
function create_order_from_spallets( st_numb varchar2 , user_id1 varchar2 ) return int is
  ret1 int;
  CREATE_DATE1  DATE  ;
  WARE_ID1      INTEGER ;
  ADDR1         VARCHAR2(255 BYTE);
  STATE1        VARCHAR2(50 BYTE);
  ORDDATE1      DATE;
  ord_id int;

 cursor sss is 
      select EI, max( TARESIZE ) TARESIZE, max( TAREWEIGHT ) TAREWEIGHT, 
      sum( ORIGINAL_ORDER_WEIGHT ) ORIGINAL_ORDER_WEIGHT, sum( ORIGINAL_QUANTITY ) ORIGINAL_QUANTITY,
      sum( PACK_COUNT ) PACK_COUNT, sum( QUANTITY  ) QUANTITY, sum(ORDER_WEIGHT) ORDER_WEIGHT,
      ARTICUL , SORTFIELD , PAL.WARE_ID , SHORTNAME
      from  RRL_SBORKA_PALLET_ROWS RR , RRL_SBORKA_PALLETS PAL
     where  RR.PALLET_UID = PAL.Pallet_Uid and PAL.ST_NUMBER = st_numb 
group by EI,        PACK_COUNT , QUANTITY , ORDER_WEIGHT ,
      ARTICUL , SORTFIELD , PAL.WARE_ID , SHORTNAME
order by SORTFIELD;

begin
  
  select RRL_ORDERS_SQ.NEXTVAL into  ord_id from dual;
  delete from RABAEV.RRL_ORDERS where ORD_NUMBER= st_numb; -- Строки удалятся каскадно.
  -- Создаем шапку
  
  select PAL.CREATE_DATE , PAL.WARE_ID , PAL.ADDR , PAL.State , PAL.CREATE_DATE  into
   CREATE_DATE1 , WARE_ID1 ,ADDR1 ,STATE1  , ORDDATE1 
   from RRL_SBORKA_PALLETS PAL where  PAl.St_Number=st_numb and rownum=1;
   
   
  insert into  RABAEV.RRL_ORDERS (ID, CREATE_DATE ,WARE_ID ,ADDR ,STATE ,ORDDATE , USER_ID , ORD_NUMBER) 
  values( ord_id , CREATE_DATE1,WARE_ID1 ,ADDR1 ,STATE1  , ORDDATE1, user_id1 , st_numb );
  
  
  for s in sss  loop
  
  
  insert into  RRL_ORDER_ROWS 
  (
    ORDER_ID                ,
    ARTICUL                 ,
    SHORTNAME               ,
    EI                      ,
    ORDER_WEIGHT            ,
    QUANTITY                ,
    SORTFIELD               ,
    WARE_ID                 ,
    PACK_COUNT              ,
    ORIGINAL_QUANTITY       ,
    ORIGINAL_ORDER_WEIGHT   ,
    CONDITION   ,
    TARESIZE  ,
    TAREWEIGHT
  ) values (
   ord_id,
    s.ARTICUL                 ,
    s.SHORTNAME               ,
    s.EI                      ,
    s.ORDER_WEIGHT            ,
    s.QUANTITY                ,
    s.SORTFIELD               ,
    s.WARE_ID                 ,
    s.PACK_COUNT              ,
    s.ORIGINAL_QUANTITY       ,
    s.ORIGINAL_ORDER_WEIGHT   ,
    0  ,
    s.TARESIZE  ,
    s.TAREWEIGHT
  );
  end loop;  
  -- Создаем строки - копируем из  RRL_SBORKA_PALLET_ROWS в   RABAEV.RRL_ORDER_ROWS  
  return ord_id;
end;



/*


FUNCTION RABAEV.RRL_GIVE_NEXT_OPALLET_NUMBER
(
    PREV_PALLET_ID  varchar2 ,
    USER_ID1        varchar2
 )
 -- СОЗДАЕТ ЕЩЕ 1 ПАЛЛЕТ ДЛЯ СТ, ПАЛЛЕТ КОТОРОГО ПЕРЕДАН 
RETURN varchar2 IS 

    tmpVar varchar2(50);
    ret int;
    ADDR1 varchar2(255) ;
    PALLET_NUMBER1 int;
    PALLET_UID1     VARCHAR2 (100);
    STATE1    VARCHAR2(100) ;
    STDATE1 Date;
    ware_id1 int;
    NAPR1 varchar2(255);
    id2 int;
BEGIN


  ret:=0;
  select PP.ST_NUMBER , ADDR , STATE , STDATE , ware_id , NAPR into tmpVar , ADDR1 , STATE1 , STDATE1 , ware_id1 , NAPR1 
    from RRL_SBORKA_PALLETS PP where PP.PALLET_UID=PREV_PALLET_ID;
  select (max(PALLET_NUMBER )+1) into  PALLET_NUMBER1  from RRL_SBORKA_PALLETS PP where  PP.ST_NUMBER = tmpVar ;

  PALLET_UID1:= Concat( 'OP_' , Concat( Concat( tmpVar , '_'  ) ,  PALLET_NUMBER1  ) );


  id2 := RABAEV.RRL_SBORKA_PALLETS_ADD2 (
      tmpVar,
      ADDR1 ,
      PALLET_NUMBER1  ,
      PALLET_UID1      ,
      STATE1     ,
      STDATE1  ,
      NAPR1  ,
      USER_ID1  ,
      ware_id1 );
RETURN PALLET_UID1;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN       RETURN '';
     WHEN OTHERS THEN       RAISE;
END RRL_GIVE_NEXT_OPALLET_NUMBER;



*/



begin
  -- Initialization
  null;
end compl;
/

prompt
prompt Creating package body DOCK_PLANNING
prompt ===================================
prompt
create or replace package body rabaev.DOCK_PLANNING is

 
  function IS_AUTO_PLAN_DOCK(  TT_ID int) return int is
      AUTO_PLAN_DOCK1 int;   
  begin
    
    select max( WR.AUTO_PLAN_DOCK ) AUTO_PLAN_DOCK into AUTO_PLAN_DOCK1 from RRL_SBORKA_PALLETS PAL , RRL_WARES WR
    where PAL.Transtask_Id=TT_ID and WR.ID=ware_id ;
           return AUTO_PLAN_DOCK1;
           
  exception when no_data_found then return 0;
     when others then return 0; 
  end;

begin
 null;
end DOCK_PLANNING;
/

prompt
prompt Creating package body GOODS_TO_PICK
prompt ===================================
prompt
create or replace package body rabaev.GOODS_TO_PICK is

function add_summary_task( ware_id1 int ) return int
is
begin
    select RRL_SUMMARY_PICK_LIST_SQ.Nextval into id1 from dual;
    insert into  RABAEV.RRL_SUMMARY_PICK_LIST 
    (ID ,CREATEDATE , CONDITION , ware_id) 
    values  
    ( id1  , systimestamp  , 0 , ware_id1 );
return id1;
end;



-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int
is
tmp1 int;
begin
   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;
 return 1;
 exception when no_data_found then return 0;
end;

-- СОЗДАНИЕ СУММАРНОГО СБОРОЧНОГО ЛИСТА 
function add_pallet_2_summary_task2(  PUID varchar2  ) return int
is
tmp1 int;
wid1 int;
summary_task_id1 int;
begin

   select ware_id into wid1 from   RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID;
   summary_task_id1:= get_opened_summary_task( wid1 );

   select condition into tmp1 from  RABAEV.RRL_SUMMARY_PICK_LIST 
   where id=summary_task_id1 and condition=0;
   update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 
   where PALLET_UID=PUID and summary_task_id  is null;

   select PAL.SUMMARY_TASK_ID into summary_task_id1 from RRL_SBORKA_PALLETS PAL where PAL.PALLET_UID = PUID ;
   return summary_task_id1;
   
 exception when no_data_found then return 0;
end;


 -- ПОЛУЧИТЬ ПЕРВЫЙ СОЗДАННЫЙ И НЕЗАВЕРШЕННЫЙ СУММАРНЫЙ СБОРОЧНЫЙ ЛИСТ 
function get_opened_summary_task(ware_id1 int) return int
is
begin

    begin 
        select  max(ID) into id1 from RABAEV.RRL_SUMMARY_PICK_LIST 
        where condition=0 and ware_id=ware_id1 order by CREATEDATE desc  ;
        if(id1 is null) then
               return add_summary_task( ware_id1  );
        end if;
        return id1;
    exception 
        when no_data_found then  return add_summary_task( ware_id1  );
        when others then  return add_summary_task( ware_id1  );
    end ;
    return add_summary_task( ware_id1  );
end;

-- МЕРА БЛИЗОСТИ ПРИ ПОДБОРЕ ПАЛЛЕТЫ В ХРАНЕНИИ
-- Паллеты выбираются в порядке Срока годности и Близости к месту сборки.
-- Близость к месту сборки = Мера. =  x +z*100.
function distance_2_pick( CELL1 varchar2 , ware_id1 int ) return number is
x1 number  ;
y1 number ;
z1 number;
Y_VISOTA1 number;
begin
   select x,y,z , Y_VISOTA into x1,y1,z1 , Y_VISOTA1 from RRL_CELLS CL 
          where CELL=CELL1 and CL.WARE_ID=ware_id1;
  if(Y_VISOTA1 is null) then 
               Y_VISOTA1:=y1;
  end if;

  if z1 is null then z1:=0;
  end if; 
return x1+Y_VISOTA1*10+Z1;
 exception 
  when no_data_found then  return 100;
    when others then return 100;
end;


function update_wt_row( summary_task_id1 int , 
       articul1 varchar2 , QUANTITY1 number , QUANTITY_PLANNED1 number ,
       QUANTITY_COMPLETE1 number  ) return int 
is
cond1 int;
id1 int;
begin
    select id into id1 from RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;
    update RRL_SUMMARY_PICK_LIST_ROWS set 
           QUANTITY= QUANTITY1, QUANTITY_COMPLETE=QUANTITY_COMPLETE1 , 
           QUANTITY_PLANNED=QUANTITY_PLANNED1 , condition=cond1
    where
           ARTICUL = articul1 and SPL_ID = summary_task_id1;

  return id1;
exception
  when no_data_found then   
  begin
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;
  end;
  when others then   
  begin
    
    delete from RABAEV.RRL_SUMMARY_PICK_LIST_ROWS where ARTICUL = articul1 and SPL_ID = summary_task_id1;  
    insert into RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
    (ARTICUL , SPL_ID , QUANTITY , QUANTITY_COMPLETE , QUANTITY_PLANNED , CONDITION )
     values ( articul1 , summary_task_id1 , QUANTITY1 , QUANTITY_COMPLETE1 , QUANTITY_PLANNED1  ,  cond1 );
    return 1;

  end;    
  
end update_wt_row;



-- СОЗДАТЬ ЗАДАЧИ ДЛЯ ВОДИТЕЛЕЙ   РИЧТРАКА 
/* на основании номера ССЛ (Суммарного сборочного листа) выбираем 
строки паллет, привязанных к этому ССЛ. 
Артикулы упорядочиваем в порядке сборки
*/
 
function delete_wtasks( summary_task_id1 int ) return int is
begin
  
delete from RABAEV.RRL_SUMMARY_PICK_LIST where ID = summary_task_id1;
return 0;
end;

function create_wtasks( summary_task_id1 int ) return int is
   ware_id2 int;
   articul3 varchar2(50);
   skolko_nado number;
   count2 number;
   tmp1 int ;
   
   flag_last_pal1 int;
   flag_partial1 int;
   cell_otb varchar2(50);
skolko_pologeno number;
   
-- КУРСОР СУММАРНЫЙ ЛИСТ .       
  cursor sss is
  select ARTICUL , Q , SEQ , SEQ_GROUP from (
  select ARTICUL , Q , compl.show_sq(ARTICUL , ware_id2) SEQ , 
   compl.show_sq_gr(ARTICUL , ware_id2) SEQ_GROUP
   from (
       select RS.ARTICUL , sum( RS.QUANTITY ) Q 
       from RABAEV.RRL_SBORKA_PALLETS PAL , 
       RABAEV.RRL_SBORKA_PALLET_ROWS RS , RRL_ARTICULS ART
       where PAL.SUMMARY_TASK_ID = summary_task_id1 and
       PAL.PALLET_UID=RS.PALLET_UID and RS.QUANTITY >0
       and ART.ACTICUL = RS.ARTICUL and ART.CELL='E-6-6-6-6'
        group by RS.ARTICUL
       ) )
   order by SEQ_GROUP ,SEQ 
   ; -- order by порядок сборки 


-- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ  
  cursor ostat is
  select RM.REMAIN , RM.CELL , RM.UID_POLETA , 
  distance_2_pick(RM.CELL , ware_id2 ) dist  , PL.EXPIRY_DATE
    from RRL_REMAINS RM , RRL_CELLS CL , RRL_PALLETS PL 
    where CL.WARE_ID=ware_id2 and RM.CELL=CL.CELL
   and CL.BLOCKED_FOR_POPOLNENIE=0 and CL.BLOCKED_FOR_REMAINS=0
   and PL.UID_PALLET=RM.UID_POLETA and PL.ARTICUL=articul3 and RM.REMAIN>0
  order by EXPIRY_DATE , dist  ; -- КУРСОР С ОСТАТКАМИ НА СКЛАДЕ ВО ВСЕХ ДОСТУПНЫХ ЯЧЕЙКАХ   



begin
  cell_otb:='';
  DBMS_OUTPUT.put_line( 'Начало create_wtasks ');
select condition , WARE_ID into tmp , ware_id2 
       from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1;

    if(tmp<>0) then
     return 0;    
    end if;
update RABAEV.RRL_SUMMARY_PICK_LIST set condition =1 where id=summary_task_id1; 
delete from RABAEV.RRL_WT where parent_id = summary_task_id1 and type1='WR1';

    for ss in sss loop -- По всем строкам ссумарного сборочного листа (ССЛ)
        -- DBMS_OUTPUT.put_line(  ss.ARTICUL ); 
         articul3:= ss.ARTICUL ; 
         cell_otb:='';
         begin
                    select CELL into cell_otb from rrl_articuls where acticul= articul3;
         exception
           when no_data_found then cell_otb:='NO';
         end;
         skolko_nado := ss.q;
         skolko_pologeno:=0;
         -- для каждой строки Артикул, количество подбираем 
         -- необходимое количество товара на паллетах в Хранении
         --    Берем его как максимально подходящий по срокам, наиболее близко-стоящий
         for ost1 in ostat loop

              flag_last_pal1 :=0;
              flag_partial1  :=0;
   
         if(skolko_nado>0) then
                  count2 :=  min2 ( ost1.Remain , skolko_nado );
                  -- если ost1.Remain > skolko_nado ставим метку последнего неполного паллета 
                  if  ost1.Remain > skolko_nado then 
                       flag_partial1:=1;
                  end if;
                  
                  skolko_nado:= skolko_nado - count2 ;
                  DBMS_OUTPUT.put_line( 
                   concat( concat( concat( concat( ' ARTICUL=' , ss.ARTICUL )  ,
                   concat( ' CELL =' , ost1.CELL ) ) , concat(  ' dist=' , to_char(ost1.dist) ) ) ,
                   concat (concat( ' UID_POLETA =' , ost1.UID_POLETA ) ,
                   concat( ' EXPIRY_DATE =' , to_char( ost1.EXPIRY_DATE ) ) )   
                   ) ) ;
                   -- ДОБАВЛЯЕМ ДАННЫЙ ПАЛЛЕТ НА СПУСК ВНИЗ. 
                  
                  -- если  skolko_nado=0 ставим метку последнего паллета
                  if(skolko_nado=0) then
                  flag_last_pal1 :=1;
                  end if;
                  
                  insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   
                    --PLAN_START_TIME ,PLAN_END_TIME , FACT_START_TIME ,FACT_END_TIME ,
                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_partial ,
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  ost1.UID_POLETA  , ost1.cell , cell_otb , count2 , 
                  --null , null ,null , null 
                  null , 0 , summary_task_id1 , flag_partial1 , flag_last_pal1 );
                  skolko_pologeno := skolko_pologeno +count2;
                    

                  
                  
                  
                  
                  -- КОНЕЦ СОЗДАНИЯ WTASK.
         end if;
         end loop;
         
         -- НЕ ХВАТАЕТ 
         if( skolko_nado>0 ) then
          DBMS_OUTPUT.put_line( concat( concat( 'для артикула ' , ss.articul ) , concat( ' не хватает ' ,  skolko_nado ) ) );
         
          insert into RABAEV.RRL_WT
                  (  
                  ORDER1 , 
                  articul ,
                    TYPE1 , --{ WR – Задача ричтраку на пополнение WR1 – Задача ричтраку на пополнение зоны динамического подбора }
                    PUID  , FROM1 , TO1   , COUNT1 ,   
                    
                    WORKER  , -- РИЧТРАК 
                    CONDTION   ,  -- Состояние. 0-не назначена 1-назначена 2-начата 3-закончена.
                    PARENT_ID , -- Ссылка на создателя.  summary_task_id
                    flag_last_pal
                  ) values ( 
                  ss.seq ,
                  articul3 ,
                  'WR1' ,  'NULL'  , 'INVENT' , cell_otb , skolko_nado ,  
                  null , 0 , summary_task_id1 , 1 );
         
         end if;
         -- НЕ ХВАТАЕТ 
         
         
         tmp1:=update_wt_row( summary_task_id1  , 
                        ss.articul  , ss.q ,  skolko_pologeno ,
                        0  );
         
    end loop;
--    Закрываем ССЛ (condition=1)
     DBMS_OUTPUT.put_line( 'Конец create_wtasks ');
    update  RABAEV.RRL_SUMMARY_PICK_LIST  set condition=2 where id=summary_task_id1;
return 1;
end ;

-- Функции стратегии размещения товара по ячейкам. 

begin
  -- Initialization
 null;
end GOODS_TO_PICK;
/

prompt
prompt Creating package body REVIZION
prompt ==============================
prompt
create or replace package body rabaev.REVIZION is

 

 --- СОЗДАНИЕ РЕВИЗИИ ПО СКЛАДУ
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int is
id1 int;    

  begin

      insert into RABAEV.RRL_REVIZION
      (
        WARE_ID     ,
        CREATE_DATE  ,
        CONDITION   ,
        USER_ID    
      )values (  ware_id1, sysdate  , 0 , user_id1  ) ;
      select RABAEV.RRL_REVISION_SQ.Currval into id1 from dual;

    return id1;
  end;

-- Обнуляет остатки данного артикула в данной ячейке
function clear_cell( cell1 varchar2 , puid varchar2   ) return int is  
begin

delete from rrl_remains rr where   rr.cell=cell1 and rr.uid_poleta= puid;
return  1;
exception
  when others then null;
end;

-- Обнуляет остатки данного артикула в данной ячейке
function clear_cell2( cell1 varchar2     ) return int is  
begin

delete from rrl_remains rr where   rr.cell=cell1  ;
return  1;
exception
  when others then null;
end;

-- ДОБАВЛЕНИЕ СТРОКИ ДЛЯ РЕВИЗИИ ПО СКЛАДУ 
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    
begin
  delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  and CELL= cell1;
  insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE )
   values ( revision_id1 , cell1 , sysdate  );
  select RRL_REVISION_ROW_SQ.Currval  into id1 from dual;
  return id1;
end;

function revision_cell_kor( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1024);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'ревизия закрыта';
         end if;
         exception 
           when no_data_found then return 'ревизии нет';
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ РЕВИЗИИ --- 
  
      begin  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- ПРОВЕРЯЕМ СОСТОЯНИЕ СТРОКИ --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL_KOR( CELL1  ,    count2 ,    user_id3 )  ;
    rem5 :=concat( concat( ' кор=' , to_char(count2) ) , concat( 'кор. время=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;


begin
null;
end REVIZION;
/

prompt
prompt Creating trigger ORDER_MOV_HIST_TRG
prompt ===================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.ORDER_MOV_HIST_TRG
BEFORE INSERT 
ON RABAEV.ORDER_MOV_HIST FOR EACH ROW
DECLARE
BEGIN

if :New.ID is null then

  SELECT RABAEV.ORDER_MOV_HIST_ID.NEXTVAL
    INTO :New.ID 
        FROM dual;
        
end if;
    
 

END;
/

prompt
prompt Creating trigger RRL_CROSS_DOCKING_ZONES_TRG
prompt ============================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_CROSS_DOCKING_ZONES_TRG
BEFORE INSERT
ON RABAEV.RRL_CROSS_DOCKING_ZONES 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      
  
if :New.ID is null then
  select RRL_CROSS_DOCKING_ZONES_SQ.NEXTVAL into  :New.ID from dual;
end if;
  
END;
/

prompt
prompt Creating trigger RRL_ORDER_PALLET_ROWS_TRG
prompt ==========================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_ORDER_PALLET_ROWS_TRG
BEFORE INSERT
ON RABAEV.RRL_ORDER_PALLET_ROWS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      
  
  if :New.ID is null then
  select RRL_ORDER_PALLET_ROWS_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;
/

prompt
prompt Creating trigger RRL_ORDER_ROWS_TRG
prompt ===================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_ORDER_ROWS_TRG
BEFORE INSERT
ON RABAEV.RRL_ORDER_ROWS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)
  
if :New.ID is null then
  select RRL_SUMMARY_PICK_LIST_ROWS_SQ.NEXTVAL into  :New.ID from dual;
end if;
 
END;
/

prompt
prompt Creating trigger RRL_ORDERS_DELETE
prompt ==================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_ORDERS_DELETE
BEFORE DELETE
ON RABAEV.RRL_ORDERS 
REFERENCING NEW AS NEW OLD AS OLD
FOR EACH ROW
BEGIN


delete from  RABAEV.RRL_ORDER_ROWS where ORDER_ID=  :Old.ID;
delete from  RABAEV.RRL_ORDER_PALLET_ROWS   where ORDER_ID=  :Old.ID;


  -- your code here 
  -- (Trigger template "Default" could not be loaded.) 
END;
/

prompt
prompt Creating trigger RRL_ORDERS_TRG
prompt ===============================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_ORDERS_TRG
BEFORE INSERT
ON RABAEV.RRL_ORDERS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)       
if :New.ID is null then
  select RRL_ORDERS_SQ.NEXTVAL into  :New.ID from dual;
end if;
  
END;
/

prompt
prompt Creating trigger RRL_PRIHOD_NAKLAD_TRG
prompt ======================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_PRIHOD_NAKLAD_TRG
BEFORE INSERT 
ON RABAEV.RRL_PRIHOD_NAKLAD FOR EACH ROW
DECLARE
BEGIN


if :New.ID is null then
  SELECT RRL_PRIH_ORD_ID.NEXTVAL
    INTO :New.ID
    FROM dual;
    end if;
    



END;
/

prompt
prompt Creating trigger RRL_REVISION_ROW_TRG
prompt =====================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_REVISION_ROW_TRG
BEFORE INSERT
ON RABAEV.RRL_REVISION_ROW 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      
  
  
  if :New.ID is null then
  select RRL_REVISION_ROW_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;
/

prompt
prompt Creating trigger RRL_REVIZION_TRG
prompt =================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_REVIZION_TRG
BEFORE INSERT
ON RABAEV.RRL_REVIZION 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)      
  
if :New.ID is null then
  select RRL_REVISION_SQ.NEXTVAL into  :New.ID from dual;
end if;

END;
/

prompt
prompt Creating trigger RRL_SBORKA_PALLETS_DEL
prompt =======================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_SBORKA_PALLETS_DEL
BEFORE DELETE
ON RABAEV.RRL_SBORKA_PALLETS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN


  
  insert into    RABAEV.RRL_SBORKA_PALLETS_HISTORY
(
  
  PALLET_UID  ,
  USER_ID     ,
  ZONE        ,
  EVENT       ,
  TIME1       
  ) 
  values( 
  :Old.PALLET_UID , 
  :Old.USER_ID_LAST_UPD , 
  'ORA' , 
  'DEL' , 
  systimestamp  );


  
  
END;
/

prompt
prompt Creating trigger RRL_SBORKA_PALLETS_HISTORY_TRG
prompt ===============================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_SBORKA_PALLETS_HISTORY_TRG
BEFORE INSERT 
ON RABAEV.RRL_SBORKA_PALLETS_HISTORY FOR EACH ROW
DECLARE
BEGIN

if :New.ID is null then

  SELECT  RABAEV.RRL_SBORKA_PALLETS_HISTSQ.NEXTVAL 
    INTO   :New.ID 
        FROM dual;
        
        
    SELECT  SYSDATE 
    INTO   :New.TIME1 
        FROM dual;      
        
end if;
    
 

END;
/

prompt
prompt Creating trigger RRL_SBORKA_PALLETS_TRG
prompt =======================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_SBORKA_PALLETS_TRG
BEFORE INSERT 
ON RABAEV.RRL_SBORKA_PALLETS FOR EACH ROW
DECLARE
BEGIN


if :New.ID is null then
  SELECT RRL_SBORKA_PALLETS_SQ.NEXTVAL
    INTO :New.ID
    FROM dual;
    end if;
 

  SELECT SYSTIMESTAMP
    INTO :New.CREATE_DATE
    FROM dual;


END;
/

prompt
prompt Creating trigger RRL_SUMMARY_PICK_LIST_DELETE
prompt =============================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_SUMMARY_PICK_LIST_DELETE
BEFORE DELETE
ON RABAEV.RRL_SUMMARY_PICK_LIST 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
/* Formatted on 2011/06/21 17:54 (Formatter Plus v4.8.8) */
BEGIN
   -- your code here
   -- (Trigger template "Default" could not be loaded.)
   UPDATE rrl_sborka_pallets ppp
      SET ppp.summary_task_id = NULL
    WHERE summary_task_id = :OLD.ID;

   DELETE FROM rabaev.rrl_summary_pick_list_rows rws
         WHERE rws.spl_id = :OLD.ID;

   DELETE FROM rabaev.rrl_wt
         WHERE parent_id = :OLD.ID;
END;
/

prompt
prompt Creating trigger RRL_SUMMARY_PICK_LIST_ROWS_TRG
prompt ===============================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_SUMMARY_PICK_LIST_ROWS_TRG
BEFORE INSERT
ON RABAEV.RRL_SUMMARY_PICK_LIST_ROWS 
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)           
  
  if :New.ID is null then
  select RRL_SUMMARY_PICK_LIST_ROWS_SQ.NEXTVAL into  :New.ID from dual;
end if;
  
END;
/

prompt
prompt Creating trigger RRL_T_EVENT_UPDATE_REMAIN
prompt ==========================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_t_event_update_remain
  AFTER INSERT
  ON RABAEV.RRL_EVENTS   for each row
declare
  vRemain number;
  procedure UpRemain
    -- Процедура увеличивает остаток в ячейке :new.cell_to на :new.count_event
  is

  begin
    -- смотрим, что лежит в новой ячейке
    -- проверяем только наличие по текущей полете... Хорошо было бы проверить эту ячейку на
    -- наличие в ней чего-нить от других полет и сделать какие-нибудь выводы ...
    select sum(remain) into vRemain
    from RRL_remains
    where cell = :new.cell_to
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then
      -- в ячейке таких полет не обнаружено. добавляем запись
     insert into RRL_remains (uid_poleta, cell, remain , othod_nakl_id , TIME_OF_LAST_UPDATE ) 
     values (:new.uid_poleta, :new.cell_to, :new.count_event , :new.othod_nakl_id , SYSTIMESTAMP );
    else
      -- есть какой-то остаток
      update RRL_remains
      set remain = remain+:new.count_event , othod_nakl_id =  :new.othod_nakl_id , TIME_OF_LAST_UPDATE = SYSTIMESTAMP 
      where cell = :new.cell_to
      and uid_poleta = :new.uid_poleta;
    end if;   
    
  end;


  
  
  
  
  procedure DownRemain
    -- Процедура уменьшает остаток в ячейке :new.cell_from на :new.count_event
  is
  begin
    select sum(remain) into vRemain -- на всякий случай сделали сумму
    from RRL_remains
    where cell = :new.cell_from
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then 
      -- странно, однако, в ячейке не та полета, или ячейка совсем пустая...
      -- запишем отрицательный остаток 
      insert into RRL_remains(uid_poleta, cell, remain ,  TIME_OF_LAST_UPDATE  ) 
      values (:new.uid_poleta , :new.cell_from, -:new.count_event , SYSTIMESTAMP );
    elsif vRemain = :new.count_event then
      -- из ячейки все будет выбрано подчистую, она останется пустая.
      -- поэтому наверно остаток можно удалить
      delete from RRL_remains
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    else
      -- остаток какой-то не нулевой остается (может быть и отрицательный)
      -- проапдейтим остаток
      update RRL_remains
      set remain = remain-:new.count_event , TIME_OF_LAST_UPDATE=SYSTIMESTAMP
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    end if;   
  end;  

begin

    if(:new.count_event<>0) then
      if :new.type_event = 1 then  
        -- если событие это приемка
        -- добавляем запись в таблицу остатков
        UpRemain;
      elsif :new.type_event = 2 then  
        -- если событие это перемещение
        -- меняем данные в таблице остатков
        DownRemain;
        UpRemain;
      elsif :new.type_event = 3 then  
        -- если событие это отбор
        DownRemain;
      end if;
    end if;
  
end;
/

prompt
prompt Creating trigger RRL_TR_VEHICLE_TRG
prompt ===================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_TR_VEHICLE_TRG
BEFORE INSERT 
ON RABAEV.RRL_TR_VEHICLE FOR EACH ROW
DECLARE
BEGIN

    if :New.ID is null then

      SELECT  RABAEV.RRL_TR_VEHICLE_SQ.NEXTVAL 
        INTO   :New.ID 
            FROM dual;           
    end if;
        

END;
/

prompt
prompt Creating trigger RRL_TR_VODITEL_TRG
prompt ===================================
prompt
CREATE OR REPLACE TRIGGER RABAEV.RRL_TR_VODITEL_TRG
BEFORE INSERT 
ON RABAEV.RRL_TR_VODITEL FOR EACH ROW
DECLARE
BEGIN

    if :New.ID is null then

      SELECT  RABAEV.RRL_TR_VODITEL_SQ.NEXTVAL 
        INTO   :New.ID 
            FROM dual;           
    end if;
        

END;
/

prompt
prompt Creating trigger RRL_WT_TRG
prompt ===========================
prompt
create or replace trigger rabaev.RRL_WT_TRG
  before insert on rrl_wt  
  for each row
declare
  -- local variables here
begin
  
if :New.ID is null then
  select RRL_WT_SQ.NEXTVAL into  :New.ID from dual;
end if;
  
  
  
end RRL_WT_TRG;
/

prompt
prompt Creating trigger SFERA_EAN_TRG
prompt ==============================
prompt
CREATE OR REPLACE TRIGGER RABAEV.SFERA_EAN_TRG
BEFORE INSERT 
ON RABAEV.SFERA_EAN FOR EACH ROW
DECLARE
BEGIN


if :New.УИД is null then
  SELECT SFERA_EAN_ID.NEXTVAL
    INTO :New.УИД
    FROM dual;
    end if;
    



END;
/


spool off
