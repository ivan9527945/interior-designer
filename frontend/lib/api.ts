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
    // TODO (Sprint 1): 401 時導去 /login
    return Promise.reject(error);
  }
);
