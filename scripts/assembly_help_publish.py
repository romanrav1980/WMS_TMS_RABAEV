"""Publish the reviewed assembly guide through native knowledge commands."""
import json,sys
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import KnowledgeMetadataService
from app.modules.platform.infrastructure.wiki_publication import WikiPublication
from app.modules.platform.infrastructure.metadata_io import MetadataError
from app.modules.platform.api.metadata_inputs import Command,normalize

def main():
 g=OracleGateway();service=KnowledgeMetadataService(g);wiki=WikiPublication(g,ROOT);results=[]
 ids=['assembly-scale']
 drafts=[]
 for article_id in ids:
  preview=wiki.preview('admin',article_id)
  try:current=service.article('admin',article_id)
  except MetadataError as error:
   if error.status!=404:raise
   current=None
  version=current['version'] if current else 0
  prefix='ASSEMBLY.HELP:'+uuid4().hex
  saved=wiki.import_draft('admin',dict(operation_id=prefix+':import',source_id=article_id,source_revision=preview['source_revision'],expected_version=version,reason='Owner requested standalone assembly application and integrated wiki help'))
  drafts.append((article_id,preview,saved['version'],prefix))
 for article_id,preview,version,prefix in drafts:
  # Add only curated cross-links; retain the exact wiki source revision in the imported draft history.
  payload={key:preview[key] for key in ('article_id','space_id','title','summary','body','sources','required_permissions')}
  payload.update(related=['store-scale-gateway','store-receiving-recovery'],expected_version=version,reason='Connect assembly scales and recovery within the local knowledge base')
  linked=service.command('admin',normalize(Command(operation_id=prefix+':links',command_type='ARTICLE_SAVE',payload=payload),'KNOWLEDGE'))
  published=service.command('admin',normalize(Command(operation_id=prefix+':publish',command_type='PUBLISH',payload=dict(article_id=article_id,expected_version=linked['version'],reason='Publish reviewed instructions for the separate assembly terminal')),'KNOWLEDGE'))
  actual=service.article('admin',article_id,True)
  assert actual['body']==preview['body'] and actual['sources']==preview['sources']
  results.append(dict(article_id=article_id,version=published['version'],source_revision=preview['source_revision'],related=len(actual['related'])))
 result=dict(status='PASS',articles=results,stock_effect='NONE')
 (ROOT/'reports/retailcase/2026-10-15/assembly-scale/help-publication.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
