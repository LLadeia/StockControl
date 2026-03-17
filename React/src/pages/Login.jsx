import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

export default function Login() {
  const [username, setUsername] = useState("testuser");
  const [password, setPassword] = useState("testpass123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await axios.post(`${API_URL}/token/`, { username, password });
      localStorage.setItem("token", response.data.access);
      localStorage.setItem("user_type", "user");
      navigate("/Dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Credenciais inválidas");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      width: "100%", minHeight: "100vh",
      display: "flex", alignItems: "center", justifyContent: "center",
      background: "var(--bg)",
      backgroundImage: "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(79,142,247,0.12) 0%, transparent 70%)",
      padding: "20px"
    }}>
      <div style={{ width: "100%", maxWidth: 400 }}>

        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12,
            background: "var(--accent-glow)", border: "1px solid rgba(79,142,247,0.3)",
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            fontSize: "1.4em", marginBottom: 16
          }}>⬡</div>
          <h1 style={{ fontFamily: "'Syne', sans-serif", fontSize: "1.5rem", marginBottom: 6 }}>StockControl</h1>
          <p style={{ color: "var(--text3)", fontSize: "0.88em" }}>Sistema de Controle de Produção</p>
        </div>

        <div style={{
          background: "var(--bg2)", border: "1px solid var(--border)",
          borderRadius: 12, padding: 28
        }}>
          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div className="form-group">
              <label>Usuário</label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Senha</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Digite sua senha"
              />
            </div>

            {error && (
              <div style={{
                padding: "10px 14px", background: "var(--red-bg)",
                border: "1px solid rgba(247,93,93,0.25)", borderRadius: 7,
                color: "var(--red)", fontSize: "0.86em"
              }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="primary"
              style={{ marginTop: 4, padding: "0.7em 1.4em", fontSize: "0.95em" }}
            >
              {loading ? "Entrando…" : "Entrar"}
            </button>
          </form>

          <div style={{
            marginTop: 22, paddingTop: 18,
            borderTop: "1px solid var(--border)",
            fontSize: "0.8em", color: "var(--text3)"
          }}>
            <p style={{ marginBottom: 8, fontFamily: "'DM Mono', monospace", letterSpacing: "0.05em" }}>CREDENCIAIS DE TESTE</p>
            <div style={{ display: "flex", gap: 16 }}>
              <span>user: <code style={{ color: "var(--text2)" }}>testuser</code></span>
              <span>senha: <code style={{ color: "var(--text2)" }}>testpass123</code></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
