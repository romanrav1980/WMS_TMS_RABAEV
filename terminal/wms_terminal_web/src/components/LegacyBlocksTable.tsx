import { Empty, Table } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { LegacyBlock } from "../types";

type Row = {
  key: string;
  index: number;
  functionName: string;
  values: string;
};

const columns: ColumnsType<Row> = [
  { title: "#", dataIndex: "index", width: 58 },
  { title: "Блок", dataIndex: "functionName", width: 190 },
  { title: "Значения", dataIndex: "values" }
];

export function LegacyBlocksTable({ blocks }: { blocks: LegacyBlock[] }) {
  if (!blocks.length) return <Empty description="Нет данных" />;

  const rows = blocks.map((block, index) => ({
    key: `${block.function_name}-${index}`,
    index: index + 1,
    functionName: block.function_name,
    values: Object.entries(block.values)
      .map(([key, value]) => `${key}: ${value}`)
      .join(" | ")
  }));

  return <Table columns={columns} dataSource={rows} pagination={false} size="small" scroll={{ x: true }} />;
}
