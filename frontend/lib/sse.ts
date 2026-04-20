/**
 * EventSource wrapper。自動在 3 次錯誤後切換到 polling fallback（TODO）。
 */

export interface SSEHandlers {
  onProgress?: (data: unknown) => void;
  onCompleted?: (data: unknown) => void;
  onError?: (e: Event) => void;
}

export function openRenderStream(renderId: string, handlers: SSEHandlers): () => void {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const es = new EventSource(`${apiBase}/renders/${renderId}/stream`, {
    withCredentials: true,
  });

  es.addEventListener("progress", (e) => {
    try {
      handlers.onProgress?.(JSON.parse((e as MessageEvent).data));
    } catch {
      /* noop */
    }
  });
  es.addEventListener("completed", (e) => {
    try {
      handlers.onCompleted?.(JSON.parse((e as MessageEvent).data));
    } catch {
      /* noop */
    }
    es.close();
  });
  es.onerror = (e) => {
    handlers.onError?.(e);
  };

  return () => es.close();
}
