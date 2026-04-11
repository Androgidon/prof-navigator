"use client";

import { useMemo } from "react";

export function useDirtyFormState<T>(initialData: T | null, currentData: T | null) {
  return useMemo(() => {
    if (!initialData || !currentData) {
      return false;
    }
    return JSON.stringify(initialData) !== JSON.stringify(currentData);
  }, [initialData, currentData]);
}
