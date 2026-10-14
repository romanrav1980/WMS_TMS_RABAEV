import ast
from tools.architecture.python_calls import application_receivers, typed_command_execute

def test_only_resolved_unmodified_application_command_is_exempt(tmp_path):
    module="app.modules.inventory.application.command"
    path=tmp_path/"command.py"
    path.write_text("class Command:\n    def execute(self, request): pass\n",encoding="utf-8")
    tree=ast.parse("from app.modules.inventory.application.command import Command\ndef run(command: Command):\n    command.execute(request)\n")
    fn=tree.body[1]
    receivers=application_receivers(tree,fn,"app.routers",{module:path})
    assert receivers==frozenset({"command"})
    assert typed_command_execute(fn.body[0].value,receivers)
    for text in ["command.execute('select * from x')","command.callproc('x')","gateway.execute(request)"]:
        assert not typed_command_execute(ast.parse(text).body[0].value,receivers)
    modified=ast.parse("from app.modules.inventory.application.command import Command\ndef run(command: Command):\n    command=gateway\n    command.execute(request)")
    assert not application_receivers(modified,modified.body[1],"app.routers",{module:path})
