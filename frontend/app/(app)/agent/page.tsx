import { AgentDetails } from "@/components/agent/AgentDetails";

export default function AgentPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">本機 Agent</h1>
      <AgentDetails />
    </div>
  );
}
