import { ShieldCheck } from "lucide-react";

export function Footer() {
  return (
    <footer className="py-3 sm:h-12 shrink-0 border-t border-line bg-surface flex flex-col sm:flex-row items-center justify-between gap-2 px-4 sm:px-6 text-[11px] sm:text-[12.5px] text-muted text-center sm:text-left">
      <span className="font-medium">भू DRISTI v2.1.0</span>
      <div className="flex items-center gap-2 sm:gap-3 text-[11px] sm:text-[12.5px]">
        <span>NTRO Internal Use Only</span>
        <span className="text-line-strong">|</span>
        <span>All data classified</span>
      </div>
      <span className="flex items-center gap-1.5 text-teal text-[11.5px] sm:text-[12.5px]">
        <ShieldCheck size={14} className="shrink-0" />
        Secure Session
        <span className="ml-1 h-2 w-2 rounded-full bg-success-soft shrink-0" />
      </span>
    </footer>
  );
}
