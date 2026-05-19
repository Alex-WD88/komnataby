# Komnataby — Frontend

React 18 + Vite приложение для сервиса аренды квартир **komnata.by**.

## 📦 Установка

```bash
npm install
```

## 🚀 Запуск

```bash
# Создайте .env из шаблона
cp .env.example .env

# Запустите dev-сервер
npm run dev
```

Откройте http://localhost:5173 в браузере.

## 📋 Скрипты

| Команда        | Описание                     |
|---------------|------------------------------|
| `npm run dev` | Запуск dev-сервера (HMR)     |
| `npm run build`  | Сборка продакшен-бандла |
| `npm run lint`   | ESLint проверка          |
| `npm run preview`  | Превью продакшен-сборки |

## 🔧 Конфигурация

Переменные окружения:

| Переменная       | Описание                    | По умолчанию              |
|-----------------|-----------------------------|---------------------------|
| `VITE_API_URL`  | Базовый URL API бэкенда    | `http://localhost:8000/api/v1` |

## 📁 Структура

```
src/
├── components/
│   ├── axios.jsx      — Axios с JWT-интерцепторами
│   ├── App.jsx        — Маршрутизация
│   ├── home.jsx       — Домашняя страница
│   ├── login.jsx      — Вход
│   ├── register.jsx   — Регистрация
│   ├── logout.jsx     — Выход
│   ├── dashboard.jsx  — Панель пользователя
│   ├── listings.jsx   — Список объявлений
│   ├── listing-detail.jsx — Детали объявления
│   └── navigate.jsx   — Навигационная шапка
├── App.css            — Стили App
├── index.css          — Базовые стили
└── main.jsx           — Точка входа
```

## 🔐 Авторизация

Токены хранятся в `localStorage`:
- `access_token` — JWT access-токен
- `refresh_token` — JWT refresh-токен

Axios-интерцептор автоматически добавляет `Authorization: Bearer <token>` к запросам
и обновляет токен при истечении.
