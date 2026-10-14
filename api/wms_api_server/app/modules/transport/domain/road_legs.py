"""Explain road-cache legs without treating a speed estimate as a routed duration."""
from decimal import Decimal,ROUND_CEILING

def ordered_stops(members: list[dict]) -> tuple[list[str],list[str]]:
    if not members:return [],["TRIP_HAS_NO_DESTINATION_MEMBERS"]
    values={};issues=[]
    for m in members:
        address=m.get("address");ordinal=m.get("route_ordinal")
        if not address or ordinal is None:
            issues.append("STOP_ADDRESS_OR_ORDER_UNKNOWN");continue
        n=Decimal(str(ordinal))
        if not n.is_finite()or n<0 or n!=n.to_integral_value():issues.append("STOP_ORDER_INVALID");continue
        values[address]=min(values.get(address,n),n)
    ranked=sorted(values,key=lambda a:(values[a],a))
    if len(set(values.values()))!=len(values):issues.append("DIFFERENT_STOPS_HAVE_EQUAL_ORDER")
    return ranked,sorted(set(issues))

def summarise_legs(depot: str,stops: list[str],costs: dict,issues: list[str]) -> dict:
    sequence=[depot,*stops,depot];legs=[];total=Decimal(0);back=None
    for i,(a,b)in enumerate(zip(sequence,sequence[1:])):
        row=costs.get((a,b))
        reason=None;minutes=None
        if a==b:reason="DEPOT_OR_STOP_REPEATED_WITHOUT_ROAD_LEG"
        elif row is None:reason="MATRIX_PAIR_MISSING"
        elif not row["fresh"]:reason="MATRIX_PAIR_STALE"
        elif row["duration_basis"]!="ROAD_PROFILE_ESTIMATE":reason="DISTANCE_SPEED_TIME_IS_ESTIMATE"
        elif row["duration_min"]is None or Decimal(row["duration_min"])<=0:reason="MATRIX_DURATION_UNKNOWN"
        else:minutes=Decimal(row["duration_min"]);total+=minutes
        legs.append({"from_address":a,"to_address":b,"duration_min":str(minutes)if minutes is not None else None,
                     "distance_km":row["distance_km"]if row else None,"duration_basis":row["duration_basis"]if row else None,
                     "provider":row["provider"]if row else None,"legacy_updated_at":row["updated_at"]if row else None,
                     "unknown_reason":reason})
        if i==len(sequence)-2:back=minutes
    unknown=[x["unknown_reason"]for x in legs if x["unknown_reason"]]
    usable=not issues and bool(stops)and not unknown and back is not None
    outbound=total-back if usable else None
    return {"stops":stops,"legs":legs,"source_issues":issues,"unknown_leg_count":len(unknown),
            "status":"ROAD_PROFILE_ESTIMATE_AVAILABLE"if usable else "ROAD_DURATION_UNKNOWN",
            "drive_min":int(outbound.to_integral_value(rounding=ROUND_CEILING))if outbound is not None else None,
            "drive_back_min":int(back.to_integral_value(rounding=ROUND_CEILING))if usable else None,
            "time_window_admission":False,"physical_capacity_verified":False,"operational_admission":False,
            "depot_basis":"DISPATCHER_EXPLICIT_ADDRESS"}
