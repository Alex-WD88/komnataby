/**
 * Listings.jsx — страница со списком объявлений.
 *
 * Функционал:
 * - Просмотр списка объявлений с пагинацией.
 * - Фильтрация по городу, поиску, диапазону цен.
 * - Сортировка (по дате, по цене).
 * - Создание / редактирование / удаление объявлений (только для авторизованных).
 *
 * Авторизация:
 * - Проверка через access_token в localStorage.
 * - ID текущего пользователя извлекается из JWT-токена.
 */

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "./axios";

/**
 * Извлекает user_id из JWT-токена.
 *
 * ВНИМАНИЕ: Это клиентская логика — токен можно подделать.
 * Серверная проверка прав остаётся в views.py (IsListingOwnerOrReadOnly).
 */
const getUserIdFromToken = () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return null;
    // Декодируем payload JWT (вторая часть токена)
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id || null;
  } catch {
    return null;
  }
};

const Listings = () => {
  // Состояние списка объявлений
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);

  // Фильтры
  const [filters, setFilters] = useState({
    search: "",
    city: "",
    min_price: "",
    max_price: "",
    ordering: "date_desc",
  });

  // Форма создания/редактирования
  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    city: "",
  });
  const [editingId, setEditingId] = useState(null);

  // Информация о авторизации
  const isAuth = Boolean(localStorage.getItem("access_token"));
  const currentUserId = getUserIdFromToken();

  /**
   * Загрузка объявлений с фильтрацией и пагинацией.
   *
   * @param {number} next - номер страницы
   * @param {object} customFilters - кастомные фильтры (если не текущие)
   */
  const loadListings = async (next = page, customFilters = filters) => {
    setIsLoading(true);
    setError("");
    try {
      const params = {
        page: next,
        page_size: 6,
        ...customFilters,
      };
      const { data } = await api.get("/listings/", { params });
      const payload = data?.results || {};
      setItems(payload?.data ?? []);
      setTotal(data?.count ?? 0);
      setNextPage(data?.next);
      setPrevPage(data?.previous);
      setPage(next);
    } catch (err) {
      setError(
        err.response?.data?.error?.message || "Не удалось загрузить объявления."
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Первая загрузка при монтировании компонента
  useEffect(() => {
    loadListings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Обработчики формы
  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  /**
   * Отправка формы — создание или обновление объявления.
   */
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    // Валидация на клиенте
    if (form.title.trim().length < 3) {
      setError("Заголовок должен содержать минимум 3 символа.");
      return;
    }
    if (!form.city.trim()) {
      setError("Укажите город.");
      return;
    }

    try {
      const payload = {
        title: form.title,
        description: form.description,
        price: Number(form.price),
        city: form.city,
      };

      if (editingId) {
        // Обновление существующего объявления
        await api.patch(`/listings/${editingId}/`, payload);
      } else {
        // Создание нового объявления
        await api.post("/listings/", payload);
      }

      // Сбрасываем форму
      setForm({ title: "", description: "", price: "", city: "" });
      setEditingId(null);
      // Перезагружаем список
      await loadListings();
    } catch (err) {
      setError(
        err.response?.data?.error?.message || "Не удалось сохранить объявление."
      );
    }
  };

  // Обработчики фильтров
  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = async (event) => {
    event.preventDefault();
    await loadListings(1); // Сбрасываем на первую страницу
  };

  const resetFilters = async () => {
    const nextFilters = {
      search: "",
      city: "",
      min_price: "",
      max_price: "",
      ordering: "date_desc",
    };
    setFilters(nextFilters);
    await loadListings(1, nextFilters);
  };

  // Действия с объявлениями
  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      title: item.title,
      description: item.description || "",
      price: String(item.price),
      city: item.city,
    });
    // Прокрутка к форме
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const removeListing = async (id) => {
    // Подтверждение удаления
    if (!window.confirm("Вы уверены, что хотите удалить это объявление?")) {
      return;
    }

    setError("");
    try {
      await api.delete(`/listings/${id}/`);
      await loadListings();
    } catch (err) {
      setError(
        err.response?.data?.error?.message || "Не удалось удалить объявление."
      );
    }
  };

  return (
    <section className="page">
      <h2>Объявления</h2>
      <p className="muted">Поиск и управление объявлениями об аренде.</p>

      {/* --- Фильтры --- */}
      <form className="filters-row" onSubmit={applyFilters}>
        <input
          name="search"
          placeholder="Поиск по заголовку"
          value={filters.search}
          onChange={handleFilterChange}
        />
        <input
          name="city"
          placeholder="Город"
          value={filters.city}
          onChange={handleFilterChange}
        />
        <input
          name="min_price"
          type="number"
          min="0"
          placeholder="Мин. цена"
          value={filters.min_price}
          onChange={handleFilterChange}
        />
        <input
          name="max_price"
          type="number"
          min="0"
          placeholder="Макс. цена"
          value={filters.max_price}
          onChange={handleFilterChange}
        />
        <select name="ordering" value={filters.ordering} onChange={handleFilterChange}>
          <option value="date_desc">Сначала новые</option>
          <option value="date_asc">Сначала старые</option>
          <option value="price_asc">Цена: по возрастанию</option>
          <option value="price_desc">Цена: по убыванию</option>
        </select>
        <button type="submit">Применить</button>
        <button type="button" className="secondary-btn" onClick={resetFilters}>
          Сбросить
        </button>
      </form>

      {/* --- Форма создания / редактирования --- */}
      {isAuth ? (
        <form className="auth-form" onSubmit={handleSubmit}>
          <h3>{editingId ? "Редактировать объявление" : "Создать объявление"}</h3>
          <label htmlFor="title">Заголовок</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            minLength={3}
            placeholder="Например: Комната в Минске"
          />
          <label htmlFor="description">Описание</label>
          <input
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Подробности об аренде"
          />
          <label htmlFor="price">Цена (BYN/мес)</label>
          <input
            id="price"
            name="price"
            type="number"
            min="1"
            value={form.price}
            onChange={handleChange}
            required
            placeholder="500"
          />
          <label htmlFor="city">Город</label>
          <input
            id="city"
            name="city"
            value={form.city}
            onChange={handleChange}
            required
            minLength={2}
            placeholder="Минск"
          />
          <button type="submit">
            {editingId ? "Сохранить изменения" : "Создать объявление"}
          </button>
          {editingId && (
            <button
              type="button"
              className="secondary-btn"
              onClick={() => {
                setEditingId(null);
                setForm({ title: "", description: "", price: "", city: "" });
              }}
            >
              Отменить редактирование
            </button>
          )}
        </form>
      ) : (
        <p className="muted">Войдите в систему, чтобы создавать объявления.</p>
      )}

      {/* --- Сообщения об ошибках --- */}
      {error && <p className="error">{error}</p>}
      {isLoading && <p className="muted">Загрузка объявлений...</p>}
      {!isLoading && !error && items.length === 0 && (
        <p className="muted">Объявлений пока нет.</p>
      )}

      {/* --- Сетка объявлений --- */}
      {!isLoading && items.length > 0 && (
        <div className="listings-grid">
          {items.map((item) => (
            <article key={item.id} className="listing-card">
              <h3>
                <Link to={`/listings/${item.id}`}>{item.title}</Link>
              </h3>
              <p className="muted">{item.city}</p>
              <p>{item.description || "Описание отсутствует"}</p>
              <p>
                <strong>{item.price} BYN/мес</strong>
              </p>
              <p className="muted">Автор: {item.created_by}</p>
              {/* Кнопки редактирования/удаления — только для автора */}
              {isAuth &&
                currentUserId &&
                item.created_by_id === currentUserId && (
                  <div className="actions-row">
                    <button
                      type="button"
                      className="secondary-btn"
                      onClick={() => startEdit(item)}
                    >
                      Редактировать
                    </button>
                    <button
                      type="button"
                      className="danger-btn"
                      onClick={() => removeListing(item.id)}
                    >
                      Удалить
                    </button>
                  </div>
                )}
            </article>
          ))}
        </div>
      )}

      {/* --- Пагинация --- */}
      {!isLoading && total > 0 && (
        <div className="pagination-row">
          <button
            type="button"
            className="secondary-btn"
            onClick={() => loadListings(page - 1)}
            disabled={!prevPage}
          >
            Назад
          </button>
          <span className="muted">Страница {page}</span>
          <button
            type="button"
            className="secondary-btn"
            onClick={() => loadListings(page + 1)}
            disabled={!nextPage}
          >
            Далее
          </button>
        </div>
      )}
    </section>
  );
};

export default Listings;
