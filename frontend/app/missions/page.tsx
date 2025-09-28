"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

export default function MissionsPage() {
  const { data } = useQuery({ queryKey: ["missions"], queryFn: () => api<any>("/missions") });
  return (
    <div className="py-10">
      <Badge className="border-cyan-300/30 bg-cyan-400/10 text-cyan-200">MISSION EXPLORER</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Kepler · K2 · TESS</h1>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {(data?.missions ?? []).map((m: any) => (
          <Card key={m.id}><CardBody>
            <div className="text-xl font-bold">{m.name}</div>
            <div className="text-xs text-white/50">{m.years} · {m.targets.toLocaleString()} targets</div>
            <p className="mt-2 text-sm text-white/70">{m.description}</p>
            <div className="mt-3 text-sm text-cyan-300">{m.candidates.toLocaleString()} candidates</div>
          </CardBody></Card>
        ))}
      </div>
    </div>
  );
}
