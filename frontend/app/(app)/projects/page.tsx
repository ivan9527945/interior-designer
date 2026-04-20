import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function ProjectsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">專案</h1>
        <Link href="/projects/new">
          <Button>新建專案</Button>
        </Link>
      </div>
      <div className="rounded-lg border p-12 text-center text-sm text-muted-foreground">
        尚未建立任何專案。
      </div>
    </div>
  );
}
