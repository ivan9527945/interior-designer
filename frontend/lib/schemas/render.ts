import { z } from "zod";

import { RENDER_STATUS } from "../constants";

export const renderSchema = z.object({
  id: z.string().uuid(),
  space_id: z.string().uuid(),
  style_id: z.string().uuid(),
  status: z.enum(RENDER_STATUS),
  phase_percent: z.number().int().min(0).max(100),
  settings: z.record(z.unknown()),
  started_at: z.string().nullable().optional(),
  finished_at: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  output_file_ids: z.array(z.string().uuid()).default([]),
  created_at: z.string(),
});

export type Render = z.infer<typeof renderSchema>;
