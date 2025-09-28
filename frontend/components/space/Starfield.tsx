"use client";
import { useEffect, useRef } from "react";

/** Lightweight canvas starfield — zero deps, GPU-cheap. */
export function SpaceCanvas() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const c = ref.current!;
    const ctx = c.getContext("2d")!;
    let raf = 0;
    const stars = Array.from({ length: 220 }, () => ({ x: Math.random(), y: Math.random(), z: Math.random() * 0.9 + 0.1, r: Math.random() * 1.6 + 0.3 }));
    const resize = () => { c.width = c.offsetWidth; c.height = c.offsetHeight; };
    resize();
    window.addEventListener("resize", resize);
    const tick = () => {
      ctx.clearRect(0, 0, c.width, c.height);
      const g = ctx.createRadialGradient(c.width * 0.7, c.height * 0.25, 0, c.width * 0.7, c.height * 0.25, c.width * 0.6);
      g.addColorStop(0, "rgba(109,40,217,0.35)"); g.addColorStop(1, "rgba(3,0,20,0)");
      ctx.fillStyle = g; ctx.fillRect(0, 0, c.width, c.height);
      for (const s of stars) {
        s.x -= 0.0004 * s.z; if (s.x < 0) s.x = 1;
        ctx.globalAlpha = 0.35 + s.z * 0.65;
        ctx.fillStyle = s.z > 0.7 ? "#a5f3fc" : "#e9d5ff";
        ctx.beginPath(); ctx.arc(s.x * c.width, s.y * c.height, s.r, 0, Math.PI * 2); ctx.fill();
      }
      ctx.globalAlpha = 1;
      raf = requestAnimationFrame(tick);
    };
    tick();
    return () => { cancelAnimationFrame(raf); window.removeEventListener("resize", resize); };
  }, []);
  return <canvas ref={ref} className="absolute inset-0 h-full w-full" aria-hidden />;
}
