"use client";

import { useState, useEffect } from "react";

interface CsatPopoverProps {
  renderId: string;
}

const STORAGE_KEY = (id: string) => `csat_${id}`;

export function CsatPopover({ renderId }: CsatPopoverProps) {
  const [visible, setVisible] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    // 若已評分過，不再顯示
    const existing = localStorage.getItem(STORAGE_KEY(renderId));
    if (existing) return;

    const timer = setTimeout(() => setVisible(true), 3000);
    return () => clearTimeout(timer);
  }, [renderId]);

  const handleSelect = (score: number) => {
    setSelected(score);
    localStorage.setItem(STORAGE_KEY(renderId), String(score));
    setSubmitted(true);
    setTimeout(() => setVisible(false), 1500);
  };

  const handleClose = () => {
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 w-72 rounded-xl border bg-white p-4 shadow-2xl dark:bg-zinc-900">
      <div className="mb-3 flex items-start justify-between gap-2">
        <p className="text-sm font-medium leading-snug">
          ✨ 渲染完成！您覺得這次結果如何？
        </p>
        <button
          type="button"
          onClick={handleClose}
          className="shrink-0 rounded p-0.5 text-muted-foreground hover:bg-muted"
          aria-label="關閉"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {submitted ? (
        <p className="text-center text-sm text-emerald-600">感謝您的回饋！</p>
      ) : (
        <div className="flex justify-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => handleSelect(star)}
              className={`text-2xl transition-transform hover:scale-125 focus:outline-none ${
                selected !== null && star <= selected
                  ? "text-amber-400"
                  : "text-gray-300 hover:text-amber-300"
              }`}
              aria-label={`${star} 星`}
            >
              ★
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
