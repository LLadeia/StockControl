import { Link } from "react-router-dom";

const cards = [
  { to: "/products",      icon: "▦",  title: "Produtos",          desc: "Cadastrar e gerenciar produtos" },
  { to: "/raw-materials", icon: "⬡",  title: "Matérias-Primas",   desc: "Controlar estoque de insumos" },
  { to: "/relations",     icon: "⬡",  title: "Associações",       desc: "Vincular matérias aos produtos" },
  { to: "/production",    icon: "◈",  title: "Produção",          desc: "Planejar e registrar produções" },
];

export default function Dashboard() {
  return (
    <div className="container" style={{ paddingTop: 40 }}>
      <div style={{ marginBottom: 36 }}>
        <p style={{ fontFamily: "'DM Mono', monospace", fontSize: "0.75em", letterSpacing: "0.1em", color: "var(--text3)", textTransform: "uppercase", marginBottom: 8 }}>
          Sistema de Controle
        </p>
        <h1 style={{ fontSize: "2rem", marginBottom: 6 }}>Painel de Produção</h1>
        <p style={{ color: "var(--text3)", fontSize: "0.9em" }}>Gerencie produtos, insumos e planeje sua produção</p>
      </div>

      <nav style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
        {cards.map(c => (
          <Link key={c.to} to={c.to} className="dashboard-card">
            <div style={{
              width: 38, height: 38, borderRadius: 8,
              background: "var(--accent-glow)", border: "1px solid rgba(79,142,247,0.2)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "1.1em", color: "var(--accent)", marginBottom: 14, fontFamily: "monospace"
            }}>
              {c.icon}
            </div>
            <h3>{c.title}</h3>
            <p>{c.desc}</p>
          </Link>
        ))}
      </nav>
    </div>
  );
}
