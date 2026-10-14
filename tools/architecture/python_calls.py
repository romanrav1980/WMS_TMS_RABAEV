"""Resolve typed application command receivers; execute is not always a DB call."""
import ast
import importlib.util
import re
from pathlib import Path

def application_receivers(tree: ast.Module,function: ast.FunctionDef|ast.AsyncFunctionDef,package: str,names: dict[str,Path]) -> frozenset[str]:
    imports={}
    for node in tree.body:
        if not isinstance(node,ast.ImportFrom):continue
        module=node.module or ""
        if node.level:
            try:module=importlib.util.resolve_name("."*node.level+module,package)
            except ImportError:continue
        if ".modules."not in module or ".application."not in module:continue
        for item in node.names:imports[item.asname or item.name]=(module,item.name)
    assigned={node.id for node in ast.walk(function)if isinstance(node,ast.Name)and isinstance(node.ctx,ast.Store)}
    result=set()
    for argument in function.args.posonlyargs+function.args.args+function.args.kwonlyargs:
        annotation=argument.annotation
        if not isinstance(annotation,ast.Name)or annotation.id not in imports or argument.arg in assigned:continue
        module,class_name=imports[annotation.id];path=names.get(module)
        if path is None:continue
        target=ast.parse(path.read_text(encoding="utf-8-sig"))
        classes=[node for node in target.body if isinstance(node,ast.ClassDef)and node.name==class_name and not node.bases]
        if len(classes)!=1:continue
        methods=[node for node in classes[0].body if isinstance(node,ast.FunctionDef)and node.name=="execute"]
        if len(methods)==1:
            result.add(argument.arg)
    return frozenset(result)

def typed_command_execute(node: ast.Call,receivers: frozenset[str]) -> bool:
    target=node.func
    if not isinstance(target,ast.Attribute)or target.attr!="execute"or not isinstance(target.value,ast.Name)or target.value.id not in receivers:return False
    if node.args and isinstance(node.args[0],ast.Constant)and isinstance(node.args[0].value,str):
        if re.match(r"\s*(select|with|insert|update|delete|merge|begin|declare|alter|create|drop|truncate)\b",node.args[0].value,re.I):return False
    return True
