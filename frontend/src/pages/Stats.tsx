import { useEffect, useState } from "react";
import { Link as RouterLink, useParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api, type LinkStats } from "../lib/api";

export function Stats() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<LinkStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .stats(Number(id))
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Load failed"));
  }, [id]);

  if (error) return <div className="text-sm text-red-700">Error: {error}</div>;
  if (!data) return <div className="text-sm text-slate-500">Loading...</div>;

  return (
    <div className="space-y-6">
      <div>
        <RouterLink to="/links" className="text-sm text-slate-600 underline">
          ← Back to all links
        </RouterLink>
        <h2 className="mt-2 text-2xl font-semibold">
          /{data.code}{" "}
          <span className="text-slate-500 text-base font-normal">
            — {data.total_clicks} total clicks
          </span>
        </h2>
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-4">
        <div className="text-sm font-medium text-slate-700">
          Last 7 days of clicks
        </div>
        <div className="mt-4 h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#0f172a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
