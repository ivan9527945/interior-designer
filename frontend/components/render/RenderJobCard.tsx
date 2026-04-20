"use client";

import { useEffect } from "react";
import { useRenderProgress } from "@/hooks/useRenderProgress";
import { useRenderQueueStore } from "@/stores/useRenderQueueStore";

interface Props {
  renderId: string;
  initialStatus?: string;
  initialPercent?: number;
}

const PHASE_LABELS: Record<string, string> = {
  setup: "初始化",
  dxf: "DXF 解析",
  sketchup: "建模",
  material: "套材質",
  vray: "V-Ray 渲染",
  upload: "上傳結果",
  done: "完成",
};

export function RenderJobCard({ renderId, initialStatus, initialPercent }: Props) {
  const setProgress = useRenderQueueStore((s) => s.setProgress);
  useRenderProgress(renderId);

  // seed initial values from server so card doesn't flash "unknown"
  useEffect(() => {
    if (initialStatus) {
      setProgress(renderId, { status: initialStatus as never, percent: initialPercent ?? 0 });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const progress = useRenderQueueStore((s) => s.byId[renderId]) ?? {
    status: initialStatus ?? "unknown",
    percent: initialPercent ?? 0,
  };

  const phaseLabel = progress.phase ? (PHASE_LABELS[progress.phase] ?? progress.phase) : null;

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="font-mono text-xs text-muted-foreground">{renderId.slice(0, 8)}</div>
        <div className="text-sm font-medium">{progress.status}</div>
      </div>
      <div className="h-2 w-full overflow-hidden rounded bg-muted">
        <div
          className="h-full bg-primary transition-all duration-500"
          style={{ width: `${progress.percent}%` }}
        />
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
        {phaseLabel ? <span>階段：{phaseLabel}</span> : <span />}
        <span>{progress.percent}%</span>
      </div>
    </div>
  );
}
