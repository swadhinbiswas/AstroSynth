export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const FEATURE_FIELDS = [
  { key: "orbital_period", label: "Orbital Period (days)", def: 12.5, min: 0.2, max: 2000, step: 0.1 },
  { key: "transit_duration", label: "Transit Duration (hrs)", def: 3.2, min: 0.2, max: 30, step: 0.1 },
  { key: "planet_radius", label: "Planet Radius (R⊕)", def: 2.1, min: 0.2, max: 30, step: 0.1 },
  { key: "stellar_radius", label: "Stellar Radius (R☉)", def: 0.95, min: 0.1, max: 10, step: 0.01 },
  { key: "stellar_mass", label: "Stellar Mass (M☉)", def: 0.9, min: 0.08, max: 5, step: 0.01 },
  { key: "stellar_temp", label: "Stellar Temp (K)", def: 5600, min: 2500, max: 10000, step: 10 },
  { key: "transit_depth", label: "Transit Depth (ppm)", def: 1200, min: 1, max: 100000, step: 10 },
  { key: "snr", label: "Signal-to-Noise", def: 45, min: 0.5, max: 5000, step: 0.5 },
  { key: "semi_major_axis", label: "Semi-major Axis (AU)", def: 0.11, min: 0.005, max: 10, step: 0.005 },
  { key: "equilibrium_temp", label: "Equilibrium Temp (K)", def: 800, min: 50, max: 4000, step: 5 },
] as const;

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}
