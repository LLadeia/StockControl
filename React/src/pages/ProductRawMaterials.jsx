import { useEffect, useState } from "react";
import api from "/src/api/api.js";
import Spinner from "/src/components/Spinner.jsx";
import ModalForm from "/src/components/ModalForm.jsx";
import EditForm from "/src/pages/EditForm.jsx";

export default function ProductRawMaterials() {
  const [products, setProducts] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [associations, setAssociations] = useState([]);

  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedMaterial, setSelectedMaterial] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [manufacturingPrice, setManufacturingPrice] = useState(0);

  const [editing, setEditing] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [pRes, mRes, aRes] = await Promise.all([
        api.get("products/"),
        api.get("raw-materials/"),
        api.get("product-raw-materials/"),
      ]);
      setProducts(pRes.data);
      setMaterials(mRes.data);
      setAssociations(aRes.data);
    } catch (err) {
      pushToast("error", "Erro ao carregar dados");
    }
    setLoading(false);
  };

  const pushToast = (type, message) => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, type, message }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  };

  const associate = async () => {
    if (!selectedProduct || !selectedMaterial || !quantity) return pushToast("error", "Preencha o formulário");
    setLoading(true);
    try {
      // Verifica estoque
      const mat = (await api.get(`raw-materials/${selectedMaterial}/`)).data;
      if (mat.stock < Number(quantity)) {
        pushToast("error", "Sem estoque suficiente");
        setLoading(false);
        return;
      }

      // Cria associação
      await api.post(`product-raw-materials/`, {
        product: selectedProduct,
        raw_material: selectedMaterial,
        quantity: Number(quantity),
        manufacturing_price: Number(manufacturingPrice) || 0,
      });

      // Debita matéria-prima
      await api.patch(`raw-materials/${selectedMaterial}/`, { stock: mat.stock - Number(quantity) });

      pushToast("success", "Matéria-prima adicionada ao produto");
      setSelectedMaterial("");
      setQuantity(1);
      setManufacturingPrice(0);
      await loadData();
    } catch (err) {
      pushToast("error", "Erro ao associar");
    }
    setLoading(false);
  };

  const removeAssociation = async (id) => {
    if (!confirm("Deseja remover essa associação?")) return;
    setLoading(true);
    try {
      await api.delete(`product-raw-materials/${id}/`);
      pushToast("success", "Associação removida");
      await loadData();
    } catch (err) {
      pushToast("error", "Erro ao remover");
    }
    setLoading(false);
  };

  const openEdit = (assoc) => {
    setEditing(assoc);
    setModalVisible(true);
  };

  const saveEdit = async (values) => {
    setLoading(true);
    try {
      const assoc = editing;
      const oldQty = Number(assoc.quantity);
      const newQty = Number(values.quantity);

      // Ajusta estoque da matéria-prima envolvida
      const matRes = await api.get(`raw-materials/${assoc.raw_material}/`);
      const mat = matRes.data;
      const diff = newQty - oldQty;
      if (diff > 0 && mat.stock < diff) {
        pushToast("error", "Estoque insuficiente para aumentar quantidade");
        setLoading(false);
        return;
      }

      await api.patch(`product-raw-materials/${assoc.id}/`, { quantity: newQty });
      await api.patch(`raw-materials/${assoc.raw_material}/`, { stock: mat.stock - diff });

      pushToast("success", "Associação atualizada");
      setModalVisible(false);
      setEditing(null);
      await loadData();
    } catch (err) {
      pushToast("error", "Erro ao salvar edição");
    }
    setLoading(false);
  };

  // Filtra associações do produto selecionado
  const filteredAssocs = selectedProduct 
    ? associations.filter(a => String(a.product) === String(selectedProduct))
    : associations;

  return (
    <div className="container">
      <div className="page-header">
        <h1>🔗 Associar Matérias-Primas ao Produto</h1>
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
          <h3>Adicionar Associação</h3>
          <div style={{ display: "grid", gap: 12 }}>
            <div className="form-group">
              <label>Produto</label>
              <select value={selectedProduct} onChange={e => setSelectedProduct(e.target.value)}>
                <option value="">Selecione um produto</option>
                {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Matéria-Prima</label>
              <select value={selectedMaterial} onChange={e => setSelectedMaterial(e.target.value)}>
                <option value="">Selecione uma matéria-prima</option>
                {materials.map(m => <option key={m.id} value={m.id}>{m.name} (estoque: {m.stock})</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Quantidade Necessária</label>
              <input type="number" min="0.01" step="0.01" value={quantity} onChange={e => setQuantity(e.target.value)} />
            </div>

            <div className="form-group">
              <label>Valor da Fabricação</label>
              <input type="number" min="0.00" step="0.01" value={manufacturingPrice} onChange={e => setManufacturingPrice(e.target.value)} />
            </div>

            <button onClick={associate} disabled={loading} style={{ marginTop: 8 }}>
              {loading ? <><Spinner size={16} /> Adicionando</> : "Adicionar Associação"}
            </button>
          </div>
        </aside>

        <section>
          <h3>Lista de Matérias-Primas por Produto</h3>
          
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label>Filtrar por Produto</label>
            <select value={selectedProduct} onChange={e => setSelectedProduct(e.target.value)}>
              <option value="">-- Listar Todos --</option>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          {loading ? <Spinner /> : (
            <table>
              <thead>
                <tr>
                  <th>Produto</th>
                  <th>Matéria-Prima</th>
                  <th style={{ textAlign: "right", width: 100 }}>Preço Mat.</th>
                  <th style={{ textAlign: "center", width: 80 }}>Qtd</th>
                  <th style={{ textAlign: "right", width: 120 }}>Fab.</th>
                  <th style={{ textAlign: "right", width: 120 }}>Custo Total</th>
                  <th style={{ width: 140, textAlign: "center" }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filteredAssocs.map(a => {
                  const product = products.find(p => p.id === a.product);
                  const material = materials.find(m => m.id === a.raw_material);
                  const materialPrice = parseFloat(material?.price || 0);
                  const manufacturing = parseFloat(a.manufacturing_price || 0);
                  const totalCost = materialPrice * parseFloat(a.quantity) + (manufacturing || 0);
                  return (
                    <tr key={a.id}>
                      <td>{a.product_name || a.product}</td>
                      <td>{a.raw_material_name || a.raw_material}</td>
                      <td style={{ textAlign: "right" }}>R$ {materialPrice.toFixed(2)}</td>
                      <td style={{ textAlign: "center" }}>{a.quantity}</td>
                      <td style={{ textAlign: "right" }}>R$ {(parseFloat(a.manufacturing_price) || 0).toFixed(2)}</td>
                      <td style={{ textAlign: "right", fontWeight: "bold" }}>R$ {Number(totalCost || 0).toFixed(2)}</td>
                      <td style={{ textAlign: "center" }}>
                        <div className="action-buttons">
                          <button onClick={() => openEdit(a)}>Editar</button>
                          <button onClick={() => removeAssociation(a.id)} className="delete-btn">Deletar</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </section>
      </div>

      <div>

      <ModalForm title="Editar Quantidade" visible={modalVisible} onClose={() => { setModalVisible(false); setEditing(null); }}>
        {editing && <EditForm assoc={editing} materials={materials} products={products} onCancel={() => { setModalVisible(false); setEditing(null); }} onSave={saveEdit} />}
      </ModalForm>
    </div>

    </div>
  );
}