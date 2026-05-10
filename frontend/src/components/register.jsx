import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./axios";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/register/", { username, password });
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.error?.message || "Registration failed. Try another username.");
    }
  };

  return (
    <section className="page auth-page">
      <h2>Create account</h2>
      <form className="auth-form" onSubmit={submit}>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          value={username}
          required
          onChange={(e) => setUsername(e.target.value)}
        />
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          value={password}
          required
          onChange={(e) => setPassword(e.target.value)}
        />
        {error ? <p className="error">{error}</p> : null}
        <button type="submit">Register</button>
      </form>
    </section>
  );
};

export default Register;