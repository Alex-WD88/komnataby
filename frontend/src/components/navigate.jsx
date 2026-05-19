/**
 * Navigate.jsx — навигационная шапка приложения.
 *
 * Отображает:
 * - Логотип (ссылка на главную).
 * - Навигационные ссылки.
 * - Кнопки входа/регистрации или выхода — в зависимости от авторизации.
 *
 * Проверка авторизации: через access_token в localStorage.
 */

import React from "react";
import { Link } from "react-router-dom";

const Navigate = () => {
  // Проверяем авторизацию
  const isAuth = Boolean(localStorage.getItem("access_token"));

  return (
    <header className="app-header">
      {/* Логотип */}
      <Link to="/" className="brand">
        Komnata.by
      </Link>

      {/* Навигационные ссылки */}
      <nav className="nav-links">
        <Link to="/">Главная</Link>
        <Link to="/listings">Объявления</Link>

        {isAuth ? (
          <>
            <Link to="/dashboard">Панель</Link>
            <Link to="/logout">Выйти</Link>
          </>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register">Регистрация</Link>
          </>
        )}
      </nav>
    </header>
  );
};

export default Navigate;
