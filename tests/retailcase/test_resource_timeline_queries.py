from api.wms_api_server.app.modules.resources.infrastructure import timeline_queries


def test_loading_query_skips_per_unit_owner_check_only_for_native_admin(monkeypatch):
    captured = []

    def capture(_cursor, sql, params):
        captured.append((sql, params))
        return []

    monkeypatch.setattr(timeline_queries, "read_rows", capture)
    params = {"ware": 10, "actor": "admin", "start_at": 1, "finish_at": 2}

    timeline_queries.loading_rows(object(), params, actor_is_admin=True)
    timeline_queries.loading_rows(object(), params, actor_is_admin=False)

    admin_sql, admin_params = captured[0]
    operator_sql, operator_params = captured[1]
    assert admin_params == operator_params == params
    assert "or 1=0" in admin_sql
    assert "RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,f.WARE_ID,a.OWNER_ID,0)<>1" not in admin_sql
    assert "RRL_TRADE_STOCK_GUARD.owner_allowed(:actor,f.WARE_ID,a.OWNER_ID,0)<>1" in operator_sql
    for sql in (admin_sql, operator_sql):
        assert "RRL_ACCESS_API.allowed(:actor,'transport_dispatch_view','WAREHOUSE'" in sql
        assert "RRL_TRADE_SITE site where site.WARE_ID=f.WARE_ID" in sql
        assert "where f.WARE_ID=:ware" in sql


def test_transport_query_bounds_operations_before_scoped_pallet_checks(monkeypatch):
    captured = []

    def capture(_cursor, sql, params):
        captured.append((sql, params))
        return []

    monkeypatch.setattr(timeline_queries, "read_rows", capture)
    params = {"ware": 1, "actor": "admin", "local_start": object(), "local_finish": object()}
    timeline_queries.transport_rows(object(), params)
    sql, passed = captured[0]
    assert passed is params
    assert "with candidate_operations as" in sql
    assert "/*+ materialize */" in sql
    assert sql.index("candidate_operations") < sql.index("RRL_SBORKA_PALLETS")
    assert "PLAN_START<:local_finish" in sql and "FACT_START<:local_finish" in sql
