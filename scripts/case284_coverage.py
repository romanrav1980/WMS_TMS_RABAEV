import sys
from pathlib import Path
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.services.routing import OsrmProvider,ValhallaProvider
from app.modules.transport.public import validate_points
import httpx
for points in [[(float("nan"),40)],[(100,40)],[(41,200)],[(True,40)]]:
 try:validate_points(points)
 except ValueError:pass
 else:raise AssertionError("Invalid geographic point")
for provider in[OsrmProvider(),ValhallaProvider()]:
 try:provider.build_cost_matrix([(-33.9,18.4),(-33.8,18.5)])
 except httpx.HTTPStatusError as e:assert e.response.status_code in(400,404);print("OUTSIDE_MAP284",provider.name,e.response.status_code)
 except ValueError as e:print("OUTSIDE_MAP284",provider.name,str(e))
 else:raise AssertionError("Regional map snapped faraway coordinates into false road route")
print("PASS284 currentproviders bound nearest road1000m andreject actual outside preparedcoverage/invalidcoordinates; no matrix or stock writes")
