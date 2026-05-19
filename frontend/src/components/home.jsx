/**
 * Home.jsx — домашняя страница.
 *
 * Проверяет доступность backend (health check) и загружает
 * приветственное сообщение с защищённого эндпоинта /home/.
 *
 * Если пользователь не авторизован — показывает сообщение об ошибке.
 */

import React, { useEffect, useState } from "react";
import api from "./axios";

const Home = () => {
  const [health, setHealth] = useState("loading"); // "loading" | "online" | "offline"
  const [message, setMessage] = useState("");
  const [isLoadingHome, setIsLoadingHome] = useState(false);
  const [homeError, setHomeError] = useState("");

  useEffect(() => {
    const loadData = async () => {
      // 1. Проверяем health-эндпоинт backend
      try {
        await api.get("/health/");
        setHealth("online");
      } catch {
        setHealth("offline");
      }

      // 2. Пытаемся загрузить защищённые данные
      setIsLoadingHome(true);
      setHomeError("");
      try {
        const { data } = await api.get("/home/");
        setMessage(data?.data?.message || "");
      } catch (err) {
        setMessage("");
        setHomeError(
          err.response?.data?.error?.message ||
            "Для просмотра защищённых данных необходимо войти."
        );
      } finally {
        setIsLoadingHome(false);
      }
    };

    loadData();
  }, []);

  return (
    <section className="page">
      <h1>Добро пожаловать в Komnata.by</h1>
      <p className="muted">
        Статус бэкенда:{" "}
        <strong style={{ color: health === "online" ? "#16a34a" : "#dc2626" }}>
          {health === "online" ? "Онлайн" : health === "offline" ? "Оффлайн" : "Проверка..."}
        </strong>
      </p>
      {isLoadingHome && <p className="muted">Загрузка защищённых данных...</p>}
      {!isLoadingHome && message && <p>{message}</p>}
      {!isLoadingHome && !message && <p className="muted">{homeError || "Нет данных."}</p>}
    </section>
  );
};

export default Home;
