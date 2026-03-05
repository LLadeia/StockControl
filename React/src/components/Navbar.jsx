import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import "../styles/navbar.css";

export default function Navbar() {
  const [isSuperUser, setIsSuperUser] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const userType = localStorage.getItem("user_type");
    setIsSuperUser(userType === "superuser");
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_type");
    setIsSuperUser(false);
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="navbar-links">
        <Link to="/" className="nav-link">
          🏠 Dashboard
        </Link>
        <Link to="/products" className="nav-link">
          📦 Produtos
        </Link>
        <Link to="/raw-materials" className="nav-link">
          🧪 Matérias-Primas
        </Link>
        <Link to="/relations" className="nav-link">
          🔗 Associação
        </Link>
        <Link to="/production" className="nav-link">
          🏭 Produção
        </Link>
        
        {isSuperUser && (
          <Link to="/auditory" className="nav-link admin-link">
            🔍 Auditoria
          </Link>
        )}
      </div>

      <div className="navbar-actions">
        {isSuperUser && (
          <span className="admin-badge">
            👤 Admin
          </span>
        )}
        <button
          onClick={handleLogout}
          className="logout-btn"
        >
          🚪 Sair
        </button>
      </div>
    </nav>
  );
}
