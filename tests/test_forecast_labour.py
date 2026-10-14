from api.wms_api_server.app.modules.resources.domain.forecast_labour import forecast_labour

def test_partial_total_never_becomes_complete_capacity():
    series=[{"article":"A","base_uom":"EA","status":"READY","estimated_quantity":"1"},
            {"article":"B","base_uom":"KG","status":"READY","estimated_quantity":"10.125"}]
    basis={"status":"MAPPED","mapping":{"version_no":3},"norms":[{"article":"A","base_uom":"EA","active":1,"base_per_hour":"3"}]}
    result=forecast_labour(series,basis)
    assert result["known_person_hours"]=="0.333333334"
    assert result["total_person_hours"] is None
    assert result["status"]=="PARTIAL_ESTIMATE"
    assert result["rows"][1]["status"]=="NO_NORM"
    assert result["people_required"] is None

def test_inactive_norm_and_blocked_forecast_do_not_create_hours():
    series=[{"article":"A","base_uom":"EA","status":"READY","estimated_quantity":"12"},
            {"article":"B","base_uom":"EA","status":"NEEDS_PROJECTION","estimated_quantity":None}]
    basis={"status":"MAPPED","mapping":{"version_no":1},"norms":[
        {"article":"A","base_uom":"EA","active":0,"base_per_hour":"6"},
        {"article":"B","base_uom":"EA","active":1,"base_per_hour":"6"}]}
    result=forecast_labour(series,basis)
    assert [r["status"]for r in result["rows"]]==["NORM_INACTIVE","FORECAST_BLOCKED"]
    assert result["known_person_hours"] is None
    assert result["total_person_hours"] is None

def test_full_total_preserves_decimal_quantities():
    series=[{"article":"A","base_uom":"KG","status":"READY","estimated_quantity":"10.125"}]
    basis={"status":"MAPPED","mapping":{"version_no":2},"norms":[{"article":"A","base_uom":"KG","active":1,"base_per_hour":"0.125"}]}
    result=forecast_labour(series,basis)
    assert result["total_person_hours"]=="81.000000000"
    assert result["status"]=="COMPLETE_ESTIMATE"
    basis["status"]="SCOPE_MAPPING_INACTIVE"
    result=forecast_labour(series,basis)
    assert result["rows"][0]["status"]=="SCOPE_MAPPING_INACTIVE"
    assert result["total_person_hours"] is None
