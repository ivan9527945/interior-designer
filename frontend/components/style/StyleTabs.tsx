"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

const TABS = [
  { key: "preset", label: "預設風格" },
  { key: "text", label: "文字描述" },
  { key: "visual", label: "視覺參考" },
] as const;

export type StyleTabKey = (typeof TABS)[number]["key"];

export function StyleTabs({ onChange }: { onChange?: (k: StyleTabKey) => void }) {
  const [active, setActive] = useState<StyleTabKey>("preset");
  return (
    <div className="flex gap-1 border-b">
      {TABS.map((t) => (
        <button
          key={t.key}
          type="button"
          onClick={() => {
            setActive(t.key);
            onChange?.(t.key);
          }}
          className={cn(
            "border-b-2 px-4 py-2 text-sm",
            active === t.key
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground"
          )}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
