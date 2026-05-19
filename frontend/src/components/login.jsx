/**
 * Login.jsx — страница входа в систему.
 *
 * Форма с полями username и password.
 * При успешной отправке сохраняет access и refresh токены в localStorage
 * и перенаправляет на /dashboard.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./axios";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const { data } = await api.post("/token/", { username, password });

      // Сохраняем токены в localStorage
      localStorage.setItem("access_token", data.data.access);
      localStorage.setItem("refresh_token", data.data.refresh);

      // Перенаправляем на dashboard
      navigate("/dashboard");
    } catch (err) {
      // Форматируем сообщение об ошибке
      const msg =
        err.response?.data?.error?.message ||
        "Ошибка входа. Проверьте имя пользователя и пароль.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="page auth-page">
      <h2>Вход в систему</h2>
      <form className="auth-form" onSubmit={submit}>
        <label htmlFor="username">Имя пользователя</label>
        <input
          id="username"
          name="username"
          type="text"
          value={username}
          required
          minLength={3}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Введите имя пользователя"
        />

        <label htmlFor="password">Пароль</label>
        <input
          id="password"
          name="password"
          type="password"
          value={password}
          required
          minLength={8}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Введите пароль (мин. 8 символов)"
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Вход..." : "Войти"}
        </button>
      </form>
    </section>
  );
};

export default Login;
