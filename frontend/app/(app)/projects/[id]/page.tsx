export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">專案詳情</h1>
      <div className="font-mono text-xs text-muted-foreground">{params.id}</div>
      <div className="rounded-lg border p-6 text-sm text-muted-foreground">
        Space 列表待接線（Sprint 1）。
      </div>
    </div>
  );
}
