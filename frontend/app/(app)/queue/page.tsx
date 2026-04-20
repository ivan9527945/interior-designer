"use client";

import { useQuery } from "@tanstack/react-query";
import { rendersApi, type RenderRecord } from "@/lib/api";
import { RenderJobCard } from "@/components/render/RenderJobCard";

const ACTIVE_STATUSES = ["pending", "assigned", "parsing", "modeling", "material", "rendering"];

export default function QueuePage() {
  const { data: renders, isLoading } = useQuery<RenderRecord[]>({
    queryKey: ["renders", "active"],
    queryFn: () => rendersApi.list(),
    refetchInterval: 5000,
  });

  const active = renders?.filter((r) => ACTIVE_STATUSES.includes(r.status)) ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">渲染佇列</h1>

      {isLoading && (
        <div className="text-sm text-muted-foreground">載入中…</div>
      )}

      {!isLoading && active.length === 0 && (
        <div className="rounded-lg border p-6 text-sm text-muted-foreground">
          目前沒有進行中的渲染。
        </div>
      )}

      <div className="space-y-3">
        {active.map((r) => (
          <RenderJobCard key={r.id} renderId={r.id} initialStatus={r.status} initialPercent={r.phase_percent} />
        ))}
      </div>
    </div>
  );
}
