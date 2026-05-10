create or replace package TOOLS is

  
  function maintain_indexes  return int  ;

end TOOLS;
/
create or replace package body TOOLS is

   

  -- Function and procedure implementations
  function maintain_indexes  return int is
  begin
     
    execute immediate 'alter index RABAEV.RRL_CELLS_PK rebuild';
    execute immediate 'alter index RABAEV.RRL_CELLS_I7  rebuild';
    execute immediate 'alter index RABAEV.RRL_CELLS_I8  rebuild';
    execute immediate 'alter index RABAEV.RRL_CELLS_I9  rebuild';
    execute immediate 'alter index RABAEV.RRL_CELLS_WARE_ID  rebuild';
    execute immediate 'alter index RABAEV.RRL_PALLETS_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_PALLETS_MI  rebuild';
    execute immediate 'alter index RABAEV.RRL_REMAINS_IND  rebuild';
    execute immediate 'alter index RABAEV.PALLET_ROW_ID_I8  rebuild';
    execute immediate 'alter index RABAEV.RRL_EVENTS_DATE_EVENT  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_SB_I   rebuild';
    execute immediate 'alter index RABAEV.RRL_EVENTS_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I_99  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I9  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_ZONE_IN  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_ZONE  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I5  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I2  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I7  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALLETS_I88  rebuild';
    execute immediate 'alter index RABAEV.RRL_PALLETS_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_PALLETS_NAKLAD  rebuild';
    execute immediate 'alter index RABAEV.RRL_PALLETS_MI  rebuild';
    execute immediate 'alter index RABAEV.RRL_TRANSPORT_TASK  rebuild'; 
    execute immediate 'alter index RABAEV.RRL_TRANSPORT_TASK_DOCK_RESERV  rebuild';
    execute immediate 'alter index RABAEV.RRL_TRANSPORT_TASK_DOCK  rebuild';
    execute immediate 'alter index RABAEV.RRL_TRANSPORT_TASK_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_PRIHOD_NAKLAD_1  rebuild';
    execute immediate 'alter index RABAEV.RRL_PRIHOD_NAKLAD_I2  rebuild';
    execute immediate 'alter index RABAEV.RRL_PRIHOD_NAKLAD_ID  rebuild';
    execute immediate 'alter index RABAEV.RRL_PRIHOD_NAKLAD_4  rebuild';
    execute immediate 'alter index RABAEV.RRL_PRIHOD_NAKLAD_I8  rebuild';
    execute immediate 'alter index RABAEV.RRL_ARTICULS_I4  rebuild';
    execute immediate 'alter index RABAEV.PALLET_MULTIPLE_I  rebuild';
    execute immediate 'alter index RABAEV.RRL_ARTICULS_PK  rebuild';
    execute immediate 'alter index RABAEV.RRL_ARTICULS_BARCODE_SHT  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALL_ROWS_PARTSI1  rebuild';
    execute immediate 'alter index RABAEV.RRL_SBORKA_PALL_ROWS_PARTSPK  rebuild';
    execute immediate 'alter index RABAEV.RRL_COMPL_SEQ_I1  rebuild';
    execute immediate 'alter index RABAEV.RRL_COMPL_SEQ_I2  rebuild'; 
    execute immediate 'alter index RABAEV.RRL_COMPL_SEQ_I3  rebuild';
    execute immediate 'alter index RABAEV.RRL_ARTICUL_MODS_I5  rebuild';
    execute immediate 'alter index RABAEV.RRL_ARTICUL_MODS_ID  rebuild';  
    execute immediate 'alter index RABAEV.ART  rebuild';

 




  
    return 1;
  end;

begin
  -- Initialization
 null;
end TOOLS;
/
