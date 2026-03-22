import Link from "next/link";
import { ApiKeyInput } from "@/components/ApiKeyInput";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-semibold tracking-tight">
            LLM Selector
          </Link>
          <nav className="flex items-center gap-4">
            <Link
              href="/advisor"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Advisor
            </Link>
            <Link
              href="/models"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Models
            </Link>
          </nav>
        </div>
        <ApiKeyInput />
      </div>
    </header>
  );
}
