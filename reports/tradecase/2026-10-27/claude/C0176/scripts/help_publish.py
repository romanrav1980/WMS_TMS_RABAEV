"""C-0176: publish the trip place removal guide through the existing wiki draft import and knowledge commands (no stock effect)."""
import json, sys
from pathlib import Path
from uuid import uuid4
ROOT = Path(__file__).resolve().parents[6]
sys.path[:0] = [str(ROOT / 'api/wms_api_server'), str(ROOT / 'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import KnowledgeMetadataService
from app.modules.platform.infrastructure.wiki_publication import WikiPublication
from app.modules.platform.infrastructure.metadata_io import MetadataError
from app.modules.platform.api.metadata_inputs import Command, normalize

ARTICLE = 'trip-place-removal'
g = OracleGateway(); service = KnowledgeMetadataService(g); wiki = WikiPublication(g, ROOT)
preview = wiki.preview('admin', ARTICLE)
try:
    current = service.article('admin', ARTICLE)
except MetadataError as error:
    if error.status != 404: raise
    current = None
prefix = 'C0176.HELP:' + uuid4().hex
saved = wiki.import_draft('admin', dict(operation_id=prefix + ':import', source_id=ARTICLE, source_revision=preview['source_revision'],
                                        expected_version=current['version'] if current else 0, reason='C-0176 selected place removal guide'))
published = service.command('admin', normalize(Command(operation_id=prefix + ':publish', command_type='PUBLISH',
    payload=dict(article_id=ARTICLE, expected_version=saved['version'], reason='Publish reviewed selected place removal guide')), 'KNOWLEDGE'))
actual = service.article('admin', ARTICLE, True)
assert actual['body'] == preview['body']
result = dict(status='PASS', article_id=ARTICLE, version=published['version'], source_revision=preview['source_revision'], stock_effect='NONE')
(Path(__file__).resolve().parents[1] / 'help-publication.json').write_text(json.dumps(result, indent=1), encoding='utf-8'); print(json.dumps(result))
