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


@dataclass(frozen=True)
class TradeDemand:
    line_id: int
    quantity: Decimal
    dispatch_order: int
    classes: tuple[str, ...]  # physical classes (owner|SKU|MRC|expiry) this row's trade terms accept


@dataclass(frozen=True)
class TradeAllocation:
    quantities: dict[int, Decimal]
    sources: dict[int, dict[str, Decimal]]


def _fefo(key: str) -> tuple[str, str]:
    return key.rsplit("|", 1)[-1], key  # earliest expiry first, then the key itself


def allocate_trade_pool(demands: tuple[TradeDemand, ...], free: dict[str, Decimal], step: Decimal) -> TradeAllocation:
    """C-0160: whole-step shares of a trade site; a row draws only on the classes it accepts. Rows that accept exactly the same classes
    share them proportionally (the existing algorithm); rows with overlapping but different class sets are served in dispatch order,
    FEFO within each row. Every split is proven again by the native pool command; nothing here is trusted on its own."""
    if len(demands) > 2000 or len({d.line_id for d in demands}) != len(demands):
        raise ValueError("Pool must contain at most 2000 distinct order lines")
    left = dict(free)
    quantities = {d.line_id: Decimal(0) for d in demands}
    sources: dict[int, dict[str, Decimal]] = {}
    active = [d for d in demands if d.quantity >= step and d.classes]
    parent = {d.line_id: d.line_id for d in active}

    def root(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    owner: dict[str, int] = {}
    for d in active:
        for key in d.classes:
            if key in owner:
                parent[root(d.line_id)] = root(owner[key])
            else:
                owner[key] = d.line_id
    groups: dict[int, list[TradeDemand]] = {}
    for d in active:
        groups.setdefault(root(d.line_id), []).append(d)

    def draw(d: TradeDemand, want: Decimal) -> None:
        for key in sorted(d.classes, key=_fefo):
            take = min(want, (left.get(key, Decimal(0)) // step) * step)
            if take > 0:
                left[key] -= take
                want -= take
                quantities[d.line_id] += take
                sources.setdefault(d.line_id, {})[key] = sources.get(d.line_id, {}).get(key, Decimal(0)) + take
            if want <= 0:
                break
    for rows in groups.values():
        rows.sort(key=lambda d: (d.dispatch_order, d.line_id))
        if len({frozenset(d.classes) for d in rows}) == 1:
            shared = sum((left.get(k, Decimal(0)) for k in rows[0].classes), Decimal(0))
            split = allocate_pool(tuple(PoolDemand(d.line_id, d.quantity, d.dispatch_order) for d in rows), shared, step)
            for d in rows:
                draw(d, split.quantities[d.line_id])
        else:
            for d in rows:
                draw(d, (d.quantity // step) * step)
    return TradeAllocation(quantities, sources)
