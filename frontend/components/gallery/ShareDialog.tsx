"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { rendersApi, type ShareResponse } from "@/lib/api";

interface ShareDialogProps {
  renderId: string;
  open: boolean;
  onClose: () => void;
}

const SHARE_BASE =
  typeof process !== "undefined"
    ? process.env.NEXT_PUBLIC_SHARE_BASE || "http://localhost:3001"
    : "http://localhost:3001";

export function ShareDialog({ renderId, open, onClose }: ShareDialogProps) {
  const queryClient = useQueryClient();
  const [copied, setCopied] = useState(false);

  const {
    data: shareData,
    isLoading,
    error,
  } = useQuery<ShareResponse>({
    queryKey: ["render-share", renderId],
    queryFn: () => rendersApi.getShare(renderId),
    enabled: open,
    retry: false,
  });

  const createShareMutation = useMutation({
    mutationFn: () => rendersApi.createShare(renderId),
    onSuccess: (data) => {
      queryClient.setQueryData(["render-share", renderId], data);
    },
  });

  const shareToken = shareData?.token ?? createShareMutation.data?.token;
  const expiresAt = shareData?.expiresAt ?? createShareMutation.data?.expiresAt;
  const shareUrl = shareToken
    ? `${SHARE_BASE}/share/${shareToken}`
    : null;

  // 404 或尚無 share token
  const notFound =
    error &&
    (error as { response?: { status?: number } }).response?.status === 404;

  const hasShare = !!shareToken;

  const handleCopy = async () => {
    if (!shareUrl) return;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback: do nothing
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl dark:bg-zinc-900">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">分享渲染結果</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-1 text-muted-foreground hover:bg-muted"
            aria-label="關閉"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {isLoading ? (
          <div className="py-6 text-center text-sm text-muted-foreground">
            檢查分享連結中…
          </div>
        ) : hasShare ? (
          <div className="space-y-4">
            <div>
              <div className="mb-1 text-sm font-medium">分享連結</div>
              <div className="flex items-center gap-2 rounded-md border bg-muted/40 px-3 py-2">
                <span className="flex-1 break-all font-mono text-xs">{shareUrl}</span>
                <button
                  type="button"
                  onClick={handleCopy}
                  className="shrink-0 rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:opacity-90"
                >
                  {copied ? "已複製！" : "複製"}
                </button>
              </div>
            </div>

            {expiresAt && (
              <p className="text-xs text-muted-foreground">
                此連結將於{" "}
                <span className="font-medium">
                  {new Date(expiresAt).toLocaleString("zh-TW")}
                </span>{" "}
                （約 7 天後）到期。
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              尚未產生分享連結。點擊下方按鈕產生有效期 7 天的分享網址。
            </p>

            {createShareMutation.isError && (
              <p className="text-sm text-destructive">
                產生失敗：
                {(createShareMutation.error as Error)?.message ?? "請稍後再試"}
              </p>
            )}

            <button
              type="button"
              disabled={createShareMutation.isPending}
              onClick={() => createShareMutation.mutate()}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-50"
            >
              {createShareMutation.isPending ? "產生中…" : "產生分享連結"}
            </button>
          </div>
        )}

        {notFound && !hasShare && !createShareMutation.data && (
          <div className="mt-2">
            {/* notFound 已由上方 hasShare=false 分支處理 */}
          </div>
        )}
      </div>
    </div>
  );
}
