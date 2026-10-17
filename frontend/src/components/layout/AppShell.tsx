"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { Footer } from "./Footer";
import { MobileBottomNav } from "./MobileBottomNav";
import { Toaster } from "@/components/ui/Toast";
import { cn } from "@/lib/utils";

/** Routes that render full-bleed, without the app chrome (sidebar/topbar). */
const BARE_ROUTES = ["/login", "/signup"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const bare = BARE_ROUTES.some((r) => pathname.startsWith(r));

  useEffect(() => {
    try {
      const saved = localStorage.getItem("bhudristi_sidebar_collapsed");
      if (saved !== null) {
        setSidebarCollapsed(saved === "true");
      }
    } catch {
      // Ignore in SSR
    }
  }, []);

  const handleToggleSidebar = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem("bhudristi_sidebar_collapsed", String(next));
      } catch {}
      return next;
    });
  };

  if (bare) {
    return (
      <>
        {children}
        <Toaster />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-canvas">
      {/* Sidebar: desktop fixed collapsible sidebar + mobile drawer */}
      <Sidebar
        mobileOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        collapsed={sidebarCollapsed}
        onToggleCollapse={handleToggleSidebar}
      />

      <div
        className={cn(
          "flex-1 flex flex-col min-w-0 w-full transition-[padding] duration-300 ease-in-out",
          sidebarCollapsed ? "lg:pl-[72px]" : "lg:pl-[248px]"
        )}
      >
        <Topbar
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
          sidebarCollapsed={sidebarCollapsed}
          onToggleSidebar={handleToggleSidebar}
        />
        <main className="flex-1 min-w-0 w-full overflow-x-clip pb-20 sm:pb-24 lg:pb-12">
          {children}
        </main>
        <Footer collapsed={sidebarCollapsed} />
      </div>

      {/* Mobile bottom navigation bar */}
      <MobileBottomNav onOpenMenu={() => setMobileMenuOpen(true)} />

      <Toaster />
    </div>
  );
}
