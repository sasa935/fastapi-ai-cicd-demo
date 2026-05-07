export type Link = {
  id: number;
  code: string;
  original_url: string;
  short_url: string;
  created_at: string;
  clicks: number;
};

export type DailyClick = { date: string; count: number };

export type LinkStats = {
  id: number;
  code: string;
  total_clicks: number;
  daily: DailyClick[];
};

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "content-type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  list: () => request<Link[]>("/api/links"),
  create: (url: string) =>
    request<Link>("/api/links", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),
  remove: (id: number) =>
    request<void>(`/api/links/${id}`, { method: "DELETE" }),
  stats: (id: number) => request<LinkStats>(`/api/links/${id}/stats`),
};
