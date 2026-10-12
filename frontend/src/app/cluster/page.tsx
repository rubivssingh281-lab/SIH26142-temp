"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Cpu,
  Zap,
  Activity,
  ArrowLeft,
  RefreshCw,
  Sliders,
  Flame,
  Gauge,
  CheckCircle2,
  HardDrive,
  ShieldCheck,
  Server,
  Terminal,
  Play,
  RotateCcw,
} from "lucide-react";
import { toast } from "@/components/ui/Toast";
import { Card, ProgressBar } from "@/components/ui/Primitives";
import { cn } from "@/lib/utils";

interface GpuNode {
  id: string;
  name: string;
  model: string;
  status: "active" | "standby" | "throttled";
  vramUsed: number;
  vramTotal: number;
  utilization: number;
  temperature: number;
  powerWatts: number;
  powerMax: number;
  fanSpeedPct: number;
  currentTask: string;
  assignedProject: string;
}

const INITIAL_NODES: GpuNode[] = [
  {
    id: "node-01",
    name: "GPU-Cluster-Alpha-01",
    model: "NVIDIA A100-SXM4-80GB",
    status: "active",
    vramUsed: 68.4,
    vramTotal: 80,
    utilization: 94,
    temperature: 64,
    powerWatts: 345,
    powerMax: 400,
    fanSpeedPct: 78,
    currentTask: "SR_v2_20240521 (TerraSharp 4x GAN)",
    assignedProject: "Ladakh Border Infrastructure",
  },
  {
    id: "node-02",
    name: "GPU-Cluster-Alpha-02",
    model: "NVIDIA A100-SXM4-80GB",
    status: "active",
    vramUsed: 54.2,
    vramTotal: 80,
    utilization: 82,
    temperature: 58,
    powerWatts: 310,
    powerMax: 400,
    fanSpeedPct: 65,
    currentTask: "SR_v2_20240520 (Diffusion Prior 4x)",
    assignedProject: "Siachen Glacial Moraine",
  },
  {
    id: "node-03",
    name: "GPU-Cluster-Beta-03",
    model: "NVIDIA A100-SXM4-80GB",
    status: "active",
    vramUsed: 62.1,
    vramTotal: 80,
    utilization: 89,
    temperature: 61,
    powerWatts: 330,
    powerMax: 400,
    fanSpeedPct: 72,
    currentTask: "SR_v2_20240523 (Multi-Spectral ESRGAN)",
    assignedProject: "Thar Desert Surveillance",
  },
  {
    id: "node-04",
    name: "GPU-Cluster-Beta-04",
    model: "NVIDIA A100-SXM4-80GB",
    status: "standby",
    vramUsed: 12.8,
    vramTotal: 80,
    utilization: 16,
    temperature: 42,
    powerWatts: 145,
    powerMax: 400,
    fanSpeedPct: 40,
    currentTask: "Idle · Staged for high-priority emergency queue",
    assignedProject: "Standby Buffer Pool",
  },
];

export default function ClusterPage() {
  const [nodes, setNodes] = useState<GpuNode[]>(INITIAL_NODES);
  const [isRebalancing, setIsRebalancing] = useState(false);
  const [isFlushing, setIsFlushing] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string>("node-01");

  const totalVramUsed = nodes.reduce((acc, n) => acc + n.vramUsed, 0);
  const totalVram = nodes.reduce((acc, n) => acc + n.vramTotal, 0);
  const avgUtil = Math.round(nodes.reduce((acc, n) => acc + n.utilization, 0) / nodes.length);
  const totalPower = nodes.reduce((acc, n) => acc + n.powerWatts, 0);

  const handleRebalance = () => {
    setIsRebalancing(true);
    toast("Initiating NCCL peer-to-peer tensor rebalancing across nodes…", "loading");
    setTimeout(() => {
      setNodes((curr) =>
        curr.map((n) => ({
          ...n,
          utilization: n.status === "standby" ? 64 : Math.min(88, n.utilization - 8),
          vramUsed: n.status === "standby" ? 44.5 : Math.max(30, n.vramUsed - 10),
          status: "active",
        }))
      );
      setIsRebalancing(false);
      toast("GPU cluster load balanced across all 4 worker nodes!", "success");
    }, 1800);
  };

  const handleFlushCache = () => {
    setIsFlushing(true);
    toast("Purging stale intermediate tensor activation checkpoints…", "loading");
    setTimeout(() => {
      setNodes((curr) =>
        curr.map((n) => ({
          ...n,
          vramUsed: Math.max(12, Number((n.vramUsed * 0.82).toFixed(1))),
        }))
      );
      setIsFlushing(false);
      toast("GPU VRAM memory cache flushed successfully! 38.4 GB freed.", "success");
    }, 1200);
  };

  const handleRestartNode = (id: string) => {
    toast(`Restarting compute daemon on ${id}…`, "info");
    setTimeout(() => {
      toast(`${id} operational in nominal thermal envelope.`, "success");
    }, 1500);
  };

  return (
    <div className="p-4 sm:p-6 pr-6 sm:pr-8 space-y-6 max-w-[1600px] mx-auto min-w-0 w-full overflow-hidden">
      {/* Top breadcrumb & action bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-line pb-4">
        <div>
          <div className="flex items-center gap-2 text-[12px] text-muted mb-1">
            <Link href="/queue" className="inline-flex items-center gap-1 text-primary hover:underline">
              <ArrowLeft size={13} /> Processing Queue
            </Link>
            <span>/</span>
            <span>GPU Cluster Telemetry</span>
          </div>
          <h1 className="text-[26px] font-semibold text-ink flex items-center gap-3">
            <Server className="text-primary" size={28} />
            Hardware &amp; Inference Cluster Topology
          </h1>
          <p className="text-[13px] text-muted mt-0.5">
            Real-time telemetry, thermal management, and NCCL peer-to-peer interconnect for NTRO PS-26142
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleFlushCache}
            disabled={isFlushing}
            className="inline-flex items-center gap-1.5 h-10 px-3.5 rounded-lg border border-line bg-surface text-[12.5px] font-medium text-ink hover:bg-canvas transition disabled:opacity-60"
          >
            <RotateCcw size={15} />
            {isFlushing ? "Flushing…" : "Flush VRAM Cache"}
          </button>
          <button
            onClick={handleRebalance}
            disabled={isRebalancing}
            className="inline-flex items-center gap-2 h-10 px-4 rounded-lg bg-primary text-white text-[12.5px] font-semibold hover:bg-primary-hover shadow-sm transition disabled:opacity-60"
          >
            <Sliders size={16} />
            {isRebalancing ? "Rebalancing…" : "Rebalance Cluster"}
          </button>
        </div>
      </div>

      {/* Aggregate Overview KPI Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-gradient-to-br from-surface to-canvas/40 border-line">
          <div className="text-[12px] text-muted flex items-center gap-1.5">
            <Cpu size={16} className="text-primary" /> Active Accelerators
          </div>
          <div className="text-[28px] font-bold text-ink mt-1">4x A100</div>
          <div className="text-[11.5px] text-emerald-700 font-medium mt-0.5 flex items-center gap-1">
            <CheckCircle2 size={13} /> 100% Online · Healthy
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-surface to-canvas/40 border-line">
          <div className="text-[12px] text-muted flex items-center gap-1.5">
            <Activity size={16} className="text-[#0F8C7F]" /> Aggregate Load
          </div>
          <div className="text-[28px] font-bold text-ink mt-1">{avgUtil}%</div>
          <div className="text-[11.5px] text-muted mt-0.5">Balanced Tensor Schedule</div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-surface to-canvas/40 border-line">
          <div className="text-[12px] text-muted flex items-center gap-1.5">
            <HardDrive size={16} className="text-amber-600" /> Total VRAM Consumed
          </div>
          <div className="text-[28px] font-bold text-ink mt-1">
            {totalVramUsed.toFixed(1)} <span className="text-[16px] text-muted font-normal">/ {totalVram} GB</span>
          </div>
          <div className="text-[11.5px] text-muted mt-0.5">HBM2e High-Bandwidth Memory</div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-surface to-canvas/40 border-line">
          <div className="text-[12px] text-muted flex items-center gap-1.5">
            <Zap size={16} className="text-yellow-600" /> Total Power Draw
          </div>
          <div className="text-[28px] font-bold text-ink mt-1">
            {totalPower} <span className="text-[16px] text-muted font-normal">/ 1,600 W</span>
          </div>
          <div className="text-[11.5px] text-emerald-700 font-medium mt-0.5 flex items-center gap-1">
            <ShieldCheck size={13} /> Normal Thermal Envelope
          </div>
        </Card>
      </div>

      {/* Worker Nodes Detailed Grid */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-[16px] font-semibold text-ink flex items-center gap-2">
            <Server size={18} className="text-primary" />
            Worker Accelerator Nodes
          </h2>
          <span className="text-[12px] text-muted">Auto-refreshes every 5s</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {nodes.map((n) => {
            const vramPct = Math.round((n.vramUsed / n.vramTotal) * 100);
            return (
              <Card
                key={n.id}
                className={cn(
                  "p-5 transition border",
                  selectedNode === n.id ? "border-primary shadow-md" : "border-line hover:border-line-strong"
                )}
                onClick={() => setSelectedNode(n.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-11 w-11 rounded-xl bg-primary-50 text-primary grid place-items-center font-bold text-[15px]">
                      <Cpu size={22} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[15px] font-semibold text-ink">{n.name}</span>
                        <span
                          className={cn(
                            "rounded px-2 py-0.5 text-[10px] font-bold uppercase",
                            n.status === "active"
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : "bg-amber-50 text-amber-700 border border-amber-200"
                          )}
                        >
                          {n.status}
                        </span>
                      </div>
                      <div className="text-[12px] text-muted mt-0.5">{n.model}</div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRestartNode(n.name);
                    }}
                    title="Cycle compute process"
                    className="h-8 w-8 rounded-lg border border-line text-muted hover:text-ink hover:bg-canvas grid place-items-center transition"
                  >
                    <RefreshCw size={14} />
                  </button>
                </div>

                {/* Metrics Breakdown */}
                <div className="mt-5 space-y-3 pt-3 border-t border-line">
                  <div>
                    <div className="flex justify-between text-[12px] mb-1">
                      <span className="text-muted">Compute Core Utilization</span>
                      <span className="font-semibold text-ink">{n.utilization}%</span>
                    </div>
                    <ProgressBar
                      value={n.utilization}
                      tone={n.utilization > 85 ? "primary" : "teal"}
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-[12px] mb-1">
                      <span className="text-muted">VRAM Allocation</span>
                      <span className="font-semibold text-ink">
                        {n.vramUsed} GB / {n.vramTotal} GB ({vramPct}%)
                      </span>
                    </div>
                    <ProgressBar
                      value={vramPct}
                      tone={vramPct > 80 ? "primary" : "teal"}
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-2 pt-2 text-[11.5px]">
                    <div className="rounded-lg bg-canvas p-2.5">
                      <div className="text-muted flex items-center gap-1">
                        <Flame size={13} className="text-orange-600" /> Temperature
                      </div>
                      <div className="text-[14px] font-semibold text-ink mt-0.5">
                        {n.temperature}°C
                      </div>
                    </div>

                    <div className="rounded-lg bg-canvas p-2.5">
                      <div className="text-muted flex items-center gap-1">
                        <Zap size={13} className="text-yellow-600" /> Power
                      </div>
                      <div className="text-[14px] font-semibold text-ink mt-0.5">
                        {n.powerWatts}W
                      </div>
                    </div>

                    <div className="rounded-lg bg-canvas p-2.5">
                      <div className="text-muted flex items-center gap-1">
                        <Gauge size={13} className="text-blue-600" /> Fan Speed
                      </div>
                      <div className="text-[14px] font-semibold text-ink mt-0.5">
                        {n.fanSpeedPct}%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Current Active Task */}
                <div className="mt-4 pt-3 border-t border-line/80 flex items-start gap-2 text-[12px]">
                  <Terminal size={15} className="text-primary shrink-0 mt-0.5" />
                  <div className="min-w-0 flex-1">
                    <span className="text-muted">Task: </span>
                    <span className="font-medium text-ink truncate block">{n.currentTask}</span>
                    <span className="text-[11px] text-muted">Project: {n.assignedProject}</span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Cluster Interconnect Topology & Logs */}
      <Card className="p-5">
        <h3 className="text-[16px] font-semibold text-ink mb-3 flex items-center gap-2">
          <Terminal size={17} className="text-primary" />
          NVIDIA DCGM Diagnostic &amp; Interconnect Status
        </h3>
        <div className="rounded-lg bg-[#0E1626] p-4 text-[#A7ADB3] font-mono text-[12px] space-y-1 overflow-x-auto">
          <div className="text-emerald-400">● [DCGM-DAEMON]: NVIDIA Driver 535.129.03 · CUDA 12.2 · NCCL 2.18.3 active</div>
          <div>✓ [NVLINK-TOPOLOGY]: NVLink 3.0 Full Mesh detected across GPU 0, 1, 2, 3 (600 GB/s bidirectional)</div>
          <div>✓ [ECC-CHECK]: 0 single-bit, 0 double-bit memory errors detected in past 168 hours</div>
          <div>✓ [PRECISION-UNIT]: FP16 Tensor Cores &amp; BF16 Matrix Multiplication units operational</div>
          <div className="text-[#E4A52E]">● [SCHEDULER-QUEUE]: High-priority preemption active for Mission Ladakh Border Infrastructure</div>
        </div>
      </Card>
    </div>
  );
}
