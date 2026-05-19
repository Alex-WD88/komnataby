# ==============================================================================
# Многоэтапный Dockerfile для React-фронтенда (Vite)
# ==============================================================================
# Этап 1: build — установка зависимостей и сборка
# Этап 2: nginx — раздаём собранную статику через nginx
# ==============================================================================

# ---------- Этап 1: сборка ----------
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем package.json и package-lock.json для кэширования слоёв
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY . .

# Собираем продакшен-бандл
RUN npm run build

# ---------- Этап 2: nginx ----------
FROM nginx:alpine

# Копируем собранную статику в nginx-директорию
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx (переопределяем default.conf)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Открываем порт 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost/ || exit 1

# Запускаем nginx в foreground
CMD ["nginx", "-g", "daemon off;"]
