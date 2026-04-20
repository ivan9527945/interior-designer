"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Stepper } from "@/components/layout/Stepper";
import { DwgDropzone } from "@/components/upload/DwgDropzone";
import { Button } from "@/components/ui/button";
import { projectsApi } from "@/lib/api";

export default function NewProjectPage() {
  const router = useRouter();
  const [projectName, setProjectName] = useState("");
  const [spaceName, setSpaceName] = useState("客廳");
  const [planId, setPlanId] = useState<string | null>(null);
  const [elevationId, setElevationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mut = useMutation({
    mutationFn: async () => {
      const project = await projectsApi.create(projectName || "未命名專案");
      const space = await projectsApi.createSpace(project.id, {
        name: spaceName,
        planFileId: planId ?? undefined,
        elevationFileId: elevationId ?? undefined,
      });
      return { project, space };
    },
    onSuccess: ({ project, space }) => {
      router.push(`/projects/${project.id}/spaces/${space.id}/style`);
    },
    onError: (e: Error) => setError(e.message),
  });

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">新建專案</h1>
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={0} />

      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2 grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">專案名稱</label>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              placeholder="例如：信義路案"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">空間名稱</label>
            <input
              className="w-full rounded border px-3 py-2 text-sm"
              placeholder="例如：客廳"
              value={spaceName}
              onChange={(e) => setSpaceName(e.target.value)}
            />
          </div>
        </div>

        <div>
          <div className="mb-2 text-sm font-medium">平面圖</div>
          <DwgDropzone kind="plan" onUploaded={setPlanId} />
          {planId && <div className="mt-2 text-xs text-emerald-600">✓ 已上傳</div>}
        </div>
        <div>
          <div className="mb-2 text-sm font-medium">立面圖（選填）</div>
          <DwgDropzone kind="elevation" onUploaded={setElevationId} />
          {elevationId && <div className="mt-2 text-xs text-emerald-600">✓ 已上傳</div>}
        </div>
      </div>

      {error && <div className="text-sm text-red-500">{error}</div>}

      <Button
        disabled={!planId || mut.isPending}
        onClick={() => mut.mutate()}
      >
        {mut.isPending ? "建立中…" : "下一步：選風格"}
      </Button>
    </div>
  );
}
