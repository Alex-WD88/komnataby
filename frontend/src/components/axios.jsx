/**
 * axios.jsx — настраиваемый экземпляр Axios для API-запросов.
 *
 * Функции:
 * - Автоматическая подстановка JWT-токена в заголовок Authorization.
 * - Автоматическая ротация refresh-токена при истечении access-токена.
 * - Унифицированная обработка ошибок.
 *
 * Базовый URL берётся из VITE_API_URL (из .env) или localhost:8000/api/v1.
 */

import axios from "axios";

// Базовый URL API — берётся из переменной окружения
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Флаг для предотвращения множественных одновременных запросов на refresh
let refreshInFlight = null;

/**
 * Интерцептор запросов — добавляет JWT-токен к каждому запросу.
 *
 * Если пользователь авторизован (access_token есть в localStorage),
 * токен автоматически подставляется в заголовок Authorization.
 */
api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("access_token");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

/**
 * Интерцептор ответов — обработка ошибок.
 *
 * При получении 401 (Unauthorized):
 * 1. Пытаемся обновить access-токен через refresh-токен.
 * 2. Если успешно — повторяем исходный запрос с новым токеном.
 * 3. Если не успешно — очищаем localStorage и перенаправляем на логин.
 */
api.interceptors.response.use(
  (response) => response, // Успешный ответ — возвращаем как есть
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // Обрабатываем только 401 ошибки
    if (status !== 401 || originalRequest?._retry) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      // Нет refresh-токена — пользователь неавторизован
      return Promise.reject(error);
    }

    // Помечаем запрос как повторный, чтобы избежать рекурсии
    originalRequest._retry = true;

    try {
      // Если уже есть запрос на refresh — ждём его результат
      if (!refreshInFlight) {
        refreshInFlight = api.post("/token/refresh/", { refresh: refreshToken });
      }
      const refreshResponse = await refreshInFlight;
      const newAccess = refreshResponse.data.data?.access || refreshResponse.data.access;

      if (newAccess) {
        localStorage.setItem("access_token", newAccess);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      }

      // Повторяем исходный запрос с новым токеном
      return api(originalRequest);
    } catch (refreshError) {
      // Refresh не удался — очищаем данные авторизации
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      return Promise.reject(refreshError);
    } finally {
      refreshInFlight = null;
    }
  }
);

export default api;
