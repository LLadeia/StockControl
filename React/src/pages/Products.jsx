import { useEffect, useState } from "react";
import api from '/src/api/api.js';
import Spinner from '/src/components/Spinner.jsx';
import ModalForm from '/src/components/ModalForm.jsx';

export default function Products() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ name: "", price: "" });
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [editing, setEditing] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [imageFile, setImageFile] = useState(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("products/");
      setProducts(res.data);
    } catch (err) {
      pushToast("error", "Erro ao carregar produtos");
    }
    setLoading(false);
  };

  
  async function handleSubmit(e) {
    e.preventDefault();
    await create();
  }

  const pushToast = (type, message) => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, type, message }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  };

  const create = async () => {
    if (!form.name.trim()) return pushToast("error", "Preencha o nome");
    if (!form.price || form.price <= 0) return pushToast("error", "Preencha o preço");
    setLoading(true);
    try {
      const data = new FormData();
      Object.entries(form).forEach(([k, v]) => data.append(k, v));
      if (imageFile) data.append("image", imageFile);

      await api.post("products/", data);
      pushToast("success", "Produto criado");
      setForm({ name: "", price: "" , image: null});
      await load();
    } catch (err) {
      pushToast("error", "Erro ao criar");
    }
    setLoading(false);
  };

  const remove = async (id) => {
    if (!confirm("Deseja remover esse produto?")) return;
    setLoading(true);
    try {
      await api.delete(`products/${id}/`);
      pushToast("success", "Produto removido");
      await load();
    } catch (err) {
      pushToast("error", "Erro ao remover");
    }
    setLoading(false);
  };

  const openEdit = (product) => {
    setEditing(product);
    setModalVisible(true);
  };

  const saveEdit = async (name, price, imageFile) => {
    if (!name.trim()) return pushToast("error", "Preencha o nome");
    if (!price || price <= 0) return pushToast("error", "Preencha o preço");
    setLoading(true);
    try {
      const data = new FormData();
      data.append("name", name);
      data.append("price", price);
      if (imageFile) data.append("image", imageFile);

      await api.patch(`products/${editing.id}/`, data);
      pushToast("success", "Produto atualizado");
      setModalVisible(false);
      setEditing(null);
      await load();
    } catch (err) {
      pushToast("error", "Erro ao salvar");
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1>📦 Produtos</h1>
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
          <h3>Novo Produto</h3>
          <div style={{ display: "grid", gap: 12 }}>
            <div className="form-group">
              <label>Nome</label>
              <input type="text" placeholder="Nome do produto" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Preço (R$)</label>
              <input type="number" placeholder="0,00" step="0.01" min="0" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Imagem</label>
              <input type="file" onChange={e => setImageFile(e.target.files[0])} />
            </div>
            <button onClick={create} disabled={loading} className="primary" style={{ marginTop: 4 }}>
              {loading ? <><Spinner size={16} /> Salvando…</> : "+ Criar Produto"}
            </button>
          </div>
        </aside>

        <div className="section-table">
          <h3>Produtos Cadastrados</h3>
          {loading ? (
            <div style={{ padding: 24, display: "flex", justifyContent: "center" }}><Spinner /></div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th style={{ width: 60 }}>Img</th>
                  <th>Nome</th>
                  <th style={{ textAlign: "right", width: 120 }}>Preço</th>
                  <th style={{ textAlign: "center", width: 90 }}>Estoque</th>
                  <th style={{ width: 140, textAlign: "right" }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id}>
                    <td>{p.image ? <img src={p.image} alt={p.name} style={{ width: 36, height: 36 }} /> : <span style={{ color: "var(--text3)", fontSize: "0.8em" }}>—</span>}</td>
                    <td>{p.name}</td>
                    <td style={{ textAlign: "right", fontFamily: "'DM Mono', monospace", fontSize: "0.88em", color: "var(--green)" }}>R$ {parseFloat(p.price || 0).toFixed(2)}</td>
                    <td style={{ textAlign: "center", fontFamily: "'DM Mono', monospace", fontSize: "0.88em" }}>{p.stock ?? "—"}</td>
                    <td style={{ textAlign: "right" }}>
                      <div className="action-buttons" style={{ justifyContent: "flex-end" }}>
                        <button onClick={() => openEdit(p)}>Editar</button>
                        <button onClick={() => remove(p.id)} className="delete-btn">Deletar</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <ModalForm title="Editar Produto" visible={modalVisible} onClose={() => { setModalVisible(false); setEditing(null); }}>
        {editing && <EditModal product={editing} onSave={saveEdit} onCancel={() => { setModalVisible(false); setEditing(null); }} />}
      </ModalForm>
    </div>
  );
}

function EditModal({ product, onSave, onCancel }) {
  const [name, setName] = useState(product.name);
  const [price, setPrice] = useState(product.price || "");
  const [imageFile, setImageFile] = useState(null);
  return (
    <div>
      <div className="form-group">
        <label>Nome</label>
        <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Nome do produto" />
      </div>
      <div className="form-group">
        <label>Preço</label>
        <input type="number" value={price} onChange={e => setPrice(e.target.value)} placeholder="Preço" step="0.01" min="0" />
      </div>
      <div className="form-group">
        <label>Imagem</label>
        <input type="file" onChange={e => setImageFile(e.target.files[0])} />
      </div>
      <div className="button-group">
        <button onClick={onCancel}>Cancelar</button>
        <button onClick={() => onSave(name, price, imageFile)} className="primary" style={{ background: "#646cff", color: "white", border: "none" }}>Salvar</button>
      </div>
    </div>
  );
}
