import { useState } from "react";

export default function EditForm({ assoc, onSave, onCancel }) {
  const [q, setQ] = useState(String(assoc.quantity ?? ""));
  const [manuf, setManuf] = useState(assoc.manufacturing_price ?? "");

  const handleSave = () => {
    const payload = {
      ...assoc,
      quantity: Number(q),
      manufacturing_price: manuf === "" ? null : Number(manuf)
    };
    onSave(payload);
  };

  return (
    <div style={{ display: "grid", gap: 8 }}>
      <div><strong>Produto:</strong> {assoc.product_name || assoc.product}</div>
      <div><strong>Matéria-Prima:</strong> {assoc.raw_material_name || assoc.raw_material}</div>
      
      <div className="form-group">
        <label>Quantidade</label>
        <input type="number" step="0.01" value={q} onChange={e => setQ(e.target.value)} />
      </div>

      <div className="form-group">
        <label>Valor da Fabricação</label>
        <input type="number" step="0.01" value={manuf ?? ""} onChange={e => setManuf(e.target.value)} />
      </div>

      <div className="button-group">
        <button onClick={onCancel}>Cancelar</button>
        <button onClick={handleSave} className="primary" style={{ background: "#646cff", color: "white", border: "none" }}>Salvar</button>
      </div>
    </div>
  );
}
