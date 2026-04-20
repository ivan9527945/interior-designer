"use client";

import { useForm, Controller, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { styleSchema, type StyleSchema } from "@/lib/schemas/style";

interface SchemaPreviewProps {
  schema: Record<string, unknown>;
  onSave: (s: Record<string, unknown>) => void;
}

const FINISH_OPTIONS = ["matte", "satin", "gloss"] as const;
const TONE_OPTIONS = ["light", "medium", "dark"] as const;
const DIRECTION_OPTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] as const;
const AMBIENT_OPTIONS = ["soft", "hard", "overcast", "golden-hour"] as const;
const CAMERA_TYPE_OPTIONS = ["eye-level", "axonometric", "aerial", "custom"] as const;
const FURNITURE_OPTIONS = [
  "nordic-minimal",
  "wabi-sabi",
  "industrial",
  "modern",
  "luxury",
  "american-country",
  "french",
] as const;

const labelClass = "block text-xs font-medium text-muted-foreground mb-1";
const inputClass =
  "w-full rounded-md border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring";
const selectClass =
  "rounded-md border border-input bg-background px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring";

function MaterialFields({
  prefix,
  label,
  register,
  control,
}: {
  prefix: "floor" | "wall" | "ceiling";
  label: string;
  register: ReturnType<typeof useForm<StyleSchema>>["register"];
  control: ReturnType<typeof useForm<StyleSchema>>["control"];
}) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold">{label}</p>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div>
          <label className={labelClass}>類型</label>
          <input {...register(`${prefix}.type`)} className={inputClass} placeholder="木質地板" />
        </div>
        <div>
          <label className={labelClass}>光澤</label>
          <Controller
            control={control}
            name={`${prefix}.finish`}
            render={({ field }) => (
              <select {...field} className={`${selectClass} w-full`}>
                {FINISH_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            )}
          />
        </div>
        <div>
          <label className={labelClass}>色調</label>
          <Controller
            control={control}
            name={`${prefix}.tone`}
            render={({ field }) => (
              <select {...field} className={`${selectClass} w-full`}>
                {TONE_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            )}
          />
        </div>
        <div>
          <label className={labelClass}>顏色</label>
          <Controller
            control={control}
            name={`${prefix}.color`}
            render={({ field }) => (
              <input
                type="color"
                value={field.value ?? "#ffffff"}
                onChange={(e) => field.onChange(e.target.value)}
                className="h-9 w-full cursor-pointer rounded-md border border-input"
              />
            )}
          />
        </div>
      </div>
    </div>
  );
}

export function SchemaPreview({ schema, onSave }: SchemaPreviewProps) {
  const { register, control, handleSubmit, formState: { errors } } = useForm<StyleSchema>({
    resolver: zodResolver(styleSchema),
    defaultValues: schema as StyleSchema,
  });

  const { fields: paletteFields, append: appendColor, remove: removeColor } = useFieldArray({
    control,
    // @ts-expect-error react-hook-form useFieldArray only supports object arrays; we handle string array manually
    name: "color_palette",
  });

  return (
    <form
      onSubmit={handleSubmit((data) => onSave(data as Record<string, unknown>))}
      className="space-y-6 rounded-lg border p-6"
    >
      <h2 className="text-lg font-semibold">風格預覽與編輯</h2>

      {/* Color palette */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">色盤</p>
        <div className="flex flex-wrap gap-2">
          {paletteFields.map((field, idx) => (
            <div key={field.id} className="flex items-center gap-1">
              <Controller
                control={control}
                name={`color_palette.${idx}` as `color_palette.${number}`}
                render={({ field: f }) => (
                  <input
                    type="color"
                    value={f.value as string}
                    onChange={(e) => f.onChange(e.target.value)}
                    className="h-8 w-8 cursor-pointer rounded border border-input"
                  />
                )}
              />
              <button
                type="button"
                onClick={() => removeColor(idx)}
                className="text-xs text-destructive hover:text-destructive/80"
                title="移除"
              >
                ×
              </button>
            </div>
          ))}
          {paletteFields.length < 5 && (
            <button
              type="button"
              onClick={() => appendColor("#cccccc" as unknown as Record<string, unknown>)}
              className="flex h-8 w-8 items-center justify-center rounded border border-dashed border-border text-muted-foreground hover:border-primary hover:text-primary"
            >
              +
            </button>
          )}
        </div>
        {errors.color_palette && (
          <p className="text-xs text-destructive">色盤需要 3～5 個顏色</p>
        )}
      </div>

      {/* Materials */}
      <MaterialFields prefix="floor" label="地板" register={register} control={control} />
      <MaterialFields prefix="wall" label="牆面" register={register} control={control} />
      <MaterialFields prefix="ceiling" label="天花板" register={register} control={control} />

      {/* Lighting */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">燈光</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div>
            <label className={labelClass}>色溫 (K)</label>
            <input
              type="number"
              min={2500}
              max={10000}
              {...register("lighting.sun_kelvin", { valueAsNumber: true })}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>方向</label>
            <Controller
              control={control}
              name="lighting.direction"
              render={({ field }) => (
                <select {...field} className={`${selectClass} w-full`}>
                  {DIRECTION_OPTIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              )}
            />
          </div>
          <div>
            <label className={labelClass}>強度 ({`0–3`})</label>
            <Controller
              control={control}
              name="lighting.intensity"
              render={({ field }) => (
                <input
                  type="range"
                  min={0}
                  max={3}
                  step={0.1}
                  value={field.value}
                  onChange={(e) => field.onChange(parseFloat(e.target.value))}
                  className="w-full"
                />
              )}
            />
          </div>
          <div>
            <label className={labelClass}>環境光</label>
            <Controller
              control={control}
              name="lighting.ambient"
              render={({ field }) => (
                <select {...field} className={`${selectClass} w-full`}>
                  {AMBIENT_OPTIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              )}
            />
          </div>
        </div>
      </div>

      {/* Furniture language */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">家具語言</p>
        <Controller
          control={control}
          name="furniture_language"
          render={({ field }) => (
            <select {...field} className={`${selectClass} w-48`}>
              {FURNITURE_OPTIONS.map((o) => (
                <option key={o} value={o}>{o}</option>
              ))}
            </select>
          )}
        />
      </div>

      {/* Camera */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">相機</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div>
            <label className={labelClass}>類型</label>
            <Controller
              control={control}
              name="camera.type"
              render={({ field }) => (
                <select {...field} className={`${selectClass} w-full`}>
                  {CAMERA_TYPE_OPTIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              )}
            />
          </div>
          <div>
            <label className={labelClass}>FOV</label>
            <input
              type="number"
              {...register("camera.fov", { valueAsNumber: true })}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>高度 (mm)</label>
            <input
              type="number"
              {...register("camera.height_mm", { valueAsNumber: true })}
              className={inputClass}
            />
          </div>
        </div>
      </div>

      <button
        type="submit"
        className="rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
      >
        儲存風格
      </button>
    </form>
  );
}
