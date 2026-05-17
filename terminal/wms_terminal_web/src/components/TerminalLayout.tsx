import { Button, Layout, Menu, Space } from "antd";
import {
  AuditOutlined,
  AppstoreOutlined,
  BarcodeOutlined,
  DatabaseOutlined,
  EnvironmentOutlined,
  HomeOutlined,
  InboxOutlined,
  LogoutOutlined,
  ToolOutlined
} from "@ant-design/icons";
import type { FlowKey, TerminalSession } from "../types";
import type { ReactNode } from "react";
import { API_BASE_URL, TERMINAL_APP_VERSION } from "../config";

const { Header, Sider, Content } = Layout;

type TerminalLayoutProps = {
  activeFlow: FlowKey;
  session: TerminalSession | null;
  onFlowChange: (flow: FlowKey) => void;
  onLogout: () => void;
  children: ReactNode;
};

const items = [
  { key: "home", icon: <HomeOutlined />, label: "Главная" },
  { key: "product", icon: <BarcodeOutlined />, label: "Товар" },
  { key: "lot", icon: <InboxOutlined />, label: "Паллета" },
  { key: "place", icon: <EnvironmentOutlined />, label: "Ячейка" },
  { key: "production", icon: <AppstoreOutlined />, label: "Производство" },
  { key: "legacy", icon: <ToolOutlined />, label: "Legacy" },
  { key: "diagnostics", icon: <DatabaseOutlined />, label: "Диагностика" }
];

export function TerminalLayout({ activeFlow, session, onFlowChange, onLogout, children }: TerminalLayoutProps) {
  return (
    <Layout className="terminal-shell">
      <Sider breakpoint="lg" collapsedWidth="0" width={236} className="terminal-sider">
        <div className="terminal-brand">
          <div className="terminal-brand-mark">W</div>
          <div>
            <strong>WMS TSD</strong>
            <span>terminal web</span>
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[activeFlow]}
          items={items}
          onClick={({ key }) => onFlowChange(key as FlowKey)}
        />
      </Sider>
      <Layout>
        <Header className="terminal-header">
          <Space direction="vertical" size={0}>
            <strong>{session ? `${session.userName} (${session.userId})` : "Оператор не выбран"}</strong>
            <span>API: {API_BASE_URL}</span>
          </Space>
          <Space>
            <span className="app-version">v{TERMINAL_APP_VERSION}</span>
            {session && (
              <Button icon={<LogoutOutlined />} onClick={onLogout}>
                Смена
              </Button>
            )}
          </Space>
        </Header>
        <Content className="terminal-content">{children}</Content>
        <nav className="mobile-flow-bar" aria-label="Быстрая навигация">
          {items.slice(0, 5).map((item) => (
            <button
              key={item.key}
              className={item.key === activeFlow ? "active" : ""}
              onClick={() => onFlowChange(item.key as FlowKey)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
          <button className={activeFlow === "diagnostics" ? "active" : ""} onClick={() => onFlowChange("diagnostics")}>
            <AuditOutlined />
            <span>Связь</span>
          </button>
        </nav>
      </Layout>
    </Layout>
  );
}
