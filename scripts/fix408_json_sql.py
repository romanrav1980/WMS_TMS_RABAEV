from pathlib import Path
import json
p=Path('db/migrations/2026-10-12_ni061_group_source/002_source.sql');t=p.read_text(encoding='utf-8')
t=t.replace('leaf_count number:=0;','leaf_count number:=0;\n v_uid varchar2(200);v_article varchar2(160);v_uom varchar2(20);v_qty number;v_version number;v_link number;v_parent varchar2(200);v_child varchar2(200);')
t=t.replace("node:=treat(nodes.get(i)as json_object_t);","node:=treat(nodes.get(i)as json_object_t);v_uid:=node.get_string('uid');v_version:=node.get_number('version');")
t=t.replace("where UID_PALLET=node.get_string('uid')","where UID_PALLET=v_uid").replace("HU_CONTENT_VERSION=node.get_number('version')+1","HU_CONTENT_VERSION=v_version+1")
t=t.replace("item:=treat(links.get(i)as json_object_t);","item:=treat(links.get(i)as json_object_t);v_link:=item.get_number('id');v_parent:=item.get_string('parent');v_child:=item.get_string('child');v_version:=item.get_number('version');")
t=t.replace("where HU_LINK_ID=item.get_number('id')and PARENT_UID=item.get_string('parent')and CHILD_PALLET_UID=item.get_string('child')","where HU_LINK_ID=v_link and PARENT_UID=v_parent and CHILD_PALLET_UID=v_child").replace("LINK_VERSION=item.get_number('version')+1","LINK_VERSION=v_version+1")
needle="seen_st(to_char(st)):=true;leg:=treat(part.get_array('legs').get(0)as json_object_t);"
t=t.replace(needle,needle+"\n v_uid:=leg.get_string('uid');v_article:=leg.get_string('article');v_uom:=leg.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(leg.get_string('quantity'));")
t=t.replace("NODE_UID=leg.get_string('uid')and ARTICLE_VALUE=leg.get_string('article')and UOM_VALUE=leg.get_string('base_uom')and RRL_STOCK_MATH.quantity(QTY_VALUE)=RRL_STOCK_MATH.quantity(leg.get_string('quantity'))","NODE_UID=v_uid and ARTICLE_VALUE=v_article and UOM_VALUE=v_uom and RRL_STOCK_MATH.quantity(QTY_VALUE)=v_qty")
t=t.replace("where UID_POLETA=leg.get_string('uid')","where UID_POLETA=v_uid").replace("where ARTICUL=leg.get_string('article')","where ARTICUL=v_article")
print(json.dumps({p.as_posix():t}))
