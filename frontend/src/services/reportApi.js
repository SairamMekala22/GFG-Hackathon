import api from "./api";

export const generateExecutiveReport = async (payload) => {
  const response = await api.post("/report/generate", payload);
  return response.data;
};

export default generateExecutiveReport;
