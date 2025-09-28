"use client";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

export default function LeaderboardPage() {
  const { data } = useQuery({ queryKey: ["leaderboard"], queryFn: () => api<any>("/leaderboard") });
  const rows = data?.models ?? [];
  return (
    <div className="py-10">
      <Badge className="border-amber-300/30 bg-amber-400/10 text-amber-200">MODEL COMPARISON CENTER</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Leaderboard</h1>
      <Card className="mt-6"><CardBody>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rows}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff22" />
              <XAxis dataKey="model" tick={{ fill: "#fff" }} />
              <YAxis domain={[0.85, 1]} tick={{ fill: "#fff" }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" fill="#22d3ee" />
              <Bar dataKey="f1" fill="#a855f7" />
              <Bar dataKey="roc_auc" fill="#34d399" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <table className="mt-6 w-full text-sm">
          <thead><tr className="text-left text-white/50"><th>Model</th><th>Acc</th><th>Prec</th><th>Rec</th><th>F1</th><th>ROC-AUC</th></tr></thead>
          <tbody>{rows.map((m: any) => <tr key={m.model} className="border-t border-white/10"><td className="py-2 font-bold">{m.model}</td><td>{m.accuracy}</td><td>{m.precision}</td><td>{m.recall}</td><td>{m.f1}</td><td>{m.roc_auc}</td></tr>)}</tbody>
        </table>
      </CardBody></Card>
    </div>
  );
}
