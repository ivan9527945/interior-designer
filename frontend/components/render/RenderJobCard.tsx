"use client";

import { useRenderProgress } from "@/hooks/useRenderProgress";
import { useRenderQueueStore } from "@/stores/useRenderQueueStore";

export function RenderJobCard({ renderId }: { renderId: string }) {
  useRenderProgress(renderId);
  const progress = useRenderQueueStore((s) => s.byId[renderId]) ?? {
    status: "unknown" as const,
    percent: 0,
  };

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-mono text-xs text-muted-foreground">{renderId.slice(0, 8)}</div>
        <div className="text-sm font-medium">{progress.status}</div>
      </div>
      <div className="h-2 w-full overflow-hidden rounded bg-muted">
        <div className="h-full bg-primary transition-all" style={{ width: `${progress.percent}%` }} />
      </div>
      {progress.phase ? (
        <div className="mt-2 text-xs text-muted-foreground">階段：{progress.phase}</div>
      ) : null}
    </div>
  );
}
