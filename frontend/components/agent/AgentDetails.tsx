"use client";

import { useAgentStore } from "@/stores/useAgentStore";

export function AgentDetails() {
  const { online, lastHeartbeat, machineName } = useAgentStore();
  return (
    <div className="space-y-2 rounded-lg border p-6">
      <div className="text-lg font-semibold">本機 Agent</div>
      <div className="text-sm text-muted-foreground">
        狀態：{online ? "線上" : "離線"}
      </div>
      <div className="text-sm text-muted-foreground">機器：{machineName ?? "—"}</div>
      <div className="text-sm text-muted-foreground">
        最後心跳：{lastHeartbeat ?? "—"}
      </div>
    </div>
  );
}
