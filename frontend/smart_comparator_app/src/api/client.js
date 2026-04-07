import axios from 'axios';

const PRODUCTION_API_BASE_URL = 'https://comparekart-puc5.onrender.com';

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL ||
  (__DEV__ ? 'http://10.0.2.2:8000' : PRODUCTION_API_BASE_URL);

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
});

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}
