"use client";
import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

const COLORS: Record<string, string> = {
  CONFIRMED: "#34d399",
  CANDIDATE: "#fbbf24",
  "FALSE POSITIVE": "#fb7185",
};

export default function AnalyticsPage() {
  const { data: info } = useQuery({ queryKey: ["model-info"], queryFn: () => api<any>("/model-info") });
  const { data: stats } = useQuery({
    queryKey: ["pred-stats"],
    queryFn: () => api<any>("/predictions/stats"),
    retry: false,
  });

  const imp = info?.feature_importance ?? [];
  const counts: Record<string, number> = stats?.counts ?? {};
  const pie = Object.entries(counts).map(([name, value]) => ({ name, value }));
  const total = stats?.total ?? 0;

  return (
    <div className="py-10">
      <Badge className="border-fuchsia-300/30 bg-fuchsia-400/10 text-fuchsia-200">SCIENTIFIC DASHBOARD</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Analytics</h1>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card><CardBody>
          <h3 className="font-bold">
            Global feature importance
            {info?.name ? <span className="ml-2 font-normal text-white/50">{info.name} {info.version}</span> : null}
          </h3>
          {imp.length === 0 && <p className="mt-2 text-sm text-white/50">Model not loaded.</p>}
          <div className="mt-2 space-y-1.5">
            {imp.map((f: any) => (
              <div key={f.feature} className="flex items-center gap-2 text-xs">
                <span className="w-36 truncate">{f.feature}</span>
                <div className="h-2 flex-1 rounded bg-white/10">
                  <div
                    className="h-2 rounded bg-gradient-to-r from-fuchsia-500 to-cyan-400"
                    style={{ width: `${Math.min(100, f.importance * 400)}%` }}
                  />
                </div>
                <span className="tnum w-14 text-right font-mono">{f.importance}</span>
              </div>
            ))}
          </div>
        </CardBody></Card>

        <Card><CardBody>
          <h3 className="font-bold">
            Served predictions by class
            <span className="ml-2 font-normal text-white/50">{total} total</span>
          </h3>
          {total === 0 ? (
            <p className="mt-3 text-sm text-white/50">
              No predictions recorded yet. Run a classification in Prediction Studio and this chart fills in.
              {stats === undefined && " (If you started the API without Postgres, counts stay empty.)"}
            </p>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pie} dataKey="value" nameKey="name" outerRadius={90} label>
                    {pie.map((p) => (
                      <Cell key={p.name} fill={COLORS[p.name] ?? "#8884d8"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardBody></Card>
      </div>
    </div>
  );
}
