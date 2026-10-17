"use client";

import { useEffect } from "react";
import { logoutUser } from "@/lib/auth";

export default function LogoutPage() {
  useEffect(() => {
    logoutUser("/login?logout=true");
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0E1626] text-white">
      <div className="text-center p-8">
        <div className="w-10 h-10 border-3 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-slate-300 font-mono uppercase tracking-wider">Signing out of session...</p>
      </div>
    </div>
  );
}
