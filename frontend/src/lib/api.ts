/**
 * Typed API client — the single integration seam.
 *
 * Every screen calls these functions; none call `fetch` directly. The base URL
 * is resolved once:
 *
 *   • NEXT_PUBLIC_API_BASE_URL set  → requests go to your FastAPI backend
 *   • unset                         → requests go to the built-in Next.js mock
 *                                     routes under /api/* (same shapes)
 *
 * So "integrating with FastAPI" is purely a matter of setting one env var and
 * making the backend return the shapes in src/lib/types.ts (see FASTAPI_CONTRACT.md).
 */
import type {
  ComparisonResponse,
  DashboardResponse,
  NewJobEstimate,
  NewJobPayload,
  ProjectsResponse,
  QueueResponse,
  SettingsResponse,
  ValidationResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";

/** Build a URL: absolute FastAPI path when BASE is set, else local /api route. */
function url(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return BASE ? `${BASE}/api${p}` : `/api${p}`;
}

async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const p = path.startsWith("/") ? path : `/${path}`;
  const targetUrl = url(p);

  const token = typeof window !== "undefined"
    ? (localStorage.getItem("bhudristi_token") || localStorage.getItem("ip-sakti-token"))
    : null;

  const reqHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) || {}),
  };
  if (token && !reqHeaders["Authorization"]) {
    reqHeaders["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(targetUrl, {
      cache: "no-store",
      ...init,
      headers: reqHeaders,
    });
    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("bhudristi_token");
        localStorage.removeItem("bhudristi_user");
        localStorage.removeItem("ip-sakti-token");
        localStorage.removeItem("ip-sakti-user");
        document.cookie = "bhudristi_session=; path=/; max-age=0; SameSite=Lax";
        document.cookie = "ip_sakti_session=; path=/; max-age=0; SameSite=Lax";
        window.dispatchEvent(new Event("bhudristi-auth-expired"));
      }
      if (BASE) {
        console.warn(`[भू DRISTI] Remote API ${targetUrl} returned HTTP ${res.status}. Falling back to built-in local API: /api${p}`);
        try {
          const localRes = await fetch(`/api${p}`, {
            cache: "no-store",
            headers: { "Content-Type": "application/json" },
            ...init,
          });
          if (localRes.ok) {
            return (await localRes.json()) as T;
          }
        } catch {
          // ignore fallback error and throw below
        }
      }
      throw new Error(`API ${res.status} ${res.statusText} for ${path}`);
    }
    return (await res.json()) as T;
  } catch (err) {
    if (BASE) {
      console.warn(`[भू DRISTI] Remote API ${targetUrl} unreachable (${err}). Falling back to built-in local API: /api${p}`);
      try {
        const localRes = await fetch(`/api${p}`, {
          cache: "no-store",
          headers: { "Content-Type": "application/json" },
          ...init,
        });
        if (localRes.ok) {
          return (await localRes.json()) as T;
        }
      } catch {
        // ignore fallback error and throw below
      }
    }
    throw err;
  }
}

export const api = {
  isRemote: Boolean(BASE),
  baseUrl: BASE || "(built-in mock routes)",

  getDashboard: () => get<DashboardResponse>("/dashboard"),

  getQueue: (params?: { page?: number; status?: string; project?: string; q?: string }) => {
    const s = new URLSearchParams();
    if (params?.page) s.set("page", String(params.page));
    if (params?.status && params.status !== "all") s.set("status", params.status);
    if (params?.project && params.project !== "all") s.set("project", params.project);
    if (params?.q) s.set("q", params.q);
    const qs = s.toString();
    return get<QueueResponse>(`/queue${qs ? `?${qs}` : ""}`);
  },

  getProjects: (params?: { category?: string; q?: string; sort?: string }) => {
    const s = new URLSearchParams();
    if (params?.category && params.category !== "All") s.set("category", params.category);
    if (params?.q) s.set("q", params.q);
    if (params?.sort) s.set("sort", params.sort);
    const qs = s.toString();
    return get<ProjectsResponse>(`/projects${qs ? `?${qs}` : ""}`);
  },

  getComparison: (jobId: string) => get<ComparisonResponse>(`/comparison/${encodeURIComponent(jobId)}`),

  getValidation: (jobId: string) => get<ValidationResponse>(`/validation/${encodeURIComponent(jobId)}`),

  getSettings: () => get<SettingsResponse>("/settings"),

  saveSettings: (body: Partial<SettingsResponse>) =>
    get<SettingsResponse>("/settings", { method: "PUT", body: JSON.stringify(body) }),

  estimateJob: (body: Partial<NewJobPayload> & { area_km2?: number }) =>
    get<NewJobEstimate>("/jobs/estimate", { method: "POST", body: JSON.stringify(body) }),

  submitJob: (body: NewJobPayload) =>
    get<{ job_id: string; status: string; submitted?: string }>("/jobs", { method: "POST", body: JSON.stringify(body) }),

  jobs: {
    simulateComplete: (jobId: string) =>
      get<{ status: string; job: any }>(`/jobs/${encodeURIComponent(jobId)}/simulate-complete`, { method: "POST" }),
    cancel: (jobId: string) =>
      get<{ status: string }>(`/jobs/${encodeURIComponent(jobId)}`, { method: "DELETE" }),
  },

  /** Downloadable report/document URLs (served as application/pdf) and SMTP email delivery. */
  reports: {
    validation: (jobId: string) => url(`/reports/validation/${encodeURIComponent(jobId)}`),
    comparison: (jobId: string) => url(`/reports/comparison/${encodeURIComponent(jobId)}`),
    job: (jobId: string) => url(`/reports/job/${encodeURIComponent(jobId)}`),
    invoice: (id: string, amount?: number, date?: string) => {
      const s = new URLSearchParams();
      if (amount != null) s.set("amount", String(amount));
      if (date) s.set("date", date);
      const qs = s.toString();
      return url(`/reports/invoice/${encodeURIComponent(id)}${qs ? `?${qs}` : ""}`);
    },
    email: (
      reportType: "validation" | "comparison" | "job" | "invoice",
      jobId: string,
      email?: string,
      extra?: { amount?: number; date?: string }
    ) =>
      get<{ status: string; message: string; filename?: string }>(
        `/reports/${reportType}/${encodeURIComponent(jobId)}/email`,
        {
          method: "POST",
          body: JSON.stringify({ email, ...extra }),
        }
      ),
  },

  /** Notifications service — live alerts, in-app feed, and SMTP channel testing. */
  notifications: {
    list: () => get<import("./types").NotificationItem[]>("/notifications"),
    markRead: (id: string) =>
      get<{ status: string }>(`/notifications/${encodeURIComponent(id)}/read`, { method: "POST" }),
    markAllRead: () =>
      get<{ status: string; message: string }>("/notifications/read-all", { method: "POST" }),
    dismiss: (id: string) =>
      get<{ status: string }>(`/notifications/${encodeURIComponent(id)}`, { method: "DELETE" }),
    sendTest: (email?: string, channel: string = "Email") =>
      get<{ status: string; message: string; timestamp?: string }>("/notifications/test", {
        method: "POST",
        body: JSON.stringify({ email, channel }),
      }),
    getSettings: () => get<import("./types").NotificationPreferences>("/notifications/settings"),
    saveSettings: (preferences: Partial<import("./types").NotificationPreferences>) =>
      get<{ status: string; preferences: any }>("/notifications/settings", {
        method: "PUT",
        body: JSON.stringify(preferences),
      }),
    getEmailCatalog: () =>
      get<{ total: number; smtp_server: string; types: any[] }>("/notifications/email/catalog"),
    sendEmailType: (email: string, type: string, extra?: any, provider: "auto" | "supabase" | "smtp" = "auto") =>
      get<{ status: string; type: string; recipient: string; provider: string }>(
        "/notifications/email/send-type",
        {
          method: "POST",
          body: JSON.stringify({ email, type, extra, provider }),
        }
      ),
    sendAllSampleEmails: (email?: string) =>
      get<{ status: string; recipient: string; total_dispatches: number }>(
        "/notifications/email/send-all-samples",
        {
          method: "POST",
          body: JSON.stringify({ email }),
        }
      ),
  },
};

