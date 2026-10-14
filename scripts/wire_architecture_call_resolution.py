from pathlib import Path
import json
p=Path('scripts/check_architecture.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('from tools.architecture.rules import compare_debt, cycles, feature, import_rules','from tools.architecture.rules import compare_debt, cycles, feature, import_rules\nfrom tools.architecture.python_calls import application_receivers,typed_command_execute')
s=s.replace('def walk(node: ast.AST, scope: tuple[str, ...] = (), type_only: bool = False) -> None:', 'def walk(node: ast.AST, scope: tuple[str, ...] = (), type_only: bool = False, receivers: frozenset[str] = frozenset()) -> None:')
s=s.replace('walk(child, scope, True)', 'walk(child, scope, True,receivers)').replace('walk(child, scope, type_only)', 'walk(child, scope, type_only,receivers)')
s=s.replace("                qualified = '.'.join(scope + (node.name,))", "                receivers=application_receivers(tree,node,package,names)\n                qualified = '.'.join(scope + (node.name,))")
old="if isinstance(function, ast.Attribute) and function.attr in ('execute', 'executemany', 'callproc', 'callfunc') and owner[2] in ('api', 'application', 'domain'):"
new=old[:-1]+" and not typed_command_execute(node,receivers):"
assert old in s;s=s.replace(old,new)
print(json.dumps({str(p):s},ensure_ascii=True))
