import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5050",
  timeout: 45000
});

export const generateDashboard = async (payload) => {
  const response = await api.post("/generate-dashboard", payload);
  return response.data;
};

export const uploadCsv = async (file, sessionId) => {
  const formData = new FormData();
  formData.append("file", file);
  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await api.post("/upload-csv", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });

  return response.data;
};

export const getDatasetProfile = async (sessionId) => {
  const response = await api.get("/dataset-profile", {
    params: { session_id: sessionId }
  });
  return response.data;
};

export const followUp = async (payload) => {
  const response = await api.post("/follow-up", payload);
  return response.data;
};

export default api;
