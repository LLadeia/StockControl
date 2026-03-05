import { Link } from "react-router-dom";

export default function Dashboard() {
  return (
    <div className="container">
      <div className="page-header">
        <h1>📊 Sistema de Produção</h1>
      </div>

      <nav style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 20 }}>
        <Link to="/products" className="dashboard-card">
          <div style={{ fontSize: "2.5em", marginBottom: 10 }}>📦</div>
          <h3 style={{ margin: "0 0 8px 0" }}>Cadastro de Produtos</h3>
          <p style={{ margin: 0, color: "#666", fontSize: "0.9em" }}>Gerenciar produtos</p>
        </Link>
        <Link to="/raw-materials" className="dashboard-card">
          <div style={{ fontSize: "2.5em", marginBottom: 10 }}>🧪</div>
          <h3 style={{ margin: "0 0 8px 0" }}>Matérias-Primas</h3>
          <p style={{ margin: 0, color: "#666", fontSize: "0.9em" }}>Gerenciar matérias-primas</p>
        </Link>
        <Link to="/relations" className="dashboard-card">
          <div style={{ fontSize: "2.5em", marginBottom: 10 }}>🔗</div>
          <h3 style={{ margin: "0 0 8px 0" }}>Associações</h3>
          <p style={{ margin: 0, color: "#666", fontSize: "0.9em" }}>Associar matérias aos produtos</p>
        </Link>
        <Link to="/production" className="dashboard-card">
          <div style={{ fontSize: "2.5em", marginBottom: 10 }}>🏭</div>
          <h3 style={{ margin: "0 0 8px 0" }}>Produção</h3>
          <p style={{ margin: 0, color: "#666", fontSize: "0.9em" }}>Registrar produção</p>
        </Link>
      </nav>
    </div>
  );
}
