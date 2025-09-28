"use client";
import { useState } from "react";
import { useAstroStore } from "@/lib/store";
import { Badge, Button, Card, CardBody } from "@/components/ui/card";

export default function WorkspacePage() {
  const { history } = useAstroStore();
  const [notes, setNotes] = useState<Record<number, string>>({});
  function exportMd() {
    const md = `# AstroSynth Report\n\n${history.map((h, i) => `## Experiment ${i + 1}\n- Class: **${h?.predicted_class}** (${((h?.confidence ?? 0) * 100).toFixed(1)}%)\n- Notes: ${notes[i] ?? ""}\n`).join("\n")}`;
    const blob = new Blob([md], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "astrosynth-report.md"; a.click();
  }
  return (
    <div className="py-10">
      <Badge className="border-emerald-300/30 bg-emerald-400/10 text-emerald-200">RESEARCH WORKSPACE</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Experiments</h1>
      <p className="mt-2 text-white/60">Predictions from this browser session are auto-saved here. Add notes, export Markdown.</p>
      <div className="mt-4"><Button onClick={exportMd}>Export report (.md)</Button></div>
      <div className="mt-6 grid gap-4">
        {history.length === 0 && <Card><CardBody className="text-white/50">No experiments yet — run a classification in Prediction Studio first.</CardBody></Card>}
        {history.map((h, i) => (
          <Card key={i}><CardBody>
            <div className="font-bold">Experiment {i + 1}: {h?.predicted_class} · {((h?.confidence ?? 0) * 100).toFixed(1)}%</div>
            <input placeholder="Add a note…" value={notes[i] ?? ""} onChange={(e) => setNotes({ ...notes, [i]: e.target.value })}
              className="mt-2 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2 text-sm" />
          </CardBody></Card>
        ))}
      </div>
    </div>
  );
}
