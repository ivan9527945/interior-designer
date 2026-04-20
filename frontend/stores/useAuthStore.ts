import { create } from "zustand";

interface AuthState {
  userId: string | null;
  email: string | null;
  setUser: (u: { userId: string; email: string } | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  userId: null,
  email: null,
  setUser: (u) => set({ userId: u?.userId ?? null, email: u?.email ?? null }),
}));
