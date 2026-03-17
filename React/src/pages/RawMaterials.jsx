import { useEffect, useState } from "react";
import api from '/src/api/api.js';
import Spinner from '/src/components/Spinner.jsx';
import ModalForm from '/src/components/ModalForm.jsx';

export default function RawMaterials() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", stock: 0, price: "" });
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [editing, setEditing] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [imageFile, setImageFile] = useState(null);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("raw-materials/");
      setItems(res.data);
    } catch (err) {
      pushToast("error", "Erro ao carregar");
    }
    setLoading(false);
  };

  const pushToast = (type, message) => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, type, message }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  };

  const create = async () => {
    if (!form.name.trim()) return pushToast("error", "Preencha o nome");
    setLoading(true);
    try {
      const data = new FormData();
      Object.entries(form).forEach(([k, v]) => data.append(k, v));
      if (imageFile) data.append("image", imageFile);

      await api.post("raw-materials/", data);
      pushToast("success", "Matéria-prima criada");
      setForm({ name: "", stock: 0, price: "" , image: null});
      setImageFile(null);
      await load();
    } catch (err) {
      pushToast("error", "Erro ao criar");
    }
    setLoading(false);
  };

  const remove = async (id) => {
    if (!confirm("Deseja remover?")) return;
    setLoading(true);
    try {
      await api.delete(`raw-materials/${id}/`);
      pushToast("success", "Removido");
      await load();
    } catch (err) {
      pushToast("error", "Erro ao remover");
    }
    setLoading(false);
  };

  const openEdit = (item) => {
    setEditing(item);
    setModalVisible(true);
  };

  const saveEdit = async (values, imageFile) => {
    if (!values.name.trim()) return pushToast("error", "Preencha o nome");
    setLoading(true);
    try {
      const data = new FormData();
      Object.entries(values).forEach(([k, v]) => data.append(k, v));
      if (imageFile) data.append("image", imageFile);

      await api.patch(`raw-materials/${editing.id}/`, data);
      pushToast("success", "Atualizado");
      setModalVisible(false);
      setEditing(null);
      setImageFile(null);
      await load();
    } catch (err) {
      pushToast("error", "Erro ao salvar");
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1>🧪 Matérias-Primas</h1>
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
          <h3>Nova Matéria-Prima</h3>
          <div style={{ display: "grid", gap: 12 }}>
            <div className="form-group">
              <label>Nome</label>
              <input type="text" placeholder="Nome da matéria-prima" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Preço</label>
              <input type="number" placeholder="Preço" step="0.01" min="0" value={form.price} onChange={e => setForm({ ...form, price: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Estoque</label>
              <input type="number" placeholder="Estoque" min="0" step="1" value={form.stock} onChange={e => setForm({ ...form, stock: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Imagem</label>
              <input type="file" onChange={e => setImageFile(e.target.files[0])} />
            </div>
            <button onClick={create} disabled={loading} className="primary" style={{ marginTop: 4 }}>
              {loading ? <><Spinner size={16} /> Salvando…</> : "+ Criar Matéria-Prima"}
            </button>
          </div>
        </aside>

        <div className="section-table">
          <h3>Estoque de Matérias-Primas</h3>
          {loading ? (
            <div style={{ padding: 24, display: "flex", justifyContent: "center" }}><Spinner /></div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th style={{ width: 60 }}>Img</th>
                  <th>Nome</th>
                  <th style={{ textAlign: "right", width: 110 }}>Preço Unit.</th>
                  <th style={{ textAlign: "center", width: 90 }}>Estoque</th>
                  <th style={{ textAlign: "right", width: 120 }}>Valor Total</th>
                  <th style={{ width: 140, textAlign: "right" }}>Ações</th>
                </tr>
              </thead>
              <tbody>
                {items.map(i => {
                  const price = parseFloat(i.price || 0);
                  const stock = parseFloat(i.stock || 0);
                  const totalValue = price * stock;
                  return (
                    <tr key={i.id}>
                      <td>{i.image ? <img src={i.image} alt={i.name} style={{ width: 36, height: 36 }} /> : <span style={{ color: "var(--text3)", fontSize: "0.8em" }}>—</span>}</td>
                      <td>{i.name}</td>
                      <td style={{ textAlign: "right", fontFamily: "'DM Mono', monospace", fontSize: "0.88em" }}>R$ {price.toFixed(2)}</td>
                      <td style={{ textAlign: "center", fontFamily: "'DM Mono', monospace", fontSize: "0.88em" }}>{stock}</td>
                      <td style={{ textAlign: "right", fontFamily: "'DM Mono', monospace", fontSize: "0.88em", color: "var(--green)", fontWeight: 600 }}>R$ {totalValue.toFixed(2)}</td>
                      <td style={{ textAlign: "right" }}>
                        <div className="action-buttons" style={{ justifyContent: "flex-end" }}>
                          <button onClick={() => openEdit(i)}>Editar</button>
                          <button onClick={() => remove(i.id)} className="delete-btn">Deletar</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <ModalForm title="Editar Matéria-Prima" visible={modalVisible} onClose={() => { setModalVisible(false); setEditing(null); }}>
        {editing && <EditModal item={editing} onSave={saveEdit} onCancel={() => { setModalVisible(false); setEditing(null); }} />}
      </ModalForm>
    </div>
  );
}

function EditModal({ item, onSave, onCancel }) {
  const [values, setValues] = useState({ name: item.name, stock: item.stock, price: item.price || "" });
  const [imageFile, setImageFile] = useState(null);
  return (
    <div>
      <div className="form-group">
        <label>Nome</label>
        <input type="text" value={values.name} onChange={e => setValues({ ...values, name: e.target.value })} />
      </div>
      <div className="form-group">
        <label>Estoque</label>
        <input type="number" min="0" step="1" value={values.stock} onChange={e => setValues({ ...values, stock: e.target.value })} />
      </div>
      <div className="form-group">
        <label>Preço</label>
        <input type="number" min="0" step="0.01" value={values.price} onChange={e => setValues({ ...values, price: e.target.value })} />
      </div>
      <div className="form-group">
        <label>Imagem</label>
        <input type="file" onChange={e => setImageFile(e.target.files[0])} />
      </div>
      <div className="button-group">
        <button onClick={onCancel}>Cancelar</button>
        <button onClick={() => onSave(values, imageFile)} className="primary" style={{ background: "#646cff", color: "white", border: "none" }}>Salvar</button>
      </div>
    </div>
  );
}
