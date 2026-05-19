/**
 * App.jsx — корневой компонент приложения.
 *
 * Настраивает маршрутизацию через React Router:
 * - /          — домашняя страница
 * - /login     — вход
 * - /register  — регистрация
 * - /logout    — выход
 * - /dashboard — панель пользователя (защищённый маршрут)
 * - /listings  — список объявлений
 * - /listings/:id — детальное объявление
 * - *          — редирект на главную (404)
 */

import "./App.css";
import {
  BrowserRouter,
  Navigate as RouterNavigate,
  Route,
  Routes,
} from "react-router-dom";

// Компоненты страниц
import Home from "./components/home";
import Login from "./components/login";
import Logout from "./components/logout";
import Navigate from "./components/navigate";
import Register from "./components/register";
import Dashboard from "./components/dashboard";
import Listings from "./components/listings";
import ListingDetail from "./components/listing-detail";

/**
 * PrivateRoute — защищённый маршрут.
 *
 * Проверяет наличие access_token в localStorage.
 * Если токен есть — рендерит дочерний компонент.
 * Если токена нет — перенаправляет на /login.
 */
const PrivateRoute = ({ children }) => {
  const isAuth = Boolean(localStorage.getItem("access_token"));
  return isAuth ? children : <RouterNavigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        {/* Навигационная шапка */}
        <Navigate />
        {/* Основной контент */}
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/register" element={<Register />} />
            <Route path="/listings" element={<Listings />} />
            <Route path="/listings/:id" element={<ListingDetail />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            {/* 404 — редирект на главную */}
            <Route path="*" element={<RouterNavigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
