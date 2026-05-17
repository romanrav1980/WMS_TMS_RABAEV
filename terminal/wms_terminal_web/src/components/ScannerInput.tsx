import { Button, Input, Space } from "antd";
import { ScanOutlined } from "@ant-design/icons";
import { useScanInput } from "../scanner/useScanInput";

type ScannerInputProps = {
  placeholder: string;
  buttonText?: string;
  disabled?: boolean;
  onScan: (value: string) => void;
};

export function ScannerInput({ placeholder, buttonText = "Сканировать", disabled, onScan }: ScannerInputProps) {
  const scan = useScanInput({ onScan });

  return (
    <Space.Compact className="scan-input">
      <Input
        ref={scan.inputRef}
        value={scan.value}
        onChange={(event) => scan.setValue(event.target.value)}
        onKeyDown={scan.onKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        size="large"
        autoComplete="off"
      />
      <Button type="primary" size="large" icon={<ScanOutlined />} disabled={disabled} onClick={scan.submit}>
        {buttonText}
      </Button>
    </Space.Compact>
  );
}
