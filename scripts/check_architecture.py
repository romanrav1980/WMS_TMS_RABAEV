"""NICORA architecture gate: AST boundaries, cycles and non-growing legacy debt."""
from __future__ import annotations
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.architecture.rules import compare_debt, cycles, feature, import_rules


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def python_records(root: Path, policy: dict) -> list[dict]:
    source_root = root / policy['python_root']
    names = {}
    for path in sorted(source_root.rglob('*.py')):
        if '__pycache__' in path.parts:
            continue
        relative = path.relative_to(source_root).with_suffix('')
        parts = list(relative.parts)
        if parts[-1] == '__init__':
            parts.pop()
        names['.'.join(['app'] + parts)] = path
    records = []
    for module, path in names.items():
        text = path.read_text(encoding='utf-8-sig')
        record = {'path': path.relative_to(root).as_posix(), 'lines': len(text.splitlines()),
                  'imports': [], 'functions': [], 'errors': [], 'violations': []}
        records.append(record)
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            record['errors'].append(str(exc))
            continue
        owner = feature(record['path'])
        package = module if path.name == '__init__.py' else module.rpartition('.')[0]
        def resolve(name: str, node: ast.AST, type_only: bool) -> None:
            if name.startswith('api.wms_api_server.app'):
                name = 'app' + name[len('api.wms_api_server.app'):]
            candidate = name
            while candidate and candidate not in names:
                candidate = candidate.rpartition('.')[0]
            if candidate in names:
                target = names[candidate].relative_to(root).as_posix()
                record['imports'].append({'target': target, 'typeOnly': type_only})
            elif name == 'app' or name.startswith('app.'):
                record['errors'].append('Unresolved local import: ' + name)
            elif owner and owner[2] == 'domain' and name.split('.')[0] not in sys.stdlib_module_names:
                record['violations'].append('domain-external-dependency:' + name)
        def walk(node: ast.AST, scope: tuple[str, ...] = (), type_only: bool = False) -> None:
            if isinstance(node, ast.If) and (isinstance(node.test, ast.Name) and node.test.id == 'TYPE_CHECKING' or
                    isinstance(node.test, ast.Attribute) and node.test.attr == 'TYPE_CHECKING'):
                for child in node.body:
                    walk(child, scope, True)
                for child in node.orelse:
                    walk(child, scope, type_only)
                return
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolve(alias.name, node, type_only)
            elif isinstance(node, ast.ImportFrom):
                name = node.module or ''
                if node.level:
                    try:
                        name = importlib.util.resolve_name('.' * node.level + name, package)
                    except ImportError as exc:
                        record['errors'].append(str(exc))
                        return
                for alias in node.names:
                    resolve(name + '.' + alias.name, node, type_only)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified = '.'.join(scope + (node.name,))
                record['functions'].append({'name': qualified, 'lines': node.end_lineno - node.lineno + 1})
                if owner:
                    arguments = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                    arguments += [arg for arg in (node.args.vararg, node.args.kwarg) if arg]
                    if node.returns is None or any(arg.annotation is None and arg.arg not in ('self', 'cls') for arg in arguments):
                        record['violations'].append('new-module-untyped-function:' + qualified)
                scope += (node.name,)
            elif isinstance(node, ast.ClassDef):
                scope += (node.name,)
            if isinstance(node, ast.Call):
                function = node.func
                dynamic = (isinstance(function, ast.Name) and function.id in ('__import__', 'import_module') or
                           isinstance(function, ast.Attribute) and function.attr == 'import_module')
                if dynamic:
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        resolve(node.args[0].value, node, type_only)
                    elif owner:
                        record['errors'].append('Non-literal dynamic import requires explicit architecture review')
            if isinstance(node, ast.Call) and owner:
                function = node.func
                if isinstance(function, ast.Attribute) and function.attr in ('commit', 'rollback') and owner[2] in ('api', 'application', 'domain'):
                    record['violations'].append('transaction-outside-unit-of-work:' + '.'.join(scope))
                if isinstance(function, ast.Attribute) and function.attr in ('execute', 'executemany', 'callproc', 'callfunc') and owner[2] in ('api', 'application', 'domain'):
                    record['violations'].append('database-call-outside-infrastructure:' + '.'.join(scope))
            for child in ast.iter_child_nodes(node):
                walk(child, scope, type_only)
        walk(tree)
    return records


def collect(root: Path, policy: dict) -> tuple[Counter, dict, list[str]]:
    records = python_records(root, policy)
    for frontend in policy['frontend_roots']:
        result = subprocess.run(['node', str(ROOT / 'tools/architecture/frontend_graph.cjs'), str(root), frontend],
                                capture_output=True, text=True, encoding='utf-8', timeout=60)
        if result.returncode:
            raise RuntimeError(f'Cannot inspect {frontend}: {result.stderr[-2000:]}')
        records.extend(json.loads(result.stdout))
    debt = Counter()
    errors = []
    graph = {record['path']: set() for record in records}
    for record in records:
        path = record['path']
        errors.extend(path + ': ' + error for error in record['errors'])
        owner = feature(path)
        if owner and owner[1] not in policy['domains']:
            errors.append(path + ': module owner is not registered')
        if owner and owner[0] == 'modules' and owner[2] and owner[2] not in policy['layers']:
            errors.append(path + ': unregistered module layer')
        if record['lines'] > policy['limits']['file_lines']:
            debt['file-size:' + path] = record['lines']
        for function in record['functions']:
            if function['lines'] > policy['limits']['function_lines']:
                debt['function-size:' + path + ':' + function['name']] += function['lines']
        for violation in record.get('violations', []):
            debt[violation + ':' + path] += 1
        for dependency in record['imports']:
            target = dependency['target']
            for rule in import_rules(path, target, policy):
                debt[rule + ':' + path + ' -> ' + target] += 1
            if not dependency['typeOnly'] and target in graph:
                graph[path].add(target)
    for component in cycles(graph):
        # Edge-specific allowances block any added edge, even inside an existing cycle.
        for source in sorted(component):
            for target in sorted(graph[source] & component):
                debt['cycle-edge:' + source + ' -> ' + target] = 1
    return debt, {'files': len(records), 'cycle_components': len(cycles(graph)),
                  'debt_items': len(debt)}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, default=ROOT / 'config/architecture/nicora-policy.json')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'config/architecture/legacy-debt.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'tmp/nicora_quality/architecture.json')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--capture-baseline', action='store_true', help='One-time initial snapshot; refuses to replace existing debt.')
    action.add_argument('--tighten-baseline', action='store_true', help='Only remove/reduce allowances; cannot authorize new debt.')
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text(encoding='utf-8'))
    debt, stats, errors = collect(ROOT, policy)
    if errors:
        write_json(args.report, {'passed': False, 'errors': errors, **stats})
        print('\n'.join(errors[:20]))
        return 1
    if args.capture_baseline:
        if args.baseline.exists():
            raise SystemExit('Existing baseline cannot be overwritten. Tighten it or explicitly review policy/debt changes.')
        baseline = {'version': 1, 'captured_at': datetime.now(timezone.utc).isoformat(),
                    'entries': {key: {'maximum': amount, 'owner': policy['debt_owner'],
                                     'reason': policy['debt_reason'], 'remediation': policy['debt_remediation']}
                                for key, amount in sorted(debt.items())}}
        write_json(args.baseline, baseline)
    else:
        baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
    regressions, stale = compare_debt(debt, baseline)
    if args.tighten_baseline and not regressions:
        baseline['entries'] = {key: {**baseline['entries'][key], 'maximum': amount} for key, amount in sorted(debt.items())}
        write_json(args.baseline, baseline)
        stale = []
    invalid_entries = [key for key, entry in baseline.get('entries', {}).items()
                       if not all(entry.get(field) for field in ('owner', 'reason', 'remediation', 'maximum'))]
    passed = not (regressions or stale or invalid_entries)
    write_json(args.report, {'passed': passed, **stats, 'regressions': regressions,
                            'stale_allowances': stale, 'invalid_debt_entries': invalid_entries})
    print(f'Architecture: {"PASS" if passed else "FAIL"}; {stats}')
    for key, result in list(regressions.items())[:15]:
        print(f'NEW/GROWN: {key} ({result["actual"]} > {result["allowed"]})')
    if stale:
        print('Debt decreased: run --tighten-baseline and review the smaller allowance file.')
    return int(not passed)


if __name__ == '__main__':
    raise SystemExit(main())
