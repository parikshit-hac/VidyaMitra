import api from "./api";

export async function createCareerPlan(payload) {
  const { data } = await api.post("/career/plan", payload);
  return data;
}

export async function getCareerRoadmaps(limit = 10) {
  const { data } = await api.get("/career/roadmaps", { params: { limit } });
  return data;
}
