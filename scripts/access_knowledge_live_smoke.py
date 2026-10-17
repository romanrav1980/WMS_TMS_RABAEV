"""Live Oracle metadata fixtures; no existing user assignment or stock mutation."""
import json
import sys
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"api/wms_api_server"),str(ROOT/"scripts")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService,KnowledgeMetadataService,NativePublishedHelp,MetadataError
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.modules.platform.infrastructure.wiki_publication import WikiPublication

def main():
    gateway=OracleGateway();access=AccessMetadataService(gateway);knowledge=KnowledgeMetadataService(gateway)
    suffix=uuid4().hex[:8];prefix="ak"+suffix
    first=prefix+"u1";second=prefix+"u2";objects=[prefix+"a",prefix+"b"]
    limited=prefix+"limited";candidate=prefix+"candidate";broker=prefix+"broker";branch=prefix+"dc";role=prefix+"dispatcher";read_role=prefix+"reader";group=prefix+"group";frozen_group=prefix+"frozen";space=prefix+"space";other_space=prefix+"other";article=prefix+"-article";secret=prefix+"-secret";imported=prefix+"-import"
    op_prefix=prefix+":";checks=[]
    now=datetime.now(timezone.utc)
    def command(kind,payload,actor="admin",domain="ACCESS",op=None):
        body=normalize(Command(operation_id=op or op_prefix+uuid4().hex,command_type=kind,payload=payload),domain)
        return (access if domain=="ACCESS" else knowledge).command(actor,body)
    def allowed(user,permission,obj):
        return gateway.fetch_all("select RRL_ACCESS_API.allowed(:actor,:permission,'WAREHOUSE',:id) ALLOWED from dual",{"actor":user,"permission":permission,"id":obj})[0]["allowed"]
    def assign(name,user,role_id,scope_kind,scope_id=None,**extra):
        return command("ASSIGN",dict(assignment_id=prefix+name,username=user,role_id=role_id,scope_kind=scope_kind,scope_id=scope_id,
          membership="CURRENT",valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(days=1)).isoformat(),reason="isolated acceptance",expected_version=0)|extra)
    def expect(code,fn):
        try:fn()
        except MetadataError as error:
            assert error.code==code,(error.code,code);return
        raise AssertionError("Expected "+code)
    try:
        with gateway.transaction("access.smoke.fixture") as cursor:
            for user in (first,second):
                cursor.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:name,:password,'NONE',1,0,1)",{"id":user,"name":"Isolated access fixture","password":secrets.token_urlsafe(24)})
        for obj in objects:command("OBJECT_SAVE",dict(kind="WAREHOUSE",object_id=obj,title="Fixture "+obj,active=True,expected_version=0))
        command("ROLE_SAVE",dict(role_id=role,title="Fixture dispatcher",permissions=["fixture_write"],active=True,expected_version=0))
        command("ROLE_SAVE",dict(role_id=read_role,title="Fixture reader",permissions=["fixture_read"],active=True,expected_version=0))
        command("GROUP_SAVE",dict(group_id=group,title="Fixture group",member_kind="WAREHOUSE",members=[dict(kind="WAREHOUSE",object_id=objects[0])],active=True,expected_version=0))
        assign("write",first,role,"GROUP",group)
        assign("read",first,read_role,"NETWORK")
        assert allowed(first,"fixture_write",objects[0])==1
        assert allowed(first,"fixture_write",objects[1])==0
        assert allowed(first,"fixture_read",objects[1])==1
        assert allowed(second,"fixture_write",objects[0])==0
        checks.append("role_scope_pairing_no_cartesian_expansion")
        assign("snapshot",second,role,"GROUP",group,membership="SNAPSHOT",snapshot_version=1)
        command("GROUP_SAVE",dict(group_id=group,title="Fixture group",member_kind="WAREHOUSE",members=[dict(kind="WAREHOUSE",object_id=x)for x in objects],active=True,expected_version=1))
        assert allowed(first,"fixture_write",objects[1])==1 and allowed(second,"fixture_write",objects[1])==0
        checks.append("current_and_snapshot_membership")
        assign("expired",second,read_role,"NETWORK",valid_from=(now-timedelta(days=2)).isoformat(),valid_until=(now-timedelta(days=1)).isoformat())
        assert allowed(second,"fixture_read",objects[0])==0
        command("REVOKE",dict(assignment_id=prefix+"write",expected_version=1,reason="fixture revoke"))
        assert allowed(first,"fixture_write",objects[0])==0
        checks.append("expiry_and_revocation")
        command("OBJECT_SAVE",dict(kind="DC",object_id=branch,title="Fixture DC",active=True,expected_version=0))
        command("OBJECT_SAVE",dict(kind="WAREHOUSE",object_id=objects[0],title="Fixture A",parent_kind="DC",parent_id=branch,active=True,expected_version=1))
        revision=access.me("admin","GLOBAL_ADMIN")["access_revision"]
        assign("branch",second,read_role,"ORG_BRANCH","DC:"+branch,membership="SNAPSHOT",snapshot_version=revision)
        command("OBJECT_SAVE",dict(kind="WAREHOUSE",object_id=objects[1],title="Fixture B",parent_kind="DC",parent_id=branch,active=True,expected_version=1))
        assert allowed(second,"fixture_read",objects[0])==1 and allowed(second,"fixture_read",objects[1])==0
        checks.append("branch_snapshot_does_not_expand")
        command("ROLE_SAVE",dict(role_id=broker,title="Fixture delegator",permissions=["access_assign_manage","access_group_manage","access_role_manage","access_admin_view"],active=True,expected_version=0))
        assign("broker",first,broker,"PLATFORM")
        assign("mandate",first,role,"WAREHOUSE",objects[0],valid_until=(now+timedelta(hours=1)).isoformat())
        grant=dict(assignment_id=prefix+"delegated",username=second,role_id=role,scope_kind="WAREHOUSE",scope_id=objects[0],membership="CURRENT",
         valid_from=now.isoformat(),valid_until=(now+timedelta(minutes=30)).isoformat(),reason="fixture delegation",expected_version=0)
        command("ASSIGN",grant,actor=first)
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("ASSIGN",grant|{"assignment_id":prefix+"outside","scope_id":objects[1]},actor=first))
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("ASSIGN",grant|{"assignment_id":prefix+"long","valid_until":(now+timedelta(hours=2)).isoformat()},actor=first))
        assign("livegroup",second,role,"GROUP",group)
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("GROUP_SAVE",dict(group_id=group,title="Cannot expand other assignments",member_kind="WAREHOUSE",members=[dict(kind="WAREHOUSE",object_id=objects[1])],active=True,expected_version=2),actor=first))
        checks.append("delegation_scope_and_lifetime_same_grant")
        limited_payload=dict(role_id=limited,title="Delegated role",permissions=["fixture_write"],active=True,expected_version=0)
        command("ROLE_SAVE",limited_payload,actor=first)
        command("ASSIGN",grant|{"assignment_id":prefix+"limitedgrant","role_id":limited},actor=first)
        command("ROLE_SAVE",limited_payload|{"title":"Within mandate","expected_version":1},actor=first)
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("ROLE_SAVE",limited_payload|{"permissions":["fixture_write","fixture_private"],"expected_version":2},actor=first))
        command("ROLE_SAVE",dict(role_id=candidate,title="Unassigned design",permissions=["fixture_private"],active=True,expected_version=0),actor=first)
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("ASSIGN",grant|{"assignment_id":prefix+"escalate","username":first,"role_id":candidate},actor=first))
        assert allowed(first,"fixture_private",objects[0])==0
        checks.append("role_designer_mandate_no_self_escalation")

        frozen_payload=dict(group_id=frozen_group,title="Frozen fixture",member_kind="WAREHOUSE",members=[dict(kind="WAREHOUSE",object_id=objects[0])],active=True,expected_version=0)
        command("GROUP_SAVE",frozen_payload)
        assign("frozengrant",second,role,"GROUP",frozen_group,membership="SNAPSHOT",snapshot_version=1)
        command("GROUP_SAVE",frozen_payload|{"active":False,"expected_version":1})
        expect("DELEGATION_OUTSIDE_MANDATE",lambda:command("GROUP_SAVE",frozen_payload|{"expected_version":2},actor=first))
        preview=access.preview_group("admin",frozen_payload|{"expected_version":2})
        assert preview["activation_changed"] and preview["affected_total"]==1
        checks.append("snapshot_reactivation_mandate_and_impact_preview")

        why=access.explain(first,first,"fixture_write","WAREHOUSE",objects[0])
        assert why["allowed"] and why["reasons"][0]["source"]=="ASSIGNMENT"
        checks.append("native_explanation_sources")

        replay_op=op_prefix+"replay"
        payload=dict(role_id=role,title="Fixture dispatcher",permissions=["fixture_write"],active=True,expected_version=1)
        first_result=command("ROLE_SAVE",payload,op=replay_op);second_result=command("ROLE_SAVE",payload,op=replay_op)
        assert first_result["version"]==2 and second_result["replayed"] is True
        expect("OPERATION_CONFLICT",lambda:command("ROLE_SAVE",payload|{"title":"different"},op=replay_op))
        expect("VERSION_CONFLICT",lambda:command("ROLE_SAVE",payload))
        checks.append("durable_receipt_and_payload_version_conflicts")
        concurrent_op=op_prefix+"concurrent"
        concurrent_payload=payload|{"expected_version":2}
        with ThreadPoolExecutor(max_workers=2) as pool:
            result=list(pool.map(lambda _:command("ROLE_SAVE",concurrent_payload,op=concurrent_op),range(2)))
        assert sum(not r["replayed"]for r in result)==1 and {r["version"]for r in result}=={3}
        checks.append("concurrent_same_operation_once")
        command("SPACE_SAVE",dict(space_id=space,title="Fixture knowledge",expected_version=0),domain="KNOWLEDGE")
        draft=dict(article_id=article,space_id=space,title="Fixture public",summary="fixture",body="Published original",related=[],sources=[],required_permissions=[],reason="fixture",expected_version=0)
        command("ARTICLE_SAVE",draft,domain="KNOWLEDGE")
        help_reader=NativePublishedHelp(knowledge,second)
        assert help_reader.detail(article,set()) is None
        command("PUBLISH",dict(article_id=article,expected_version=1,reason="fixture publication"),domain="KNOWLEDGE")
        assert help_reader.detail(article,set())["body"]=="Published original"
        command("SPACE_SAVE",dict(space_id=other_space,title="Fixture moved",expected_version=0),domain="KNOWLEDGE")
        command("ARTICLE_SAVE",draft|{"body":"Unpublished replacement","space_id":other_space,"expected_version":2},domain="KNOWLEDGE")
        assert help_reader.detail(article,set())["body"]=="Published original"
        assert help_reader.detail(article,set())["space_id"]==space
        assert any(item["article_id"]==article for item in knowledge.articles(second,space,"",None,50))
        assert not any(item["article_id"]==article for item in knowledge.articles(second,other_space,"",None,50))
        checks.append("draft_does_not_replace_publication")
        command("ARTICLE_SAVE",draft|{"article_id":secret,"body":"fixture-private-needle","required_permissions":["fixture_private"],"expected_version":0},domain="KNOWLEDGE")
        command("PUBLISH",dict(article_id=secret,expected_version=1,reason="private fixture"),domain="KNOWLEDGE")
        assert help_reader.detail(secret,set()) is None
        assert help_reader.search("fixture-private-needle",set(),20)==[]
        command("ARTICLE_SAVE",draft|{"related":[secret],"expected_version":3},domain="KNOWLEDGE")
        command("PUBLISH",dict(article_id=article,expected_version=4,reason="fixture links"),domain="KNOWLEDGE")
        assert help_reader.detail(article,set())["related"]==[]
        expect("ACCESS_DENIED",lambda:knowledge.history(second,article,20))
        checks.append("private_search_detail_links_history_hidden")
        command("ARCHIVE",dict(article_id=article,expected_version=5,reason="fixture archive"),domain="KNOWLEDGE")
        assert help_reader.detail(article,set()) is None
        checks.append("archive_hidden_from_reader")
        source_root=ROOT/"tmp"/("wiki-publication-"+prefix)
        (source_root/"docs/help").mkdir(parents=True)
        (source_root/"wiki").mkdir()
        source_path=source_root/"wiki/instruction.md"
        source_path.write_text("# Fixture\n\n## Instruction\nOriginal source text.\n",encoding="utf-8")
        manifest=[dict(source_id="fixture",article_id=imported,space_id=space,title="Imported fixture",summary="Fixture",path="wiki/instruction.md",section="Instruction",status="APPROVED",owner="platform")]
        (source_root/"docs/help/wiki-sources.json").write_text(json.dumps(manifest),encoding="utf-8")
        publication=WikiPublication(gateway,source_root)
        preview=publication.preview("admin","fixture")
        request=dict(operation_id=op_prefix+"import",source_id="fixture",source_revision=preview["source_revision"],expected_version=0,reason="fixture import")
        imported_result=publication.import_draft("admin",request)
        assert imported_result["version"]==1 and help_reader.detail(imported,set())is None
        source_path.write_text("# Fixture\n\n## Instruction\nChanged source.\n",encoding="utf-8")
        assert publication.import_draft("admin",request)["replayed"] is True
        expect("OPERATION_CONFLICT",lambda:publication.import_draft("admin",request|{"reason":"different"}))
        expect("WIKI_SOURCE_CHANGED_RECONCILE_PREVIOUS",lambda:publication.import_draft("admin",request|{"operation_id":op_prefix+"new-import"}))
        expect("WIKI_SOURCE_NOT_ALLOWED",lambda:publication.preview("admin","../private"))
        expect("ACCESS_DENIED",lambda:publication.preview(second,"fixture"))
        checks.append("curated_wiki_import_receipt_survives_source_change")

    finally:
        with gateway.transaction("access.smoke.cleanup")as cursor:
            for sql in ["delete from RRL_KNOWLEDGE_REV where ARTICLE_ID in(:article,:secret,:imported)","delete from RRL_KNOWLEDGE_ARTICLE where ARTICLE_ID in(:article,:secret,:imported)"]:
                cursor.execute(sql,{"article":article,"secret":secret,"imported":imported})
            cursor.execute("delete from RRL_KNOWLEDGE_SPACE where SPACE_ID in(:id,:other)",{"id":space,"other":other_space})
            cursor.execute("delete from RRL_ACCESS_ASSIGNMENT where USERNAME in(:first,:second)",{"first":first,"second":second})
            cursor.execute("delete from RRL_ACCESS_GROUP_MEMBER where GROUP_ID in(:id,:frozen)",{"id":group,"frozen":frozen_group})
            cursor.execute("delete from RRL_ACCESS_GROUP where GROUP_ID in(:id,:frozen)",{"id":group,"frozen":frozen_group})
            for table in ("RRL_ACCESS_ROLE_RIGHT","RRL_ACCESS_ROLE"):
                cursor.execute("delete from "+table+" where ROLE_ID in(:role,:reader,:broker,:limited,:candidate)",{"role":role,"reader":read_role,"broker":broker,"limited":limited,"candidate":candidate})
            cursor.execute("delete from RRL_ACCESS_BRANCH_MEMBER where BRANCH_KEY=:id",{"id":"DC:"+branch})
            cursor.execute("delete from RRL_ACCESS_OBJECT where OBJECT_ID in(:a,:b)",{"a":objects[0],"b":objects[1]})
            cursor.execute("delete from RRL_ACCESS_OBJECT where KIND='DC' and OBJECT_ID=:id",{"id":branch})
            cursor.execute("delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix",{"prefix":op_prefix+"%"})
            cursor.execute("delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix",{"prefix":op_prefix+"%"})
            cursor.execute("delete from RUSERS where ID in(:first,:second)",{"first":first,"second":second})
    result={"status":"PASS","checks":checks,"isolated_prefix":prefix,"fixture_cleaned":True,"stock_effect":"NONE"}
    target=ROOT/"reports/retailcase/2026-10-14/access-knowledge/native-smoke.json"
    target.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))

if __name__=="__main__":main()
