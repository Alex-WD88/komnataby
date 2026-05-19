/**
 * Logout.jsx — страница выхода из системы.
 *
 * При монтировании:
 * 1. Отправляет refresh-токен на эндпоинт /logout/ (блокирует токен на сервере).
 * 2. Очищает localStorage (access_token и refresh_token).
 * 3. Перенаправляет на /login.
 *
 * Ошибки серверного logout игнорируются — локальная очистка всё равно происходит.
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "./axios";

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const performLogout = async () => {
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          // Блокируем refresh-токен на сервере
          await api.post("/logout/", { refresh_token: refreshToken });
        }
      } catch {
        // Игнорируем ошибки серверного logout — локальная очистка всё равно произойдёт
      } finally {
        // Всегда очищаем локальные данные
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
      }
    };

    performLogout();
  }, [navigate]);

  return <section className="page">Выход...</section>;
};

export default Logout;
