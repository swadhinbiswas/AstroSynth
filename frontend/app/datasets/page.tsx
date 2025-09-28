"use client";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Badge, Card, CardBody } from "@/components/ui/card";

export default function DatasetsPage() {
  const [mission, setMission] = useState("");
  const { data } = useQuery({ queryKey: ["datasets", mission], queryFn: () => api<any>(`/datasets${mission ? `?mission=${mission}` : ""}`) });
  return (
    <div className="py-10">
      <Badge className="border-violet-400/30 bg-violet-400/10 text-violet-200">DATASET EXPLORER</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">NASA datasets</h1>
      <div className="mt-4 flex gap-2">
        {["", "kepler", "k2", "tess"].map((m) => (
          <button key={m} onClick={() => setMission(m)} className={`rounded-lg px-4 py-1.5 text-sm ${mission === m ? "bg-cyan-400 text-black font-bold" : "border border-white/15 bg-white/5"}`}>{m || "all"}</button>
        ))}
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {(data?.datasets ?? []).map((d: any) => (
          <Card key={d.id}><CardBody>
            <div className="font-bold">{d.name}</div>
            <div className="text-xs text-white/50">{d.mission} · {d.version} · {d.rows.toLocaleString()} rows</div>
            <a href={d.url} target="_blank" className="mt-3 inline-block text-sm text-cyan-300">NASA Exoplanet Archive →</a>
          </CardBody></Card>
        ))}
      </div>
    </div>
  );
}
