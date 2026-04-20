import { cn } from "@/lib/utils";

export interface StepperProps {
  steps: string[];
  current: number;
}

export function Stepper({ steps, current }: StepperProps) {
  return (
    <ol className="flex items-center gap-4">
      {steps.map((label, i) => (
        <li
          key={label}
          className={cn(
            "flex items-center gap-2 text-sm",
            i === current ? "font-semibold text-primary" : "text-muted-foreground"
          )}
        >
          <span
            className={cn(
              "flex h-6 w-6 items-center justify-center rounded-full border text-xs",
              i === current ? "border-primary bg-primary text-primary-foreground" : ""
            )}
          >
            {i + 1}
          </span>
          {label}
        </li>
      ))}
    </ol>
  );
}
