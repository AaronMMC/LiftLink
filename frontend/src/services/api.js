import axios from "axios";
import { getToken } from "./auth";
import { awsConfig } from "../config/aws";

const api = axios.create({
  baseURL: awsConfig.apiBaseUrl,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const createProfile = (data) => api.post("/instructors", data);
export const getProfile = (id) => api.get(`/instructors/${id}`);
export const updateProfile = (id, data) => api.put(`/instructors/${id}`, data);
export const searchInstructors = (params) =>
  api.get("/instructors", { params });
export const createEntry = (data) => api.post("/progress", data);
export const listEntries = () => api.get("/progress");
export const getHistory = (clientId) =>
  api.get(`/clients/${clientId}/history`);

export default api;
