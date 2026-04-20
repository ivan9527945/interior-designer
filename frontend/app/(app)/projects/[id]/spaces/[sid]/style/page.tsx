"use client";

import { Stepper } from "@/components/layout/Stepper";
import { StyleTabs } from "@/components/style/StyleTabs";

export default function SpaceStylePage() {
  return (
    <div className="space-y-6">
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={1} />
      <h1 className="text-2xl font-semibold">選擇風格</h1>
      <StyleTabs />
      <div className="rounded-lg border p-6 text-sm text-muted-foreground">
        Preset / Text / Visual 三種輸入待 Sprint 3 實作。
      </div>
    </div>
  );
}
