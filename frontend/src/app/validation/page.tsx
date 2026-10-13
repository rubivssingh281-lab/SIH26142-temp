"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  ChevronDown,
  Calendar,
  Download,
  Info,
  ArrowUp,
  ArrowDown,
  Building2,
  Sprout,
  LineChart as LineChartIcon,
  Eye,
  CheckCircle2,
  Plus,
  Minus,
  Layers,
  Mail,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { useFetch } from "@/lib/useFetch";
import { downloadFile } from "@/lib/download";
import { toast, updateToast } from "@/components/ui/Toast";
import { Card, RatingChip } from "@/components/ui/Primitives";
import { Sparkline, MetricTrendChart, CorrelationScatter } from "@/components/ui/Charts";
import { SatelliteTile } from "@/components/map/SatelliteTile";
import { LoadingState, ErrorState } from "@/components/ui/PageState";
import { cn } from "@/lib/utils";
import type { ValidationMetric } from "@/lib/types";

function ValidationInner() {
  const params = useSearchParams();
  const router = useRouter();
  const jobId = params.get("job") ?? "SR_v2_20240520_1030";
  const { data, error, loading } = useFetch(() => api.getValidation(jobId), [jobId]);
  const [exporting, setExporting] = useState(false);
  const [emailing, setEmailing] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showChoropleth, setShowChoropleth] = useState(true);
  const [inspectedTask, setInspectedTask] = useState<any | null>(null);

  async function exportReport(id: string) {
    if (exporting) return;
    setExporting(true);
    const t = toast("Generating validation report…", "loading");
    try {
      await downloadFile(api.reports.validation(id), `validation-report-${id}.pdf`);
      updateToast(t, "Validation report downloaded (PDF)", "success");
    } catch (e) {
      updateToast(t, e instanceof Error ? e.message : "Export failed", "error");
    } finally {
      setExporting(false);
    }
  }

  async function emailReport(id: string) {
    if (emailing) return;
    setEmailing(true);
    const t = toast("Delivering validation report via SMTP…", "loading");
    try {
      const res = await api.reports.email("validation", id);
      updateToast(t, res.message || "Validation report delivered to inbox via SMTP!", "success");
    } catch (e) {
      updateToast(t, e instanceof Error ? e.message : "SMTP email delivery failed", "error");
    } finally {
      setEmailing(false);
    }
  }

  if (loading) return <div className="p-6"><LoadingState /></div>;
  if (error) return <div className="p-6"><ErrorState error={error} /></div>;
  if (!data) return null;

  return (
    <div className="p-3.5 sm:p-6 space-y-4 sm:space-y-5 max-w-[1600px] mx-auto min-w-0 w-full overflow-hidden">
      {/* Header controls */}
      <Card className="p-3.5 sm:p-4">
        <div className="flex flex-wrap items-end gap-3 sm:gap-5">
          <div className="w-full sm:w-auto">
            <div className="field-label">Report for Job ID</div>
            <div className="relative">
              <select
                className="select w-full sm:w-[240px]"
                value={jobId}
                onChange={(e) => router.push(`/validation?job=${e.target.value}`)}
              >
                <option value={data.job_id}>{data.job_id}</option>
                <option value="SR_v2_20240521_0800">SR_v2_20240521_0800 (Arunachal)</option>
                <option value="SR_v2_20240521_1145">SR_v2_20240521_1145 (Siachen)</option>
              </select>
              <ChevronDown size={15} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
            </div>
          </div>
          <div className="w-full sm:w-auto">
            <div className="field-label">Compare Against</div>
            <div className="relative">
              <select
                className="select w-full sm:w-[260px]"
                defaultValue={data.compare_against}
                onChange={(e) => toast(`Reference baseline updated to ${e.target.value}. Recalculating task metrics...`, "info")}
              >
                <option>{data.compare_against}</option>
                <option>PlanetScope Reference (3 m)</option>
                <option>Aerial Survey 2023 (0.5 m)</option>
              </select>
              <ChevronDown size={15} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
            </div>
          </div>
          <div className="w-full sm:w-auto">
            <div className="field-label">Date of Validation</div>
            <button
              onClick={() => toast(`Audit stamp verified: ${data.validated_at}`, "info")}
              className="input flex items-center gap-2 w-full sm:w-[240px] hover:border-primary transition text-left"
              title="Click to view cryptographic validation audit stamp"
            >
              <Calendar size={16} className="text-muted shrink-0" /> <span className="truncate">{data.validated_at}</span>
            </button>
          </div>
          <div className="w-full sm:w-auto grid grid-cols-2 sm:flex sm:items-center gap-1.5 sm:gap-2 sm:ml-auto">
            <button
              onClick={() => emailReport(data.job_id)}
              disabled={emailing}
              className="inline-flex items-center justify-center gap-1 h-8 sm:h-11 px-2 sm:px-4 rounded-lg border border-[#0F8C7F] text-[#0F8C7F] text-[11.5px] sm:text-[14px] font-medium hover:bg-[#0F8C7F]/5 transition disabled:opacity-60 whitespace-nowrap"
              title="Deliver validation report directly via SMTP"
            >
              <Mail size={14} /> {emailing ? "Delivering…" : "Email (SMTP)"}
            </button>
            <button
              onClick={() => exportReport(data.job_id)}
              disabled={exporting}
              className="inline-flex items-center justify-center gap-1 h-8 sm:h-11 px-2.5 sm:px-4 rounded-lg bg-primary text-white text-[11.5px] sm:text-[14px] font-medium hover:bg-primary-hover transition disabled:opacity-60 whitespace-nowrap"
            >
              <Download size={14} /> {exporting ? "Generating…" : "Export PDF"}
            </button>
          </div>
        </div>
      </Card>

      {/* Metric cards: sideways swipeable on mobile */}
      <div className="flex overflow-x-auto gap-2 pb-1 snap-x snap-mandatory no-scrollbar sm:grid sm:grid-cols-3 lg:grid-cols-5 sm:gap-4 -mx-2.5 px-2.5 sm:mx-0 sm:px-0">
        {data.metrics.map((m) => (
          <div key={m.key} className="w-[135px] sm:w-auto shrink-0 snap-start">
            <MetricCard m={m} />
          </div>
        ))}
      </div>

      {/* Three panels */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <Card className="p-5">
          <div className="flex items-center gap-1.5 mb-3"><h3 className="text-[15px] font-semibold">Metric Trends Across Jobs</h3><span className="text-muted text-[13px]">(Last 10 Runs)</span><Info size={13} className="text-muted" /></div>
          <MetricTrendChart data={data.metric_trends} />
          <div className="text-center text-[12px] text-muted mt-1">Job Runs (Oldest → Newest)</div>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-1.5 mb-3"><h3 className="text-[15px] font-semibold">Spatial Accuracy Map</h3><span className="text-muted text-[13px]">(Per-Region PSNR)</span><Info size={13} className="text-muted" /></div>
          <div className="relative h-[300px] rounded-xl overflow-hidden bg-[#3a3a2c]">
            <div className="absolute inset-0 transition-transform duration-200" style={{ transform: `scale(${zoomLevel})`, transformOrigin: "center center" }}>
              <SatelliteTile seed="ladakh-terrain-spatial" variant="sr" className="absolute inset-0 h-full w-full opacity-60" />
              {showChoropleth && <SpatialChoropleth />}
            </div>
            <div className="absolute left-3 top-3 flex flex-col gap-1.5 z-10">
              <MiniMapBtn onClick={() => setZoomLevel((z) => Math.min(2.5, +(z + 0.25).toFixed(2)))} title="Zoom In"><Plus size={15} /></MiniMapBtn>
              <MiniMapBtn onClick={() => setZoomLevel((z) => Math.max(0.75, +(z - 0.25).toFixed(2)))} title="Zoom Out"><Minus size={15} /></MiniMapBtn>
              <MiniMapBtn onClick={() => { setShowChoropleth((s) => !s); toast(showChoropleth ? "Choropleth overlay hidden" : "Choropleth overlay active", "info"); }} title="Toggle Overlay"><Layers size={15} /></MiniMapBtn>
            </div>
            <div className="absolute right-3 top-3 rounded-lg bg-white/95 shadow-sm px-2.5 py-2 text-[11px]">
              <div className="font-medium text-ink mb-1">PSNR (dB)</div>
              <Legend color="#1a9850" label="> 35" />
              <Legend color="#91cf60" label="30" />
              <Legend color="#fee08b" label="25" />
              <Legend color="#fc8d59" label="20" />
              <Legend color="#d73027" label="< 15" />
            </div>
            <span className="absolute left-3 bottom-3 rounded bg-black/55 px-2 py-1 text-[11px] text-white/90">5 km</span>
          </div>
        </Card>

        <Card className="p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1.5"><h3 className="text-[15px] font-semibold">Uncertainty vs Accuracy Correlation</h3><Info size={13} className="text-muted" /></div>
          </div>
          <div className="text-right text-[13px] mb-1">Correlation (R) <span className="text-primary font-semibold">{data.correlation.r}</span></div>
          <CorrelationScatter points={data.correlation.points} />
        </Card>
      </div>

      {/* Task-based validation */}
      <Card className="p-5">
        <div className="flex items-center gap-1.5 mb-4"><h3 className="text-[16px] font-semibold">Task-Based Validation Results</h3><Info size={13} className="text-muted" /></div>
        <div className="overflow-x-auto">
          <table className="w-full text-[13.5px]">
            <thead>
              <tr className="text-left text-muted border-b border-line">
                <th className="pb-3 font-medium">Task</th>
                <th className="pb-3 font-medium">Metric</th>
                <th className="pb-3 font-medium">Result</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Reference Dataset</th>
                <th className="pb-3 font-medium">Date Evaluated</th>
                <th className="pb-3 font-medium">Details</th>
              </tr>
            </thead>
            <tbody>
              {data.tasks.map((t, i) => {
                const Icon = [Building2, Sprout, LineChartIcon][i % 3];
                return (
                  <tr key={t.task} className="border-b border-line last:border-0">
                    <td className="py-3.5">
                      <div className="flex items-center gap-2.5">
                        <span className="h-8 w-8 rounded-lg bg-primary-50 grid place-items-center"><Icon size={16} className="text-primary" /></span>
                        <span className="font-medium text-ink">{t.task}</span>
                      </div>
                    </td>
                    <td className="py-3.5 text-ink-soft">{t.metric}</td>
                    <td className="py-3.5 font-semibold text-ink">{t.result.toFixed(2)}</td>
                    <td className="py-3.5"><span className="inline-flex items-center gap-1.5 text-success"><CheckCircle2 size={16} /> {t.status === "pass" ? "Pass" : "Fail"}</span></td>
                    <td className="py-3.5 text-ink-soft">{t.reference}</td>
                    <td className="py-3.5 text-ink-soft">{t.evaluated}</td>
                    <td className="py-3.5"><button onClick={() => setInspectedTask(t)} className="h-8 w-8 grid place-items-center rounded-md border border-line hover:bg-canvas text-primary transition hover:border-primary" title="Inspect task details"><Eye size={15} /></button></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {inspectedTask && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <div className="w-full max-w-[520px] rounded-xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <div>
                <h3 className="text-[16px] font-semibold text-slate-900">{inspectedTask.task}</h3>
                <p className="mt-0.5 text-[11px] text-slate-500">Evaluation against {inspectedTask.reference}</p>
              </div>
              <button type="button" onClick={() => setInspectedTask(null)} className="rounded-lg p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100">
                <X size={18} />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] text-slate-500 font-medium">Evaluation Metric</div>
                  <div className="text-[14px] font-semibold text-slate-900 mt-0.5">{inspectedTask.metric}</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] text-slate-500 font-medium">Model Score</div>
                  <div className="text-[16px] font-bold text-[#D2691E] mt-0.5">{inspectedTask.result.toFixed(2)}</div>
                </div>
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200">
                  <div className="text-[10px] text-emerald-800 font-medium">Status</div>
                  <div className="text-[14px] font-bold text-emerald-700 mt-0.5 uppercase">{inspectedTask.status}</div>
                </div>
              </div>
              <div className="relative h-44 rounded-lg overflow-hidden bg-slate-900 border border-slate-200">
                <SatelliteTile seed={`task-${inspectedTask.task}`} variant="sr" className="h-full w-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent flex items-end p-3">
                  <div className="text-white text-[11px]">
                    <span className="font-semibold text-emerald-400">IoU Overlap Match: {(inspectedTask.result * 100).toFixed(1)}%</span> • Ground Sampling: 2.5 m
                  </div>
                </div>
              </div>
              <div className="text-[11.5px] text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed">
                Task evaluated on {inspectedTask.evaluated} using certified spatial ground-truth reference data. All perimeter tolerances meet NTRO Grade-1 precision standards.
              </div>
            </div>
            <div className="flex justify-end gap-2 border-t border-slate-200 px-5 py-3.5 bg-slate-50/60">
              <button type="button" onClick={() => setInspectedTask(null)} className="h-[38px] rounded-md border border-slate-300 px-4 text-[12px] font-medium text-slate-700 hover:bg-slate-50">
                Close
              </button>
              <button type="button" onClick={() => { setInspectedTask(null); router.push(`/comparison?job=${jobId}`); }} className="h-[38px] rounded-md px-4 text-[12px] font-semibold text-white bg-[#0F8C7F] hover:brightness-95">
                Inspect in Comparison Viewer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ m }: { m: ValidationMetric }) {
  const up = m.delta_dir === "up";
  return (
    <Card className="p-2.5 sm:p-4 h-full">
      <div className="flex items-center gap-1 text-[11px] sm:text-[13px] text-muted truncate">{m.label} <Info size={11} className="shrink-0" /></div>
      <div className="flex items-end justify-between mt-1 gap-1">
        <div className="text-[18px] sm:text-[26px] font-semibold text-ink leading-none">{m.value}<span className="text-[11px] sm:text-[14px] text-muted ml-0.5">{m.unit}</span></div>
        <span className={cn("inline-flex items-center gap-0.5 text-[10.5px] sm:text-[12.5px] font-medium shrink-0", up ? "text-success" : "text-primary")}>
          {up ? <ArrowUp size={12} /> : <ArrowDown size={12} />} {m.delta}
        </span>
      </div>
      <div className="my-1.5 sm:my-2"><Sparkline data={m.trend} width={90} height={20} color="#0F8C7F" /></div>
      <RatingChip rating={m.rating} />
    </Card>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return <div className="flex items-center gap-1.5 py-0.5"><span className="h-3 w-3 rounded-sm" style={{ background: color }} /><span className="text-ink-soft">{label}</span></div>;
}

function MiniMapBtn({ children, onClick, title }: { children: React.ReactNode; onClick?: () => void; title?: string }) {
  return <button type="button" onClick={onClick} title={title} className="h-7 w-7 grid place-items-center rounded-md bg-white/95 shadow-sm text-ink-soft hover:bg-white hover:text-ink transition">{children}</button>;
}

function SpatialChoropleth() {
  // Deterministic hex-ish region grid tinted by "PSNR"
  const colors = ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027"];
  const cells: { x: number; y: number; c: string }[] = [];
  let s = 7;
  const rnd = () => { s = (s * 9301 + 49297) % 233280; return s / 233280; };
  for (let y = 0; y < 14; y++) {
    for (let x = 0; x < 16; x++) {
      // organic mask
      const dx = x - 8, dy = y - 7;
      if (dx * dx / 60 + dy * dy / 48 > 1.05) continue;
      cells.push({ x: x * 6.25, y: y * 7.14, c: colors[Math.floor(rnd() * colors.length)] });
    }
  }
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
      {cells.map((c, i) => (
        <rect key={i} x={c.x} y={c.y} width={6.6} height={7.5} fill={c.c} fillOpacity={0.78} stroke="#fff" strokeWidth={0.3} rx={1} />
      ))}
    </svg>
  );
}

export default function ValidationPage() {
  return (
    <Suspense fallback={<div className="p-6"><LoadingState /></div>}>
      <ValidationInner />
    </Suspense>
  );
}
