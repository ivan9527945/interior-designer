"use client";

import { useDropzone } from "react-dropzone";

import { usePresignedUpload } from "@/hooks/usePresignedUpload";

export interface DwgDropzoneProps {
  kind: "plan" | "elevation";
  onUploaded: (fileId: string) => void;
}

export function DwgDropzone({ kind, onUploaded }: DwgDropzoneProps) {
  const { upload } = usePresignedUpload();
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/acad": [".dwg", ".dxf"] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
    onDrop: async ([file]) => {
      if (!file) return;
      const fileId = await upload(file, kind);
      onUploaded(fileId);
    },
  });

  return (
    <div
      {...getRootProps()}
      className="flex h-40 cursor-pointer items-center justify-center rounded-lg border-2 border-dashed p-6 text-sm text-muted-foreground hover:bg-muted/50"
    >
      <input {...getInputProps()} />
      {isDragActive ? "放開上傳…" : `拖入 ${kind === "plan" ? "平面" : "立面"} DWG/DXF（< 100MB）`}
    </div>
  );
}
