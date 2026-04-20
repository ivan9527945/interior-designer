"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "@/lib/api";

const MINIO_BASE = process.env.NEXT_PUBLIC_MINIO_ENDPOINT || "http://localhost:9000";

export default function SharePage() {
  const { token } = useParams<{ token: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ["public-share", token],
    queryFn: () => publicApi.getShare(token),
    retry: false,
    enabled: !!token,
  });

  const is404 =
    error &&
    (error as { response?: { status?: number } }).response?.status === 404;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-gray-500">載入中…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-12 w-12 text-gray-300"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v3.75M12 15.75h.008v.008H12V15.75zM21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h1 className="text-xl font-semibold text-gray-700">
          {is404 ? "此連結已過期或不存在" : "載入失敗"}
        </h1>
        <p className="text-sm text-gray-500">
          {is404
            ? "分享連結可能已到期，請向原作者重新索取。"
            : "請稍後再試，或確認網路連線是否正常。"}
        </p>
      </div>
    );
  }

  const { render, expiresAt } = data;
  const outputIds = render.output_file_ids ?? [];
  const quality = (render.settings as { quality?: string }).quality ?? "—";

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 簡單頂部 Logo */}
      <header className="border-b bg-white px-6 py-4">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <span className="text-lg font-bold tracking-tight">RenderStudio</span>
          <span className="text-xs text-gray-400">公開分享頁</span>
        </div>
      </header>

      <main className="mx-auto max-w-3xl space-y-6 px-4 py-8">
        {/* 基本資訊 */}
        <div className="rounded-lg border bg-white p-5 shadow-sm">
          <h1 className="mb-3 text-xl font-semibold">渲染結果分享</h1>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
            {render.finished_at && (
              <>
                <dt className="text-gray-500">完成時間</dt>
                <dd>{new Date(render.finished_at).toLocaleString("zh-TW")}</dd>
              </>
            )}
            <dt className="text-gray-500">畫質</dt>
            <dd className="capitalize">{quality}</dd>
            <dt className="text-gray-500">連結到期</dt>
            <dd>
              {expiresAt
                ? new Date(expiresAt).toLocaleString("zh-TW")
                : "—"}
            </dd>
          </dl>
        </div>

        {/* 輸出圖片 */}
        {outputIds.length > 0 ? (
          <div className="space-y-4">
            {outputIds.map((fileId) => {
              const imgUrl = `${MINIO_BASE}/renderstudio/${fileId}`;
              return (
                <div
                  key={fileId}
                  className="overflow-hidden rounded-xl border bg-white shadow-sm"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={imgUrl}
                    alt="渲染結果"
                    className="w-full object-contain"
                    style={{ maxHeight: "75vh" }}
                  />
                </div>
              );
            })}
          </div>
        ) : (
          <div className="rounded-lg border bg-white p-6 text-center text-sm text-gray-500">
            此分享尚無輸出圖片。
          </div>
        )}

        {/* 頁腳 */}
        <p className="text-center text-xs text-gray-400">
          由 RenderStudio 製作 · 室內設計渲染平台
        </p>
      </main>
    </div>
  );
}
