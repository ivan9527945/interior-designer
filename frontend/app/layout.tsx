import type { Metadata } from "next";
import type { ReactNode } from "react";

import "../styles/globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";

export const metadata: Metadata = {
  title: "RenderStudio",
  description: "Web + 本機 Agent 室內渲染平台",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-Hant">
      <body>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
