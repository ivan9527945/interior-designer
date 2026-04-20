import { create } from "zustand";

interface AgentState {
  online: boolean;
  lastHeartbeat: string | null;
  machineName: string | null;
  setStatus: (s: Partial<AgentState>) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  online: false,
  lastHeartbeat: null,
  machineName: null,
  setStatus: (s) => set(s),
}));
