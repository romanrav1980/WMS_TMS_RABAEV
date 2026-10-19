"""Fixed-orientation whole-box capacity ceiling; it grants no allocation or loading authority."""
from decimal import Decimal,ROUND_FLOOR,localcontext

def box_capacity(capacity_kg:Decimal,capacity_m3:Decimal,dimensions:tuple[Decimal,...],planned:list[dict],candidate:dict,requested:int)->dict:
    with localcontext()as context:
        context.prec=80
        weight=sum((p['boxes']*p['weight']for p in planned),Decimal(0))
        volume=sum((p['boxes']*p['volume']for p in planned),Decimal(0))
        free_weight=max(Decimal(0),capacity_kg-weight);free_volume=max(Decimal(0),capacity_m3-volume)
        by_weight=int((free_weight/candidate['weight']).to_integral_value(rounding=ROUND_FLOOR))
        by_volume=int((free_volume/candidate['volume']).to_integral_value(rounding=ROUND_FLOOR))
        same=all(p['dimensions']==candidate['dimensions']for p in planned)
        geometry=None
        if same:
            total=1
            for vehicle_axis,box_axis in zip(dimensions,candidate['dimensions']):total*=int(vehicle_axis//box_axis)
            geometry=max(0,total-sum(int(p['boxes'])for p in planned))
        maximum=min(by_weight,by_volume,geometry)if geometry is not None else None
        return dict(planned_weight_kg=format(weight.normalize(),'f'),planned_volume_m3=format(volume.normalize(),'f'),free_weight_kg=format(free_weight.normalize(),'f'),free_volume_m3=format(free_volume.normalize(),'f'),
                    box_limit_weight=by_weight,box_limit_volume=by_volume,box_limit_geometry=geometry,
                    maximum_boxes=maximum,requested_boxes=requested,fitting_boxes=min(requested,maximum)if maximum is not None else None,
                    remaining_boxes=max(0,requested-maximum)if maximum is not None else None)
