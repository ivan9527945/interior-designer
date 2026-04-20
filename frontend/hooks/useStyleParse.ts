import { useMutation } from "@tanstack/react-query";

import { api } from "../lib/api";
import type { StyleSchema } from "../lib/schemas/style";

export function useStyleParseText() {
  return useMutation<StyleSchema, Error, { description: string }>({
    mutationFn: async ({ description }) => {
      const { data } = await api.post<StyleSchema>("/style/parse/text", { description });
      return data;
    },
  });
}
