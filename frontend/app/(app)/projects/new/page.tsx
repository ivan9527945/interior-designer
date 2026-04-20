"use client";

import { useState } from "react";

import { Stepper } from "@/components/layout/Stepper";
import { DwgDropzone } from "@/components/upload/DwgDropzone";
import { Button } from "@/components/ui/button";

export default function NewProjectPage() {
  const [planId, setPlanId] = useState<string | null>(null);
  const [elevationId, setElevationId] = useState<string | null>(null);

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">新建專案</h1>
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={0} />
      <div className="grid grid-cols-2 gap-6">
        <div>
          <div className="mb-2 text-sm font-medium">平面圖</div>
          <DwgDropzone kind="plan" onUploaded={setPlanId} />
          {planId ? <div className="mt-2 text-xs text-emerald-600">已上傳</div> : null}
        </div>
        <div>
          <div className="mb-2 text-sm font-medium">立面圖</div>
          <DwgDropzone kind="elevation" onUploaded={setElevationId} />
          {elevationId ? <div className="mt-2 text-xs text-emerald-600">已上傳</div> : null}
        </div>
      </div>
      <Button disabled={!planId}>下一步：選風格</Button>
    </div>
  );
}
