import { create } from "zustand";

interface ProjectState {
  currentProjectId: string | null;
  currentSpaceId: string | null;
  setCurrent: (p: { projectId?: string | null; spaceId?: string | null }) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  currentProjectId: null,
  currentSpaceId: null,
  setCurrent: ({ projectId, spaceId }) =>
    set((s) => ({
      currentProjectId: projectId !== undefined ? projectId : s.currentProjectId,
      currentSpaceId: spaceId !== undefined ? spaceId : s.currentSpaceId,
    })),
}));
