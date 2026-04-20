"use client";

import { useQuery } from "@tanstack/react-query";
import { agentsApi } from "@/lib/api";
import { useAgentStore } from "@/stores/useAgentStore";

export default function AgentPage() {
  const { online, machineName, lastHeartbeat } = useAgentStore();

  const { data: statusData, isLoading } = useQuery({
    queryKey: ["agent-status"],
    queryFn: () => agentsApi.status(),
    refetchInterval: 10_000,
  });

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold">本機 Agent</h1>

      {/* Agent 狀態卡片 */}
      <div className="rounded-lg border p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span
              className={`inline-block h-3 w-3 rounded-full ${
                online ? "bg-emerald-500" : "bg-gray-400"
              }`}
            />
            <div>
              <div className="text-sm font-semibold">
                {machineName ?? "未知機器"}
              </div>
              <div className="text-xs text-muted-foreground">
                {online ? "線上" : "離線"} ·{" "}
                最後心跳：
                {lastHeartbeat
                  ? new Date(lastHeartbeat).toLocaleString("zh-TW")
                  : "—"}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => window.open("http://localhost:9787/diag", "_blank")}
            className="rounded-md border px-4 py-1.5 text-sm font-medium hover:bg-muted"
          >
            診斷
          </button>
        </div>
      </div>

      {/* Agent 設定說明 */}
      <div className="rounded-lg border p-5 shadow-sm space-y-4">
        <h2 className="text-lg font-semibold">安裝與設定</h2>

        <div className="space-y-1">
          <div className="text-sm font-medium">API Base URL</div>
          <code className="block rounded bg-muted px-3 py-2 text-xs text-muted-foreground">
            {apiBase}
          </code>
        </div>

        <div className="space-y-1">
          <div className="text-sm font-medium">安裝步驟</div>
          <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
            <li>下載下方的 .pkg 安裝檔並執行</li>
            <li>
              安裝完成後，Agent 將自動連線至{" "}
              <span className="font-mono text-xs">{apiBase}</span>
            </li>
            <li>確認上方狀態點變為綠色即代表連線成功</li>
          </ol>
        </div>

        <div>
          <span
            className="inline-block cursor-not-allowed rounded-md bg-primary/40 px-4 py-2 text-sm font-medium text-primary-foreground opacity-60"
            title="即將推出"
          >
            下載 RenderStudio Agent (.pkg)
          </span>
          {/* 正式連結：href="/downloads/renderstudio-agent.pkg" */}
          <p className="mt-1 text-xs text-muted-foreground">安裝包準備中，敬請期待。</p>
        </div>
      </div>

      {/* 近期心跳時間表格 */}
      <div className="rounded-lg border shadow-sm">
        <div className="border-b px-5 py-3">
          <h2 className="text-base font-semibold">已連線 Agents</h2>
        </div>

        {isLoading ? (
          <div className="p-5 text-sm text-muted-foreground">載入中…</div>
        ) : !statusData?.agents?.length ? (
          <div className="p-5 text-sm text-muted-foreground">目前沒有已連線的 Agent。</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-5 py-2 text-left font-medium text-muted-foreground">ID</th>
                <th className="px-5 py-2 text-left font-medium text-muted-foreground">機器名稱</th>
                <th className="px-5 py-2 text-left font-medium text-muted-foreground">最後心跳</th>
              </tr>
            </thead>
            <tbody>
              {statusData.agents.map((agent) => (
                <tr key={agent.id} className="border-b last:border-0 hover:bg-muted/30">
                  <td className="px-5 py-2 font-mono text-xs text-muted-foreground">
                    {agent.id.slice(0, 8)}…
                  </td>
                  <td className="px-5 py-2">{agent.machineName ?? "—"}</td>
                  <td className="px-5 py-2 text-muted-foreground">
                    {agent.lastHeartbeat
                      ? new Date(agent.lastHeartbeat).toLocaleString("zh-TW")
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
