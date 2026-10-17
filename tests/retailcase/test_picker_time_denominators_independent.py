"""Independent finite-second oracle for interval union, pause subtraction and as-of clipping."""
from datetime import datetime,timedelta,timezone
from random import Random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'api/wms_api_server'))
from app.modules.resources.domain.picker_time_denominators import ConfirmedTimeInterval,ConfirmedTimeCoverage,picker_time_denominators


def test_random_spans_against_independent_finite_second_sets():
    start=datetime(2026,10,15,21,tzinfo=timezone.utc)
    observed=start+timedelta(seconds=180)
    for seed in range(100):
        random=Random(seed);facts=[];seconds={kind:set()for kind in('WORK','PAUSE','ACTUAL_SHIFT')}
        for kind in seconds:
            for index in range(random.randrange(0,15)):
                left=random.randrange(-100,280);right=left+random.randrange(1,180)
                facts.append(ConfirmedTimeInterval(f'{kind}:{index}','ROOT.KPI',kind,start+timedelta(seconds=left),start+timedelta(seconds=right),True))
                seconds[kind].update(range(max(0,left),min(180,right)))
        coverage=[ConfirmedTimeCoverage(kind,'ROOT.KPI',kind,start,start+timedelta(seconds=240),observed,True,True)for kind in seconds]
        result=picker_time_denominators('ROOT.KPI',start,start+timedelta(seconds=240),observed,facts,coverage)
        work=len(seconds['WORK']-seconds['PAUSE']);shift=len(seconds['ACTUAL_SHIFT'])
        assert result.assembly.duration_microseconds==work*1_000_000,(seed,result,work)
        assert result.actual_shift.duration_microseconds==shift*1_000_000,(seed,result,shift)
        assert result.assembly.status==('AVAILABLE'if work else'NO_DATA')
        assert result.actual_shift.status==('AVAILABLE'if shift else'NO_DATA')
