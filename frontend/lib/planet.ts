export type Disposition = "CONFIRMED" | "CANDIDATE" | "FALSE POSITIVE";

export type PlanetInput = {
  radius: number; // Earth radii
  temp: number; // equilibrium temp, K
  period: number; // orbital period, days
  disposition: Disposition;
};

export type Palette = { base: [string, string, string]; spot: string; emissive: string; emissiveIntensity: number };

/** Surface palette driven by equilibrium temperature (lava → desert → gas → temperate → ice). */
export function paletteForTemp(temp: number): Palette {
  if (temp >= 1500) return { base: ["#3b0a06", "#a52a0c", "#ffb347"], spot: "#ff5a1f", emissive: "#ff4400", emissiveIntensity: 0.55 };
  if (temp >= 800) return { base: ["#2b1408", "#8a4b16", "#e8a04c"], spot: "#c96a1e", emissive: "#b34700", emissiveIntensity: 0.25 };
  if (temp >= 400) return { base: ["#3a2a12", "#a67c3a", "#f2dfae"], spot: "#7c5a24", emissive: "#000000", emissiveIntensity: 0 };
  if (temp >= 200) return { base: ["#0b2a4a", "#1f7a5c", "#9fd8c9"], spot: "#2b6cb0", emissive: "#000000", emissiveIntensity: 0 };
  return { base: ["#0e1e3a", "#4a7fb5", "#e8f4ff"], spot: "#bcd7f0", emissive: "#000000", emissiveIntensity: 0 };
}

/** Atmosphere accent driven by the model verdict. */
export function accentForClass(d: Disposition): string {
  if (d === "CONFIRMED") return "#34d399";
  if (d === "CANDIDATE") return "#fbbf24";
  return "#fb7185";
}

/** Illustrative derived quantities — clearly labelled estimates, computed in real time. */
export function telemetry(input: PlanetInput) {
  const insolation = Math.pow(input.temp / 255, 4); // vs Earth eq. temp
  const hz = input.temp >= 200 && input.temp <= 320 ? "Habitable-zone candidate" : input.temp < 200 ? "Too cold (beyond HZ)" : "Too hot (inside HZ)";
  const type = input.radius >= 6 ? "Gas giant" : input.radius >= 2 ? "Mini-Neptune" : input.radius >= 1 ? "Super-Earth" : "Sub-Earth";
  return { insolation, hz, type };
}
