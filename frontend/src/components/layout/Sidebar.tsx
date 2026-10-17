"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  PlusSquare,
  SlidersHorizontal,
  Images,
  ClipboardList,
  History,
  Settings,
  X,
} from "lucide-react";
import { Logo } from "./Logo";
import { cn } from "@/lib/utils";
import { CURRENT_USER } from "@/lib/mock-data";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutGrid },
  { href: "/new-job", label: "New Enhancement Job", icon: PlusSquare },
  { href: "/queue", label: "Processing Queue", icon: SlidersHorizontal },
  { href: "/comparison", label: "Comparison Viewer", icon: Images },
  { href: "/validation", label: "Validation Reports", icon: ClipboardList },
  { href: "/projects", label: "Project History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ mobileOpen = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  const renderNavLinks = (closeOnSelect = false) => (
    <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      {NAV.map((item) => {
        const active = pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={closeOnSelect ? onClose : undefined}
            className={cn(
              "relative flex items-center gap-3 rounded-lg px-3 h-11 text-[14px] transition-colors",
              active
                ? "bg-primary-50 text-primary font-semibold"
                : "text-ink-soft hover:bg-canvas hover:text-ink"
            )}
          >
            {active && <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r bg-primary" />}
            <Icon size={19} strokeWidth={2} className="shrink-0" />
            <span className="truncate">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );

  const renderUserFooter = (closeOnSelect = false) => (
    <div className="border-t border-line p-3 shrink-0">
      <Link
        href="/settings"
        onClick={closeOnSelect ? onClose : undefined}
        className="flex items-center gap-3 px-1 py-2 rounded-lg hover:bg-canvas transition-colors"
      >
        <Avatar />
        <div className="min-w-0 leading-tight">
          <div className="text-[13.5px] font-semibold text-ink truncate">{CURRENT_USER.name}</div>
          <div className="text-[12px] text-muted truncate">{CURRENT_USER.role}</div>
        </div>
        <span className="ml-auto h-2.5 w-2.5 rounded-full bg-success-soft ring-2 ring-success-bg" />
      </Link>
    </div>
  );

  return (
    <>
      {/* 1. Desktop Persistent Sidebar (>= 1024px) */}
      <aside className="hidden lg:flex fixed inset-y-0 left-0 w-[248px] h-screen bg-surface border-r border-line flex-col z-30">
        <div className="h-16 sm:h-[76px] flex items-center border-b border-line px-5 shrink-0">
          <Logo showText />
        </div>
        {renderNavLinks(false)}
        {renderUserFooter(false)}
      </aside>

      {/* 2. Mobile Slide-Over Drawer (< 1024px) */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop overlay */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity animate-in fade-in duration-200"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Drawer container */}
          <aside className="fixed inset-y-0 left-0 w-[280px] max-w-[85vw] bg-surface border-r border-line flex flex-col shadow-2xl z-50 animate-in slide-in-from-left duration-250">
            <div className="h-16 flex items-center justify-between border-b border-line px-5">
              <Logo showText />
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 rounded-lg text-ink-soft hover:bg-canvas hover:text-ink transition"
                aria-label="Close menu"
              >
                <X size={20} />
              </button>
            </div>
            {renderNavLinks(true)}
            {renderUserFooter(true)}
          </aside>
        </div>
      )}
    </>
  );
}

function Avatar() {
  return (
    <div className="h-9 w-9 shrink-0 rounded-full bg-primary text-white grid place-items-center text-[13px] font-semibold">
      {CURRENT_USER.initials}
    </div>
  );
}
