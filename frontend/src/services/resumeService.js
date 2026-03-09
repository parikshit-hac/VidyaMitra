import api from "./api";

export async function uploadResumeFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post("/resume/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });

  return data;
}

export async function analyzeResume(resumeId, payload) {
  const { data } = await api.post(`/resume/${resumeId}/analyze`, payload);
  return data;
}

export async function uploadResumeToStorage(payload) {
  const { data } = await api.post("/resources/storage/upload", payload);
  return data;
}

export async function getResumeDetail(resumeId) {
  const { data } = await api.get(`/resume/${resumeId}`);
  return data;
}
