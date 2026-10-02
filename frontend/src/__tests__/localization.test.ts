import { describe, expect, it } from "vitest";
import { localized, type LocalizedText } from "../api/types";

describe("localized() helper", () => {
  const sampleText: LocalizedText = {
    en: "English test",
    ur: "اردو ٹیسٹ",
    sd: "سنڌي ٽيسٽ",
  };

  it("resolves English (.en) when language is 'en'", () => {
    expect(localized(sampleText, "en")).toBe("English test");
  });

  it("resolves Urdu (.ur) when language is 'ur'", () => {
    expect(localized(sampleText, "ur")).toBe("اردو ٹیسٹ");
  });

  it("resolves Sindhi (.sd) when language is 'sd'", () => {
    expect(localized(sampleText, "sd")).toBe("سنڌي ٽيسٽ");
  });

  it("falls back to English (.en) for Urdu when .ur is null", () => {
    const textWithoutUrdu: LocalizedText = {
      en: "English test",
      ur: null,
      sd: "سنڌي ٽيسٽ",
    };
    expect(localized(textWithoutUrdu, "ur")).toBe("English test");
  });

  it("falls back to English (.en) for Sindhi when .sd is null", () => {
    const textWithoutSindhi: LocalizedText = {
      en: "English test",
      ur: "اردو ٹیسٹ",
      sd: null,
    };
    expect(localized(textWithoutSindhi, "sd")).toBe("English test");
  });
});
