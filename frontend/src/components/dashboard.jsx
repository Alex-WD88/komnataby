import React, { useEffect, useState } from "react";
import api from "./axios";

const Dashboard = () => {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setIsLoading(true);
      try {
        const { data } = await api.get("/home/");
        setMessage(data?.data?.message || "");
      } catch (err) {
        setError(err.response?.data?.error?.message || "You need to login to access dashboard.");
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  return (
    <section className="page">
      <h2>Dashboard</h2>
      {isLoading ? <p className="muted">Loading dashboard...</p> : null}
      {message ? <p>{message}</p> : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
};

export default Dashboard;
