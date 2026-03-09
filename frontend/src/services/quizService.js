import api from "./api";

export async function generateQuiz(payload) {
  const { data } = await api.post("/quiz/generate", payload);
  return data;
}

export async function submitQuiz(payload) {
  const { data } = await api.post("/quiz/submit", payload);
  return data;
}

export async function getQuizHistory(limit = 10) {
  const { data } = await api.get("/quiz/history", { params: { limit } });
  return data;
}
