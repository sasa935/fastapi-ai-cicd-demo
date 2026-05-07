import { useState } from "react";
import { CopyButton } from "../components/CopyButton";
import { api, type Link } from "../lib/api";

export function Home() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<Link | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const link = await api.create(url);
      setResult(link);
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to shorten URL");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Shorten a URL</h2>
        <p className="text-slate-600 text-sm mt-1">
          Paste a long URL below and we'll give you a tidy short link.
        </p>
      </div>

      <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row">
        <input
          aria-label="URL"
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/some/long/path"
          className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-slate-900 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      {result && (
        <div className="rounded-md border border-slate-200 bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Your short URL</div>
          <div className="mt-1 flex items-center gap-3">
            <a
              href={result.short_url}
              className="text-lg font-mono text-slate-900 underline"
              target="_blank"
              rel="noreferrer"
            >
              {result.short_url}
            </a>
            <CopyButton value={result.short_url} />
          </div>
          <div className="mt-2 text-sm text-slate-600 truncate">
            → {result.original_url}
          </div>
        </div>
      )}
    </div>
  );
}
