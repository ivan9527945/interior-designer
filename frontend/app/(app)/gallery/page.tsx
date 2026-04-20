"use client";

import Link from "next/link";
import Image from "next/image";
import { useQuery } from "@tanstack/react-query";
import { rendersApi, type RenderRecord } from "@/lib/api";

const MINIO_BASE = process.env.NEXT_PUBLIC_MINIO_ENDPOINT || "http://localhost:9000";

function RenderCard({ render }: { render: RenderRecord }) {
  const previewKey = render.output_file_ids[0];
  const previewUrl = previewKey
    ? `${MINIO_BASE}/renderstudio/${previewKey}`
    : null;

  return (
    <Link href={`/gallery/${render.id}`} className="group block rounded-lg border overflow-hidden hover:shadow-md transition-shadow">
      {previewUrl ? (
        /* 使用 fill 模式：外層容器設定 aspect-ratio，Image 自動填滿 */
        <div className="relative w-full aspect-video">
          <Image
            src={previewUrl}
            alt="渲染結果"
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover group-hover:opacity-95 transition-opacity"
          />
        </div>
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
              onClick={(e) => e.stopPropagation()}
            >
              下載
            </a>
          )}
          <span className="text-xs text-muted-foreground">→ 詳情</span>
        </div>
      </div>
    </Link>
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
