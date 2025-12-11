const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function fetchState() {
  const res = await fetch(`${API_BASE}/state`);
  if (!res.ok) throw new Error("Failed to fetch state");
  return res.json();
}

export async function analyzeNext() {
  const res = await fetch(`${API_BASE}/analyze`, { method: "POST" });
  if (!res.ok) throw new Error("Analyze failed");
  return res.json();
}

export async function verify(decision) {
  const res = await fetch(`${API_BASE}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision }),
  });
  if (!res.ok) throw new Error("Verify failed");
  return res.json();
}

export function frameUrl(filename) {
  if (!filename) return "";
  return `${API_BASE}/static/${filename}`;
}

