import { z } from "zod";

export const projectSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(200),
  owner_id: z.string().uuid().nullable().optional(),
  created_at: z.string(),
});

export type Project = z.infer<typeof projectSchema>;
