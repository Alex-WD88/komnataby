import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "./axios";

const ListingDetail = () => {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setIsLoading(true);
      setError("");
      try {
        const { data } = await api.get(`/listings/${id}/`);
        setItem(data?.data || null);
      } catch (err) {
        setError(err.response?.data?.error?.message || "Failed to load listing.");
      } finally {
        setIsLoading(false);
      }
    })();
  }, [id]);

  return (
    <section className="page">
      <Link to="/listings" className="secondary-btn inline-btn">
        Back to listings
      </Link>
      {isLoading ? <p className="muted">Loading listing...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      {!isLoading && !error && item ? (
        <article className="listing-detail">
          <h2>{item.title}</h2>
          <p className="muted">{item.city}</p>
          <p>{item.description || "No description"}</p>
          <p>
            <strong>{item.price}</strong>
          </p>
          <p className="muted">Created by {item.created_by}</p>
        </article>
      ) : null}
    </section>
  );
};

export default ListingDetail;
