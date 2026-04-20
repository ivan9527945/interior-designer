"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { rendersApi, type RenderRecord } from "@/lib/api";
import { useRenderProgress } from "@/hooks/useRenderProgress";
import { useRenderQueueStore } from "@/stores/useRenderQueueStore";
import { ShareDialog } from "@/components/gallery/ShareDialog";
import { CsatPopover } from "@/components/render/CsatPopover";

const MINIO_BASE = process.env.NEXT_PUBLIC_MINIO_ENDPOINT || "http://localhost:9000";

function statusColor(status: string) {
  if (status === "completed") return "text-emerald-600";
  if (status === "error") return "text-red-500";
  return "text-amber-500";
}

export default function RenderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [shareOpen, setShareOpen] = useState(false);

  const { data: render, isLoading } = useQuery<RenderRecord>({
    queryKey: ["renders", id],
    queryFn: () => rendersApi.get(id),
    refetchInterval: (query) => {
      const s = query.state.data?.status;
      return s && ["completed", "error", "cancelled"].includes(s) ? false : 5000;
    },
  });

  // SSE subscription for live progress
  useRenderProgress(render ? id : null);
  const progress = useRenderQueueStore((s) => s.byId[id]);

  const retryMutation = useMutation({
    mutationFn: () => rendersApi.retry(id),
    onSuccess: (newRender) => {
      router.push(`/gallery/${newRender.id}`);
    },
  });

  if (isLoading) {
    return <div className="p-6 text-sm text-muted-foreground">載入中…</div>;
  }
  if (!render) {
    return <div className="p-6 text-sm text-destructive">找不到渲染記錄。</div>;
  }

  const liveStatus = progress?.status ?? render.status;
  const livePercent = progress?.percent ?? render.phase_percent;
  const outputIds = render.output_file_ids;

  const canRetry = liveStatus === "error" || liveStatus === "cancelled";
  const canShare = liveStatus === "completed";

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.back()}
          className="text-sm text-muted-foreground underline"
        >
          ← 返回
        </button>
        <h1 className="text-xl font-semibold">渲染詳情</h1>
      </div>

      {/* Status card */}
      <div className="rounded-lg border p-4">
        <div className="mb-3 flex items-center justify-between">
          <span className="font-mono text-xs text-muted-foreground">{id}</span>
          <span className={`text-sm font-semibold ${statusColor(liveStatus)}`}>
            {liveStatus}
          </span>
        </div>

        {liveStatus !== "completed" && liveStatus !== "error" && (
          <>
            <div className="h-2 w-full overflow-hidden rounded bg-muted">
              <div
                className="h-full bg-primary transition-all duration-500"
                style={{ width: `${livePercent}%` }}
              />
            </div>
            <div className="mt-1 text-right text-xs text-muted-foreground">{livePercent}%</div>
          </>
        )}

        {render.error_message && (
          <div className="mt-3 rounded bg-destructive/10 p-3 text-sm text-destructive">
            {render.error_message}
          </div>
        )}

        <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <dt className="text-muted-foreground">建立時間</dt>
          <dd>{new Date(render.created_at).toLocaleString("zh-TW")}</dd>
          {render.started_at && (
            <>
              <dt className="text-muted-foreground">開始時間</dt>
              <dd>{new Date(render.started_at).toLocaleString("zh-TW")}</dd>
            </>
          )}
          {render.finished_at && (
            <>
              <dt className="text-muted-foreground">完成時間</dt>
              <dd>{new Date(render.finished_at).toLocaleString("zh-TW")}</dd>
              <dt className="text-muted-foreground">耗時</dt>
              <dd>
                {Math.round(
                  (new Date(render.finished_at).getTime() -
                    new Date(render.started_at!).getTime()) /
                    1000
                )}{" "}
                秒
              </dd>
            </>
          )}
          <dt className="text-muted-foreground">畫質</dt>
          <dd>{(render.settings as { quality?: string }).quality ?? "—"}</dd>
        </dl>
      </div>

      {/* 行動按鈕列（在 output images 之前） */}
      {(canRetry || canShare) && (
        <div className="flex flex-wrap gap-3">
          {canRetry && (
            <button
              type="button"
              disabled={retryMutation.isPending}
              onClick={() => retryMutation.mutate()}
              className="rounded-md border border-amber-400 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50 dark:bg-amber-950/30 dark:text-amber-400"
            >
              {retryMutation.isPending ? "重試中…" : "重試"}
            </button>
          )}
          {retryMutation.isError && (
            <span className="self-center text-sm text-destructive">
              重試失敗：{(retryMutation.error as Error)?.message ?? "請稍後再試"}
            </span>
          )}

          {canShare && (
            <button
              type="button"
              onClick={() => setShareOpen(true)}
              className="rounded-md border border-sky-400 bg-sky-50 px-4 py-2 text-sm font-medium text-sky-700 hover:bg-sky-100 dark:bg-sky-950/30 dark:text-sky-400"
            >
              分享
            </button>
          )}
        </div>
      )}

      {/* Output images */}
      {outputIds.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-lg font-medium">渲染結果</h2>
          <div className="grid gap-4">
            {outputIds.map((fileId) => {
              const imgUrl = `${MINIO_BASE}/renderstudio/${fileId}`;
              return (
                <div key={fileId} className="overflow-hidden rounded-lg border">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={imgUrl}
                    alt="渲染結果"
                    className="w-full object-contain"
                    style={{ maxHeight: "70vh" }}
                  />
                  <div className="flex items-center justify-between p-3">
                    <span className="font-mono text-xs text-muted-foreground">
                      {fileId.slice(0, 8)}
                    </span>
                    <a
                      href={imgUrl}
                      download={`render_${fileId}.png`}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:opacity-90"
                    >
                      下載原圖
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : liveStatus === "completed" ? (
        <div className="rounded-lg border p-6 text-sm text-muted-foreground">
          渲染完成但尚無輸出檔案。
        </div>
      ) : null}

      {/* Share Dialog */}
      <ShareDialog
        renderId={id}
        open={shareOpen}
        onClose={() => setShareOpen(false)}
      />

      {/* CSAT Popover — 只在 completed 時顯示 */}
      {liveStatus === "completed" && <CsatPopover renderId={id} />}
    </div>
  );
}
