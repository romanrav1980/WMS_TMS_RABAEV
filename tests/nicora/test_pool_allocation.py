"""Requirement examples and conservation for the actual pure allocation rule."""
from decimal import Decimal as D
from app.modules.inventory.domain.pool_allocation import PoolDemand,allocate_pool

def run(needs,available,step="1"):
    return allocate_pool(tuple(PoolDemand(i+1,D(n),i) for i,n in enumerate(needs)),D(available),D(step))

def test_requirement_proportions_and_whole_quantum():
    assert list(run(["60","40"],"50").quantities.values())==[D("30"),D("20")]
    assert list(run(["40","30","30"],"100").quantities.values())==[D("40"),D("30"),D("30")]
    assert list(run(["3","3","3","3","3"],"3").quantities.values())==[D("1"),D("1"),D("1"),D("0"),D("0")]

def test_no_zero_share_if_budget_covers_every_customer():
    result=run(["100","1","1"],"3")
    assert list(result.quantities.values())==[D("1"),D("1"),D("1")]
    assert list(run(["40","40","20"],"7").quantities.values())==[D("3"),D("3"),D("1")]

def test_fractional_pick_quantum_and_large_quantity():
    result=run(["1.5","1"],"1.4","0.25")
    assert sum(result.quantities.values())==D("1.25") and result.remaining==D("0.15")
    result=run(["10000000000000000000000000000000000000","1"],"5000000000000000000000000000000000000")
    assert result.quantities[2]==D("1") and result.remaining==D("0")

def test_conservation_limits_and_positive_share():
    for needs in (["0","4","7"],["100","1","1"],["40","40","20"],["1","1","1","1"]):
        for available in range(15):
            result=run(needs,str(available));values=list(result.quantities.values())
            assert sum(values)<=D(available)
            assert all(D(0)<=value<=D(need) for value,need in zip(values,needs))
            if available>=sum(D(need)>0 for need in needs):assert all(value>0 for value,need in zip(values,needs) if D(need)>0)
