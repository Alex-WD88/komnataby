/**
 * vite.config.js — конфигурация Vite для React-приложения.
 *
 * Использует плагин @vitejs/plugin-react для:
 * - Fast Refresh (горячая перезагрузка при изменении файлов)
 * -jsx-преобразования через Babel
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Настройка dev-server
  server: {
    port: 5173,
    host: true, // Доступен по всем сетевым интерфейсам (для Docker)
  },
});
