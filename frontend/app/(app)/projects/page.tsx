"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { projectsApi, type Project } from "@/lib/api";

function CreateProjectDialog({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const mut = useMutation({
    mutationFn: () => projectsApi.create(name),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["projects"] }); onClose(); },
  });
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-sm rounded-lg border bg-background p-6 shadow-lg space-y-4">
        <h2 className="text-lg font-semibold">新建專案</h2>
        <input
          className="w-full rounded border px-3 py-2 text-sm"
          placeholder="專案名稱"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && name && mut.mutate()}
        />
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>取消</Button>
          <Button disabled={!name || mut.isPending} onClick={() => mut.mutate()}>
            {mut.isPending ? "建立中…" : "建立"}
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: projects, isLoading } = useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: projectsApi.list,
  });

  return (
    <div className="space-y-6">
      {showCreate && <CreateProjectDialog onClose={() => setShowCreate(false)} />}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">專案</h1>
        <Button onClick={() => setShowCreate(true)}>新建專案</Button>
      </div>

      {isLoading && (
        <div className="rounded-lg border p-12 text-center text-sm text-muted-foreground">載入中…</div>
      )}

      {!isLoading && (!projects || projects.length === 0) && (
        <div className="rounded-lg border p-12 text-center text-sm text-muted-foreground">
          尚未建立任何專案。
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <div className="rounded-lg border p-4 hover:bg-muted/50 transition-colors cursor-pointer">
                <div className="font-medium">{p.name}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {new Date(p.created_at).toLocaleDateString("zh-TW")}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
