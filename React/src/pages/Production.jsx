import { useEffect, useState } from "react";
import api from '/src/api/api.js';
import Spinner from '/src/components/Spinner.jsx';

export default function Production() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [productions, setProductions] = useState([]);
  const [associations, setAssociations] = useState([]);

  useEffect(() => {
    loadInitial();
  }, []);

  const loadInitial = async () => {
    setLoading(true);
    try {
      const [pRes, prodRes, assocRes] = await Promise.all([
        api.get("products/"),
        api.get("production-logs/"),
        api.get("product-raw-materials/")
      ]);
      setProducts(pRes.data);
      setProductions(prodRes.data);
      setAssociations(assocRes.data);
    } catch (err) {
      pushToast("error", "Erro ao carregar dados");
      console.error(err);
    }
    setLoading(false);
  };

  const pushToast = (type, message) => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, type, message }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  };

  const checkCanProduce = async (productId) => {
    setLoading(true);
    try {
      const res = await api.get(`products/${productId}/can_produce/`);
      setStatus(res.data);
    } catch (err) {
      pushToast("error", "Erro ao verificar estoque");
      setStatus(null);
    }
    setLoading(false);
  };

  const produce = async () => {
    if (!selectedProduct) return;

    setLoading(true);
    try {
      const res = await api.post(
        `products/${selectedProduct}/produce/`,
        { quantity }
      );
      pushToast("success", `✅ Produzido com sucesso! ${quantity}x`);
      setSelectedProduct(null);
      setQuantity(1);
      setStatus(null);
      await loadInitial();
    } catch (err) {
      const msg = err.response?.data?.raw_material 
        ? `❌ Sem estoque: ${err.response.data.raw_material}`
        : "Estoque insuficiente";
      pushToast("error", msg);
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1>🏭 Produção</h1>
      </div>

      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type}`}>
            {t.message}
          </div>
        ))}
      </div>

      <div className="form-top-layout">
        <aside className="form-section">
          <h3>🔧 Produzir Agora</h3>
          <div style={{ display: "grid", gap: 16 }}>
            <div className="form-group">
              <label>Produto</label>
              <select
                value={selectedProduct || ""}
                onChange={(e) => {
                  setSelectedProduct(e.target.value);
                  checkCanProduce(e.target.value);
                }}
              >
                <option value="">Selecione um produto</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {selectedProduct && associations.filter(a => String(a.product) === String(selectedProduct)).length > 0 && (
              <div style={{ padding: 12, background: "#e3f2fd", borderRadius: 6 }}>
                {(() => {
                  const productAssocs = associations.filter(a => String(a.product) === String(selectedProduct));
                  let unitCost = 0;
                  productAssocs.forEach(assoc => {
                    const matPrice = parseFloat(assoc.raw_material_price || 0);
                    const manuf = parseFloat(assoc.manufacturing_price || 0);
                    unitCost += (matPrice * parseFloat(assoc.quantity)) + manuf;
                  });
                  const totalCost = unitCost * (quantity || 1);
                  return (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                      <div>
                        <small style={{ color: "#666" }}>Preço Unitário</small>
                        <p style={{ margin: 0, fontSize: "1.4em", fontWeight: "bold", color: "#007bff" }}>
                          R$ {unitCost.toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <small style={{ color: "#666" }}>Preço Total ({quantity}x)</small>
                        <p style={{ margin: 0, fontSize: "1.4em", fontWeight: "bold", color: "#28a745" }}>
                          R$ {totalCost.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}

            {loading && (
              <div style={{ color: "#007bff", display: "flex", alignItems: "center", gap: 8 }}>
                <Spinner size={20} /> Verificando estoque...
              </div>
            )}

            {status && !loading && (
              <div style={{ padding: 12, borderRadius: 6, background: status.can_produce ? "#e8f5e9" : "#ffebee" }}>
                {status.can_produce ? (
                  <p style={{ color: "green", margin: 0 }}>✅ Pode produzir</p>
                ) : (
                  <div style={{ color: "red", margin: 0 }}>
                    <p style={{ margin: "0 0 6px 0", fontWeight: "bold" }}>❌ Falta: {status.limiting_raw_material}</p>
                    <small>Necessário: {status.required} | Disponível: {status.available}</small>
                  </div>
                )}
              </div>
            )}

            <div className="form-group">
              <label>Quantidade</label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={e => setQuantity(e.target.value)}
              />
            </div>

            <button
              onClick={produce}
              disabled={loading || !status?.can_produce}
              style={{ padding: 12, background: status?.can_produce ? "#007bff" : "#ccc", color: "#fff", border: "none", borderRadius: 4, cursor: status?.can_produce ? "pointer" : "not-allowed", fontWeight: "bold", marginTop: 8 }}
            >
              {loading ? <><Spinner size={16} /> Produzindo...</> : "Produzir Agora"}
            </button>
          </div>
        </aside>

        <section>
          <h3>📋 Histórico de Produções</h3>
          {loading ? <Spinner /> : (
            <div style={{ overflowY: "auto", maxHeight: "600px" }}>
              {productions.length === 0 ? (
                <p style={{ color: "#999" }}>Nenhuma produção registrada</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Produto</th>
                      <th style={{ textAlign: "right", width: 120 }}>Preço Unit.</th>
                      <th style={{ textAlign: "center", width: 100 }}>Qtd</th>
                      <th style={{ textAlign: "right", width: 120 }}>Preço Total</th>
                      <th style={{ width: 180 }}>Data/Hora</th>
                    </tr>
                  </thead>
                  <tbody>
                    {productions.map(p => (
                        <tr key={p.id}>
                          <td>{p.product_name}</td>
                          <td style={{ textAlign: "right" }}>R$ {parseFloat(p.unit_price || 0).toFixed(2)}</td>
                          <td style={{ textAlign: "center" }}>x{p.quantity}</td>
                          <td style={{ textAlign: "right", fontWeight: "bold" }}>R$ {parseFloat(p.total_price || 0).toFixed(2)}</td>
                          <td style={{ fontSize: "0.9em", color: "#666" }}>{formatDate(p.created_at)}</td>
                        </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
