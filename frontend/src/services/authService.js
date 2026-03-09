import api from "./api";

export const loginRequest = async (payload) => {
  const { data } = await api.post("/auth/login", payload);
  return data;
};

export const registerRequest = async (payload) => {
  const { data } = await api.post("/auth/register", payload);
  return data;
};
