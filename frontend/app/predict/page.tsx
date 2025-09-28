"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { FEATURE_FIELDS, api } from "@/lib/api";
import { useAstroStore } from "@/lib/store";
import { classColor } from "@/lib/utils";
import { Badge, Button, Card, CardBody } from "@/components/ui/card";

export default function PredictPage() {
  const [form, setForm] = useState<Record<string, number>>(
    Object.fromEntries(FEATURE_FIELDS.map((f) => [f.key, f.def]))
  );
  const { result, setResult } = useAstroStore();
  const mut = useMutation({
    mutationFn: (body: Record<string, number>) => api<any>("/predict", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: (d) => setResult(d),
  });

  const probs = result ? Object.entries(result.probabilities).map(([name, value]) => ({ name, value })) : [];
  const shap = result?.explanations?.values ?? [];
  const COLORS: Record<string, string> = { CONFIRMED: "#34d399", CANDIDATE: "#fbbf24", "FALSE POSITIVE": "#fb7185" };

  return (
    <div className="py-10">
      <Badge className="border-violet-400/30 bg-violet-400/10 text-violet-200">PREDICTION STUDIO</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Classify an observation</h1>
      <p className="mt-2 text-white/60">Enter transit + stellar parameters, or upload a CSV/JSON file with the same columns.</p>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card><CardBody>
          <div className="grid grid-cols-2 gap-3">
            {FEATURE_FIELDS.map((f) => (
              <label key={f.key} className="block">
                <span className="text-xs text-white/60">{f.label}</span>
                <input type="number" step={f.step} value={form[f.key]} onChange={(e) => setForm({ ...form, [f.key]: Number(e.target.value) })}
                  className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-cyan-400" />
              </label>
            ))}
          </div>
          <div className="mt-4 flex gap-2">
            <Button disabled={mut.isPending} onClick={() => mut.mutate(form)}>{mut.isPending ? "Classifying…" : "Classify →"}</Button>
            <Button variant="ghost" onClick={() => setForm(Object.fromEntries(FEATURE_FIELDS.map((f) => [f.key, f.def])))}>Reset</Button>
          </div>
          {mut.isError && <p className="mt-3 text-sm text-rose-300">Backend unreachable — is FastAPI running on :8000? Error: {(mut.error as Error).message}</p>}
          <details className="mt-4 text-sm text-white/60">
            <summary className="cursor-pointer text-cyan-300">Batch upload (CSV / JSON)</summary>
            <UploadBox />
          </details>
        </CardBody></Card>

        <Card><CardBody>
          {!result && <p className="text-white/50">No prediction yet. Hit <b>Classify</b> — the demo backend answers in ~100ms.</p>}
          {result && (
            <div>
              <Badge className={classColor(result.predicted_class)}>{result.predicted_class} · {(result.confidence * 100).toFixed(1)}%</Badge>
              <div className="mt-4 h-44">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={probs} layout="vertical">
                    <XAxis type="number" domain={[0, 1]} hide />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fill: "#fff", fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="value">{probs.map((p) => <Cell key={p.name} fill={COLORS[p.name] ?? "#8884d8"} />)}</Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <h3 className="mt-4 font-bold">Why this decision? (SHAP)</h3>
              <div className="mt-2 space-y-1.5">
                {shap.slice(0, 8).map((s: any) => (
                  <div key={s.feature} className="flex items-center gap-2 text-xs">
                    <span className="w-36 truncate text-white/70">{s.feature}</span>
                    <div className="h-2 flex-1 rounded bg-white/10">
                      <div className="h-2 rounded bg-gradient-to-r from-violet-500 to-cyan-400" style={{ width: `${Math.min(100, Math.abs(s.shap_value) * 400 + 4)}%` }} />
                    </div>
                    <span className="w-20 text-right font-mono text-white/70">{s.shap_value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardBody></Card>
      </div>
    </div>
  );
}

function UploadBox() {
  const [out, setOut] = useState("");
  async function onFile(f: File) {
    const text = await f.text();
    try {
      let rows: any[] = [];
      if (f.name.endsWith(".json")) rows = JSON.parse(text).rows ?? JSON.parse(text);
      else {
        const [head, ...lines] = text.trim().split("\n");
        const cols = head.split(",");
        rows = lines.slice(0, 5).map((l) => Object.fromEntries(l.split(",").map((v, i) => [cols[i].trim(), Number(v)])));
      }
      const r = await api<any>("/batch-predict", { method: "POST", body: JSON.stringify({ rows }) });
      setOut(`Classified ${r.count}: ` + r.results.map((x: any) => `${x.predicted_class}(${(x.confidence * 100).toFixed(0)}%)`).join(", "));
    } catch (e: any) { setOut("Upload failed: " + e.message); }
  }
  return (
    <div className="mt-2">
      <input type="file" accept=".csv,.json" onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} className="text-xs" />
      {out && <p className="mt-2 text-xs text-emerald-200">{out}</p>}
    </div>
  );
}
