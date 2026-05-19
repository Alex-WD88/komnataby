/**
 * Dashboard.jsx — защищённая панель пользователя.
 *
 * Загружает приветственное сообщение с защищённого эндпоинта /home/.
 * Требует авторизации (access_token в localStorage).
 */

import React, { useEffect, useState } from "react";
import api from "./axios";

const Dashboard = () => {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      setIsLoading(true);
      try {
        const { data } = await api.get("/home/");
        setMessage(data?.data?.message || "");
      } catch (err) {
        // Ошибка загрузки — скорее всего, токен истёк
        setError(
          err.response?.data?.error?.message ||
            "Необходимо войти в систему для доступа к панели."
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, []);

  return (
    <section className="page">
      <h2>Панель пользователя</h2>
      {isLoading && <p className="muted">Загрузка панели...</p>}
      {message && <p>{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
};

export default Dashboard;
