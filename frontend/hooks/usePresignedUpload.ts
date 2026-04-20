import axios from "axios";

import { api } from "../lib/api";

export interface PresignedPutResult {
  fileId: string;
  url: string;
  expiresAt: string;
}

export function usePresignedUpload() {
  async function upload(file: File, kind: "plan" | "elevation" | "ref_image"): Promise<string> {
    const { data } = await api.post<PresignedPutResult>("/uploads/presign", {
      filename: file.name,
      contentType: file.type,
      kind,
    });

    await axios.put(data.url, file, {
      headers: { "Content-Type": file.type },
    });

    await api.post("/uploads/complete", { fileId: data.fileId });
    return data.fileId;
  }

  return { upload };
}
