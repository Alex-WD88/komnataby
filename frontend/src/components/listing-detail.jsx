/**
 * ListingDetail.jsx — детальная страница одного объявления.
 *
 * Загружает данные объявления по ID из URL-параметра.
 * Отображает: заголовок, город, описание, цену, автора.
 */

import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "./axios";

const ListingDetail = () => {
  const { id } = useParams(); // ID объявления из URL
  const [item, setItem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadListing = async () => {
      setIsLoading(true);
      setError("");
      try {
        const { data } = await api.get(`/listings/${id}/`);
        setItem(data?.data || null);
      } catch (err) {
        setError(
          err.response?.data?.error?.message || "Не удалось загрузить объявление."
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadListing();
  }, [id]);

  return (
    <section className="page">
      {/* Кнопка «Назад» */}
      <Link to="/listings" className="secondary-btn inline-btn">
        ← Назад к объявлениям
      </Link>

      {isLoading && <p className="muted">Загрузка объявления...</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && !error && item && (
        <article className="listing-detail">
          <h2>{item.title}</h2>
          {item.image && (
            <img
              src={`${import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"}/media/${item.image}`}
              alt={item.title}
              style={{ maxWidth: "100%", borderRadius: 8, marginBottom: 12 }}
            />
          )}
          <p className="muted">{item.city}</p>
          <p>{item.description || "Описание отсутствует"}</p>
          <p>
            <strong>{item.price} BYN/мес</strong>
          </p>
          <p className="muted">Создано: {item.created_by}</p>
          <p className="muted">Дата: {new Date(item.created_at).toLocaleDateString("ru-RU")}</p>
        </article>
      )}
    </section>
  );
};

export default ListingDetail;
