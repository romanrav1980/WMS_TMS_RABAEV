create table RRL_TRADE_TOPUP_ADOPTION(
 RESERVATION_ID number not null,PROPOSAL_ID number not null,HOLD_RESERVATION_ID number not null,PICK_WAVE_ID number not null,
 PICK_TASK_ID number not null,PICK_PLAN_LINE_ID number not null,BASE_QTY number not null,OPERATION_ID varchar2(100)not null,
 ACTOR varchar2(50)not null,ADOPTED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_TOPUP_ADOPT_PK primary key(RESERVATION_ID),
 constraint RRL_TRADE_TOPUP_ADOPT_PROP_FK foreign key(PROPOSAL_ID)references RRL_TRADE_TOPUP_PROPOSAL(PROPOSAL_ID),
 constraint RRL_TRADE_TOPUP_ADOPT_HOLD_FK foreign key(RESERVATION_ID)references RRL_TRADE_TOPUP_HOLD(RESERVATION_ID),
 constraint RRL_TRADE_TOPUP_ADOPT_QTY check(BASE_QTY>0)
);
create index RRL_TRADE_TOPUP_ADOPT_PROP_IX on RRL_TRADE_TOPUP_ADOPTION(PROPOSAL_ID,PICK_WAVE_ID);
