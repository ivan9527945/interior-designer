import { z } from "zod";

/**
 * Zod 版 StyleSchema。單一事實來源是 backend Pydantic。
 * Sprint 3 會接 `json-schema-to-zod` 自動 codegen 取代手寫。
 */

const hexColor = z.string().regex(/^#[0-9A-Fa-f]{6}$/);

export const materialSchema = z.object({
  type: z.string(),
  finish: z.enum(["matte", "satin", "gloss"]).default("matte"),
  tone: z.enum(["light", "medium", "dark"]).default("medium"),
  color: hexColor.nullable().optional(),
});

export const lightingSchema = z.object({
  sun_kelvin: z.number().int().min(2500).max(10000),
  direction: z.enum(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
  intensity: z.number().min(0).max(3),
  ambient: z.enum(["soft", "hard", "overcast", "golden-hour"]),
});

export const cameraSchema = z.object({
  type: z.enum(["eye-level", "axonometric", "aerial", "custom"]).default("eye-level"),
  fov: z.number().int().default(50),
  height_mm: z.number().int().default(1600),
});

export const styleSchema = z.object({
  color_palette: z.array(hexColor).min(3).max(5),
  floor: materialSchema,
  wall: materialSchema,
  ceiling: materialSchema,
  lighting: lightingSchema,
  furniture_language: z.enum([
    "nordic-minimal",
    "wabi-sabi",
    "industrial",
    "modern",
    "luxury",
    "american-country",
    "french",
  ]),
  camera: cameraSchema,
});

export type StyleSchema = z.infer<typeof styleSchema>;
