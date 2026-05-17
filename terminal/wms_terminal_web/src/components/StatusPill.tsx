import { Tag } from "antd";
import type { ReactNode } from "react";

type StatusPillProps = {
  status: "ok" | "warn" | "error" | "idle";
  children: ReactNode;
};

const colors = {
  ok: "success",
  warn: "warning",
  error: "error",
  idle: "processing"
} as const;

export function StatusPill({ status, children }: StatusPillProps) {
  return <Tag color={colors[status]}>{children}</Tag>;
}
