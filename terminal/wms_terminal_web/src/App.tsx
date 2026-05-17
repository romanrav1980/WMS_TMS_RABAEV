import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Input,
  Modal,
  Row,
  Space,
  Spin,
  Statistic,
  Table,
  Tabs,
  Typography,
  message
} from "antd";
import type { ColumnsType } from "antd/es/table";
import {
  ApiOutlined,
  CheckCircleOutlined,
  CloudSyncOutlined,
  DatabaseOutlined,
  SendOutlined,
  WarningOutlined
} from "@ant-design/icons";
import { getApiErrorMessage } from "./api/client";
import {
  confirmLotCheck,
  confirmPlaceCheck,
  executeLegacyPayload,
  getDbPing,
  getHealth,
  getLotItems,
  getPlaceItems,
  getProductByBarcode,
  getProductionBatchStatus,
  getTerminalUser
} from "./api/wmsApi";
import { LegacyBlocksTable } from "./components/LegacyBlocksTable";
import { ScannerInput } from "./components/ScannerInput";
import { StatusPill } from "./components/StatusPill";
import { TerminalLayout } from "./components/TerminalLayout";
import { API_BASE_URL } from "./config";
import { createJournalEntry, listJournalEntries, saveJournalEntry } from "./store/localJournal";
import { getPalletIdentifierLabel, normalizePalletIdentifier } from "./scanner/identifiers";
import type { DbPingResponse, FlowKey, JournalEntry, LegacyBlock, LegacyExecuteResponse, TerminalSession } from "./types";

const SESSION_KEY = "wms-terminal-session";

function loadSession(): TerminalSession | null {
  try {
    const value = localStorage.getItem(SESSION_KEY);
    return value ? (JSON.parse(value) as TerminalSession) : null;
  } catch {
    return null;
  }
}

function saveSession(session: TerminalSession | null) {
  if (!session) {
    localStorage.removeItem(SESSION_KEY);
    return;
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function getValue(block: LegacyBlock | undefined, keys: string[]): string {
  if (!block) return "";
  for (const key of keys) {
    const value = block.values[key];
    if (value) return value;
  }
  return "";
}

function legacyDateTime(date = new Date()): string {
  const pad = (value: number) => value.toString().padStart(2, "0");
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()} ${pad(date.getHours())}:${pad(
    date.getMinutes()
  )}:${pad(date.getSeconds())}`;
}

function getUserSession(blocks: LegacyBlock[], userId: string): TerminalSession | null {
  const user = blocks.find((block) => block.function_name === "USER_INFO");
  if (!user) return null;
  return {
    userId,
    userName: user.values.NAME || userId,
    wareId: user.values.ware_id,
    rights: user.values,
    signedInAt: new Date().toISOString()
  };
}

function App() {
  const [session, setSession] = useState<TerminalSession | null>(() => loadSession());
  const [activeFlow, setActiveFlow] = useState<FlowKey>("home");
  const [journal, setJournal] = useState<JournalEntry[]>([]);

  const refreshJournal = async () => {
    try {
      setJournal(await listJournalEntries());
    } catch {
      setJournal([]);
    }
  };

  useEffect(() => {
    refreshJournal();
  }, []);

  const handleSession = (nextSession: TerminalSession | null) => {
    setSession(nextSession);
    saveSession(nextSession);
    if (!nextSession) setActiveFlow("home");
  };

  const page = useMemo(() => {
    if (!session) return <LoginPage onLogin={handleSession} />;
    if (activeFlow === "product") return <ProductLookup onJournal={refreshJournal} />;
    if (activeFlow === "lot") return <LotCheck session={session} onJournal={refreshJournal} />;
    if (activeFlow === "place") return <PlaceAudit session={session} onJournal={refreshJournal} />;
    if (activeFlow === "production") return <ProductionTrace />;
    if (activeFlow === "legacy") return <LegacyConsole session={session} />;
    if (activeFlow === "diagnostics") return <Diagnostics journal={journal} onRefreshJournal={refreshJournal} />;
    return <Home session={session} onFlowChange={setActiveFlow} />;
  }, [activeFlow, journal, session]);

  return (
    <TerminalLayout activeFlow={activeFlow} session={session} onFlowChange={setActiveFlow} onLogout={() => handleSession(null)}>
      {page}
    </TerminalLayout>
  );
}

function LoginPage({ onLogin }: { onLogin: (session: TerminalSession) => void }) {
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const login = async (scanValue?: string) => {
    const nextUserId = (scanValue || userId).trim();
    if (!nextUserId) return;
    setLoading(true);
    setError("");
    try {
      const blocks = await getTerminalUser(nextUserId);
      const session = getUserSession(blocks, nextUserId);
      if (!session) throw new Error("Пользователь не найден или не активен.");
      onLogin(session);
      message.success(`Вход выполнен: ${session.userName}`);
    } catch (error) {
      setError(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <Card className="login-card">
        <Space direction="vertical" size="large" className="full-width">
          <div>
            <Typography.Title level={2}>WMS Terminal</Typography.Title>
            <Typography.Text type="secondary">Вход оператора через WMS API / GET_RUSER</Typography.Text>
          </div>
          {error && <Alert type="error" showIcon message={error} />}
          <Input
            size="large"
            value={userId}
            onChange={(event) => setUserId(event.target.value)}
            onPressEnter={() => login()}
            placeholder="Код оператора"
            autoFocus
          />
          <Button type="primary" size="large" block loading={loading} onClick={() => login()}>
            Войти
          </Button>
          <ScannerInput placeholder="Или отсканируйте код оператора" disabled={loading} onScan={login} />
        </Space>
      </Card>
    </div>
  );
}

function Home({ session, onFlowChange }: { session: TerminalSession; onFlowChange: (flow: FlowKey) => void }) {
  const cards = [
    { flow: "product" as FlowKey, title: "Товар", text: "Поиск по EAN/DataMatrix", icon: <ApiOutlined /> },
    { flow: "lot" as FlowKey, title: "Паллета", text: "GET_LOT_ITEMS и подтверждение", icon: <CheckCircleOutlined /> },
    { flow: "place" as FlowKey, title: "Ячейка", text: "Остатки и ревизия места", icon: <DatabaseOutlined /> },
    { flow: "production" as FlowKey, title: "Производство", text: "Партии, SSCC, CRPT, Mercury", icon: <CloudSyncOutlined /> },
    { flow: "legacy" as FlowKey, title: "Legacy", text: "Тест FUNC=...| протокола", icon: <WarningOutlined /> },
    { flow: "diagnostics" as FlowKey, title: "Связь", text: "API, Oracle, журнал", icon: <DatabaseOutlined /> }
  ];

  return (
    <Space direction="vertical" size="large" className="full-width">
      <section className="operator-strip">
        <div>
          <Typography.Title level={3}>Смена оператора: {session.userName}</Typography.Title>
          <Typography.Text type="secondary">Склад: {session.wareId || "не указан"} | вход: {new Date(session.signedInAt).toLocaleString()}</Typography.Text>
        </div>
        <StatusPill status="ok">online-first</StatusPill>
      </section>
      <Row gutter={[16, 16]}>
        {cards.map((card) => (
          <Col xs={24} sm={12} xl={8} key={card.flow}>
            <button className="flow-card" onClick={() => onFlowChange(card.flow)}>
              <span className="flow-card-icon">{card.icon}</span>
              <strong>{card.title}</strong>
              <small>{card.text}</small>
            </button>
          </Col>
        ))}
      </Row>
    </Space>
  );
}

function ProductLookup({ onJournal }: { onJournal: () => void }) {
  const [blocks, setBlocks] = useState<LegacyBlock[]>([]);
  const [barcode, setBarcode] = useState("");
  const [loading, setLoading] = useState(false);
  const product = blocks.find((block) => block.function_name === "END_GET_PRODUCT_INFO");

  const scan = async (value: string) => {
    setBarcode(value);
    setLoading(true);
    try {
      const response = await getProductByBarcode(value);
      setBlocks(response);
      if (!response.length) message.warning("Товар не найден.");
      const entry = createJournalEntry("product-lookup", value, { barcode: value, resultCount: response.length });
      entry.status = response.length ? "accepted" : "rejected";
      entry.updatedAt = new Date().toISOString();
      await saveJournalEntry(entry);
      onJournal();
    } catch (error) {
      message.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <TerminalPage title="Поиск товара" subtitle="GET_PRODUCT_INFO через WMS API">
      <ScannerInput placeholder="Скан EAN / DataMatrix / штрихкод" disabled={loading} onScan={scan} />
      <Spin spinning={loading}>
        {barcode && <Typography.Text type="secondary">Последний скан: {barcode}</Typography.Text>}
        {product ? (
          <Descriptions bordered size="small" column={1} className="result-descriptions">
            <Descriptions.Item label="UID">{getValue(product, ["УИД"])}</Descriptions.Item>
            <Descriptions.Item label="Наименование">{getValue(product, ["ИМЯ"])}</Descriptions.Item>
            <Descriptions.Item label="Адрес">{getValue(product, ["АДРЕС"])}</Descriptions.Item>
            <Descriptions.Item label="ШК штуки">{getValue(product, ["ШК_ШТУКИ"])}</Descriptions.Item>
            <Descriptions.Item label="ШК блока">{getValue(product, ["ШК_БЛОКА"])}</Descriptions.Item>
            <Descriptions.Item label="ШК короба">{getValue(product, ["ШК_КОРОБ"])}</Descriptions.Item>
          </Descriptions>
        ) : (
          <Empty description="Отсканируйте товар" />
        )}
        <LegacyBlocksTable blocks={blocks} />
      </Spin>
    </TerminalPage>
  );
}

function LotCheck({ session, onJournal }: { session: TerminalSession; onJournal: () => void }) {
  const [usscc, setUsscc] = useState("");
  const [response, setResponse] = useState<LegacyExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  const lotLines = response?.blocks.filter((block) => block.function_name === "LOT_LINE") || [];
  const summary = response?.blocks.find((block) => block.function_name === "LOT_LINES");

  const scan = async (value: string) => {
    const identifier = normalizePalletIdentifier(value);
    setUsscc(identifier.value);
    if (identifier.changed) {
      message.info(`Скан нормализован: ${getPalletIdentifierLabel(identifier)}`);
    }
    setLoading(true);
    try {
      setResponse(await getLotItems(identifier.value));
    } catch (error) {
      message.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const confirmOk = () => {
    Modal.confirm({
      title: "Подтвердить проверку паллеты без ошибок?",
      content: `Будет выполнен POST /api/terminal/lots/${usscc}/check и запись в Oracle через совместимый Tserver-flow.`,
      okText: "Подтвердить",
      cancelText: "Отмена",
      onOk: async () => {
        setSending(true);
        const payload = {
          user_id: session.userId,
          error_count: 0,
          errors: [],
          vp_lines: lotLines
            .map((line) => getValue(line, ["УИД"]))
            .filter(Boolean)
            .map((uid) => ({ pallet_uid: usscc, uid, checked_at: legacyDateTime() }))
        };
        const entry = createJournalEntry("lot-check", usscc, { palletIdentifier: usscc, ...payload });
        try {
          entry.status = "sent";
          await saveJournalEntry(entry);
          await confirmLotCheck(usscc, payload);
          entry.status = "accepted";
          entry.message = "END_LOT_CHECK_PASSED";
          message.success("Паллета подтверждена.");
        } catch (error) {
          entry.status = "rejected";
          entry.message = getApiErrorMessage(error);
          message.error(entry.message);
        } finally {
          entry.updatedAt = new Date().toISOString();
          await saveJournalEntry(entry);
          onJournal();
          setSending(false);
        }
      }
    });
  };

  return (
    <TerminalPage title="Проверка паллеты / лота" subtitle="GET_LOT_ITEMS + LOT_CHECK_PASSED">
      <ScannerInput placeholder="Идентификатор паллеты: UID или SSCC" disabled={loading || sending} onScan={scan} />
      <Spin spinning={loading || sending}>
        {summary && (
          <Row gutter={[16, 16]} className="stats-row">
            <Col span={8}><Statistic title="Паллета" value={usscc} /></Col>
            <Col span={8}><Statistic title="Строк" value={summary.values.lines_count_must_be || lotLines.length} /></Col>
            <Col span={8}><Statistic title="Заказ" value={summary.values.order_number || "-"} /></Col>
          </Row>
        )}
        {response ? (
          <>
            <Button type="primary" size="large" icon={<SendOutlined />} disabled={!lotLines.length} onClick={confirmOk}>
              Подтвердить без ошибок
            </Button>
            <LegacyBlocksTable blocks={response.blocks} />
          </>
        ) : (
          <Empty description="Отсканируйте паллету" />
        )}
      </Spin>
    </TerminalPage>
  );
}

function PlaceAudit({ session, onJournal }: { session: TerminalSession; onJournal: () => void }) {
  const [placeId, setPlaceId] = useState("");
  const [response, setResponse] = useState<LegacyExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const placeLines = response?.blocks.filter((block) => block.function_name === "PL") || [];

  const scan = async (value: string) => {
    setPlaceId(value);
    setLoading(true);
    try {
      setResponse(await getPlaceItems(value));
    } catch (error) {
      message.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const confirmMatched = () => {
    Modal.confirm({
      title: "Подтвердить ревизию ячейки без расхождений?",
      content: "Это write-операция PLACE_CHECK_PASSED через WMS API.",
      okText: "Подтвердить",
      cancelText: "Отмена",
      onOk: async () => {
        const payload = { pallet_id: placeId, errors: [], inventory_lines: [] };
        const entry = createJournalEntry("place-check", placeId, { ...payload, user: session.userId });
        try {
          entry.status = "sent";
          await saveJournalEntry(entry);
          await confirmPlaceCheck(payload);
          entry.status = "accepted";
          entry.message = "END_PALLET_CHECK_PASSED";
          message.success("Ревизия ячейки подтверждена.");
        } catch (error) {
          entry.status = "rejected";
          entry.message = getApiErrorMessage(error);
          message.error(entry.message);
        } finally {
          entry.updatedAt = new Date().toISOString();
          await saveJournalEntry(entry);
          onJournal();
        }
      }
    });
  };

  return (
    <TerminalPage title="Проверка ячейки" subtitle="GET_PLACE_ITEMS + PLACE_CHECK_PASSED">
      <ScannerInput placeholder="Скан ячейки / места" disabled={loading} onScan={scan} />
      <Spin spinning={loading}>
        {response ? (
          <>
            <Row gutter={[16, 16]} className="stats-row">
              <Col span={12}><Statistic title="Ячейка" value={placeId} /></Col>
              <Col span={12}><Statistic title="Строк остатков" value={placeLines.length} /></Col>
            </Row>
            <Button type="primary" size="large" icon={<SendOutlined />} onClick={confirmMatched}>
              Подтвердить без расхождений
            </Button>
            <LegacyBlocksTable blocks={response.blocks} />
          </>
        ) : (
          <Empty description="Отсканируйте ячейку" />
        )}
      </Spin>
    </TerminalPage>
  );
}

function ProductionTrace() {
  const [batchId, setBatchId] = useState("");
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);

  const load = async (value?: string) => {
    const id = (value || batchId).trim();
    if (!id) return;
    setBatchId(id);
    setLoading(true);
    try {
      setStatus(await getProductionBatchStatus(id));
    } catch (error) {
      setStatus(null);
      message.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <TerminalPage title="Производство и прослеживаемость" subtitle="Партии, SSCC, CRPT, Mercury">
      <ScannerInput placeholder="ID партии производства" disabled={loading} onScan={load} />
      <Space.Compact className="manual-input">
        <Input value={batchId} onChange={(event) => setBatchId(event.target.value)} onPressEnter={() => load()} />
        <Button type="primary" loading={loading} onClick={() => load()}>Проверить</Button>
      </Space.Compact>
      <Spin spinning={loading}>
        {status ? <pre className="json-view">{JSON.stringify(status, null, 2)}</pre> : <Empty description="Введите ID партии" />}
      </Spin>
    </TerminalPage>
  );
}

function LegacyConsole({ session }: { session: TerminalSession }) {
  const [payload, setPayload] = useState(`FUNC=GET_RUSER|USERID=${session.userId}|`);
  const [response, setResponse] = useState<LegacyExecuteResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const execute = async () => {
    setLoading(true);
    try {
      setResponse(await executeLegacyPayload(payload));
    } catch (error) {
      message.error(getApiErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <TerminalPage title="Legacy Tserver console" subtitle="Тест совместимости FUNC=...| протокола">
      <Input.TextArea rows={5} value={payload} onChange={(event) => setPayload(event.target.value)} />
      <Button type="primary" loading={loading} onClick={execute}>Выполнить</Button>
      {response && (
        <>
          <Alert type="info" showIcon message="Encoded legacy response" description={<code>{response.payload}</code>} />
          <LegacyBlocksTable blocks={response.blocks} />
        </>
      )}
    </TerminalPage>
  );
}

function Diagnostics({ journal, onRefreshJournal }: { journal: JournalEntry[]; onRefreshJournal: () => void }) {
  const [health, setHealth] = useState<string>("unknown");
  const [db, setDb] = useState<DbPingResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const [healthResponse, dbResponse] = await Promise.all([getHealth(), getDbPing()]);
      setHealth(healthResponse.status);
      setDb(dbResponse);
      message.success("Связь с API и Oracle проверена.");
    } catch (error) {
      setHealth("error");
      setDb(null);
      message.error(getApiErrorMessage(error));
    } finally {
      await onRefreshJournal();
      setLoading(false);
    }
  };

  const columns: ColumnsType<JournalEntry> = [
    { title: "Время", dataIndex: "createdAt", render: (value: string) => new Date(value).toLocaleString() },
    { title: "Flow", dataIndex: "flow" },
    { title: "Ресурс", dataIndex: "resourceKey" },
    { title: "Статус", dataIndex: "status" },
    { title: "Сообщение", dataIndex: "message" }
  ];

  return (
    <TerminalPage title="Диагностика" subtitle="API, Oracle и локальный журнал устройства">
      <Button type="primary" size="large" loading={loading} onClick={run}>Проверить связь</Button>
      <Row gutter={[16, 16]} className="stats-row">
        <Col xs={24} md={8}><Card><Statistic title="API" value={health} /></Card></Col>
        <Col xs={24} md={8}><Card><Statistic title="Oracle user" value={db?.user_name || "-"} /></Card></Col>
        <Col xs={24} md={8}><Card><Statistic title="Service" value={db?.service_name || API_BASE_URL} /></Card></Col>
      </Row>
      <Table columns={columns} dataSource={journal} rowKey="id" size="small" pagination={{ pageSize: 8 }} scroll={{ x: true }} />
    </TerminalPage>
  );
}

function TerminalPage({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <Space direction="vertical" size="large" className="full-width terminal-page">
      <div className="page-title">
        <div>
          <Typography.Title level={2}>{title}</Typography.Title>
          <Typography.Text type="secondary">{subtitle}</Typography.Text>
        </div>
      </div>
      {children}
    </Space>
  );
}

export default App;
