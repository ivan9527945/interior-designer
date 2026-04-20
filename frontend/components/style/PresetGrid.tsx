"use client";

import { useQuery } from "@tanstack/react-query";

import { stylesApi, type StyleRecord } from "@/lib/api";
import { cn } from "@/lib/utils";

interface PresetGridProps {
  onSelect: (s: StyleRecord) => void;
  selected?: string;
}

export function PresetGrid({ onSelect, selected }: PresetGridProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["styles", "preset"],
    queryFn: () => stylesApi.list("preset"),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-40 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-destructive">載入預設風格失敗，請稍後再試。</p>
    );
  }

  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">目前沒有預設風格。</p>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {data.map((style) => {
        const palette = Array.isArray(style.schema_json?.color_palette)
          ? (style.schema_json.color_palette as string[]).slice(0, 5)
          : [];

        return (
          <button
            key={style.id}
            type="button"
            onClick={() => onSelect(style)}
            className={cn(
              "flex flex-col gap-2 rounded-lg border p-4 text-left transition-colors hover:bg-accent",
              selected === style.id ? "border-primary ring-1 ring-primary" : "border-border"
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-sm font-medium">{style.name}</span>
              <span className="shrink-0 rounded-full bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                {style.kind}
              </span>
            </div>
            {palette.length > 0 && (
              <div className="flex gap-1">
                {palette.map((color, idx) => (
                  <span
                    key={idx}
                    className="inline-block rounded-sm"
                    style={{ width: 16, height: 16, backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
