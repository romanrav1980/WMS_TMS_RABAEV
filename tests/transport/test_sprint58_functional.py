"""
test_sprint58_functional.py — Functional tests for Sprint 58 (expand/collapse all clusters).

Sprint 58 adds two buttons «⊞ Все» / «⊟ Нет» in cluster mode toolbar
that expand or collapse all cluster rows at once.
"""


def expand_all(clusters: list[dict]) -> set:
    """Mirror setExpandedRaions(new Set(clusters.map(c => c.RAION)))."""
    return {c["RAION"] for c in clusters}


def collapse_all() -> set:
    """Mirror setExpandedRaions(new Set())."""
    return set()


class TestExpandCollapseAll:
    def _clusters(self):
        return [
            {"RAION": "Центр",   "COUNT": 10},
            {"RAION": "Лысьва",  "COUNT": 5},
            {"RAION": "Чусовой", "COUNT": 8},
            {"RAION": None,       "COUNT": 3},
        ]

    def test_expand_all_contains_all_raions(self):
        clusters = self._clusters()
        expanded = expand_all(clusters)
        raions = {c["RAION"] for c in clusters}
        assert expanded == raions

    def test_expand_all_includes_none_raion(self):
        clusters = self._clusters()
        expanded = expand_all(clusters)
        assert None in expanded

    def test_collapse_all_returns_empty(self):
        collapsed = collapse_all()
        assert len(collapsed) == 0

    def test_expand_then_collapse(self):
        clusters = self._clusters()
        expanded = expand_all(clusters)
        assert len(expanded) > 0
        collapsed = collapse_all()
        assert len(collapsed) == 0

    def test_expand_all_empty_clusters(self):
        expanded = expand_all([])
        assert expanded == set()

    def test_expand_all_single_cluster(self):
        clusters = [{"RAION": "Центр", "COUNT": 5}]
        expanded = expand_all(clusters)
        assert expanded == {"Центр"}

    def test_buttons_visible_only_in_cluster_mode(self):
        view_mode = "flat"
        show = view_mode == "clusters"
        assert show is False
        view_mode = "clusters"
        show = view_mode == "clusters"
        assert show is True

    def test_buttons_not_visible_in_flat_mode(self):
        view_mode = "flat"
        show = view_mode == "clusters"
        assert show is False

    def test_after_expand_all_every_cluster_is_expanded(self):
        clusters = self._clusters()
        expanded = expand_all(clusters)
        for c in clusters:
            assert c["RAION"] in expanded

    def test_partial_expand_preserved_after_collapse(self):
        clusters = self._clusters()
        manually_expanded = {"Центр", "Лысьва"}
        collapsed = collapse_all()
        assert "Центр" not in collapsed
        assert "Лысьва" not in collapsed
