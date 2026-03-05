import React from "react";
import "../styles/spinner.css";

export default function Spinner({ size = 24 }) {
  return (
    <div className="spinner-container" style={{ width: size, height: size }}>
      <div className="spinner" style={{ width: size, height: size }} />
    </div>
  );
}
