"""Keep startup errors visible when launched without a console on Windows."""
from pathlib import Path
import runpy
import sys
import traceback

root = Path(__file__).resolve().parent
(root / 'runtime').mkdir(exist_ok=True)
sys.stdout = sys.stderr = (root / 'runtime/server.log').open('a', encoding='utf-8', buffering=1)
sys.path.insert(0, str(root))
sys.argv = [str(root / 'server.py'), '--port', '4379']
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
except BaseException:
    traceback.print_exc()
    raise
