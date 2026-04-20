import axios, { type AxiosInstance } from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export const api: AxiosInstance = axios.create({
  baseURL,
  withCredentials: true,
  timeout: 30_000,
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── typed helpers ──────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  owner_id: string | null;
  created_at: string;
}

export interface Space {
  id: string;
  project_id: string;
  name: string;
  plan_file_id: string | null;
  elevation_file_id: string | null;
  parsed_plan: Record<string, unknown> | null;
  created_at: string;
}

export interface StyleRecord {
  id: string;
  name: string;
  kind: string;
  schema_json: Record<string, unknown>;
  created_at: string;
}

export interface RenderRecord {
  id: string;
  space_id: string;
  style_id: string;
  status: string;
  phase_percent: number;
  settings: Record<string, unknown>;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
  output_file_ids: string[];
  created_at: string;
}

export const projectsApi = {
  list: () => api.get<Project[]>("/projects").then((r) => r.data),
  create: (name: string) => api.post<Project>("/projects", { name }).then((r) => r.data),
  get: (id: string) => api.get<Project>(`/projects/${id}`).then((r) => r.data),
  createSpace: (projectId: string, body: { name: string; planFileId?: string; elevationFileId?: string }) =>
    api.post<Space>(`/projects/${projectId}/spaces`, body).then((r) => r.data),
  listSpaces: (projectId: string) =>
    api.get<Space[]>(`/projects/${projectId}/spaces`).then((r) => r.data),
};

export const rendersApi = {
  list: (params?: { renderStatus?: string; spaceId?: string }) =>
    api.get<RenderRecord[]>("/renders", { params }).then((r) => r.data),
  create: (body: { spaceId: string; styleId: string; settings: Record<string, unknown> }) =>
    api.post<RenderRecord>("/renders", body).then((r) => r.data),
  get: (id: string) => api.get<RenderRecord>(`/renders/${id}`).then((r) => r.data),
  cancel: (id: string) => api.delete(`/renders/${id}`),
};

export const stylesApi = {
  list: (kind?: string) => api.get<StyleRecord[]>("/styles", { params: kind ? { kind } : {} }).then((r) => r.data),
  create: (body: { name: string; kind: string; schema_json: Record<string, unknown> }) =>
    api.post<StyleRecord>("/styles", body).then((r) => r.data),
  parseText: (description: string) =>
    api.post<Record<string, unknown>>("/style/parse/text", { description }).then((r) => r.data),
  parseVisual: (description: string, images: File[]) => {
    const form = new FormData();
    form.append("description", description);
    images.forEach((img) => form.append("images", img));
    return api.post<Record<string, unknown>>("/style/parse/visual", form).then((r) => r.data);
  },
};

export interface AgentStatusResponse {
  online: boolean;
  count: number;
  agents: { id: string; machineName: string | null; lastHeartbeat: string | null }[];
}

export const agentsApi = {
  status: () => api.get<AgentStatusResponse>("/agent/status").then((r) => r.data),
};
