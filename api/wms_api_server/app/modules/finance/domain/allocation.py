from decimal import Decimal,ROUND_FLOOR,localcontext

def allocate_cents(amount: Decimal,weights: list[tuple[str,Decimal]]) -> dict[str,Decimal]:
    if amount<=0 or amount!=amount.quantize(Decimal("0.01")) or not weights or len({key for key,_ in weights})!=len(weights) or any(weight<=0 or not weight.is_finite() for _,weight in weights):
        raise ValueError("Allocation requires exact positive amount and unique positive weights")
    with localcontext() as context:
        context.prec=60
        total=sum((weight for _,weight in weights),Decimal("0"))
        shares={key:amount*weight/total for key,weight in weights}
        floors={key:value.quantize(Decimal("0.01"),rounding=ROUND_FLOOR)for key,value in shares.items()}
        remainder=int((amount-sum(floors.values()))*100)
        ordered=sorted(shares,key=lambda key:(-(shares[key]-floors[key]),key))
        for key in ordered[:remainder]:floors[key]+=Decimal("0.01")
        if sum(floors.values())!=amount:raise ValueError("Allocation does not preserve original amount")
        return floors
