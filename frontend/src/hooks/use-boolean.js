"use client";
import { useCallback, useState } from "react";

export function useBoolean(initialValue) {
  const [value, setValue] = useState(initialValue || false);
  const onToggle = useCallback(() => setValue((prev) => !prev), []);
  const onTrue = useCallback(() => setValue(true), []);
  const onFalse = useCallback(() => setValue(false), []);
  const onSet = useCallback((newValue) => setValue(newValue), []);
  return { value, onToggle, onTrue, onFalse, onSet };
}
