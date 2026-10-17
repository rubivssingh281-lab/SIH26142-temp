"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { Footer } from "./Footer";
import { MobileBottomNav } from "./MobileBottomNav";
import { Toaster } from "@/components/ui/Toast";

/** Routes that render full-bleed, without the app chrome (sidebar/topbar). */
const BARE_ROUTES = ["/login", "/signup"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const bare = BARE_ROUTES.some((r) => pathname.startsWith(r));

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
      {/* Sidebar: desktop fixed sidebar + mobile drawer */}
      <Sidebar
        mobileOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0 w-full lg:pl-[248px]">
        <Topbar onOpenMobileMenu={() => setMobileMenuOpen(true)} />
        <main className="flex-1 min-w-0 w-full overflow-x-clip pb-16 lg:pb-0">
          {children}
        </main>
        <Footer />
      </div>

      {/* Mobile bottom navigation bar */}
      <MobileBottomNav onOpenMenu={() => setMobileMenuOpen(true)} />

      <Toaster />
    </div>
  );
}
