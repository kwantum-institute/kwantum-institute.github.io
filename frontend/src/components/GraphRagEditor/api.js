const API_BASE = import.meta.env.VITE_GRAPHRAG_API_URL || "http://localhost:8000/api/graphrag";

async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const defaults = {
    headers: {
      "Content-Type": "application/json",
    },
  };
  const response = await fetch(url, { ...defaults, ...options });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }
  return response.json();
}

export const fetchNodes = () => apiFetch("/nodes/");
export const fetchEdges = () => apiFetch("/edges/");
export const createNode = (node) => apiFetch("/nodes/", { method: "POST", body: JSON.stringify(node) });
export const updateNode = (id, node) => apiFetch(`/nodes/${id}/`, { method: "PATCH", body: JSON.stringify(node) });
export const deleteNode = (id) => apiFetch(`/nodes/${id}/`, { method: "DELETE" });
export const createEdge = (edge) => apiFetch("/edges/", { method: "POST", body: JSON.stringify(edge) });
export const deleteEdge = (id) => apiFetch(`/edges/${id}/`, { method: "DELETE" });
export const searchChunks = (q) => apiFetch(`/search/?q=${encodeURIComponent(q)}`);
export const batchImport = (payload) => apiFetch("/batch/", { method: "POST", body: JSON.stringify(payload) });
export const exportMermaid = () => apiFetch("/mermaid/");
export const fetchProvenance = (targetId) => apiFetch(`/provenance/?target_id=${encodeURIComponent(targetId)}`);
export const runResearch = (query, privacyScore = 0.5, routingLogits = null) =>
  apiFetch("/research/", { method: "POST", body: JSON.stringify({ query, privacy_score: privacyScore, routing_logits: routingLogits }) });
export const fetchArchitecture = () => apiFetch("/architecture/");
export const runTune = (config, baselineOnly = false) => apiFetch("/tune/", { method: "POST", body: JSON.stringify({ config, baseline_only: baselineOnly }) });
