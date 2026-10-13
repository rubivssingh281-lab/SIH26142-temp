"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  PlusSquare,
  SlidersHorizontal,
  Images,
  Menu,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface MobileBottomNavProps {
  onOpenMenu: () => void;
}

export function MobileBottomNav({ onOpenMenu }: MobileBottomNavProps) {
  const pathname = usePathname();

  const items = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutGrid },
    { href: "/new-job", label: "New Job", icon: PlusSquare },
    { href: "/queue", label: "Queue", icon: SlidersHorizontal },
    { href: "/comparison", label: "Compare", icon: Images },
  ];

  return (
    <nav
      aria-label="Mobile bottom navigation"
      className="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-surface/95 backdrop-blur border-t border-line px-2 py-1 flex items-center justify-around shadow-[0_-4px_16px_rgba(0,0,0,0.06)]"
      style={{ paddingBottom: "max(0.25rem, env(safe-area-inset-bottom))" }}
    >
      {items.map((item) => {
        const active = pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center justify-center flex-1 py-1.5 px-1 rounded-lg text-[11px] font-medium transition-colors select-none",
              active
                ? "text-primary font-semibold"
                : "text-ink-soft hover:text-ink active:scale-95"
            )}
          >
            <Icon size={20} strokeWidth={active ? 2.3 : 1.8} className="mb-0.5 shrink-0" />
            <span className="truncate max-w-[64px]">{item.label}</span>
          </Link>
        );
      })}

      <button
        type="button"
        onClick={onOpenMenu}
        className="flex flex-col items-center justify-center flex-1 py-1.5 px-1 rounded-lg text-[11px] font-medium text-ink-soft hover:text-ink active:scale-95 transition-colors select-none"
        aria-label="Open full menu"
      >
        <Menu size={20} strokeWidth={1.8} className="mb-0.5 shrink-0" />
        <span className="truncate max-w-[64px]">More</span>
      </button>
    </nav>
  );
}
