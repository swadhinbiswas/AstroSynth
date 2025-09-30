"use client";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

type Row = {
  model: string;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  f1: number | null;
  roc_auc: number | null;
  is_best?: boolean;
};

export default function LeaderboardPage() {
  const { data } = useQuery({ queryKey: ["leaderboard"], queryFn: () => api<any>("/leaderboard") });
  const rows: Row[] = data?.models ?? [];
  const trained = data?.trained;
  const meta = data?.meta ?? {};
  const fmt = (v: number | null) => (v === null || v === undefined ? "—" : v.toFixed(3));

  return (
    <div className="py-10">
      <Badge className="border-amber-300/30 bg-amber-400/10 text-amber-200">MODEL COMPARISON CENTER</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Leaderboard</h1>
      <p className="mt-2 text-sm text-white/60">
        {trained
          ? `Metrics read from ml/artifacts/registry.json${meta.trained_at ? `, last trained ${meta.trained_at.slice(0, 10)}` : ""}.`
          : "No training run found yet."}
      </p>

      {!trained && (
        <Card className="mt-6"><CardBody>
          <p className="text-white/70">
            Run <span className="font-mono text-cyan-300">python ml/scripts/train.py --config ml/configs/base.yaml</span> to
            produce metrics. The API serves whatever that run wrote; it does not ship placeholder scores.
          </p>
        </CardBody></Card>
      )}

      {trained && (
        <Card className="mt-6"><CardBody>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff22" />
                <XAxis dataKey="model" tick={{ fill: "#fff" }} />
                <YAxis domain={[0.5, 1]} tick={{ fill: "#fff" }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="accuracy" fill="#22d3ee" />
                <Bar dataKey="f1" fill="#a855f7" />
                <Bar dataKey="roc_auc" fill="#34d399" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <table className="mt-6 w-full text-sm">
            <thead>
              <tr className="text-left text-white/50">
                <th>Model</th><th>Acc</th><th>Prec</th><th>Rec</th><th>F1</th><th>ROC-AUC</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((m) => (
                <tr key={m.model} className="border-t border-white/10">
                  <td className="py-2 font-bold">
                    {m.is_best && <span className="mr-1">🥇</span>}
                    {m.model}
                  </td>
                  <td className="tnum">{fmt(m.accuracy)}</td>
                  <td className="tnum">{fmt(m.precision)}</td>
                  <td className="tnum">{fmt(m.recall)}</td>
                  <td className="tnum font-semibold">{fmt(m.f1)}</td>
                  <td className="tnum">{fmt(m.roc_auc)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody></Card>
      )}
    </div>
  );
}
