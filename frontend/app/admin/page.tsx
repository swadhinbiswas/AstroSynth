"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

export default function AdminPage() {
  const { data: fb } = useQuery({ queryKey: ["feedback"], queryFn: () => api<any>("/feedback") });
  return (
    <div className="py-10">
      <Badge className="border-rose-300/30 bg-rose-400/10 text-rose-200">ADMIN PANEL</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Ops overview</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <Card><CardBody><h3 className="font-bold">Feedback inbox ({fb?.count ?? 0})</h3>
          {(fb?.items ?? []).slice(-5).map((f: any, i: number) => <p key={i} className="mt-1 text-sm text-white/60">{f.user_label} — {f.comment}</p>)}
        </CardBody></Card>
        <Card><CardBody><h3 className="font-bold">Ops links</h3>
          <ul className="mt-2 space-y-1 text-sm text-cyan-300">
            <li><a href="http://localhost:9090" target="_blank">Prometheus →</a></li>
            <li><a href="http://localhost:3001" target="_blank">Grafana →</a></li>
            <li><a href="http://localhost:8000/docs" target="_blank">OpenAPI docs →</a></li>
          </ul>
        </CardBody></Card>
      </div>
    </div>
  );
}
