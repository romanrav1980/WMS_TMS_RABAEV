"""Isolated real financial object approval; no FINANCE recognition/outbox or stock changes."""
import sys,json,secrets
from contextlib import contextmanager
import oracledb
from uuid import uuid4
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.db import oracle_connection,rows_as_dicts
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import normalize,Command
from app.modules.finance.infrastructure.expense_catalog import set_article
from app.modules.finance.infrastructure.expense_reports import report_expense
from app.modules.finance.infrastructure.expense_decisions import decide_expense
from app.modules.finance.contracts import LogisticsCostError

class RollbackGateway:
    def __init__(self,cursor): self.cursor=cursor;self.sequence=0
    @contextmanager
    def transaction(self,label):
        self.sequence+=1;point="AF_FIXTURE_"+str(self.sequence)
        self.cursor.execute("savepoint "+point)
        try: yield self.cursor
        except Exception:
            self.cursor.execute("rollback to savepoint "+point)
            raise
    def fetch_all(self,sql,params=None):
        self.cursor.execute(sql,params or {})
        return rows_as_dicts(self.cursor)

def run(gateway):
    access=AccessMetadataService(gateway);prefix="af"+uuid4().hex[:8]
    author=prefix+"a";reviewer=prefix+"r";role=prefix+"role";expense=prefix+":expense";vehicle=2000000000+int(uuid4().hex[:7],16)
    now=datetime.now(timezone.utc);checks=[]
    def command(kind,payload):
        return access.command("admin",normalize(Command(operation_id=prefix+":"+uuid4().hex,command_type=kind,payload=payload),"ACCESS"))
    def expect_independent(call):
        try: call()
        except LogisticsCostError as error:
            assert error.code=="EXPENSE_INDEPENDENT_DECISION_REQUIRED" and error.status==403
        else: raise AssertionError("Self approval accepted")
    try:
        with gateway.transaction("finance.access.fixture")as cursor:
            for actor in (author,reviewer):
                cursor.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Finance fixture',:password,'NONE',1,0,1)",{"id":actor,"password":secrets.token_urlsafe(24)})
            cursor.execute("insert into RRL_TR_VEHICLE(ID,NUM)values(:id,:num)",{"id":vehicle,"num":prefix})
        command("ROLE_SAVE",dict(role_id=role,title="Isolated financial approval",permissions=["edit_bill_tt","expense_logist_approve","expense_finance_approve"],active=True,expected_version=0))
        for actor in (author,reviewer):
            command("ASSIGN",dict(assignment_id=prefix+actor[-1],username=actor,role_id=role,scope_kind="WAREHOUSE",scope_id="1",membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),reason="isolated finance acceptance",expected_version=0))
        set_article(gateway,prefix,"Isolated vehicle expense","VEHICLE",False,True,0,"admin")
        report_expense(gateway,expense,1,prefix,"VEHICLE",vehicle,"0.01","GEL",now.date().isoformat(),"ISOLATED_FIXTURE","temporary acceptance",author)
        expect_independent(lambda:decide_expense(gateway,prefix+":self",expense,"LOGIST","APPROVE","NONE","fixture","fixture",author))
        saved=decide_expense(gateway,prefix+":logist",expense,"LOGIST","APPROVE","NONE","fixture","fixture",reviewer)
        assert saved["status"]=="LOGIST_APPROVED"
        assert decide_expense(gateway,prefix+":logist",expense,"LOGIST","APPROVE","NONE","fixture","fixture",reviewer)==saved
        expect_independent(lambda:decide_expense(gateway,prefix+":finance-self",expense,"FINANCE","APPROVE","NONE","fixture","fixture",reviewer))
        expect_independent(lambda:decide_expense(gateway,prefix+":finance-author",expense,"FINANCE","APPROVE","NONE","fixture","fixture",author))
        data=gateway.fetch_all("select RRL_ACCESS_API.allowed(:actor,'create_tt_price','WAREHOUSE','1') RATE_ALLOWED,RRL_ACCESS_API.allowed(:actor,'expense_finance_approve','WAREHOUSE','2') FOREIGN_ALLOWED from dual",{"actor":reviewer})[0]
        assert data["rate_allowed"]==0 and data["foreign_allowed"]==0
        checks=["author_cannot_approve_own_expense","separate_approver_with_narrow_scoped_permission","saved_receipt_replay","logist_cannot_finance_same_expense","author_cannot_finance","no_rate_edit_or_foreign_warehouse_grant"]
    finally:
        pass # The outer Oracle lease always rolls the entire fixture back.
    result=dict(status="PASS",checks=checks,fixture_cleaned=True,stock_effect="NONE",finance_recognition="NOT_EXECUTED")
    return result
if __name__=="__main__":
    with oracle_connection() as connection:
        try: result=run(RollbackGateway(connection.cursor()))
        finally: connection.rollback()
    (ROOT/"reports/retailcase/2026-10-14/access-knowledge/finance-independence.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))
