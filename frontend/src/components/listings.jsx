import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "./axios";

const getUserIdFromToken = () => {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return null;
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id || null;
  } catch {
    return null;
  }
};

const Listings = () => {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);
  const [filters, setFilters] = useState({
    search: "",
    city: "",
    min_price: "",
    max_price: "",
    ordering: "date_desc",
  });
  const [form, setForm] = useState({
    title: "",
    description: "",
    price: "",
    city: "",
  });
  const [editingId, setEditingId] = useState(null);

  const isAuth = Boolean(localStorage.getItem("access_token"));
  const currentUserId = getUserIdFromToken();

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
      setError(err.response?.data?.error?.message || "Failed to load listings.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadListings();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        title: form.title,
        description: form.description,
        price: Number(form.price),
        city: form.city,
      };
      if (editingId) {
        await api.patch(`/listings/${editingId}/`, payload);
      } else {
        await api.post("/listings/", payload);
      }
      setForm({ title: "", description: "", price: "", city: "" });
      setEditingId(null);
      await loadListings();
    } catch (err) {
      setError(err.response?.data?.error?.message || "Failed to save listing.");
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = async (event) => {
    event.preventDefault();
    await loadListings(1);
  };

  const resetFilters = async () => {
    const nextFilters = { search: "", city: "", min_price: "", max_price: "", ordering: "date_desc" };
    setFilters(nextFilters);
    await loadListings(1, nextFilters);
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      title: item.title,
      description: item.description || "",
      price: String(item.price),
      city: item.city,
    });
  };

  const removeListing = async (id) => {
    setError("");
    try {
      await api.delete(`/listings/${id}/`);
      await loadListings();
    } catch (err) {
      setError(err.response?.data?.error?.message || "Failed to delete listing.");
    }
  };

  return (
    <section className="page">
      <h2>Listings</h2>
      <p className="muted">Demo feature module for project wrapper.</p>

      <form className="filters-row" onSubmit={applyFilters}>
        <input
          name="search"
          placeholder="Search by title"
          value={filters.search}
          onChange={handleFilterChange}
        />
        <input name="city" placeholder="City" value={filters.city} onChange={handleFilterChange} />
        <input
          name="min_price"
          type="number"
          min="0"
          placeholder="Min price"
          value={filters.min_price}
          onChange={handleFilterChange}
        />
        <input
          name="max_price"
          type="number"
          min="0"
          placeholder="Max price"
          value={filters.max_price}
          onChange={handleFilterChange}
        />
        <select name="ordering" value={filters.ordering} onChange={handleFilterChange}>
          <option value="date_desc">Newest first</option>
          <option value="date_asc">Oldest first</option>
          <option value="price_asc">Price low to high</option>
          <option value="price_desc">Price high to low</option>
        </select>
        <button type="submit">Apply</button>
        <button type="button" className="secondary-btn" onClick={resetFilters}>
          Reset
        </button>
      </form>

      {isAuth ? (
        <form className="auth-form" onSubmit={handleSubmit}>
          <h3>{editingId ? "Edit listing" : "Create listing"}</h3>
          <label htmlFor="title">Title</label>
          <input id="title" name="title" value={form.title} onChange={handleChange} required />
          <label htmlFor="description">Description</label>
          <input id="description" name="description" value={form.description} onChange={handleChange} />
          <label htmlFor="price">Price</label>
          <input
            id="price"
            name="price"
            type="number"
            min="1"
            value={form.price}
            onChange={handleChange}
            required
          />
          <label htmlFor="city">City</label>
          <input id="city" name="city" value={form.city} onChange={handleChange} required />
          <button type="submit">{editingId ? "Save changes" : "Create listing"}</button>
          {editingId ? (
            <button
              type="button"
              className="secondary-btn"
              onClick={() => {
                setEditingId(null);
                setForm({ title: "", description: "", price: "", city: "" });
              }}
            >
              Cancel edit
            </button>
          ) : null}
        </form>
      ) : (
        <p className="muted">Login to create listings.</p>
      )}

      {error ? <p className="error">{error}</p> : null}

      {isLoading ? <p className="muted">Loading listings...</p> : null}
      {!isLoading && !error && items.length === 0 ? <p className="muted">No listings yet.</p> : null}
      {!isLoading && items.length > 0 ? (
        <div className="listings-grid">
          {items.map((item) => (
            <article key={item.id} className="listing-card">
              <h3>
                <Link to={`/listings/${item.id}`}>{item.title}</Link>
              </h3>
              <p className="muted">{item.city}</p>
              <p>{item.description || "No description"}</p>
              <p>
                <strong>{item.price}</strong>
              </p>
              <p className="muted">by {item.created_by}</p>
              {isAuth && currentUserId && item.created_by_id === currentUserId ? (
                <div className="actions-row">
                  <button type="button" className="secondary-btn" onClick={() => startEdit(item)}>
                    Edit
                  </button>
                  <button type="button" className="danger-btn" onClick={() => removeListing(item.id)}>
                    Delete
                  </button>
                </div>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
      {!isLoading && total > 0 ? (
        <div className="pagination-row">
          <button type="button" className="secondary-btn" onClick={() => loadListings(page - 1)} disabled={!prevPage}>
            Previous
          </button>
          <span className="muted">Page {page}</span>
          <button type="button" className="secondary-btn" onClick={() => loadListings(page + 1)} disabled={!nextPage}>
            Next
          </button>
        </div>
      ) : null}
    </section>
  );
};

export default Listings;
