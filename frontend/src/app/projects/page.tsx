"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Search,
  ChevronDown,
  LayoutGrid,
  List,
  Plus,
  MoreVertical,
  ExternalLink,
  Briefcase,
  CalendarDays,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  X,
  FolderPlus,
  SlidersHorizontal,
  ClipboardList,
  Eye,
} from "lucide-react";
import { api } from "@/lib/api";
import { useFetch } from "@/lib/useFetch";
import { toast } from "@/components/ui/Toast";
import { Card, Donut, ProgressBar, Pill } from "@/components/ui/Primitives";
import { SatelliteTile } from "@/components/map/SatelliteTile";
import { LoadingState, ErrorState } from "@/components/ui/PageState";
import { PROJECT_CATEGORIES } from "@/lib/mock-data";
import type { Project } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function ProjectsPage() {
  const router = useRouter();
  const [category, setCategory] = useState("All");
  const [q, setQ] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");
  const [page, setPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // New Project form states
  const [newProjectName, setNewProjectName] = useState("");
  const [newProjectCategory, setNewProjectCategory] = useState("Border Infrastructure");
  const [newProjectDescription, setNewProjectDescription] = useState("");
  const [newProjectArea, setNewProjectArea] = useState("1450");

  const { data, error, loading } = useFetch(() => api.getProjects({ category, q }), [category, q]);

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) {
      toast("Please enter a project name", "error");
      return;
    }

    const name = newProjectName.trim();
    localStorage.setItem("bhudristi_selected_project", name);
    setShowCreateModal(false);
    toast(`Mission project "${name}" created and set as active workspace!`, "success");
    setNewProjectName("");
    setNewProjectDescription("");
    setTimeout(() => {
      router.push("/dashboard");
    }, 800);
  };

  const handleOpenProject = (name: string) => {
    localStorage.setItem("bhudristi_selected_project", name);
    toast(`Active workspace switched to "${name}"`, "info");
    router.push("/dashboard");
  };

  return (
    <div className="p-4 sm:p-6 pr-6 sm:pr-8 space-y-5 max-w-[1600px] mx-auto min-w-0 w-full overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-4">
        <h1 className="text-[24px] font-semibold text-ink">All Projects</h1>
        <div className="relative flex-1 min-w-[240px] max-w-[420px]">
          <Search size={17} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
          <input className="input pl-10" placeholder="Search projects..." value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        <div>
          <div className="text-[11.5px] text-muted mb-0.5">Sort by</div>
          <div className="relative">
            <select className="select w-[160px]"><option>Recent</option><option>Name</option><option>Area</option></select>
            <ChevronDown size={15} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
          </div>
        </div>
        <div className="inline-flex rounded-lg border border-line-strong p-1 gap-1 self-end">
          <button onClick={() => setView("grid")} className={cn("h-9 w-9 grid place-items-center rounded-md", view === "grid" ? "bg-primary-50 text-primary" : "text-muted")}><LayoutGrid size={17} /></button>
          <button onClick={() => setView("list")} className={cn("h-9 w-9 grid place-items-center rounded-md", view === "list" ? "bg-primary-50 text-primary" : "text-muted")}><List size={17} /></button>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="self-end inline-flex items-center gap-2 h-11 px-4 rounded-lg bg-primary hover:bg-primary-hover text-white text-[14px] font-semibold shadow-sm transition"
        >
          <Plus size={17} /> Create New Project
        </button>
      </div>

      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        {PROJECT_CATEGORIES.map((c) => (
          <button key={c} onClick={() => { setCategory(c); setPage(1); }}
            className={cn("h-9 px-4 rounded-lg text-[13.5px] font-medium border transition",
              category === c ? "bg-primary text-white border-primary" : "bg-surface text-ink-soft border-line hover:bg-canvas")}>
            {c}
          </button>
        ))}
      </div>

      {loading && !data ? <LoadingState /> : error ? <ErrorState error={error} /> : data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 auto-rows-min">
            {data.projects.map((p, i) =>
              i === 0 ? (
                <FeaturedCard key={p.id} p={p} onOpen={() => handleOpenProject(p.name)} />
              ) : (
                <CompactCard key={p.id} p={p} onOpen={() => handleOpenProject(p.name)} />
              )
            )}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-1.5 pt-4">
            <PageBtn onClick={() => setPage((p) => Math.max(1, p - 1))}><ChevronLeft size={15} /></PageBtn>
            {[1, 2, 3, 4, 5].map((n) => (
              <PageBtn key={n} active={n === page} onClick={() => setPage(n)}>
                {n}
              </PageBtn>
            ))}
            <span className="px-1 text-muted">…</span>
            <PageBtn onClick={() => setPage(10)}>10</PageBtn>
            <PageBtn onClick={() => setPage((p) => Math.min(10, p + 1))}><ChevronRight size={15} /></PageBtn>
          </div>
        </>
      )}

      {/* CREATE NEW PROJECT MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-150">
          <div className="w-full max-w-lg rounded-2xl border border-line bg-surface p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div className="flex items-center gap-2">
                <FolderPlus className="text-primary" size={22} />
                <h3 className="text-[18px] font-semibold text-ink">Create New Observation Project</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="h-8 w-8 rounded-lg hover:bg-canvas grid place-items-center text-muted hover:text-ink transition"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateProject} className="space-y-4 text-[13px]">
              <div>
                <label className="field-label">Project Mission Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Pangong Tso Surveillance Corridor"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  className="input"
                  autoFocus
                />
              </div>

              <div>
                <label className="field-label">Strategic Category *</label>
                <select
                  value={newProjectCategory}
                  onChange={(e) => setNewProjectCategory(e.target.value)}
                  className="select"
                >
                  <option>Border Infrastructure</option>
                  <option>Glacial &amp; Hydrology</option>
                  <option>Desert &amp; Arid Zones</option>
                  <option>Urban &amp; Forward Bases</option>
                  <option>Coastal &amp; Maritime</option>
                </select>
              </div>

              <div>
                <label className="field-label">Mission Brief &amp; Scope</label>
                <textarea
                  rows={3}
                  placeholder="Describe observation mandate, Sentinel-2 target frequency, and operational focus…"
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  className="w-full rounded-lg border border-line bg-surface p-3 text-[13px] outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="field-label">Target Area (km²)</label>
                <input
                  type="number"
                  value={newProjectArea}
                  onChange={(e) => setNewProjectArea(e.target.value)}
                  className="input"
                />
              </div>

              <div className="rounded-lg bg-canvas p-3 text-[12px] text-muted space-y-1">
                <div>🔒 <strong>Security Classification:</strong> Level 3 - NTRO Restricted Workspace</div>
                <div>🛰️ <strong>Default Super-Resolution Pipeline:</strong> TerraSharp v2.1 (4x Resolution Gain)</div>
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-line">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="h-10 px-4 rounded-lg border border-line bg-surface font-medium text-ink hover:bg-canvas transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="h-10 px-5 rounded-lg bg-primary text-white font-semibold hover:bg-primary-hover shadow-sm transition"
                >
                  Initialize Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function FeaturedCard({ p, onOpen }: { p: Project; onOpen: () => void }) {
  return (
    <Card className="md:row-span-2 border-primary/40 ring-1 ring-primary/20 overflow-hidden flex flex-col">
      <div className="relative h-[220px]">
        <SatelliteTile seed={p.cover_image} variant="sr" className="h-full w-full" />
        <div className="absolute right-3 top-3"><Pill tone="active">{cap(p.status)}</Pill></div>
      </div>
      <div className="p-5 flex-1 flex flex-col">
        <div className="flex items-center gap-2">
          <h3 className="text-[18px] font-semibold text-ink">{p.name}</h3>
          <Pill tone="active">{cap(p.status)}</Pill>
        </div>
        <p className="text-[13px] text-muted mt-1.5 leading-snug">{p.description}</p>

        <div className="grid grid-cols-4 gap-2 mt-4 items-center">
          <Stat icon={<Briefcase size={14} />} value={String(p.jobs)} label="Jobs" />
          <Stat icon={<CalendarDays size={14} />} value={p.last_updated} label="Last updated" small />
          <Stat icon={<Maximize2 size={14} />} value={`${p.total_area_km2.toLocaleString()} km²`} label="Total area" small />
          <div className="flex flex-col items-center"><Donut value={p.complete_pct} size={54} /><span className="text-[11px] text-muted mt-1">Complete</span></div>
        </div>

        <div className="mt-5">
          <div className="text-[13px] font-medium text-ink mb-3">Recent Job Runs</div>
          <div className="flex items-center">
            {p.recent_runs.map((r, i) => (
              <div key={i} className="flex-1 flex flex-col items-center relative">
                {i < p.recent_runs.length - 1 && <div className="absolute top-2 left-1/2 w-full h-0.5 bg-teal/40" />}
                <span className={cn("relative z-10 h-4 w-4 rounded-full border-2 border-white",
                  r.status === "completed" ? "bg-teal" : r.status === "failed" ? "bg-primary" : r.status === "queued" ? "bg-line-strong" : "bg-warning-soft")} />
                <span className="text-[11px] text-muted mt-1.5">{r.date}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between">
          <div>
            <div className="text-[13px] font-medium text-ink mb-2">Team Members</div>
            <div className="flex -space-x-2">
              {p.team.map((t) => (
                <span key={t.initials} className="h-8 w-8 rounded-full ring-2 ring-white grid place-items-center text-[11px] font-semibold text-white" style={{ background: t.color }}>{t.initials}</span>
              ))}
              <span className="h-8 w-8 rounded-full ring-2 ring-white bg-canvas grid place-items-center text-[11px] font-medium text-ink-soft">+2</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onOpen}
            className="inline-flex items-center gap-2 h-11 px-4 rounded-lg bg-primary text-white text-[14px] font-semibold hover:bg-primary-hover shadow-sm transition"
          >
            Open Project <ExternalLink size={15} />
          </button>
        </div>
      </div>
    </Card>
  );
}

function CompactCard({ p, onOpen }: { p: Project; onOpen: () => void }) {
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <Card className="overflow-hidden flex flex-col relative group">
      <div className="relative h-[150px]">
        <SatelliteTile seed={p.cover_image} variant="sr" className="h-full w-full" />
        <div className="absolute right-3 top-3 flex items-center gap-2">
          <Pill tone={p.status === "active" ? "active" : "archived"}>{cap(p.status)}</Pill>
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="h-8 w-8 grid place-items-center rounded-md bg-white/95 shadow-sm text-ink-soft hover:text-ink transition"
          >
            <MoreVertical size={15} />
          </button>
        </div>

        {menuOpen && (
          <div className="absolute right-3 top-12 z-20 w-44 rounded-xl border border-line bg-surface p-1.5 shadow-xl text-[12px]">
            <button
              onClick={() => {
                setMenuOpen(false);
                onOpen();
              }}
              className="w-full text-left px-2.5 py-1.5 rounded-md hover:bg-canvas flex items-center gap-2 text-ink font-medium"
            >
              <Eye size={13} /> Open in Dashboard
            </button>
            <button
              onClick={() => {
                setMenuOpen(false);
                router.push("/queue");
              }}
              className="w-full text-left px-2.5 py-1.5 rounded-md hover:bg-canvas flex items-center gap-2 text-ink-soft"
            >
              <SlidersHorizontal size={13} /> Queue Jobs
            </button>
            <button
              onClick={() => {
                setMenuOpen(false);
                router.push("/validation");
              }}
              className="w-full text-left px-2.5 py-1.5 rounded-md hover:bg-canvas flex items-center gap-2 text-ink-soft"
            >
              <ClipboardList size={13} /> Validation Reports
            </button>
          </div>
        )}
      </div>

      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between gap-2">
            <h3
              onClick={onOpen}
              className="text-[15.5px] font-semibold text-ink cursor-pointer hover:text-primary transition"
            >
              {p.name}
            </h3>
          </div>
          <div className="grid grid-cols-4 gap-2 mt-3 items-center">
            <Stat value={String(p.jobs)} label="Jobs" />
            <Stat value={p.last_updated} label="Last updated" small />
            <Stat value={`${p.total_area_km2.toLocaleString()} km²`} label="Total area" small />
            <div className="flex flex-col items-center"><Donut value={p.complete_pct} size={48} /><span className="text-[10.5px] text-muted mt-1">Complete</span></div>
          </div>
          <ProgressBar value={p.complete_pct} className="mt-3" />
        </div>

        <div className="mt-4 pt-3 border-t border-line flex justify-end">
          <button
            type="button"
            onClick={onOpen}
            className="text-[12.5px] font-semibold text-primary hover:underline inline-flex items-center gap-1"
          >
            Open Project →
          </button>
        </div>
      </div>
    </Card>
  );
}

function Stat({ icon, value, label, small }: { icon?: React.ReactNode; value: string; label: string; small?: boolean }) {
  return (
    <div>
      <div className={cn("font-semibold text-ink flex items-center gap-1", small ? "text-[12.5px]" : "text-[16px]")}>
        {icon && <span className="text-muted">{icon}</span>}{value}
      </div>
      <div className="text-[11px] text-muted">{label}</div>
    </div>
  );
}

function PageBtn({ children, active, onClick }: { children: React.ReactNode; active?: boolean; onClick?: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "h-9 min-w-9 px-2 grid place-items-center rounded-md text-[13px] transition",
        active ? "bg-primary text-white font-semibold" : "border border-line hover:bg-canvas text-ink-soft"
      )}
    >
      {children}
    </button>
  );
}

function cap(s: string) { return s.charAt(0).toUpperCase() + s.slice(1); }
