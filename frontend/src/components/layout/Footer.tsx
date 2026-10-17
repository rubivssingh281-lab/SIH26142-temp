import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface FooterProps {
  collapsed?: boolean;
}

export function Footer({ collapsed = false }: FooterProps) {
  return (
    <footer
      className={cn(
        "fixed bottom-0 right-0 z-20 h-9 sm:h-10 border-t border-line bg-surface/95 backdrop-blur flex items-center justify-between px-3 sm:px-4 text-[11px] sm:text-[12px] text-muted transition-[left] duration-300 ease-in-out select-none shadow-[0_-1px_3px_rgba(0,0,0,0.04)]",
        "bottom-0 left-0",
        collapsed ? "lg:left-[72px]" : "lg:left-[248px]",
        "max-lg:bottom-[52px] max-sm:hidden"
      )}
    >
      <span className="font-medium truncate">भू DRISTI v2.1.0</span>
      <div className="hidden sm:flex items-center gap-2 sm:gap-3 text-[11px] sm:text-[12px] truncate">
        <span>NTRO Internal Use Only</span>
        <span className="text-line-strong">|</span>
        <span>All data classified</span>
      </div>
      <span className="flex items-center gap-1.5 text-teal text-[11px] sm:text-[12px] shrink-0">
        <ShieldCheck size={13} className="shrink-0" />
        <span className="hidden xs:inline">Secure Session</span>
        <span className="ml-1 h-2 w-2 rounded-full bg-success-soft shrink-0" />
      </span>
    </footer>
  );
}
