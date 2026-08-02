/**
 * Shared API base URLs for browser clients.
 *
 * Defaults to same-origin paths so Vercel production works without
 * hardcoding localhost. Override via Vite env for special setups.
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "/api";

export const GRAPHRAG_API_URL =
  import.meta.env.VITE_GRAPHRAG_API_URL?.replace(/\/$/, "") ||
  `${API_BASE_URL}/graphrag`;
