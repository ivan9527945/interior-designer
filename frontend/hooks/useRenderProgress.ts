import { useEffect } from "react";

import { openRenderStream } from "../lib/sse";
import { useRenderQueueStore } from "../stores/useRenderQueueStore";

export function useRenderProgress(renderId: string | null) {
  const setProgress = useRenderQueueStore((s) => s.setProgress);

  useEffect(() => {
    if (!renderId) return;
    const close = openRenderStream(renderId, {
      onProgress: (data) => setProgress(renderId, data as never),
      onCompleted: (data) => {
        const d = data as { previewUrl?: string };
        setProgress(renderId, {
          status: "completed",
          percent: 100,
          previewUrl: d.previewUrl,
        });
      },
    });
    return close;
  }, [renderId, setProgress]);
}
