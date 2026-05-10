import "./App.css";
import { BrowserRouter, Navigate as RouterNavigate, Route, Routes } from "react-router-dom";
import Home from "./components/home";
import Login from "./components/login";
import Logout from "./components/logout";
import Navigate from "./components/navigate";
import Register from "./components/register";
import Dashboard from "./components/dashboard";
import Listings from "./components/listings";
import ListingDetail from "./components/listing-detail";

const PrivateRoute = ({ children }) => {
  const isAuth = Boolean(localStorage.getItem("access_token"));
  return isAuth ? children : <RouterNavigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navigate />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/register" element={<Register />} />
            <Route path="/listings" element={<Listings />} />
            <Route path="/listings/:id" element={<ListingDetail />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<RouterNavigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;