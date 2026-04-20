"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { stylesApi } from "@/lib/api";

interface TextStyleInputProps {
  onParsed: (schema: Record<string, unknown>) => void;
}

export function TextStyleInput({ onParsed }: TextStyleInputProps) {
  const [description, setDescription] = useState("");

  const { mutate, isPending, error } = useMutation({
    mutationFn: (desc: string) => stylesApi.parseText(desc),
    onSuccess: (data) => {
      onParsed(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim()) {
      mutate(description.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="例：北歐極簡風，淺橡木地板，白色牆面，自然採光…"
        rows={5}
        className="w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />
      {error && (
        <p className="text-sm text-destructive">
          解析失敗：{(error as Error).message ?? "請稍後再試"}
        </p>
      )}
      <button
        type="submit"
        disabled={isPending || !description.trim()}
        className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {isPending && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4z"
            />
          </svg>
        )}
        {isPending ? "解析中…" : "解析風格"}
      </button>
    </form>
  );
}
