import React from "react";
import { Link } from "react-router-dom";

const Navigate = () => {
  const isAuth = Boolean(localStorage.getItem("access_token"));

  return (
    <header className="app-header">
      <Link to="/" className="brand">
        Komnata.by
      </Link>
      <nav className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/listings">Listings</Link>
        {isAuth ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/logout">Logout</Link>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  );
};

export default Navigate;