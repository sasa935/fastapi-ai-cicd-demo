import { useEffect, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import { api, type Link } from "../lib/api";

export function Links() {
  const [links, setLinks] = useState<Link[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLinks(await api.list());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, []);

  async function remove(id: number) {
    await api.remove(id);
    setLinks((prev) => prev.filter((l) => l.id !== id));
  }

  if (loading) return <div className="text-sm text-slate-500">Loading...</div>;
  if (error)
    return <div className="text-sm text-red-700">Error: {error}</div>;
  if (links.length === 0)
    return (
      <div className="rounded-md border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        No links yet. Create your first one on the home page.
      </div>
    );

  return (
    <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-2 text-left">Short</th>
            <th className="px-4 py-2 text-left">Target</th>
            <th className="px-4 py-2 text-right">Clicks</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {links.map((l) => (
            <tr key={l.id}>
              <td className="px-4 py-2 font-mono">
                <a
                  href={l.short_url}
                  className="text-slate-900 underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  /{l.code}
                </a>
              </td>
              <td className="px-4 py-2 max-w-xs truncate text-slate-600">
                {l.original_url}
              </td>
              <td className="px-4 py-2 text-right tabular-nums">{l.clicks}</td>
              <td className="px-4 py-2 text-right">
                <RouterLink
                  to={`/links/${l.id}`}
                  className="mr-3 text-slate-700 underline"
                >
                  Stats
                </RouterLink>
                <button
                  onClick={() => remove(l.id)}
                  className="text-red-600 hover:underline"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
