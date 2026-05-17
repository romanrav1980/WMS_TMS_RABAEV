import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import type { InputRef } from "antd";

type UseScanInputOptions = {
  onScan: (value: string) => void;
};

export function useScanInput({ onScan }: UseScanInputOptions) {
  const [value, setValue] = useState("");
  const inputRef = useRef<InputRef | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const submit = () => {
    const normalized = value.trim();
    if (!normalized) return;
    onScan(normalized);
    setValue("");
    requestAnimationFrame(() => inputRef.current?.focus());
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    }
  };

  return {
    value,
    setValue,
    inputRef,
    submit,
    onKeyDown
  };
}
