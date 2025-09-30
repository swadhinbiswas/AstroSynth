"use client";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import Link from "next/link";
import { SpaceCanvas } from "@/components/space/Starfield";
import { Card, CardBody, Badge } from "@/components/ui/card";

const PlanetPanel = dynamic(() => import("@/components/space/PlanetPanel").then((m) => m.PlanetPanel), {
  ssr: false,
  loading: () => <div className="grid h-[360px] place-items-center rounded-2xl bg-black/40 text-sm text-white/40">Initialising 3D renderer…</div>,
});

const STATS = [
  { k: "9,201", v: "KOI observations trained on" },
  { k: "0.782", v: "Best F1, XGBoost (real data)" },
  { k: "3", v: "Missions · Kepler K2 TESS" },
  { k: "14", v: "Features + SHAP per prediction" },
];

export default function Home() {
  return (
    <div>
      <section className="relative -mx-6 overflow-hidden px-6 pb-16 pt-20">
        <SpaceCanvas />
        <div className="relative">
        <div className="relative grid items-center gap-10 lg:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
            <Badge className="border-cyan-300/30 bg-cyan-400/10 text-cyan-200">NASA SPACE APPS CHALLENGE 2025 · AI / EXOPLANETS</Badge>
            <h1 className="font-display mt-6 max-w-3xl text-5xl font-extrabold leading-[1.05] tracking-tight md:text-7xl">
              Hunt for worlds <span className="bg-gradient-to-r from-violet-400 via-fuchsia-300 to-cyan-300 bg-clip-text text-transparent">a world away.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-balance text-lg text-white/70">
              AstroSynth classifies Kepler, K2 and TESS observations into <b>Confirmed · Candidate · False Positive</b> with
              explainable AI — SHAP attributions, probability distributions and physics-aware features.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/predict" className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-6 py-3 font-semibold shadow-lg shadow-violet-900/40">Open Prediction Studio →</Link>
              <Link href="/missions" className="rounded-xl border border-white/15 bg-white/5 px-6 py-3 font-semibold hover:bg-white/10">Explore Missions</Link>
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.94 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.15 }}>
            <PlanetPanel input={{ radius: 1.6, temp: 288, period: 365, disposition: "CONFIRMED" }} />
            <p className="mt-2 text-center text-xs text-white/40">Live 3D render · drag to orbit · a temperate super-Earth</p>
          </motion.div>
        </div>
          <div className="mt-12 grid grid-cols-2 gap-4 md:grid-cols-4">
            {STATS.map((s) => (
              <Card key={s.v}><CardBody><div className="text-3xl font-extrabold text-cyan-200">{s.k}</div><div className="mt-1 text-sm text-white/60">{s.v}</div></CardBody></Card>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 py-10 md:grid-cols-3">
        {[
          { t: "Prediction Engine", d: "Upload CSV or JSON, or enter parameters manually. Get class, confidence, probabilities and per-feature SHAP values.", h: "/predict" },
          { t: "Explainable AI", d: "Every prediction ships with global feature importance and local SHAP attributions (TreeExplainer when shap is installed).", h: "/analytics" },
          { t: "Research Workspace", d: "Predictions from this browser session are kept locally. Add notes and export a Markdown report.", h: "/workspace" },
        ].map((f) => (
          <Card key={f.t}><CardBody>
            <h3 className="text-xl font-bold">{f.t}</h3>
            <p className="mt-2 text-sm text-white/65">{f.d}</p>
            <Link href={f.h} className="mt-4 inline-block text-sm font-semibold text-cyan-300">Open →</Link>
          </CardBody></Card>
        ))}
      </section>

      <section className="py-10">
        <h2 className="font-display text-3xl font-bold">Missions</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {[["Kepler", "2009–2018 · 150k stars · 9,564 KOIs", "The planet-hunting workhorse that proved Earth-size worlds are common."], ["K2", "2014–2018 · 19 campaigns", "Kepler reborn on two wheels — surveying the ecliptic."], ["TESS", "2018–present · all-sky", "Bright nearby stars, ideal for JWST follow-up."]].map(([n, s, d]) => (
            <Card key={n}><CardBody><div className="text-lg font-bold text-violet-200">{n}</div><div className="text-xs text-white/50">{s}</div><p className="mt-2 text-sm text-white/70">{d}</p></CardBody></Card>
          ))}
        </div>
      </section>

      <section className="py-10">
        <Card><CardBody>
          <h2 className="font-display text-2xl font-bold">Built for judges, researchers and the curious.</h2>
          <p className="mt-2 text-white/65">Try the demo in 30 seconds: Prediction Studio → keep defaults → Classify. Then upload your own CSV with the same 10 columns.</p>
          <div className="mt-4 flex gap-3"><Link href="/predict" className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-black">Classify an observation</Link><Link href="/docs" className="rounded-xl border border-white/15 px-5 py-2.5 text-sm font-semibold">Read the docs</Link></div>
        </CardBody></Card>
      </section>
    </div>
  );
}
