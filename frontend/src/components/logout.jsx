import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "./axios";

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          await api.post("/logout/", { refresh_token: refreshToken });
        }
      } catch {
        // Ignore logout API errors; local logout is still required.
      } finally {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/login");
      }
    })();
  }, [navigate]);

  return <section className="page">Signing out...</section>;
};

export default Logout;