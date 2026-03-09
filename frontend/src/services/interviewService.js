import api from "./api";

export async function createInterviewSession(payload) {
  const { data } = await api.post("/interview/mock/session", payload);
  return data;
}

export async function generateInterviewQuestions(payload) {
  const { data } = await api.post("/interview/mock/questions", payload);
  return data;
}

export async function submitInterviewAnswer(sessionId, payload) {
  const { data } = await api.post(`/interview/mock/session/${sessionId}/answer`, payload);
  return data;
}

export async function evaluateInterviewAnswer(payload) {
  const { data } = await api.post("/interview/mock/evaluate", payload);
  return data;
}

export async function getInterviewSession(sessionId) {
  const { data } = await api.get(`/interview/mock/session/${sessionId}`);
  return data;
}

export async function getInterviewSessions(limit = 10) {
  const { data } = await api.get("/interview/sessions", { params: { limit } });
  return data;
}
