export const RENDER_STATUS = [
  "pending",
  "assigned",
  "parsing",
  "modeling",
  "material",
  "rendering",
  "completed",
  "error",
  "cancelled",
] as const;

export type RenderStatus = (typeof RENDER_STATUS)[number];

export const QUALITY_PRESETS = ["draft", "standard", "premium"] as const;
export type QualityPreset = (typeof QUALITY_PRESETS)[number];
