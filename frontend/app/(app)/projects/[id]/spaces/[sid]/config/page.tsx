import { Stepper } from "@/components/layout/Stepper";
import { Button } from "@/components/ui/button";

export default function SpaceConfigPage() {
  return (
    <div className="space-y-6">
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={2} />
      <h1 className="text-2xl font-semibold">渲染設定</h1>
      <div className="rounded-lg border p-6 text-sm text-muted-foreground">
        畫質 / 解析度 / 視角 / 輸出格式 — placeholder。
      </div>
      <Button>提交渲染</Button>
    </div>
  );
}
