"use client";

import { useQuery } from "@tanstack/react-query";
import { projectsApi, rendersApi } from "@/lib/api";

export default function DashboardPage() {
  const { data: projects } = useQuery({
    queryKey: ["projects"],
    queryFn: projectsApi.list,
  });
  const { data: allRenders } = useQuery({
    queryKey: ["renders"],
    queryFn: () => rendersApi.list(),
  });

  const completed = allRenders?.filter((r) => r.status === "completed") ?? [];
  const active = allRenders?.filter((r) =>
    ["pending", "assigned", "parsing", "modeling", "material", "rendering"].includes(r.status)
  ) ?? [];

  const avgMs = completed.length
    ? completed
        .filter((r) => r.started_at && r.finished_at)
        .reduce((acc, r) => {
          const ms =
            new Date(r.finished_at!).getTime() - new Date(r.started_at!).getTime();
          return acc + ms;
        }, 0) /
      Math.max(
        1,
        completed.filter((r) => r.started_at && r.finished_at).length
      )
    : null;

  const avgMin = avgMs ? (avgMs / 60000).toFixed(1) + " 分" : "—";

  const kpis = [
    { label: "本月渲染", value: allRenders ? String(allRenders.length) : "—" },
    { label: "平均耗時", value: avgMin },
    { label: "進行中", value: String(active.length) },
    { label: "專案數", value: projects ? String(projects.length) : "—" },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">儀表板</h1>
      <div className="grid grid-cols-4 gap-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">{k.label}</div>
            <div className="mt-2 text-2xl font-semibold">{k.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
