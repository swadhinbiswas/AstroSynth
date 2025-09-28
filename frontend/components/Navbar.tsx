"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/missions", label: "Missions" },
  { href: "/predict", label: "Prediction Studio" },
  { href: "/datasets", label: "Datasets" },
  { href: "/analytics", label: "Analytics" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/workspace", label: "Workspace" },
  { href: "/docs", label: "Docs" },
];

export function Navbar() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#030014]/80 backdrop-blur-xl">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-400 text-lg">✦</span>
          <span className="font-display text-lg font-bold tracking-tight">Astro<span className="text-cyan-300">Synth</span></span>
        </Link>
        <div className="hidden flex-wrap items-center gap-1 lg:flex">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className={cn("rounded-lg px-3 py-1.5 text-sm text-white/70 hover:bg-white/10 hover:text-white", path === l.href && "bg-white/10 text-white")}>{l.label}</Link>
          ))}
        </div>
        <Link href="/predict" className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-4 py-2 text-sm font-semibold">Launch Studio →</Link>
      </nav>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-white/10 py-8 text-center text-xs text-white/40">
      AstroSynth · NASA Space Apps Challenge 2025 · MIT License · Data: NASA Exoplanet Archive (Kepler / K2 / TESS)
    </footer>
  );
}
