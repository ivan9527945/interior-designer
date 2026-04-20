"use client";

import { useEffect } from "react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error("[RenderStudio] Unhandled error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6 text-center">
      <div className="text-7xl font-bold text-red-100">!</div>
      <div>
        <h1 className="text-2xl font-semibold text-gray-700">發生錯誤</h1>
        <p className="mt-2 text-sm text-gray-500">
          很抱歉，頁面發生未預期的錯誤。
        </p>
        {error?.message && (
          <p className="mt-1 font-mono text-xs text-red-400">{error.message}</p>
        )}
        {error?.digest && (
          <p className="mt-1 font-mono text-xs text-gray-400">
            錯誤代碼：{error.digest}
          </p>
        )}
      </div>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={reset}
          className="rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          重試
        </button>
        <a
          href="/"
          className="rounded-md border px-5 py-2 text-sm font-medium hover:bg-muted"
        >
          返回首頁
        </a>
      </div>
    </div>
  );
}
