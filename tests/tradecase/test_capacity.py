"""Source checks16/21/22/24 arithmetic only; native loading/admission is tested separately."""
from decimal import Decimal as D
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.integrations.domain.trade_capacity import box_capacity

def package(boxes=0):return dict(boxes=D(boxes),weight=D(10),volume=D('0.1'),dimensions=(D('0.4'),D('0.5'),D('0.5')))
def calc(requested=60,kg=8000,volume='66',dimensions=('13.2','2.5','2')):
 return box_capacity(D(kg),D(volume),tuple(D(x)for x in dimensions),[package(200),package(150),package(250)],package(),requested)
def test_source600_and60():
 r=calc();assert D(r['planned_weight_kg'])==6000 and D(r['planned_volume_m3'])==60
 assert [r[k]for k in ['box_limit_weight','box_limit_volume','box_limit_geometry','fitting_boxes','remaining_boxes']]==[200,60,60,60,0]
def test_partial80_leaves20():
 r=calc(80);assert r['fitting_boxes']==60 and r['remaining_boxes']==20
def test_body64_preserves_primary600():
 r=calc(volume='64',dimensions=('12.8','2.5','2'));assert r['fitting_boxes']==40 and r['remaining_boxes']==20
 assert r['box_limit_geometry']==40 and D(r['planned_volume_m3'])==60
def test_weight200_spare_limits20():
 r=calc(kg=6200);assert r['fitting_boxes']==20 and r['remaining_boxes']==40
def test_unproved_mixed_layout_not_volume_only():
 other=package(600);other['dimensions']=(D('.5'),D('.4'),D('.5'))
 r=box_capacity(D(8000),D(66),(D('13.2'),D('2.5'),D(2)),[other],package(),60)
 assert r['maximum_boxes']is None and r['fitting_boxes']is None
