"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";

import { accentForClass, paletteForTemp, type Disposition, type Palette, type PlanetInput } from "@/lib/planet";

export type { Disposition, Palette, PlanetInput };

/** Deterministic PRNG so the texture is stable across renders. */
function mulberry32(seed: number) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Procedural gas-giant / rocky surface — no external textures, works offline. */
function makeSurfaceTexture(p: Palette, seed: number): THREE.CanvasTexture {
  const w = 512, h = 256;
  const c = document.createElement("canvas");
  c.width = w; c.height = h;
  const ctx = c.getContext("2d")!;
  const rand = mulberry32(seed);
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, p.base[0]); grad.addColorStop(0.5, p.base[1]); grad.addColorStop(1, p.base[2]);
  ctx.fillStyle = grad; ctx.fillRect(0, 0, w, h);
  // horizontal bands with wobble
  for (let i = 0; i < 26; i++) {
    const y = rand() * h;
    const bh = 3 + rand() * 14;
    ctx.fillStyle = rand() > 0.5 ? p.base[0] : p.base[2];
    ctx.globalAlpha = 0.08 + rand() * 0.14;
    ctx.beginPath();
    for (let x = 0; x <= w; x += 8) ctx.lineTo(x, y + Math.sin(x / 40 + i) * 4);
    for (let x = w; x >= 0; x -= 8) ctx.lineTo(x, y + bh + Math.sin(x / 40 + i) * 4);
    ctx.closePath(); ctx.fill();
  }
  // storms / blotches
  ctx.globalAlpha = 0.5;
  for (let i = 0; i < 40; i++) {
    const x = rand() * w, y = rand() * h, r = 2 + rand() * 12;
    ctx.fillStyle = rand() > 0.4 ? p.spot : "#ffffff";
    ctx.globalAlpha = 0.1 + rand() * 0.3;
    ctx.beginPath(); ctx.ellipse(x, y, r * 1.6, r, rand() * 3, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function PlanetMesh({ input }: { input: PlanetInput }) {
  const ref = useRef<THREE.Mesh>(null);
  const pal = useMemo(() => paletteForTemp(input.temp), [input.temp]);
  const seed = Math.round(input.radius * 13 + input.temp);
  const texture = useMemo(() => makeSurfaceTexture(pal, seed), [pal, seed]);
  useEffect(() => () => texture.dispose(), [texture]);

  const scale = 0.7 + (Math.min(Math.max(input.radius, 0.3), 20) / 20) * 1.1;
  const spin = Math.max(0.05, 3 / Math.max(input.period, 0.5)); // short period -> fast spin (illustrative)
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * spin * 0.4;
  });

  const accent = accentForClass(input.disposition);
  const gasGiant = input.radius > 6;

  return (
    <group>
      <mesh ref={ref} scale={scale}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial map={texture} roughness={0.9} metalness={0.05} emissive={pal.emissive} emissiveIntensity={pal.emissiveIntensity} />
      </mesh>
      {/* atmosphere shell */}
      <mesh scale={scale * 1.14}>
        <sphereGeometry args={[1, 48, 48]} />
        <meshBasicMaterial color={accent} transparent opacity={0.16} side={THREE.BackSide} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      {gasGiant && (
        <mesh scale={scale} rotation-x={Math.PI / 2.35} rotation-y={0.3}>
          <ringGeometry args={[1.45, 2.3, 96]} />
          <meshBasicMaterial color="#d8c49a" transparent opacity={0.45} side={THREE.DoubleSide} />
        </mesh>
      )}
      {/* orbit path + moon */}
      <mesh rotation-x={Math.PI / 2}>
        <ringGeometry args={[scale * 2.1, scale * 2.12, 96]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.14} side={THREE.DoubleSide} />
      </mesh>
      <Moon orbit={scale * 2.1} />
    </group>
  );
}

function Moon({ orbit }: { orbit: number }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    const t = clock.elapsedTime * 0.5;
    if (ref.current) ref.current.position.set(Math.cos(t) * orbit, 0.15, Math.sin(t) * orbit);
  });
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.09, 24, 24]} />
      <meshStandardMaterial color="#cbd5e1" roughness={1} />
    </mesh>
  );
}

export function PlanetCanvas({ input, height = 380 }: { input: PlanetInput; height?: number }) {
  return (
    <div style={{ height }} className="relative w-full overflow-hidden rounded-2xl bg-black/40">
      <Canvas dpr={[1, 2]} camera={{ position: [0, 1.4, 4.6], fov: 45 }} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.55} />
        <pointLight position={[6, 3, 4]} intensity={60} color="#fff4e0" />
        <pointLight position={[-6, -2, -4]} intensity={8} color="#6d28d9" />
        <Stars radius={60} depth={30} count={2500} factor={4} fade speed={0.6} />
        <PlanetMesh input={input} />
        <OrbitControls enableZoom={false} enablePan={false} minPolarAngle={Math.PI / 3.2} maxPolarAngle={Math.PI / 1.7} autoRotate autoRotateSpeed={0.5} />
      </Canvas>
      <LiveBadge />
    </div>
  );
}

function LiveBadge() {
  return (
    <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded-full border border-white/15 bg-black/60 px-2.5 py-1 text-[11px] font-semibold tracking-wider text-white/80">
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
      </span>
      LIVE RENDER
    </div>
  );
}

export function useElapsed() {
  const [s, setS] = useState(0);
  useEffect(() => {
    const t0 = Date.now();
    const id = setInterval(() => setS(Math.floor((Date.now() - t0) / 1000)), 1000);
    return () => clearInterval(id);
  }, []);
  return s;
}
