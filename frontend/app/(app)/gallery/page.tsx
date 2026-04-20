"use client";

import { useQuery } from "@tanstack/react-query";
import { rendersApi, type RenderRecord } from "@/lib/api";

const MINIO_BASE = process.env.NEXT_PUBLIC_MINIO_ENDPOINT || "http://localhost:9000";

function RenderCard({ render }: { render: RenderRecord }) {
  const previewKey = render.output_file_ids[0];
  const previewUrl = previewKey
    ? `${MINIO_BASE}/renderstudio/${previewKey}`
    : null;

  return (
    <div className="rounded-lg border overflow-hidden">
      {previewUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={previewUrl} alt="渲染結果" className="w-full aspect-video object-cover" />
      ) : (
        <div className="w-full aspect-video bg-muted flex items-center justify-center text-xs text-muted-foreground">
          無預覽圖
        </div>
      )}
      <div className="p-3">
        <div className="text-xs text-muted-foreground">
          {render.finished_at
            ? new Date(render.finished_at).toLocaleString("zh-TW")
            : "—"}
        </div>
        <div className="mt-1 flex gap-2">
          {previewUrl && (
            <a
              href={previewUrl}
              download
              className="text-xs text-primary underline"
              target="_blank"
              rel="noreferrer"
            >
              下載
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default function GalleryPage() {
  const { data: renders, isLoading } = useQuery<RenderRecord[]>({
    queryKey: ["renders", "completed"],
    queryFn: () => rendersApi.list({ renderStatus: "completed" }),
    refetchInterval: 10000,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">成果廊</h1>

      {isLoading && (
        <div className="text-sm text-muted-foreground">載入中…</div>
      )}

      {!isLoading && (!renders || renders.length === 0) && (
        <div className="rounded-lg border p-6 text-sm text-muted-foreground">
          尚無完成的渲染圖。
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {renders?.map((r) => (
          <RenderCard key={r.id} render={r} />
        ))}
      </div>
    </div>
  );
}
