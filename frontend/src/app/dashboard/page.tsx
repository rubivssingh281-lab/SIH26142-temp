"use client";

import Link from "next/link";
import {
  Layers,
  Briefcase,
  CheckCircle2,
  Database,
  RefreshCw,
  Plus,
  UploadCloud,
  FolderPlus,
  ArrowRight,
  ChevronRight,
  MapPin,
  CalendarDays,
  Box,
  Maximize2,
  TrendingUp,
} from "lucide-react";
import { api } from "@/lib/api";
import { useFetch } from "@/lib/useFetch";
import { Card, Donut, ProgressBar, StatusBadge, Button, SectionTitle } from "@/components/ui/Primitives";
import { Sparkline } from "@/components/ui/Charts";
import { SatelliteTile, HeatmapTile } from "@/components/map/SatelliteTile";
import { MapCanvas } from "@/components/map/MapCanvas";
import { LoadingState, ErrorState } from "@/components/ui/PageState";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const { data, error, loading, refetch } = useFetch(() => api.getDashboard());

  if (loading) return <div className="p-6"><LoadingState /></div>;
  if (error) return <div className="p-6"><ErrorState error={error} /></div>;
  if (!data) return null;

  const { stats, system_status: sys, recent_job: rj, recent_jobs, last_updated } = data;

  return (
    <div className="p-2.5 sm:p-3 space-y-2.5 sm:space-y-3 min-w-0 w-full">
      <div className="flex items-center justify-between text-[11px] sm:text-[13px] text-muted">
        <span className="font-medium text-ink-soft">Dashboard Overview</span>
        <div className="flex items-center gap-1.5">
          <span>Updated: {last_updated}</span>
          <button onClick={refetch} className="h-6 w-6 sm:h-7 sm:w-7 grid place-items-center rounded-md hover:bg-canvas transition" title="Refresh data">
            <RefreshCw size={13} className="sm:hidden" />
            <RefreshCw size={15} className="hidden sm:block" />
          </button>
        </div>
      </div>

      {/* KPI row: sideways swipeable on mobile, multi-column on desktop */}
      <div className="flex overflow-x-auto gap-2 pb-1 snap-x snap-mandatory no-scrollbar sm:grid sm:grid-cols-3 lg:grid-cols-5 sm:gap-4 -mx-2.5 px-2.5 sm:mx-0 sm:px-0">
        <Link href="/projects" className="block w-[130px] sm:w-auto shrink-0 snap-start transition hover:scale-[1.01]">
          <Kpi title="Total Projects" value={stats.total_projects} sub={`${stats.active_projects} active`} icon={<Layers size={17} className="text-primary" />} iconBg="bg-primary-50" />
        </Link>
        <Link href="/queue" className="block w-[130px] sm:w-auto shrink-0 snap-start transition hover:scale-[1.01]">
          <Kpi title="Total Jobs" value={stats.total_jobs} sub={`${stats.completed_jobs} done`} icon={<Briefcase size={17} className="text-teal" />} iconBg="bg-teal-50" />
        </Link>
        <Link href="/queue" className="block w-[135px] sm:w-auto shrink-0 snap-start transition hover:scale-[1.01]">
          <Kpi
            title="Processing"
            value={stats.processing_jobs}
            sub="In queue / run"
            right={<Donut value={62} size={36} color="#0F8C7F" showLabel={false} />}
          />
        </Link>
        <Link href="/projects" className="block w-[130px] sm:w-auto shrink-0 snap-start transition hover:scale-[1.01]">
          <Kpi title="Completed" value={stats.completed_this_month} sub="This month" icon={<CheckCircle2 size={17} className="text-success" />} iconBg="bg-success-bg" />
        </Link>
        <Link href="/settings?tab=billing" className="block w-[145px] sm:w-auto shrink-0 snap-start transition hover:scale-[1.01]">
          <StorageKpi used={stats.storage_used_tb} total={stats.storage_total_tb} />
        </Link>
      </div>

      {/* Middle: Recent Job + System Status & Actions */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 sm:gap-5 min-w-0">
        <Card className="xl:col-span-2 p-2.5 sm:p-5">
          <div className="flex items-center justify-between gap-2 mb-2.5 sm:mb-4">
            <div className="flex items-center gap-1.5 min-w-0">
              <span className="h-2 w-2 rounded-full bg-teal shrink-0" />
              <h3 className="text-[14px] sm:text-[17px] font-semibold text-ink truncate">Recent Job: {rj.job_id}</h3>
            </div>
            <StatusBadge status={rj.status} />
          </div>

          {/* 3 Satellite Images SIDE-BY-SIDE on mobile to save vertical scrolling */}
          <div className="grid grid-cols-3 gap-1.5 sm:gap-3 items-stretch">
            <ImagePanel label="Sentinel-2 (LR)" chip={rj.lr_resolution}>
              <SatelliteTile seed={rj.lr_image} variant="lr" className="h-full w-full" />
            </ImagePanel>
            <div className="flex items-center justify-center relative w-full">
              <ArrowBubble className="hidden md:grid -left-3" />
              <ImagePanelInner label="भू DRISTI (SR)" chip={rj.sr_resolution}>
                <SatelliteTile seed={rj.sr_image} variant="sr" className="h-full w-full" />
              </ImagePanelInner>
              <ArrowBubble className="hidden md:grid -right-3" />
            </div>
            <ImagePanel label="Uncertainty" footer="Uncertainty" gradientFooter>
              <HeatmapTile seed={rj.uncertainty_image} className="h-full w-full" />
            </ImagePanel>
          </div>

          {/* Compact metadata strip */}
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-1.5 sm:gap-3 mt-2.5 sm:mt-5 pt-2 sm:pt-4 border-t border-line">
            <Meta icon={<Maximize2 size={13} />} label="Area" value={`${rj.area_km2} km²`} />
            <Meta icon={<MapPin size={13} />} label="Location" value={rj.location} />
            <Meta icon={<CalendarDays size={13} />} label="Acquired" value={rj.acquisition_date} />
            <Meta icon={<Box size={13} />} label="Model" value={rj.model} />
            <Meta icon={<TrendingUp size={13} />} label="Gain" value={rj.resolution_gain} />
          </div>

          <div className="mt-2.5 sm:mt-4 text-center">
            <Link href={`/comparison?job=${rj.job_id}`} className="inline-flex items-center gap-1 text-primary text-[12px] sm:text-[14px] font-medium hover:gap-2 transition-all">
              Open in Comparison Viewer <ArrowRight size={14} />
            </Link>
          </div>
        </Card>

        {/* Right column: Status & Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-1 gap-3 sm:gap-5">
          <Card className="p-2.5 sm:p-5">
            <SectionTitle>System Status</SectionTitle>
            <div className="grid grid-cols-2 gap-1.5 sm:gap-3">
              <StatusTile title="GPU Cluster" status="Healthy" statusColor="text-teal">
                <Sparkline data={sys.gpu_cluster.trend} width={75} height={20} />
              </StatusTile>
              <StatusTile title="Storage" status={`${sys.storage.used_pct}% used`} statusColor="text-ink-soft">
                <Sparkline data={sys.storage.trend} width={75} height={20} color="#0F8C7F" />
              </StatusTile>
              <StatusTile title="API Engine" status="Nominal" statusColor="text-teal" check />
              <StatusTile title="Ingestion" status="Active" statusColor="text-teal" check />
            </div>
          </Card>

          <Card className="p-2.5 sm:p-5">
            <SectionTitle>Quick Actions</SectionTitle>
            <Link href="/new-job" className="block mb-1.5 sm:mb-3">
              <Button className="w-full h-9 sm:h-11 text-[12.5px] sm:text-[14px] gap-1.5">
                <Plus size={16} /> New Enhancement Job
              </Button>
            </Link>
            <div className="grid grid-cols-2 gap-1.5 sm:gap-3">
              <Link href="/upload" className="w-full">
                <Button variant="secondary" className="w-full h-8 sm:h-10 justify-center text-[11px] sm:text-[13px] px-1 gap-1">
                  <UploadCloud size={14} /> Upload AOI
                </Button>
              </Link>
              <Link href="/projects" className="w-full">
                <Button variant="secondary" className="w-full h-8 sm:h-10 justify-center text-[11px] sm:text-[13px] px-1 gap-1">
                  <FolderPlus size={14} /> New Project
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom: Activity Map & Recent Jobs */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 sm:gap-5 min-w-0">
        <Card className="p-2.5 sm:p-5">
          <div className="flex items-center justify-between mb-2 sm:mb-4">
            <h3 className="text-[14px] sm:text-[17px] font-semibold text-ink">Project Activity Map</h3>
            <span className="text-[11px] sm:text-[12px] text-muted">Ladakh AOI</span>
          </div>
          <MapCanvas
            seed="ladakh-mtn-activity"
            className="h-[200px] sm:h-[320px]"
            scale="20 km"
            controls
            legend={
              <div className="rounded-md sm:rounded-lg bg-white/95 shadow-sm px-2 py-1.5 sm:px-3 sm:py-2.5 text-[10.5px] sm:text-[12px] space-y-1">
                {[
                  ["Completed", "#0F8C7F"],
                  ["Processing", "#0F8C7F"],
                  ["Failed", "#C64545"],
                  ["Queued", "#E0902B"],
                ].map(([l, c]) => (
                  <div key={l} className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ background: c }} />
                    <span className="text-ink-soft">{l}</span>
                  </div>
                ))}
              </div>
            }
            overlay={<ActivityPolygons />}
          />
        </Card>

        <Card className="p-2.5 sm:p-5">
          <div className="flex items-center justify-between mb-2.5 sm:mb-4">
            <h3 className="text-[14px] sm:text-[17px] font-semibold">Recent Jobs</h3>
            <Link href="/queue" className="inline-flex items-center gap-1 text-primary text-[12px] sm:text-[13.5px] font-medium">
              View All <ArrowRight size={13} />
            </Link>
          </div>
          <div className="overflow-x-auto no-scrollbar">
            <table className="w-full text-[12px] sm:text-[13.5px]">
              <thead>
                <tr className="text-left text-muted border-b border-line">
                  <th className="pb-2 font-medium">Job ID</th>
                  <th className="pb-2 font-medium">Project</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium">Gain</th>
                </tr>
              </thead>
              <tbody>
                {recent_jobs.map((j) => (
                  <tr key={j.job_id} className="border-b border-line last:border-0 hover:bg-canvas/50 transition">
                    <td className="py-2 font-medium text-ink whitespace-nowrap">
                      <Link href={`/comparison?job=${j.job_id}`} className="text-primary hover:underline font-mono text-[11.5px] sm:text-[13px]">
                        {j.job_id}
                      </Link>
                    </td>
                    <td className="py-2 text-ink-soft truncate max-w-[120px]">{j.project}</td>
                    <td className="py-2"><StatusBadge status={j.status} plain /></td>
                    <td className="py-2 text-ink-soft whitespace-nowrap">{j.resolution_gain}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------- sub-parts */

function Kpi({
  title, value, sub, icon, iconBg, right,
}: {
  title: string; value: number | string; sub: string; icon?: React.ReactNode; iconBg?: string; right?: React.ReactNode;
}) {
  return (
    <Card className="p-2 sm:p-4 h-full">
      <div className="flex items-start justify-between gap-1">
        <div className="min-w-0 flex-1">
          <div className="text-[11px] sm:text-[13px] text-muted truncate">{title}</div>
          <div className="text-[18px] sm:text-[30px] font-semibold text-ink leading-tight mt-0.5 sm:mt-1">{value}</div>
          <div className="text-[10px] sm:text-[12.5px] text-primary mt-0.5 truncate">{sub}</div>
        </div>
        {right ?? (icon && <div className={cn("h-7 w-7 sm:h-11 sm:w-11 rounded-md sm:rounded-xl grid place-items-center shrink-0", iconBg)}>{icon}</div>)}
      </div>
    </Card>
  );
}

function StorageKpi({ used, total }: { used: number; total: number }) {
  return (
    <Card className="p-2 sm:p-4 h-full">
      <div className="flex items-start justify-between gap-1">
        <div className="min-w-0 flex-1">
          <div className="text-[11px] sm:text-[13px] text-muted truncate">Storage</div>
          <div className="text-[18px] sm:text-[30px] font-semibold text-ink leading-tight mt-0.5 sm:mt-1">{used} TB</div>
          <div className="text-[10px] sm:text-[12.5px] text-muted mt-0.5 truncate">of {total} TB</div>
        </div>
        <div className="h-7 w-7 sm:h-11 sm:w-11 rounded-md sm:rounded-xl bg-canvas grid place-items-center shrink-0">
          <Database size={15} className="text-ink-soft sm:hidden" />
          <Database size={22} className="text-ink-soft hidden sm:block" />
        </div>
      </div>
      <ProgressBar value={(used / total) * 100} tone="primary" className="mt-1.5 sm:mt-3" />
    </Card>
  );
}

function ImagePanel({ label, chip, footer, gradientFooter, children }: { label: string; chip?: string; footer?: string; gradientFooter?: boolean; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] sm:text-[12.5px] text-ink-soft mb-1 text-center truncate font-medium">{label}</div>
      <div className="relative rounded-md sm:rounded-lg overflow-hidden aspect-square bg-[#3a3a2c]">
        {children}
        {chip && <span className="absolute left-1 bottom-1 sm:left-2 sm:bottom-2 rounded bg-black/70 px-1 sm:px-2 py-0.5 sm:py-1 text-[9px] sm:text-[11px] font-medium text-white">{chip}</span>}
        {footer && (
          <div className="absolute inset-x-0 bottom-0">
            {gradientFooter && <div className="h-1.5 sm:h-2 bg-gradient-to-r from-[#000004] via-[#cf4446] to-[#fcffa4]" />}
            <div className="px-1.5 py-0.5 sm:px-2 sm:py-1 text-[9px] sm:text-[11px] text-white/90 bg-black/50 truncate">{footer}</div>
          </div>
        )}
      </div>
    </div>
  );
}

function ImagePanelInner({ label, chip, children }: { label: string; chip?: string; children: React.ReactNode }) {
  return (
    <div className="w-full">
      <div className="text-[10px] sm:text-[12.5px] text-ink-soft mb-1 text-center truncate font-medium">{label}</div>
      <div className="relative rounded-md sm:rounded-lg overflow-hidden aspect-square bg-[#3a3a2c]">
        {children}
        {chip && <span className="absolute left-1 bottom-1 sm:left-2 sm:bottom-2 rounded bg-black/70 px-1 sm:px-2 py-0.5 sm:py-1 text-[9px] sm:text-[11px] font-medium text-white">{chip}</span>}
      </div>
    </div>
  );
}

function ArrowBubble({ className }: { className?: string }) {
  return (
    <div className={cn("absolute z-10 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full bg-primary text-white grid place-items-center shadow-md", className)}>
      <ChevronRight size={18} />
    </div>
  );
}

function Meta({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center sm:items-start gap-1 sm:gap-2">
      <span className="text-muted shrink-0 mt-0 sm:mt-0.5">{icon}</span>
      <div className="min-w-0">
        <div className="text-[10px] sm:text-[11.5px] text-muted truncate">{label}</div>
        <div className="text-[11.5px] sm:text-[13px] font-medium text-ink truncate">{value}</div>
      </div>
    </div>
  );
}

function StatusTile({ title, status, statusColor, check, children }: { title: string; status: string; statusColor: string; check?: boolean; children?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-line p-2 sm:p-3">
      <div className="flex items-center justify-between gap-1">
        <div className="text-[11.5px] sm:text-[13px] font-medium text-ink truncate">{title}</div>
        {check && <CheckCircle2 size={14} className="text-teal shrink-0" />}
      </div>
      <div className={cn("text-[11px] sm:text-[12.5px] mt-0.5 truncate", statusColor)}>{status}</div>
      {children && <div className="mt-1">{children}</div>}
    </div>
  );
}

function ActivityPolygons() {
  const polys = [
    { pts: "16,42 26,36 30,46 22,54 14,52", c: "#0F8C7F" },
    { pts: "34,30 44,26 46,38 38,42", c: "#0F8C7F" },
    { pts: "60,34 68,30 72,44 64,50 58,44", c: "#0F8C7F" },
    { pts: "50,58 60,54 64,68 54,72 48,64", c: "#D6532B" },
    { pts: "68,60 78,58 80,70 70,74", c: "#D6532B" },
  ];
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
      {polys.map((p, i) => (
        <polygon key={i} points={p.pts} fill={p.c} fillOpacity={0.28} stroke={p.c} strokeWidth={0.7} />
      ))}
    </svg>
  );
}
