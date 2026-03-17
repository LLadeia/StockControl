import { Link, useNavigate, useLocation } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_type");
    navigate("/");
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <span className="navbar-brand">StockControl</span>

      <div className="navbar-links">
        <Link to="/products"      className={`nav-link${isActive("/products")      ? " active" : ""}`}>Produtos</Link>
        <Link to="/raw-materials" className={`nav-link${isActive("/raw-materials") ? " active" : ""}`}>Matérias-Primas</Link>
        <Link to="/relations"     className={`nav-link${isActive("/relations")     ? " active" : ""}`}>Associações</Link>
        <Link to="/production"    className={`nav-link${isActive("/production")    ? " active" : ""}`}>Produção</Link>
      </div>

      <div className="navbar-actions">
        <button onClick={handleLogout} className="logout-btn">Sair</button>
      </div>
    </nav>
  );
}
