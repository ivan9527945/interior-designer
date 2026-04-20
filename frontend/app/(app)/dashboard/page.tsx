export default function DashboardPage() {
  const kpis = [
    { label: "本月渲染", value: "—" },
    { label: "平均耗時", value: "—" },
    { label: "達標率", value: "—" },
    { label: "線上 Agent", value: "—" },
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
      <div className="text-sm text-muted-foreground">
        Sprint 1 骨架階段 — 資料接線預計 Sprint 2 完成。
      </div>
    </div>
  );
}
