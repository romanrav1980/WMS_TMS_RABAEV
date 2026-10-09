import json
from pathlib import Path
p=Path("WindowsApplication2/WindowsApplication2/StockCommandIntent.cs");s=p.read_text(encoding="utf-8")
start=s.index('                root.SetAttribute("command", command.CommandText);')
end=s.index('                document.AppendChild(root);',start)
part=s[start:end]
half=part[:part.index('                root.SetAttribute("command", command.CommandText);',1)]
assert part==half+half
s=s[:start]+half+s[end:]
s=s.replace("new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None)","new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough)")
print(json.dumps({str(p):s},ensure_ascii=True))
