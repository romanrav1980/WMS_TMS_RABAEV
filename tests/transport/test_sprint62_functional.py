"""
test_sprint62_functional.py — Functional tests for Sprint 62 (sticky table header).

Sprint 62 adds CSS `position: sticky; top: 0` to thead th inside .dispatch-st-section.
No JS changes. Tests verify the structural preconditions that make sticky header work:
1. The container must have overflow-y: auto/scroll (already true — dispatch-st-section).
2. The <thead> <th> elements must have position: sticky + top: 0 (new CSS).
3. A background must be set on the sticky cells so rows scroll under them.
"""

import re


def parse_css_rules(css: str) -> dict[str, str]:
    """Parse CSS blocks into {selector: declarations} dict (simplified)."""
    rules = {}
    pattern = re.compile(r'([^{}]+)\{([^{}]*)\}')
    for m in pattern.finditer(css):
        sel = m.group(1).strip()
        decl = m.group(2).strip()
        rules[sel] = decl
    return rules


class TestStickyHeaderCSS:
    def _load_css(self) -> str:
        import os
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "admin", "wms_admin_frontend", "src", "styles.css"
        )
        with open(os.path.normpath(path), encoding="utf-8") as f:
            return f.read()

    def test_st_section_has_overflow_y(self):
        css = self._load_css()
        assert ".dispatch-st-section" in css
        idx = css.index(".dispatch-st-section")
        block = css[idx: idx + 300]
        assert "overflow-y" in block

    def test_sticky_rule_exists(self):
        css = self._load_css()
        assert "position: sticky" in css

    def test_sticky_rule_targets_st_section_grid_thead(self):
        css = self._load_css()
        assert ".dispatch-st-section .dispatch-grid thead th" in css

    def test_sticky_rule_has_top_zero(self):
        css = self._load_css()
        idx = css.index(".dispatch-st-section .dispatch-grid thead th")
        block = css[idx: idx + 200]
        assert "top: 0" in block

    def test_sticky_rule_has_z_index(self):
        css = self._load_css()
        idx = css.index(".dispatch-st-section .dispatch-grid thead th")
        block = css[idx: idx + 200]
        assert "z-index" in block

    def test_sticky_rule_has_background(self):
        css = self._load_css()
        idx = css.index(".dispatch-st-section .dispatch-grid thead th")
        block = css[idx: idx + 200]
        assert "background" in block
