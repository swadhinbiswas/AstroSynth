"use client";
import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

export default function AnalyticsPage() {
  const { data } = useQuery({ queryKey: ["model-info"], queryFn: () => api<any>("/model-info") });
  const imp = data?.feature_importance ?? [];
  return (
    <div className="py-10">
      <Badge className="border-fuchsia-300/30 bg-fuchsia-400/10 text-fuchsia-200">SCIENTIFIC DASHBOARD</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Analytics</h1>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card><CardBody>
          <h3 className="font-bold">Global feature importance ({data?.name} {data?.version})</h3>
          <div className="mt-2 space-y-1.5">
            {imp.map((f: any) => (
              <div key={f.feature} className="flex items-center gap-2 text-xs">
                <span className="w-36 truncate">{f.feature}</span>
                <div className="h-2 flex-1 rounded bg-white/10"><div className="h-2 rounded bg-gradient-to-r from-fuchsia-500 to-cyan-400" style={{ width: `${f.importance * 400}%` }} /></div>
                <span className="w-14 text-right font-mono">{f.importance}</span>
              </div>
            ))}
          </div>
        </CardBody></Card>
        <Card><CardBody>
          <h3 className="font-bold">Class balance (training prior)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{ name: "CONFIRMED", value: 32 }, { name: "CANDIDATE", value: 41 }, { name: "FALSE POSITIVE", value: 27 }]} dataKey="value" nameKey="name" outerRadius={90} label>
                  <Cell fill="#34d399" /><Cell fill="#fbbf24" /><Cell fill="#fb7185" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardBody></Card>
      </div>
    </div>
  );
}
