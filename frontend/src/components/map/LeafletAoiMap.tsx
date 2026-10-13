"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import L from "leaflet";
import {
  Lock,
  Unlock,
  Crosshair,
  Layers,
  Square,
  Pentagon,
  RotateCcw,
  Navigation,
  Check,
  MapPin,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Ensure Leaflet default icons work in Next.js bundle
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

export interface AoiData {
  coordinates: [number, number][]; // [[lat, lng], ...]
  centroid: { lat: number; lng: number };
  formattedLocation: string; // "34.2345° N, 77.5612° E"
  areaKm2: number;
  isLocked: boolean;
  bounds?: [[number, number], [number, number]];
  regionName?: string;
}

export interface PresetLocation {
  id: string;
  name: string;
  lat: number;
  lng: number;
  zoom: number;
  defaultPolygon: [number, number][];
}

export const PRESET_REGIONS: PresetLocation[] = [
  {
    id: "ladakh",
    name: "Ladakh Ridge",
    lat: 34.2345,
    lng: 77.5612,
    zoom: 13,
    defaultPolygon: [
      [34.246, 77.545],
      [34.251, 77.575],
      [34.238, 77.592],
      [34.221, 77.578],
      [34.217, 77.548],
    ],
  },
  {
    id: "siachen",
    name: "Siachen Glacier",
    lat: 35.4211,
    lng: 77.1089,
    zoom: 12,
    defaultPolygon: [
      [35.45, 77.08],
      [35.445, 77.14],
      [35.395, 77.135],
      [35.4, 77.075],
    ],
  },
  {
    id: "arunachal",
    name: "Arunachal Tawang",
    lat: 27.5861,
    lng: 91.8594,
    zoom: 13,
    defaultPolygon: [
      [27.598, 91.842],
      [27.602, 91.875],
      [27.574, 91.88],
      [27.57, 91.848],
    ],
  },
  {
    id: "pangong",
    name: "Pangong Tso",
    lat: 33.7595,
    lng: 78.6674,
    zoom: 12,
    defaultPolygon: [
      [33.78, 78.63],
      [33.785, 78.71],
      [33.735, 78.705],
      [33.738, 78.625],
    ],
  },
  {
    id: "thar",
    name: "Thar Desert",
    lat: 27.0238,
    lng: 71.7533,
    zoom: 13,
    defaultPolygon: [
      [27.045, 71.73],
      [27.048, 71.775],
      [27.008, 71.78],
      [27.005, 71.735],
    ],
  },
];

export function formatCoordinateString(lat: number, lng: number): string {
  const latStr = `${Math.abs(lat).toFixed(4)}° ${lat >= 0 ? "N" : "S"}`;
  const lngStr = `${Math.abs(lng).toFixed(4)}° ${lng >= 0 ? "E" : "W"}`;
  return `${latStr}, ${lngStr}`;
}

export function calculatePolygonAreaKm2(coords: [number, number][]): number {
  if (coords.length < 3) return 0;
  const R = 6371; // Earth radius in km
  const avgLat = (coords.reduce((sum, c) => sum + c[0], 0) / coords.length) * (Math.PI / 180);
  const cosAvgLat = Math.cos(avgLat);

  const points = coords.map(([lat, lng]) => ({
    x: lng * (Math.PI / 180) * R * cosAvgLat,
    y: lat * (Math.PI / 180) * R,
  }));

  let area = 0;
  for (let i = 0; i < points.length; i++) {
    const j = (i + 1) % points.length;
    area += points[i].x * points[j].y;
    area -= points[j].x * points[i].y;
  }
  return Math.abs(area) / 2;
}

export function getCentroid(coords: [number, number][]): { lat: number; lng: number } {
  if (coords.length === 0) return { lat: 34.2345, lng: 77.5612 };
  const lat = coords.reduce((sum, c) => sum + c[0], 0) / coords.length;
  const lng = coords.reduce((sum, c) => sum + c[1], 0) / coords.length;
  return { lat, lng };
}

interface LeafletAoiMapProps {
  className?: string;
  onAoiChange?: (aoi: AoiData) => void;
  initialPreset?: string;
}

export function LeafletAoiMap({
  className,
  onAoiChange,
  initialPreset = "ladakh",
}: LeafletAoiMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const polygonLayerRef = useRef<L.Polygon | null>(null);
  const vertexMarkersRef = useRef<L.CircleMarker[]>([]);
  const baseLayersRef = useRef<{ [key: string]: L.TileLayer }>({});

  const [activePreset, setActivePreset] = useState(initialPreset);
  const [mapType, setMapType] = useState<"satellite" | "hybrid" | "street">("satellite");
  const [isLocked, setIsLocked] = useState(true);
  const [activeTool, setActiveTool] = useState<"lock-center" | "polygon" | "box">("lock-center");
  const [mouseCoord, setMouseCoord] = useState<string>("34.2345° N, 77.5612° E");
  const [customPoints, setCustomPoints] = useState<[number, number][]>([]);
  const [currentAoi, setCurrentAoi] = useState<AoiData>(() => {
    const p = PRESET_REGIONS.find((r) => r.id === initialPreset) || PRESET_REGIONS[0];
    const area = calculatePolygonAreaKm2(p.defaultPolygon);
    const centroid = getCentroid(p.defaultPolygon);
    return {
      coordinates: p.defaultPolygon,
      centroid,
      formattedLocation: formatCoordinateString(centroid.lat, centroid.lng),
      areaKm2: Number(area.toFixed(2)),
      isLocked: true,
      regionName: p.name,
    };
  });

  // Render or update locked polygon & markers on the Leaflet map
  const renderPolygonOnMap = useCallback((coords: [number, number][], locked: boolean) => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    // Remove existing layers
    if (polygonLayerRef.current) {
      polygonLayerRef.current.remove();
      polygonLayerRef.current = null;
    }
    vertexMarkersRef.current.forEach((m) => m.remove());
    vertexMarkersRef.current = [];

    if (coords.length < 3) return;

    // Draw styled GeoSR polygon
    const poly = L.polygon(coords, {
      color: "#D6532B", // Brand terracotta
      weight: locked ? 2.5 : 1.5,
      opacity: 0.95,
      fillColor: "#D6532B",
      fillOpacity: locked ? 0.32 : 0.18,
      dashArray: locked ? undefined : "4, 4",
    }).addTo(map);

    polygonLayerRef.current = poly;

    // Add glowing vertex nodes
    coords.forEach(([lat, lng]) => {
      const marker = L.circleMarker([lat, lng], {
        radius: locked ? 4.5 : 3.5,
        fillColor: "#ffffff",
        fillOpacity: 1,
        color: "#D6532B",
        weight: 2,
      }).addTo(map);
      vertexMarkersRef.current.push(marker);
    });
  }, []);

  // Update AOI and trigger callback
  const commitAoi = useCallback((coords: [number, number][], locked: boolean, regionName?: string) => {
    const area = calculatePolygonAreaKm2(coords);
    const centroid = getCentroid(coords);
    const formatted = formatCoordinateString(centroid.lat, centroid.lng);
    const data: AoiData = {
      coordinates: coords,
      centroid,
      formattedLocation: formatted,
      areaKm2: Number(area.toFixed(2)),
      isLocked: locked,
      regionName,
    };
    setCurrentAoi(data);
    setIsLocked(locked);
    renderPolygonOnMap(coords, locked);
    if (onAoiChange) {
      onAoiChange(data);
    }
  }, [onAoiChange, renderPolygonOnMap]);

  // Initialize Map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const preset = PRESET_REGIONS.find((p) => p.id === initialPreset) || PRESET_REGIONS[0];

    // Create Leaflet map instance
    const map = L.map(containerRef.current, {
      center: [preset.lat, preset.lng],
      zoom: preset.zoom,
      minZoom: 3,
      maxZoom: 18,
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: true,
      dragging: true,
      touchZoom: true,
      tapHold: false,
      bounceAtZoomLimits: false,
    });

    mapRef.current = map;

    // Isolate map from parent scroll containers
    const container = containerRef.current;
    L.DomEvent.disableScrollPropagation(container);
    L.DomEvent.disableClickPropagation(container);

    // Prevent mobile page viewport scrolling while moving / dragging map
    const handleTouchStart = (e: TouchEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest("button") || target?.closest("input") || target?.closest("select")) {
        return;
      }
      e.stopPropagation();
    };

    const handleTouchMove = (e: TouchEvent) => {
      const target = e.target as HTMLElement | null;
      if (target?.closest("button") || target?.closest("input") || target?.closest("select")) {
        return;
      }
      if (e.cancelable) {
        e.preventDefault();
      }
      e.stopPropagation();
    };

    const handleWheel = (e: WheelEvent) => {
      e.stopPropagation();
    };

    container.addEventListener("touchstart", handleTouchStart, { passive: true });
    container.addEventListener("touchmove", handleTouchMove, { passive: false });
    container.addEventListener("wheel", handleWheel, { passive: true });

    // Satellite layer (Esri World Imagery)
    const satLayer = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        maxZoom: 19,
        attribution: "Esri World Imagery",
      }
    );

    // Hybrid labels layer
    const labelLayer = L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      { maxZoom: 19 }
    );

    // Street layer (CartoDB Positron)
    const streetLayer = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
        attribution: "CartoDB Voyager",
      }
    );

    baseLayersRef.current = {
      satellite: satLayer,
      hybrid: L.layerGroup([satLayer, labelLayer]) as any,
      street: streetLayer,
    };

    satLayer.addTo(map);

    // Track mouse coordinates
    map.on("mousemove", (e) => {
      setMouseCoord(formatCoordinateString(e.latlng.lat, e.latlng.lng));
    });

    // Render initial polygon
    renderPolygonOnMap(preset.defaultPolygon, true);

    // Cleanup on unmount
    return () => {
      container.removeEventListener("touchstart", handleTouchStart);
      container.removeEventListener("touchmove", handleTouchMove);
      container.removeEventListener("wheel", handleWheel);
      map.remove();
      mapRef.current = null;
    };
  }, [initialPreset, renderPolygonOnMap]);

  // Handle map type switch
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;
    Object.values(baseLayersRef.current).forEach((l) => {
      if (map.hasLayer(l)) map.removeLayer(l);
    });

    const active = baseLayersRef.current[mapType];
    if (active) {
      active.addTo(map);
    }
  }, [mapType]);

  // Lock visible display center viewport as AOI
  const lockCurrentDisplay = useCallback(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;
    const bounds = map.getBounds();

    const north = bounds.getNorth();
    const south = bounds.getSouth();
    const east = bounds.getEast();
    const west = bounds.getWest();

    // Take the central 60% of the screen as the focused AOI bounding box
    const latSpan = north - south;
    const lngSpan = east - west;
    const padLat = latSpan * 0.2;
    const padLng = lngSpan * 0.2;

    const n = north - padLat;
    const s = south + padLat;
    const e = east - padLng;
    const w = west + padLng;

    const boxPolygon: [number, number][] = [
      [n, w],
      [n, e],
      [s, e],
      [s, w],
    ];

    commitAoi(boxPolygon, true, "Display Focused Area");
  }, [commitAoi]);

  // Select Preset Region
  const handleSelectPreset = (presetId: string) => {
    const p = PRESET_REGIONS.find((r) => r.id === presetId);
    if (!p || !mapRef.current) return;
    setActivePreset(presetId);
    mapRef.current.flyTo([p.lat, p.lng], p.zoom, { duration: 1.2 });
    commitAoi(p.defaultPolygon, true, p.name);
  };

  // Geolocate user position
  const handleGeolocate = () => {
    if (!navigator.geolocation || !mapRef.current) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        if (mapRef.current) {
          mapRef.current.flyTo([latitude, longitude], 14, { duration: 1.5 });
          // create a ~2x2km AOI around user
          const span = 0.012;
          const poly: [number, number][] = [
            [latitude + span, longitude - span],
            [latitude + span, longitude + span],
            [latitude - span, longitude + span],
            [latitude - span, longitude - span],
          ];
          commitAoi(poly, true, "Local Geolocation AOI");
        }
      },
      () => {
        // Fallback or permission denied
      }
    );
  };

  // Click on map to add vertices if in polygon drawing mode
  useEffect(() => {
    if (!mapRef.current) return;
    const map = mapRef.current;

    const handleMapClick = (e: L.LeafletMouseEvent) => {
      if (isLocked) return;
      if (activeTool === "polygon") {
        const newPt: [number, number] = [e.latlng.lat, e.latlng.lng];
        const next = [...customPoints, newPt];
        setCustomPoints(next);
        renderPolygonOnMap(next, false);
      }
    };

    map.on("click", handleMapClick);
    return () => {
      map.off("click", handleMapClick);
    };
  }, [isLocked, activeTool, customPoints, renderPolygonOnMap]);

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-line bg-[#1c221d] touch-none select-none aoi-map-viewport",
        className
      )}
    >
      {/* Real Leaflet Map Container */}
      <div
        ref={containerRef}
        className="absolute inset-0 h-full w-full z-0 cursor-grab active:cursor-grabbing touch-none select-none"
      />

      {/* Reticle guide when unlocked in lock-center mode */}
      {!isLocked && activeTool === "lock-center" && (
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center z-10">
          <div className="w-[60%] h-[60%] border-2 border-dashed border-primary/80 rounded-lg bg-primary/10 flex items-center justify-center relative">
            <Crosshair className="text-primary size-6 animate-pulse" />
            <span className="absolute bottom-2 text-[10px] font-semibold tracking-wider uppercase text-white bg-black/70 px-2 py-0.5 rounded shadow">
              AOI Target Frame
            </span>
          </div>
        </div>
      )}

      {/* Top Bar: Strategic Preset Pills (Horizontally scrollable for mobile) */}
      <div className="absolute top-2 left-2 right-2 z-20 flex items-center justify-between gap-1.5 pointer-events-none">
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar pointer-events-auto bg-surface/90 backdrop-blur-md p-1 rounded-lg border border-line-strong shadow-sm max-w-[calc(100%-80px)]">
          <span className="text-[10px] font-bold text-muted px-1.5 uppercase tracking-wider shrink-0 flex items-center gap-1">
            <MapPin size={11} className="text-primary" /> AOI:
          </span>
          {PRESET_REGIONS.map((preset) => {
            const active = activePreset === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleSelectPreset(preset.id)}
                className={cn(
                  "px-2 py-0.5 rounded text-[11px] font-medium whitespace-nowrap transition-all",
                  active
                    ? "bg-primary text-white shadow-xs"
                    : "text-ink-soft hover:bg-canvas hover:text-ink"
                )}
              >
                {preset.name}
              </button>
            );
          })}
        </div>

        {/* Right Tools: Map Layer & Geolocation */}
        <div className="flex items-center gap-1 pointer-events-auto bg-surface/90 backdrop-blur-md p-1 rounded-lg border border-line-strong shadow-sm shrink-0">
          <button
            type="button"
            title="Toggle Satellite / Hybrid / Street"
            onClick={() => {
              setMapType((curr) => (curr === "satellite" ? "hybrid" : curr === "hybrid" ? "street" : "satellite"));
            }}
            className="p-1 rounded hover:bg-canvas text-ink-soft hover:text-ink transition flex items-center gap-1 text-[11px] font-medium px-1.5"
          >
            <Layers size={13} className="text-teal" />
            <span className="hidden sm:inline capitalize">{mapType}</span>
          </button>
          <button
            type="button"
            title="Locate my position"
            onClick={handleGeolocate}
            className="p-1 rounded hover:bg-canvas text-ink-soft hover:text-ink transition"
          >
            <Navigation size={13} />
          </button>
        </div>
      </div>

      {/* Floating Bottom Left: Zoom and Draw Controls */}
      <div className="absolute bottom-10 left-2 z-20 flex flex-col gap-1 pointer-events-auto bg-surface/90 backdrop-blur-md p-1 rounded-lg border border-line-strong shadow-sm">
        <button
          type="button"
          onClick={() => mapRef.current?.zoomIn()}
          className="h-6 w-6 rounded hover:bg-canvas grid place-items-center text-ink text-xs font-bold"
          title="Zoom In"
        >
          +
        </button>
        <button
          type="button"
          onClick={() => mapRef.current?.zoomOut()}
          className="h-6 w-6 rounded hover:bg-canvas grid place-items-center text-ink text-xs font-bold"
          title="Zoom Out"
        >
          -
        </button>
        <div className="h-px bg-line my-0.5" />
        <button
          type="button"
          onClick={() => {
            if (isLocked) {
              setIsLocked(false);
              setActiveTool("lock-center");
            } else {
              lockCurrentDisplay();
            }
          }}
          className={cn(
            "h-6 w-6 rounded grid place-items-center transition",
            isLocked ? "text-primary hover:bg-canvas" : "bg-primary text-white"
          )}
          title={isLocked ? "Unlock to re-center AOI" : "Lock Center Viewport as AOI"}
        >
          {isLocked ? <Unlock size={12} /> : <Lock size={12} />}
        </button>
      </div>

      {/* Bottom Center / Right: Lock status badge & Primary Lock button */}
      <div className="absolute bottom-2 left-2 right-2 z-20 flex items-center justify-between gap-1 pointer-events-none">
        {/* Lock Status Badge */}
        <div className="flex items-center gap-1.5 bg-black/75 backdrop-blur-md px-2.5 py-1 rounded-lg text-white text-[11px] font-medium border border-white/10 pointer-events-auto shadow-md">
          {isLocked ? (
            <>
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
              <span className="font-semibold text-emerald-300">LOCKED</span>
              <span className="text-white/40">|</span>
              <span className="font-semibold">{currentAoi.areaKm2} km²</span>
              <span className="hidden sm:inline text-white/70 font-mono text-[10px]">
                ({currentAoi.formattedLocation})
              </span>
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping shrink-0" />
              <span className="text-amber-300 font-semibold">ADJUSTING</span>
              <span className="text-white/70 text-[10.5px]">Pan/Zoom to aim</span>
            </>
          )}
        </div>

        {/* Action Button: Lock Visible or Unlock */}
        <div className="pointer-events-auto flex items-center gap-1">
          {!isLocked ? (
            <button
              type="button"
              onClick={lockCurrentDisplay}
              className="inline-flex items-center gap-1 h-7 px-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-[11.5px] font-semibold shadow-md transition"
            >
              <Lock size={12} /> Lock Display AOI
            </button>
          ) : (
            <button
              type="button"
              onClick={() => {
                setIsLocked(false);
                setActiveTool("lock-center");
              }}
              className="inline-flex items-center gap-1 h-7 px-2.5 rounded-lg bg-surface/90 hover:bg-canvas text-ink text-[11.5px] font-medium border border-line-strong shadow-md transition"
            >
              <Unlock size={12} /> Re-center
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
