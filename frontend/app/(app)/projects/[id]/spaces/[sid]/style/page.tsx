"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { Stepper } from "@/components/layout/Stepper";
import { StyleTabs, type StyleTabKey } from "@/components/style/StyleTabs";
import { PresetGrid } from "@/components/style/PresetGrid";
import { TextStyleInput } from "@/components/style/TextStyleInput";
import { VisualStyleInput } from "@/components/style/VisualStyleInput";
import { SchemaPreview } from "@/components/style/SchemaPreview";
import { stylesApi, type StyleRecord } from "@/lib/api";

export default function SpaceStylePage() {
  const params = useParams();
  const id = params.id as string;
  const sid = params.sid as string;
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<StyleTabKey>("preset");
  const [parsedSchema, setParsedSchema] = useState<Record<string, unknown> | null>(null);
  const [selectedStyleId, setSelectedStyleId] = useState<string | undefined>(undefined);

  const { mutate: createStyle } = useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      stylesApi.create({ name: "自訂風格", kind: "personal", schema_json: data }),
    onSuccess: (style) => {
      router.push(`/projects/${id}/spaces/${sid}/config?styleId=${style.id}`);
    },
  });

  const handleSave = (data: Record<string, unknown>) => {
    createStyle(data);
  };

  const handlePresetSelect = (s: StyleRecord) => {
    setSelectedStyleId(s.id);
    setParsedSchema(s.schema_json);
  };

  return (
    <div className="space-y-6">
      <Stepper steps={["上傳", "選風格", "渲染設定"]} current={1} />
      <h1 className="text-2xl font-semibold">選擇風格</h1>

      <StyleTabs onChange={(k) => { setActiveTab(k); }} />

      <div className="mt-4">
        {activeTab === "preset" && (
          <PresetGrid
            onSelect={handlePresetSelect}
            selected={selectedStyleId}
          />
        )}
        {activeTab === "text" && (
          <TextStyleInput onParsed={setParsedSchema} />
        )}
        {activeTab === "visual" && (
          <VisualStyleInput onParsed={setParsedSchema} />
        )}
      </div>

      {parsedSchema !== null && (
        <SchemaPreview schema={parsedSchema} onSave={handleSave} />
      )}
    </div>
  );
}
