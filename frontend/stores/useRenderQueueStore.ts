import { create } from "zustand";

import type { RenderStatus } from "../lib/constants";

export interface RenderProgress {
  status: RenderStatus | "unknown";
  percent: number;
  phase?: string;
  previewUrl?: string | null;
}

interface QueueState {
  byId: Record<string, RenderProgress>;
  setProgress: (renderId: string, p: Partial<RenderProgress>) => void;
  remove: (renderId: string) => void;
}

export const useRenderQueueStore = create<QueueState>((set) => ({
  byId: {},
  setProgress: (renderId, p) =>
    set((s) => {
      const prev: RenderProgress = s.byId[renderId] ?? { status: "unknown", percent: 0 };
      return {
        byId: {
          ...s.byId,
          [renderId]: { ...prev, ...p },
        },
      };
    }),
  remove: (renderId) =>
    set((s) => {
      const next = { ...s.byId };
      delete next[renderId];
      return { byId: next };
    }),
}));
