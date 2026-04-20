import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6 text-center">
      <div className="text-7xl font-bold text-gray-200">404</div>
      <div>
        <h1 className="text-2xl font-semibold text-gray-700">找不到頁面</h1>
        <p className="mt-2 text-sm text-gray-500">
          您要找的頁面不存在或已被移除。
        </p>
      </div>
      <Link
        href="/"
        className="rounded-md bg-primary px-5 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
      >
        返回首頁
      </Link>
    </div>
  );
}
