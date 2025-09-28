import { ReactNode } from "react";
import { cn } from "@/lib/utils";
export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-xl shadow-[0_8px_40px_-12px_rgba(109,40,217,0.5)]", className)}>{children}</div>;
}
export function CardBody({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("p-6", className)}>{children}</div>;
}
export function Badge({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-wide", className)}>{children}</span>;
}
export function Button({ children, onClick, type, disabled, variant }: { children: ReactNode; onClick?: () => void; type?: "button" | "submit"; disabled?: boolean; variant?: "ghost" }) {
  return <button type={type ?? "button"} disabled={disabled} onClick={onClick} className={cn("rounded-xl px-5 py-2.5 text-sm font-semibold transition active:scale-[0.98] disabled:opacity-50", variant === "ghost" ? "border border-white/15 bg-white/5 hover:bg-white/10" : "bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white shadow-lg shadow-violet-900/40")}>{children}</button>;
}
