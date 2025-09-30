import { describe, expect, it } from "vitest";
import { accentForClass, paletteForTemp, telemetry } from "@/lib/planet";

describe("planet helpers", () => {
  it("maps temperature to palettes", () => {
    expect(paletteForTemp(2000).emissiveIntensity).toBeGreaterThan(0); // lava glows
    expect(paletteForTemp(288).emissiveIntensity).toBe(0); // temperate, no glow
    expect(paletteForTemp(100).base[2]).toBe("#e8f4ff"); // ice
  });

  it("colours atmosphere by verdict", () => {
    expect(accentForClass("CONFIRMED")).toBe("#34d399");
    expect(accentForClass("FALSE POSITIVE")).toBe("#fb7185");
  });

  it("derives telemetry estimates", () => {
    const t = telemetry({ radius: 1, temp: 255, period: 365, disposition: "CONFIRMED" });
    expect(t.insolation).toBeCloseTo(1, 5);
    expect(t.type).toBe("Super-Earth");
    expect(telemetry({ radius: 10, temp: 1200, period: 4, disposition: "CANDIDATE" }).type).toBe("Gas giant");
  });
});
