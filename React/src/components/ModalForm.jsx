import React from "react";

export default function ModalForm({ title, children, onClose, visible }) {
  if (!visible) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button onClick={onClose} aria-label="close">✖</button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}
