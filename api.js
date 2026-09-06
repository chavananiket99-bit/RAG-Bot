//api.js
import axios from "axios";
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});
api.interceptors.request.use(
  (config) => {
    try {
      const savedAuth = localStorage.getItem("rag_auth");
      if (savedAuth) {
        const auth = JSON.parse(savedAuth);
        if (auth?.accessToken) {
          config.headers.Authorization = `Bearer ${auth.accessToken}`;
        }
      }
    } catch (error) {
      console.error("Failed to attach authentication token:", error);
    }
    return config;
  },
  (error) => Promise.reject(error),
);
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("rag_auth");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);
export async function uploadPdf(files) {
  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });
  const response = await api.post("/upload", formData);
  return response.data;
}
export async function getDocuments() {
  const response = await api.get("/documents");
  return response.data;
}
export async function askQuestion(question, conversationId = null) {
  const response = await api.post("/ask", {
    question,
    conversation_id: conversationId,
  });
  return response.data;
}
export async function deleteDocument(documentId) {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
}
export { API_BASE_URL };
