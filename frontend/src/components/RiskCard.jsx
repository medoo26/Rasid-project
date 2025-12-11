import React from "react";

const levelColors = {
  low: "#16a34a",
  medium: "#f59e0b",
  high: "#dc2626",
};

export default function RiskCard({ score, level, intent }) {
  const color = levelColors[level] || "#374151";
  return (
    <div className="card">
      <div className="card-header">
        <span className="badge" style={{ backgroundColor: color }}>
          {level?.toUpperCase() || "N/A"}
        </span>
        <span className="score">Score: {score?.toFixed?.(3) ?? "0.000"}</span>
      </div>
      <div className="card-body">
        <div className="label">Intent</div>
        <div className="value">{intent || "unknown_intent"}</div>
      </div>
    </div>
  );
}

