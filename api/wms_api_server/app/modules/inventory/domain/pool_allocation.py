"""Proportional stock allocation in whole pick quanta; no Oracle or HTTP dependencies."""
from dataclasses import dataclass
from decimal import Decimal, localcontext
from heapq import heappop, heappush

@dataclass(frozen=True)
class PoolDemand:
    line_id: int
    quantity: Decimal
    dispatch_order: int

@dataclass(frozen=True)
class PoolAllocation:
    quantities: dict[int, Decimal]
    remaining: Decimal

def allocate_pool(demands: tuple[PoolDemand,...], available: Decimal, step: Decimal) -> PoolAllocation:
    if not demands or len(demands)>2000:
        raise ValueError("Pool must contain 1..2000 order lines")
    if len({d.line_id for d in demands})!=len(demands) or any(d.line_id<1 for d in demands):
        raise ValueError("Pool order lines must have distinct positive identifiers")
    values=(available,step,*(d.quantity for d in demands))
    if any(not isinstance(v,Decimal) or not v.is_finite() or v<0 or len(v.as_tuple().digits)>38 for v in values) or step<=0:
        raise ValueError("Pool quantities require finite nonnegative Oracle decimals and a positive pick quantum")
    with localcontext() as ctx:
        ctx.prec=96
        ordered=sorted(demands,key=lambda d:(d.dispatch_order,d.line_id))
        units=[int(d.quantity//step) for d in ordered]
        active=[i for i,u in enumerate(units) if u>0]
        total=sum(units);budget=min(int(available//step),total)
        assigned=[0]*len(ordered)
        if budget>=total:
            assigned=units.copy()
        elif budget<len(active):
            for i in active[:budget]:assigned[i]=1
        else:
            assigned=[max(1,budget*u//total) if u else 0 for u in units]
            excess=sum(assigned)-budget
            if excess>0:
                donors=[(-(assigned[i]*total-budget*units[i]),-ordered[i].dispatch_order,-ordered[i].line_id,i)
                        for i in active if assigned[i]>1]
                from heapq import heapify
                heapify(donors)
                for _ in range(excess):
                    _,_,_,i=heappop(donors);assigned[i]-=1
                    if assigned[i]>1:
                        heappush(donors,(-(assigned[i]*total-budget*units[i]),-ordered[i].dispatch_order,-ordered[i].line_id,i))
            elif excess<0:
                recipients=[(-(budget*units[i]-assigned[i]*total),ordered[i].dispatch_order,ordered[i].line_id,i)
                            for i in active if assigned[i]<units[i]]
                from heapq import heapify
                heapify(recipients)
                for _ in range(-excess):
                    _,_,_,i=heappop(recipients);assigned[i]+=1
                    if assigned[i]<units[i]:
                        heappush(recipients,(-(budget*units[i]-assigned[i]*total),ordered[i].dispatch_order,ordered[i].line_id,i))
        quantities={d.line_id:step*u for d,u in zip(ordered,assigned)}
        return PoolAllocation(quantities,available-step*sum(assigned))
