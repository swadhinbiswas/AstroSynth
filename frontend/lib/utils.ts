import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
export function classColor(c: string) {
  if (c === "CONFIRMED") return "text-emerald-300 border-emerald-400/40 bg-emerald-400/10";
  if (c === "CANDIDATE") return "text-amber-300 border-amber-400/40 bg-amber-400/10";
  return "text-rose-300 border-rose-400/40 bg-rose-400/10";
}
