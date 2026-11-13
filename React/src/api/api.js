import axios from "axios";

// Endereço da API. Definido em tempo de build pela variável VITE_API_URL
// (veja .env.example); sem ela, aponta para o Django local.
export const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/";

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
