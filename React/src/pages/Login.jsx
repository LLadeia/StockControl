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
      const response = await axios.post(`${API_URL}/token/`, {
        username,
        password
      });

      const access_token = response.data.access;
      localStorage.setItem("token", access_token);
      localStorage.setItem("user_type", "user");
      
      // Redirecionar para dashboard
      navigate("/Dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      width: "100%",
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#f5f5f5",
      padding: "20px"
    }}>
      <div style={{
        backgroundColor: "#fff",
        padding: "40px",
        borderRadius: "12px",
        boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
        width: "100%",
        maxWidth: "420px"
      }}>
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <h1 style={{ margin: "0 0 12px 0", color: "#333", fontSize: "2em" }}>🔐 Login</h1>
          <p style={{ color: "#666", margin: 0, fontSize: "0.95em" }}>Sistema de Produção</p>
        </div>

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div className="form-group">
            <label>Usuário:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Digite seu usuário"
            />
          </div>

          <div className="form-group">
            <label>Senha:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: "8px",
              padding: "12px",
              backgroundColor: loading ? "#ccc" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontSize: "1em",
              fontWeight: "bold",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "background-color 0.2s"
            }}
          >
            {loading ? "🔄 Entrando..." : "🚀 Entrar"}
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: "20px",
            padding: "12px 16px",
            backgroundColor: "#f8d7da",
            border: "1px solid #f5c6cb",
            borderRadius: "6px",
            color: "#721c24",
            fontSize: "0.95em"
          }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: "32px", paddingTop: "24px", borderTop: "1px solid #eee", color: "#666", fontSize: "0.9em" }}>
          <p style={{ margin: "0 0 12px 0", fontWeight: "600" }}>
            📋 Credenciais de Teste:
          </p>
          <div style={{ background: "#f9f9f9", padding: "12px", borderRadius: "6px", marginBottom: "8px" }}>
            <p style={{ margin: "0 0 4px 0" }}>
              👤 Usuário: <code style={{ background: "#fff", padding: "2px 6px", borderRadius: "3px", fontWeight: "bold" }}>testuser</code>
            </p>
            <p style={{ margin: 0 }}>
              🔑 Senha: <code style={{ background: "#fff", padding: "2px 6px", borderRadius: "3px", fontWeight: "bold" }}>testpass123</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
