"use client";
import { PlanetCanvas, useElapsed } from "./Planet3D";
import { accentForClass, telemetry, type PlanetInput } from "@/lib/planet";
import { cn } from "@/lib/utils";

function fmt(n: number, d = 1) {
  return n.toLocaleString("en-US", { maximumFractionDigits: d, minimumFractionDigits: d });
}

export function PlanetPanel({ input }: { input: PlanetInput }) {
  const t = telemetry(input);
  const elapsed = useElapsed();
  const accent = accentForClass(input.disposition);
  return (
    <div>
      <PlanetCanvas input={input} height={360} />
      <div className="mt-3 grid grid-cols-2 gap-2 text-center sm:grid-cols-4">
        <Stat label="CLASS" value={input.disposition} accent={accent} />
        <Stat label="RADIUS" value={`${fmt(input.radius, 2)} R⊕`} />
        <Stat label="EQ. TEMP" value={`${fmt(input.temp, 0)} K`} />
        <Stat label="INSOLATION" value={`${t.insolation >= 100 ? fmt(t.insolation, 0) : fmt(t.insolation, 2)} ×⊕`} />
      </div>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-xs">
        <span className="text-white/70">
          <b className="text-white">{t.type}</b> · {t.hz} <span className="text-white/35">(estimates)</span>
        </span>
        <span className="font-mono tabular-nums text-cyan-300">T+{String(Math.floor(elapsed / 60)).padStart(2, "0")}:{String(elapsed % 60).padStart(2, "0")}</span>
      </div>
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/30 px-2 py-2">
      <div className="text-[10px] font-semibold tracking-widest text-white/40">{label}</div>
      <div className={cn("truncate font-mono text-sm font-bold tabular-nums", accent ? "" : "text-white")} style={accent ? { color: accent } : undefined}>
        {value}
      </div>
    </div>
  );
}
