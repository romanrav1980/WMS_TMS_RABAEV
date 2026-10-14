from pathlib import Path
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/quality_scope.py');s=p.read_text(encoding='utf-8-sig').replace('import hashlib','from decimal import Decimal\nimport hashlib').replace('"percent":body["sample_percent"]','"percent":Decimal(str(body["sample_percent"]))');p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/modules/inventory/public.py');s=p.read_text(encoding='utf-8');s+='''
from .contracts_quality_scope import QualityScopePort,quality_scope_service
from .api.quality_scope_routes import router as quality_scope_router
from .infrastructure.quality_scope import QualityScope

def build_quality_scope(gateway: Any) -> QualityScopePort:
    return QualityScope(gateway)
''';p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/quality_scope_composition.py');p.write_text('''from .oracle_gateway import OracleGateway
from .modules.inventory.public import QualityScopePort,build_quality_scope

def quality_scope() -> QualityScopePort:
    return build_quality_scope(OracleGateway())
''',encoding='utf-8')
p=Path('api/wms_api_server/app/main.py');s=p.read_text(encoding='utf-8');s+='''
from .modules.inventory.public import quality_scope_router,quality_scope_service
from .quality_scope_composition import quality_scope
app.include_router(quality_scope_router)
app.dependency_overrides[quality_scope_service]=quality_scope
''';p.write_text(s,encoding='utf-8')
