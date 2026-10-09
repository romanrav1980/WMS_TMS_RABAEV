"""Static module-boundary rules shared by the CLI and regression fixtures."""
from __future__ import annotations
from collections import Counter
from pathlib import PurePosixPath


def feature(path: str) -> tuple[str, str, str] | None:
    parts = PurePosixPath(path).parts
    for directory in ('modules', 'features'):
        if directory in parts:
            index = parts.index(directory)
            if len(parts) > index + 2:
                rest = parts[index + 2:]
                return directory, parts[index + 1], rest[0] if len(rest) > 1 else ''
    return None


def import_rules(source: str, target: str, policy: dict) -> list[str]:
    rules = []
    current, dependency = feature(source), feature(target)
    if current:
        kind, owner, layer = current
        if kind == 'modules':
            if dependency and dependency[0] == 'modules':
                _, other_owner, other_layer = dependency
                public = PurePosixPath(target).name in policy['backend_public_files'] and not other_layer
                if owner != other_owner and not public:
                    rules.append('cross-module-private-import')
                if layer == 'domain' and (owner != other_owner or other_layer != 'domain'):
                    rules.append('domain-outward-dependency')
                if layer == 'application' and other_layer in ('infrastructure', 'api'):
                    rules.append('application-outward-dependency')
                if layer == 'infrastructure' and other_layer == 'api':
                    rules.append('infrastructure-to-api')
                if layer == 'api' and other_layer == 'infrastructure':
                    rules.append('api-to-infrastructure')
            elif layer in ('domain', 'application', 'api'):
                rules.append('new-module-to-legacy-internal')
        elif dependency and dependency[0] == 'features' and owner != dependency[1]:
            public = PurePosixPath(target).name in policy['frontend_public_files'] and not dependency[2]
            if not public:
                rules.append('cross-feature-private-import')
    elif dependency:
        public_files = policy['backend_public_files'] if dependency[0] == 'modules' else policy['frontend_public_files']
        if dependency[2] or PurePosixPath(target).name not in public_files:
            rules.append('legacy-to-module-private-import')
    if '/routers/' in source and (target.endswith('/db.py') or target.endswith('/oracle_gateway.py')):
        rules.append('router-direct-database-import')
    if '/services/' in source and '/routers/' in target:
        rules.append('service-to-router')
    return rules


def cycles(graph: dict[str, set[str]]) -> list[set[str]]:
    index = 0
    indices, low, stack, active, found = {}, {}, [], set(), []
    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        active.add(node)
        for target in sorted(graph.get(node, set())):
            if target not in graph:
                continue
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in active:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component = set()
            while True:
                target = stack.pop()
                active.remove(target)
                component.add(target)
                if target == node:
                    break
            if len(component) > 1 or node in graph.get(node, set()):
                found.append(component)
    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return found


def compare_debt(current: Counter, baseline: dict) -> tuple[dict, list[str]]:
    entries = baseline.get('entries', {})
    regressions = {key: {'actual': amount, 'allowed': entries.get(key, {}).get('maximum', 0)}
                   for key, amount in current.items() if amount > entries.get(key, {}).get('maximum', 0)}
    stale = [key for key, entry in entries.items() if current.get(key, 0) < entry['maximum']]
    return regressions, stale
