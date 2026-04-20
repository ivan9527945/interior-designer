export default function QueuePage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">渲染佇列</h1>
      <div className="rounded-lg border p-6 text-sm text-muted-foreground">
        進行中的渲染 job 卡片 — 待 Sprint 2 接 SSE。
      </div>
    </div>
  );
}
