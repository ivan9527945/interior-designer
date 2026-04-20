export function UploadProgress({ percent }: { percent: number }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded bg-muted">
      <div className="h-full bg-primary transition-all" style={{ width: `${percent}%` }} />
    </div>
  );
}
