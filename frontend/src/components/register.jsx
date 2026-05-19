/**
 * Register.jsx — страница регистрации нового пользователя.
 *
 * Форма с полями username, password, password_confirm.
 * При успешной регистрации перенаправляет на /login.
 *
 * Клиентская валидация:
 * - username: минимум 3 символа
 * - password: минимум 8 символов
 * - password_confirm: должен совпадать с password
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./axios";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    // Клиентская валидация
    if (password !== passwordConfirm) {
      setError("Пароли не совпадают.");
      return;
    }

    setIsLoading(true);

    try {
      await api.post("/register/", {
        username,
        password,
        password_confirm: passwordConfirm,
      });
      // Регистрация успешна — перенаправляем на логин
      navigate("/login");
    } catch (err) {
      // Пытаемся извлечь понятное сообщение об ошибке
      const msg =
        err.response?.data?.error?.message ||
        "Ошибка регистрации. Попробуйте другое имя пользователя.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="page auth-page">
      <h2>Создать аккаунт</h2>
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
          placeholder="Минимум 3 символа"
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
          placeholder="Минимум 8 символов"
        />

        <label htmlFor="passwordConfirm">Подтвердите пароль</label>
        <input
          id="passwordConfirm"
          name="passwordConfirm"
          type="password"
          value={passwordConfirm}
          required
          minLength={8}
          onChange={(e) => setPasswordConfirm(e.target.value)}
          placeholder="Повторите пароль"
        />

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Регистрация..." : "Зарегистрироваться"}
        </button>
      </form>
    </section>
  );
};

export default Register;
