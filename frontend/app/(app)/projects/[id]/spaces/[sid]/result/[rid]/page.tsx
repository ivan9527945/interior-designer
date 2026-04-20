import { RenderJobCard } from "@/components/render/RenderJobCard";

export default function RenderResultPage({ params }: { params: { rid: string } }) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">渲染結果</h1>
      <RenderJobCard renderId={params.rid} />
    </div>
  );
}
