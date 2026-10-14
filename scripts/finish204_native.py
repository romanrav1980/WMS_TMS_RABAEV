from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_final_scale");out={}
p=f/"002_archive.sql";s=p.read_text(encoding="utf-8")
s=s.replace("or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID or tare.TYPE_VERSION!=typ.TYPE_VERSION","or tare.PALLET_TYPE_ID!=ct.PALLET_TYPE_ID")
s=s.replace("or tare.DEVICE_ID!=p_device.DEVICE_ID or tare.DEVICE_POLICY_VERSION!=p_device.POLICY_VERSION\n    or tare.CALIBRATION_REF!=p_device.CALIBRATION_REF or tare.MEASURED_AT>measured","or tare.DEVICE_ID!=p_device.DEVICE_ID or tare.WARE_ID!=p_device.WARE_ID or tare.POST_CELL!=p_device.POST_CELL\n    or tare.DEVICE_MODE!=p_device.DEVICE_MODE or tare.MEASUREMENT_BASIS!='GROSS' or tare.MEASURED_AT>measured")
out[str(p)]=s;out[str(f/"002_body.sql")]=s
p=f/"003_admission.sql";s=p.read_text(encoding="utf-8")
needle="create or replace package body RRL_CASE_SCALE_ADMISSION as"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
 procedure assert_empty_tare(p_task number)is
  required number;picked number;ware number;type_id number;carrier varchar2(150);n number;
 begin
  select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end,c.PICKED_QTY,c.WARE_ID,c.PALLET_TYPE_ID,c.SSCC
   into required,picked,ware,type_id,carrier from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=p_task;
  if required=0 or nvl(picked,0)>0 then return;end if;
  select count(*)into n from(select 1 from RRL_WH_SCALE_CAPTURE s join RRL_WH_SCALE_DEVICE v on v.DEVICE_ID=s.DEVICE_ID
   where s.CASE_PICK_TASK_ID=p_task and s.CAPTURE_PURPOSE='EMPTY_TARE' and s.WARE_ID=ware and s.CARRIER_IDENTIFIER=carrier
    and s.PALLET_TYPE_ID=type_id and s.MEASURED_AT>=systimestamp-numtodsinterval(24,'HOUR') and s.MEASURED_AT<=systimestamp+numtodsinterval(2,'SECOND')
    and v.WARE_ID=s.WARE_ID and v.POST_CELL=s.POST_CELL and v.DEVICE_MODE=s.DEVICE_MODE and v.ACTIVE_FLAG=1)where rownum=1;
  if n!=1 then raise_application_error(-20886,'SMALL_BOX_MEASURED_EMPTY_TARE_BEFORE_PICK_REQUIRED');end if;
 end;
""")
needle="  if not m.has('warehouse_scale_capture')then return;end if;"
# The second occurrence belongs to claim_capture; it need not add a redundant read.
assert s.count(needle)==2
s=s.replace(needle,"  assert_empty_tare(d.get_object('source').get_number('case_task_id'));\n"+needle,1)
out[str(p)]=s
out[str(f/"004_finish.sql")]="@@002_archive.sql\n@@003_admission.sql\n"
p=Path("wiki/database/nicora_ni042_final_scale_design_20261011.md");s=p.read_text(encoding="utf-8")
s=s.replace("Связь с исходным EMPTY_TARE проверяет коробку/тип/версию типа/устройство и актуальную калибровку.","Связь с исходным EMPTY_TARE проверяет коробку/тип/устройство/пост/склад/режим и измерение в пределах24ч. Калибровка проверена в момент архивирования каждого пакета; последующая смена названия типа или действующей калибровки не изменяет исторически измеренную физическую массу. Версия типа/политики остаётся в архиве. Новое брутто требует актуальной калибровки.")
s+="\nNative CASE до первого отбора требует архив EMPTY_TARE того же SSCC/склада/типа/поста и режима. Это предотвращает наполнение коробки, чья тара ещё не измерена. Показание само не проводит товар.\n";out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
