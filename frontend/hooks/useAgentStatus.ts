import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { agentsApi } from "../lib/api";
import { useAgentStore } from "../stores/useAgentStore";

export function useAgentStatus() {
  const setStatus = useAgentStore((s) => s.setStatus);

  const { data } = useQuery({
    queryKey: ["agent-status"],
    queryFn: agentsApi.status,
    refetchInterval: 10_000,
    retry: false,
  });

  useEffect(() => {
    if (data) {
      setStatus({
        online: data.online,
        machineName: data.agents[0]?.machineName ?? null,
        lastHeartbeat: data.agents[0]?.lastHeartbeat ?? null,
      });
    }
  }, [data, setStatus]);
}
