# Komnataby — сервис аренды квартир и комнат

Монорепозиторий проекта **Komnataby**, включающий:

- **Backend**: Django 4.2 + Django REST Framework + PostgreSQL + JWT-аутентификация
- **Frontend**: React 18 + Vite + React Router

---

## 📋 Быстрый старт (Docker)

Самый простой способ запустить проект — через Docker Compose.

```bash
# 1. Клонируйте репозиторий
git clone <repo-url>
cd komnataby

# 2. Создайте .env файлы
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Запустите все сервисы
docker compose up --build
```

Сервисы станут доступны:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **Swagger Docs**: http://localhost:8000/api/v1/docs/
- **Django Admin**: http://localhost:8000/admin/

### Остановка

```bash
docker compose down
```

### Очистка данных

```bash
docker compose down -v  # удаляет и данные PostgreSQL
```

---

## 🐍 Локальный запуск (без Docker)

### Backend

```bash
# 1. Создайте виртуальное окружение
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 2. Установите зависимости
pip install -r requirements.dev.txt

# 3. Создайте .env файл
cp .env.example .env
# Отредактируйте .env — укажите SECRET_KEY и параметры БД

# 4. Настройте PostgreSQL
# Убедитесь, что PostgreSQL запущен и создана база данных:
#   createdb komnata_db

# 5. Примените миграции
python manage.py migrate

# 6. Создайте суперпользователя (для админки)
python manage.py createsuperuser

# 7. Запустите сервер
python manage.py runserver
```

### Frontend

```bash
# 1. Перейдите в директорию frontend
cd frontend

# 2. Установите зависимости
npm install

# 3. Создайте .env файл
cp .env.example .env

# 4. Запустите dev-сервер
npm run dev
```

---

## 🧪 Запуск тестов

```bash
cd backend
python manage.py test authentification
```

---

## 📁 Структура проекта

```
komnataby/
├── backend/                    # Django-бэкенд
│   ├── authentification/       # Приложение: пользователи, аутентификация, listings
│   │   ├── models.py           # Модели: User, Listing
│   │   ├── serializers.py      # Сериализаторы с валидацией
│   │   ├── views.py            # API-эндпоинты
│   │   ├── urls.py             # Маршруты приложения
│   │   ├── admin.py            # Админ-панель
│   │   ├── tests.py            # Тесты
│   │   └── migrations/         # Миграции БД
│   ├── backend/                # Настройки проекта
│   │   ├── settings.py         # Конфигурация Django
│   │   ├── urls.py             # Корневые маршруты
│   │   ├── exceptions.py       # Кастомный обработчик ошибок API
│   │   └── views.py            # Health check
│   ├── Dockerfile              # Docker-образ бэкенда
│   ├── manage.py
│   ├── .env.example
│   └── requirements*.txt
├── frontend/                   # React-фронтенд
│   ├── src/
│   │   ├── components/
│   │   │   ├── axios.jsx       # Axios с JWT-интерцепторами
│   │   │   ├── App.jsx         # Маршрутизация
│   │   │   ├── home.jsx        # Домашняя страница
│   │   │   ├── login.jsx       # Вход
│   │   │   ├── register.jsx    # Регистрация
│   │   │   ├── logout.jsx      # Выход
│   │   │   ├── dashboard.jsx   # Панель пользователя
│   │   │   ├── listings.jsx    # Список объявлений
│   │   │   ├── listing-detail.jsx  # Детали объявления
│   │   │   └── navigate.jsx    # Навигационная шапка
│   │   ├── App.css             # Стили
│   │   ├── index.css           # Базовые стили
│   │   └── main.jsx            # Точка входа
│   ├── Dockerfile              # Docker-образ фронтенда
│   ├── nginx.conf              # Конфигурация nginx
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml          # Оркестрация сервисов
├── requirements.txt            # Production-зависимости
├── requirements.dev.txt        # Development-зависимости
└── SETUP.md                    # Этот файл
```

---

## 🔐 Безопасность

### Что реализовано

| Мера | Описание |
|------|----------|
| **JWT-аутентификация** | Access-токен (60 мин) + Refresh-токен (7 дней) с ротацией |
| **Rate limiting** | `/token/` — 5 запросов/мин, `/register/` — 3 запроса/мин |
| **Валидация паролей** | Минимум 8 символов, не только цифры, Django-валидаторы |
| **Валидация изображений** | MIME-тип (jpeg/png/webp/gif), размер ≤ 5 МБ |
| **CORS** | Отключён по умолчанию, включается через `DJANGO_CORS_ALLOW_ALL` |
| **CSRF** | Django CSRF-мидлваре включён |
| **Обработчик ошибок** | Унифицированный формат `{"ok": false, "error": {...}}` |

### Что нужно настроить перед продакшеном

1. **Сгенерировать новый `DJANGO_SECRET_KEY`** (никогда не используйте дефолтный!)
2. **Установить `DJANGO_DEBUG=False`**
3. **Указать `DJANGO_ALLOWED_HOSTS`** с вашими доменами
4. **Настроить `DJANGO_CORS_ALLOWED_ORIGINS`** с конкретными origin'ами
5. **Настроить HTTPS** (через Nginx или прокси)
6. **Заменить пароль PostgreSQL** на надёжный
7. **Настроить статическую раздачу** через WhiteNoise или CDN

---

## 📖 API-эндпоинты

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/v1/token/` | Получить пару токенов (login) |
| `POST` | `/api/v1/token/refresh/` | Обновить access-токен |
| `POST` | `/api/v1/register/` | Регистрация |
| `POST` | `/api/v1/logout/` | Выход (блокировка токена) |

### Объявления

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/api/v1/listings/` | Список объявлений (с пагинацией) |
| `POST` | `/api/v1/listings/` | Создать объявление |
| `GET` | `/api/v1/listings/<id>/` | Просмотр объявления |
| `PATCH` | `/api/v1/listings/<id>/` | Обновить (только автор) |
| `DELETE` | `/api/v1/listings/<id>/` | Удалить (только автор) |

### Фильтрация списка

```
GET /api/v1/listings/?search=комната&city=Минск&min_price=300&max_price=1000&ordering=price_asc
```

### Swagger документация

Откройте http://localhost:8000/api/v1/docs/ для интерактивной документации API.

---

## 🛠 Скрипты (frontend)

```bash
npm run dev       # Запуск dev-сервера
npm run build     # Сборка продакшен-бандла
npm run lint      # ESLint проверка
npm run preview   # Превью продакшен-сборки
```

## 🐛 Известные ограничения

- Нет загрузки изображений в UI (только через Swagger/admin)
- Нет email-верификации при регистрации
- Нет восстановления пароля
- Нет поиска по геолокации
- Нет чата между арендодателем и арендатором
