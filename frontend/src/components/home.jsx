import React, { useEffect, useState } from "react";
import api from "./axios";

const Home = () => {
  const [health, setHealth] = useState("loading");
  const [message, setMessage] = useState("");
  const [isLoadingHome, setIsLoadingHome] = useState(false);
  const [homeError, setHomeError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        await api.get("/health/");
        setHealth("online");
      } catch {
        setHealth("offline");
      }

      setIsLoadingHome(true);
      setHomeError("");
      try {
        const { data } = await api.get("/home/");
        setMessage(data?.data?.message || "");
      } catch (err) {
        setMessage("");
        setHomeError(err.response?.data?.error?.message || "Login to access protected API data.");
      } finally {
        setIsLoadingHome(false);
      }
    })();
  }, []);

  return (
    <section className="page">
      <h1>Project wrapper is ready</h1>
      <p className="muted">Backend status: {health}</p>
      {isLoadingHome ? <p className="muted">Loading protected data...</p> : null}
      {!isLoadingHome && message ? <p>{message}</p> : null}
      {!isLoadingHome && !message ? <p className="muted">{homeError || "No data."}</p> : null}
    </section>
  );
};

export default Home;