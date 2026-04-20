import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-80 space-y-6 rounded-lg border p-8 shadow-sm">
        <div>
          <h1 className="text-2xl font-semibold">RenderStudio</h1>
          <p className="mt-2 text-sm text-muted-foreground">使用公司 SSO 登入</p>
        </div>
        <Button className="w-full" disabled>
          Keycloak SSO（Sprint 4 接上）
        </Button>
      </div>
    </div>
  );
}
