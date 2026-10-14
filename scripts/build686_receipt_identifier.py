import json,hashlib
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/domain/pallet_identifiers.py");s=p.read_text(encoding="utf-8")
s+="""


def normalize_receipt_identifier(value: object) -> str:
    from .regulatory_pallet import sscc_value
    value=normalize_incoming_sscc(value)
    if not isinstance(value,str) or not value or len(value)>50 or len(value.encode("utf-8"))>150:
        raise ValueError("Pallet identifier must fit 50 characters and 150 UTF-8 bytes")
    if not value.isprintable() or any(character.isspace() for character in value):
        raise ValueError("Pallet identifier must contain visible non-space characters")
    if len(value)==18 and value.isascii() and value.isdigit() and sscc_value(value) is None:
        raise ValueError("Invalid SSCC check digit")
    return value
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/receiving_routes.py");s=p.read_text(encoding="utf-8").replace("BaseModel, Field, field_validator, model_validator","AliasChoices, BaseModel, Field, field_validator, model_validator").replace("from ..domain.pallet_identifiers import normalize_incoming_sscc","from ..domain.pallet_identifiers import normalize_incoming_sscc, normalize_receipt_identifier")
s=s.replace('sscc: str = Field(pattern=r"^[0-9]{18}$")','sscc: str = Field(strict=True,min_length=1,max_length=50,validation_alias=AliasChoices("pallet_identifier","sscc"))')
s=s.replace("return normalize_incoming_sscc(value)","return normalize_receipt_identifier(value)",1)
anchor="class PutawayConfirmation(BaseModel):"
validator="""    @model_validator(mode="before")
    @classmethod
    def same_identifier(cls, value: object) -> object:
        if isinstance(value,dict) and "pallet_identifier" in value and "sscc" in value:
            if normalize_receipt_identifier(value["pallet_identifier"])!=normalize_receipt_identifier(value["sscc"]):
                raise ValueError("Conflicting pallet identifiers")
        return value


"""+anchor
assert anchor in s;s=s.replace(anchor,validator);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receipt_commands.py");s=p.read_text(encoding="utf-8")
s=s.replace("from ..domain.mark_identity import canonical_mark","from ..domain.mark_identity import canonical_mark\nfrom ..domain.pallet_identifiers import normalize_receipt_identifier\nfrom ..domain.regulatory_pallet import sscc_value")
start=s.index('    if not isinstance(sscc, str)');end=s.index('    cursor.execute(',start)
s=s[:start]+"""    if normalize_receipt_identifier(sscc)!=sscc:
        raise ValueError("Use the canonical pallet identifier after scanner-prefix normalization")
"""+s[end:]
s=s.replace('"pallet_identifier": payload["sscc"], "sscc": payload["sscc"],','"pallet_identifier": payload["sscc"], "sscc": sscc_value(payload["sscc"]),')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receipt_booking.py");s=p.read_text(encoding="utf-8").replace("from .receiving_marks import ReceivingMarks","from .receiving_marks import ReceivingMarks\nfrom ..domain.regulatory_pallet import sscc_value")
s=s.replace("values(:t,'PUTAWAY','SAP_RECEIPT','SAP_SUPPLY_ORDER',:n,:a,:p,:p,", "values(:t,'PUTAWAY','SAP_RECEIPT','SAP_SUPPLY_ORDER',:n,:a,:p,:reg_sscc,")
s=s.replace('"a": line[0], "p": sscc, "w": order[1]', '"a": line[0], "p": sscc, "reg_sscc":sscc_value(sscc), "w": order[1]')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.html");s=p.read_text(encoding="utf-8").replace('Идентификатор паллеты — SSCC поставки<input id="receiptSscc" maxlength="25" inputmode="numeric">','Идентификатор паллеты<input id="receiptSscc" maxlength="50" autocomplete="off">')
out[str(p)]=s
root="db/migrations/2026-10-12_ni011_internal_receipt_identifier/"
before="create or replace "+Path("tmp/684_rrl_sap_receipt_api.sql").read_text(encoding="utf-8")+"\n/\n"
native=before.replace("p_qty number,p_naklad number,p_actor varchar2) is n number;","p_qty number,p_naklad number,p_actor varchar2) is n number;v_reg_sscc varchar2(32);v_sum number:=0;")
anchor=" g_allowed:=true;"
assert anchor in native
native=native.replace(anchor,""" if p_sscc is null or length(p_sscc)>50 or lengthb(p_sscc)>150 or regexp_like(p_sscc,'[[:space:][:cntrl:]]')then raise_application_error(-20803,'Invalid physical pallet identifier');end if;
 if regexp_like(p_sscc,'^[0-9]{18}$')then
  for i in 1..17 loop v_sum:=v_sum+to_number(substr(p_sscc,i,1))*case when mod(i,2)=1 then 3 else 1 end;end loop;
  if mod(10-mod(v_sum,10),10)=to_number(substr(p_sscc,18,1))then v_reg_sscc:=p_sscc;end if;
 end if;
 g_allowed:=true;""",1).replace("values(p_sscc,p_sscc,p_articul","values(p_sscc,v_reg_sscc,p_articul")
assert "v_reg_sscc" in native
out.update({root+"000_before_sap_receipt_api.sql":before,root+"001_sap_receipt_api.sql":native,
root+"002_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-686-sap-receipt-internal-uid'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Physical SAP receipt accepts internal pallet identity; regulatory SSCC stored only with proven GS1 check digit',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",root+"apply.sql":"@001_sap_receipt_api.sql\n@002_ledger.sql\n",root+"rollback.sql":"@000_before_sap_receipt_api.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-686-sap-receipt-internal-uid';\n/\n",root+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_SAP_RECEIPT_API';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_SAP_RECEIPT_API';\n",
root+"checkpoint.json":json.dumps({"schema":"RABAEV","service":"127.0.0.1:1521/orcl","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_sha256":hashlib.sha256(native.encode()).hexdigest(),"recovery":"paired package body rollback; no table/old data/quantity writer changes"},indent=2)})
print(json.dumps(out))
