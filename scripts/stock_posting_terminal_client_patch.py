import json
from pathlib import Path
out={}
p=Path("terminal/wms_terminal_web/src/types.ts");s=p.read_text(encoding="utf-8")
s=s.replace('"draft" | "sent" | "accepted" | "rejected"','"draft" | "sent" | "accepted" | "rejected" | "uncertain"',1)
s=s.replace("export type LotCheckPayload = {","export type LotCheckPayload = {\n  operation_id?: string;",1)
out[str(p)]=s
p=Path("terminal/wms_terminal_web/src/App.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('import { getApiErrorMessage } from "./api/client";','import { getApiErrorMessage } from "./api/client";\nimport { authenticateTerminal, clearTerminalAuth, hasTerminalAuth } from "./api/terminalAuth";\nimport { postLotQuality, hasLotQualityIntent } from "./api/lotQualityIntent";',1)
s=s.replace("    confirmLotCheck,\n","") if "    confirmLotCheck,\n" in s else s.replace("  confirmLotCheck,\n","",1)
s=s.replace("    return value ? (JSON.parse(value) as TerminalSession) : null;","    return value && hasTerminalAuth() ? (JSON.parse(value) as TerminalSession) : null;",1)
s=s.replace("    if (!nextSession) setActiveFlow(\"home\");","    if (!nextSession) { clearTerminalAuth(); setActiveFlow(\"home\"); }",1)
s=s.replace('const [userId, setUserId] = useState("");','const [userId, setUserId] = useState("");\n  const [password, setPassword] = useState("");',1)
s=s.replace('const blocks = await getTerminalUser(nextUserId);\n      const session = getUserSession(blocks, nextUserId);','const identity = await authenticateTerminal(nextUserId, password);\n      const blocks = await getTerminalUser(identity.username);\n      const session = getUserSession(blocks, identity.username);',1)
s=s.replace('if (!session) throw new Error("Пользователь не найден или не активен.");','if (!session) { clearTerminalAuth(); throw new Error("Пользователь не найден или не активен."); }',1)
s=s.replace('onLogin(session);\n      message.success','setPassword("");\n      onLogin(session);\n      message.success',1)
s=s.replace('Вход оператора через WMS API / GET_RUSER','Вход оператора WMS',1)
needle='''          <Button type="primary" size="large" block loading={loading} onClick={() => login()}>'''
replacement='''          <Input.Password size="large" value={password} onChange={event => setPassword(event.target.value)}
            onPressEnter={() => login()} placeholder="Пароль" autoComplete="current-password" />
'''+needle
assert needle in s;s=s.replace(needle,replacement,1)
s=s.replace('content: `Будет выполнен POST /api/terminal/lots/${usscc}/check и запись в Oracle через совместимый Tserver-flow.`,','content: "Результат проверки будет сохранён системой.",',1)
at=s.index('        const entry = createJournalEntry("lot-check", usscc,')
end=s.index("      }\n    });",at)
replacement='''        try {
          await postLotQuality(usscc, session.userId, payload, false);
          message.success("Паллета подтверждена.");
        } catch (error) {
          message.error(getApiErrorMessage(error));
        } finally {
          await onJournal();
          setSending(false);
        }
'''
s=s[:at]+replacement+s[end:]
# Retry reconstructs the original payload inside the intent boundary, never from newly read lines.
needle='''            <LegacyBlocksTable blocks={response.blocks} />'''
at=s.index(needle,s.index("function LotCheck"))
replacement='''            <Button size="large" disabled={sending || !hasLotQualityIntent(usscc, session.userId)}
              onClick={async () => {
                setSending(true);
                try {
                  await postLotQuality(usscc, session.userId, { user_id: session.userId, error_count: 0, errors: [], vp_lines: [] }, true);
                  message.success("Сохранённая проверка подтверждена.");
                } catch (error) { message.error(getApiErrorMessage(error)); }
                finally { await onJournal(); setSending(false); }
              }}>Повторить сохранённую проверку</Button>
'''+needle
s=s[:at]+s[at:].replace(needle,replacement,1)
out[str(p)]=s
p=Path("terminal/wms_terminal_web/src/components/StatusPill.tsx");s=p.read_text(encoding="utf-8")
# Read actual status component; extend its maps below only where present.
s=s.replace('rejected: "error"','rejected: "error", uncertain: "warning"')
s=s.replace('rejected: "Отклонено"','rejected: "Отклонено", uncertain: "Исход не подтверждён"')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
