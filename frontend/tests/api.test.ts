import { describe, expect, it } from "vitest";
import { FEATURE_FIELDS } from "@/lib/api";

describe("api constants", () => {
  it("exposes 10 physics fields", () => {
    expect(FEATURE_FIELDS).toHaveLength(10);
    expect(FEATURE_FIELDS.map((f) => f.key)).toContain("snr");
  });
});
