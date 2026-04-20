import Link from "next/link";

const NAV = [
  { href: "/dashboard", label: "儀表板" },
  { href: "/projects", label: "專案" },
  { href: "/styles", label: "風格庫" },
  { href: "/queue", label: "渲染佇列" },
  { href: "/gallery", label: "成果廊" },
  { href: "/team", label: "團隊" },
  { href: "/agent", label: "本機 Agent" },
];

export function Sidebar() {
  return (
    <aside className="w-56 border-r bg-muted/30 p-4">
      <div className="mb-6 text-lg font-semibold">RenderStudio</div>
      <nav className="flex flex-col gap-1">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded px-3 py-2 text-sm hover:bg-muted"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
