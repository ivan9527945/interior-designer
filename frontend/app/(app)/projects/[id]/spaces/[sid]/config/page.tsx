"use client";

import { useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { Stepper } from "@/components/layout/Stepper";
import { rendersApi } from "@/lib/api";
import { cn } from "@/lib/utils";

type Quality = "draft" | "standard" | "premium";

const QUALITY_OPTIONS: {
  key: Quality;
  label: string;
  description: string;
  badge?: string;
}[] = [
  {
    key: "draft",
    label: "草稿",
    description: "快速預覽，低解析度，適合確認構圖與風格方向。",
  },
  {
    key: "standard",
    label: "標準",
    description: "平衡速度與品質，適合一般提案使用。",
    badge: "推薦",
  },
  {
    key: "premium",
    label: "精品",
    description: "最高解析度，細節豐富，適合最終交付或印刷輸出。",
  },
];

export default function SpaceConfigPage() {
  const params = useParams();
  const id = params.id as string;
  const sid = params.sid as string;
  const searchParams = useSearchParams();
  const styleId = searchParams.get("styleId") ?? "";
  const router = useRouter();

  const [quality, setQuality] = useState<Quality>("standard");

  const { mutate, isPending, error } = useMutation({
    mutationFn: () =>
      rendersApi.create({
        spaceId: sid,
        styleId,
        settings: { quality },
      }),
    onSuccess: (render) => {
      router.push(`/gallery/${render.id}`);
    },
  });

  return (
    <div className="space-y-6">
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={2} />
      <h1 className="text-2xl font-semibold">渲染設定</h1>

      {/* Quality selection */}
      <div className="space-y-3">
        <p className="text-sm font-semibold">畫質</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {QUALITY_OPTIONS.map((opt) => (
            <label
              key={opt.key}
              className={cn(
                "relative flex cursor-pointer flex-col gap-1 rounded-lg border p-4 transition-colors",
                quality === opt.key
                  ? "border-primary bg-primary/5 ring-1 ring-primary"
                  : "border-border hover:border-primary/40"
              )}
            >
              <input
                type="radio"
                name="quality"
                value={opt.key}
                checked={quality === opt.key}
                onChange={() => setQuality(opt.key)}
                className="sr-only"
              />
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{opt.label}</span>
                {opt.badge && (
                  <span className="rounded-full bg-primary px-2 py-0.5 text-xs text-primary-foreground">
                    {opt.badge}
                  </span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">{opt.description}</p>
            </label>
          ))}
        </div>
      </div>

      {!styleId && (
        <p className="text-sm text-amber-600">尚未選擇風格，請返回上一步選擇風格。</p>
      )}

      {error && (
        <p className="text-sm text-destructive">
          提交失敗：{(error as Error).message ?? "請稍後再試"}
        </p>
      )}

      <button
        type="button"
        disabled={isPending || !styleId}
        onClick={() => mutate()}
        className="inline-flex items-center gap-2 rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {isPending && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z" />
          </svg>
        )}
        {isPending ? "提交中…" : "提交渲染"}
      </button>
    </div>
  );
}
