"use client";
import { create } from "zustand";

type Prediction = {
  predicted_class: string;
  confidence: number;
  probabilities: Record<string, number>;
  explanations: { values?: { feature: string; value: number; shap_value: number }[] };
} | null;

type State = {
  result: Prediction;
  history: Prediction[];
  setResult: (r: Prediction) => void;
};

export const useAstroStore = create<State>((set) => ({
  result: null,
  history: [],
  setResult: (r) => set((s) => ({ result: r, history: r ? [r, ...s.history].slice(0, 20) : s.history })),
}));
