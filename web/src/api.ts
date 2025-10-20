// web/src/api.ts
import axios from 'axios'


const proto = window.location.protocol; // http: или https:
const host = window.location.hostname;
const base = host === 'localhost' ? `${proto}//localhost:8000` : `${proto}//${host}:8000`;

const api = axios.create({ baseURL: base })

// Берём токен из Vite-окружения (или из window, если хочешь подменять на проде)
const token = (window as any).__TEAMUX_TOKEN__ || import.meta.env.VITE_API_TOKEN

if (token) {
  api.interceptors.request.use((cfg) => {
    cfg.headers = cfg.headers || {}
    cfg.headers.Authorization = `Bearer ${token}`
    return cfg
  })
}

export default api
