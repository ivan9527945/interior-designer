"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { stylesApi, type StyleRecord } from "@/lib/api";
import { cn } from "@/lib/utils";

type KindKey = "preset" | "team" | "personal";

const TABS: { key: KindKey; label: string }[] = [
  { key: "preset", label: "預設" },
  { key: "team", label: "團隊" },
  { key: "personal", label: "個人" },
];

function StyleCard({ style }: { style: StyleRecord }) {
  const palette = Array.isArray(style.schema_json?.color_palette)
    ? (style.schema_json.color_palette as string[]).slice(0, 5)
    : [];

  const date = new Date(style.created_at).toLocaleDateString("zh-TW");

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border p-4">
      <div className="flex items-start justify-between gap-2">
        <p className="truncate text-sm font-medium">{style.name}</p>
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
      <p className="text-xs text-muted-foreground">{date}</p>
    </div>
  );
}

export default function StylesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const kind: KindKey = (searchParams.get("kind") as KindKey) ?? "preset";

  const { data, isLoading, isError } = useQuery({
    queryKey: ["styles", kind],
    queryFn: () => stylesApi.list(kind),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">風格庫</h1>
        <button
          type="button"
          onClick={() => router.push("/projects")}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          新增個人風格
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => router.push(`/styles?kind=${t.key}`)}
            className={cn(
              "border-b-2 px-4 py-2 text-sm",
              kind === t.key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      )}

      {isError && (
        <p className="text-sm text-destructive">載入失敗，請稍後再試。</p>
      )}

      {!isLoading && !isError && data && data.length === 0 && (
        <p className="text-sm text-muted-foreground">此分類尚無風格。</p>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {data.map((style) => (
            <StyleCard key={style.id} style={style} />
          ))}
        </div>
      )}
    </div>
  );
}
