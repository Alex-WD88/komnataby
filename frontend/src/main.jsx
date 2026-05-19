/**
 * main.jsx — точка входа в React-приложение.
 *
 * Рендерит компонент App в DOM-элемент с id="root".
 * Использует React.StrictMode для обнаружения потенциальных проблем.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
