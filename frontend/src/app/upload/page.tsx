"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  UploadCloud,
  FileUp,
  ArrowLeft,
  CheckCircle2,
  Database,
  Layers,
  MapPin,
  Clock,
  Sparkles,
  Info,
  Trash2,
  Send,
  Plus,
} from "lucide-react";
import { toast } from "@/components/ui/Toast";
import { Card, Button, ProgressBar } from "@/components/ui/Primitives";
import { cn } from "@/lib/utils";

interface StagedFile {
  name: string;
  size: string;
  type: string;
  bands: string[];
  cloudCover: string;
  gsd: string;
  date: string;
  progress: number;
  uploaded: boolean;
}

const PRESET_FILES: StagedFile[] = [
  {
    name: "S2B_MSIL2A_20240521_T43SFU_Ladakh_B02_B04_B08.tif",
    size: "148.2 MB",
    type: "GeoTIFF (Cloud Optimized)",
    bands: ["B02 (Blue)", "B03 (Green)", "B04 (Red)", "B08 (NIR)"],
    cloudCover: "4.2%",
    gsd: "10.0 m",
    date: "21 May 2024",
    progress: 100,
    uploaded: true,
  },
  {
    name: "AOI_Sector_4B_Ladakh_Infrastructure.geojson",
    size: "420 KB",
    type: "GeoJSON Spatial Vector",
    bands: ["Polygon AOI Vector Boundary"],
    cloudCover: "0.0%",
    gsd: "N/A",
    date: "18 May 2024",
    progress: 100,
    uploaded: true,
  },
];

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<StagedFile[]>(PRESET_FILES);
  const [provider, setProvider] = useState("sentinel-2");
  const [project, setProject] = useState("Ladakh Border Infrastructure");
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleSimulateUpload = (filename?: string) => {
    setIsUploading(true);
    const newName = filename || `S2A_MSIL2A_${Date.now()}_AOI_Sector7.tif`;
    toast(`Ingesting ${newName} into Bhu-Dristi staging volume…`, "loading");

    setTimeout(() => {
      setFiles((prev) => [
        {
          name: newName,
          size: "182.4 MB",
          type: "GeoTIFF (Multi-Spectral)",
          bands: ["B02", "B03", "B04", "B08", "B11", "B12"],
          cloudCover: "2.1%",
          gsd: "10.0 m",
          date: "12 Oct 2026",
          progress: 100,
          uploaded: true,
        },
        ...prev,
      ]);
      setIsUploading(false);
      toast("Satellite scene ingested! Multi-spectral bands validated.", "success");
    }, 1500);
  };

  const handleRemove = (name: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
    toast(`Removed ${name}`, "info");
  };

  const handleStageForJob = () => {
    toast("Staging selected satellite layers into New Enhancement Job…", "loading");
    setTimeout(() => {
      router.push("/new-job");
    }, 600);
  };

  return (
    <div className="p-4 sm:p-6 pr-6 sm:pr-8 space-y-6 max-w-[1600px] mx-auto min-w-0 w-full overflow-hidden">
      {/* Top Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-line pb-4">
        <div>
          <div className="flex items-center gap-2 text-[12px] text-muted mb-1">
            <Link href="/dashboard" className="inline-flex items-center gap-1 text-primary hover:underline">
              <ArrowLeft size={13} /> Dashboard
            </Link>
            <span>/</span>
            <span>Data Ingestion</span>
          </div>
          <h1 className="text-[26px] font-semibold text-ink flex items-center gap-3">
            <UploadCloud className="text-primary" size={28} />
            Satellite Imagery &amp; AOI Ingestion Pipeline
          </h1>
          <p className="text-[13px] text-muted mt-0.5">
            Upload multi-spectral satellite scenes, shapefiles, or GeoJSON vectors for deep-learning super-resolution
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            href="/settings?tab=data"
            className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg border border-line bg-surface text-[12.5px] font-medium text-ink hover:bg-canvas transition"
          >
            <Database size={15} />
            Data Source Connections
          </Link>
          <button
            onClick={handleStageForJob}
            className="inline-flex items-center gap-2 h-10 px-4 rounded-lg bg-primary text-white text-[12.5px] font-semibold hover:bg-primary-hover shadow-sm transition"
          >
            <Send size={15} />
            Stage for Enhancement Job
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column: Dropzone & Ingestion Parameters */}
        <div className="xl:col-span-2 space-y-5">
          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              const file = e.dataTransfer.files[0];
              handleSimulateUpload(file ? file.name : undefined);
            }}
            className={cn(
              "rounded-2xl border-2 border-dashed p-8 text-center transition flex flex-col items-center justify-center bg-surface",
              isDragOver ? "border-primary bg-primary-50/20" : "border-line-strong hover:border-primary/60"
            )}
          >
            <div className="h-16 w-16 rounded-full bg-primary-50 text-primary grid place-items-center mb-4">
              <FileUp size={32} />
            </div>
            <h3 className="text-[16px] font-semibold text-ink">
              Drag &amp; drop satellite imagery or vector boundaries
            </h3>
            <p className="text-[12.5px] text-muted mt-1 max-w-[460px]">
              Supports Cloud Optimized GeoTIFF (COG), Multi-Band TIFF (10m–30m), GeoJSON, ESRI Shapefiles (.zip), and KML
            </p>

            <div className="mt-5 flex items-center gap-3">
              <label className="cursor-pointer inline-flex items-center gap-2 h-10 px-5 rounded-lg bg-primary text-white text-[13px] font-semibold hover:bg-primary-hover shadow-sm transition">
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) handleSimulateUpload(f.name);
                  }}
                />
                Browse Local Files
              </label>

              <button
                type="button"
                onClick={() => handleSimulateUpload("S2A_L2A_Ladakh_Batch_202610.tif")}
                disabled={isUploading}
                className="inline-flex items-center gap-2 h-10 px-4 rounded-lg border border-line bg-canvas/60 text-[12.5px] font-medium text-ink hover:bg-canvas transition"
              >
                <Plus size={15} /> Add Sample Sentinel-2 Scene
              </button>
            </div>

            <div className="mt-4 flex items-center gap-6 text-[11px] text-muted">
              <span>● Max Single File: 4 GB</span>
              <span>● CRS: EPSG:4326 / WGS84</span>
              <span>● Zero-Trust Encrypted Ingestion</span>
            </div>
          </div>

          {/* Staged Files List */}
          <Card className="p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[16px] font-semibold text-ink flex items-center gap-2">
                <Layers size={18} className="text-primary" />
                Staged Ingestion Files ({files.length})
              </h3>
              <span className="text-[11.5px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Ready for Pipeline
              </span>
            </div>

            <div className="space-y-3">
              {files.map((file) => (
                <div
                  key={file.name}
                  className="p-4 rounded-xl border border-line bg-canvas/30 hover:bg-canvas/60 transition flex flex-col md:flex-row md:items-center justify-between gap-3"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[14px] font-semibold text-ink truncate">{file.name}</span>
                      <span className="rounded bg-primary-50 text-primary px-2 py-0.5 text-[10px] font-bold shrink-0">
                        {file.gsd}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 mt-1.5 text-[11.5px] text-muted">
                      <span>Size: {file.size}</span>
                      <span>•</span>
                      <span>Format: {file.type}</span>
                      <span>•</span>
                      <span>Acquired: {file.date}</span>
                      <span>•</span>
                      <span className="text-teal font-medium">Cloud Cover: {file.cloudCover}</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {file.bands.map((b) => (
                        <span
                          key={b}
                          className="px-2 py-0.5 rounded text-[10px] font-medium bg-white border border-line text-slate-700"
                        >
                          {b}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                    <button
                      onClick={() => handleRemove(file.name)}
                      className="p-2 text-muted hover:text-danger rounded-lg transition"
                      title="Remove file"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}

              {files.length === 0 && (
                <div className="py-12 text-center text-muted text-[13px]">
                  No files currently staged. Upload a GeoTIFF or select a sample scene above.
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right Column: Mission Parameters */}
        <div className="space-y-5">
          <Card className="p-5">
            <h3 className="text-[16px] font-semibold text-ink mb-4">Ingestion Target Parameters</h3>

            <div className="space-y-4">
              <div>
                <label className="text-[12px] font-medium text-ink block mb-1">Target Mission Project</label>
                <select
                  value={project}
                  onChange={(e) => setProject(e.target.value)}
                  className="w-full h-10 rounded-lg border border-line bg-surface px-3 text-[13px] outline-none focus:border-primary"
                >
                  <option>Ladakh Border Infrastructure</option>
                  <option>Siachen Glacial Moraine</option>
                  <option>Thar Desert Surveillance</option>
                  <option>Arunachal Outposts</option>
                </select>
              </div>

              <div>
                <label className="text-[12px] font-medium text-ink block mb-1">Satellite Constellation</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="w-full h-10 rounded-lg border border-line bg-surface px-3 text-[13px] outline-none focus:border-primary"
                >
                  <option value="sentinel-2">Sentinel-2 MSI (ESA Copernicus · 10m)</option>
                  <option value="landsat-9">Landsat-9 OLI-2 (NASA/USGS · 30m)</option>
                  <option value="planet">PlanetScope Dove (Planet Labs · 3m)</option>
                  <option value="bhuvan">Cartosat-3 / Bhuvan (ISRO · 0.28m)</option>
                </select>
              </div>

              <div>
                <label className="text-[12px] font-medium text-ink block mb-1">Auto-Calibration &amp; Preprocessing</label>
                <div className="space-y-2 text-[12px] text-ink-soft">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="accent-primary" />
                    <span>Atmospheric BOA Top-of-Canopy Reflectance Correction</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="accent-primary" />
                    <span>Auto Cloud &amp; Shadow Masking (SCL Band)</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input type="checkbox" defaultChecked className="accent-primary" />
                    <span>Bilinear 4-band Alignment to Sentinel Grid</span>
                  </label>
                </div>
              </div>

              <div className="pt-3 border-t border-line">
                <Button onClick={handleStageForJob} className="w-full justify-center">
                  <Send size={16} /> Proceed to Job Submission
                </Button>
              </div>
            </div>
          </Card>

          <Card className="p-5 bg-gradient-to-br from-surface to-canvas/30">
            <h4 className="text-[14px] font-semibold text-ink flex items-center gap-1.5 mb-2">
              <Sparkles size={16} className="text-primary" />
              Automated Super-Resolution Ready
            </h4>
            <p className="text-[12px] text-muted leading-relaxed">
              Once staged, imagery is tiled into 512×512 patches with 64-pixel overlap to avoid boundary artifacts.
              Neural inference scales Sentinel-2 10m bands B02, B03, B04, and B08 to 2.5m analysis-ready products.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
