/**
 * Authentication client and session management for भू DRISTI.
 * Implements universal Supabase Auth + Google Firebase OAuth + Gmail SMTP OTP.
 */

export interface AuthUser {
  id: string | number;
  email: string;
  name?: string;
  first_name?: string;
  last_name?: string;
  role?: string;
  organization?: string;
  default_jurisdiction?: string;
  is_verified?: boolean;
  is_active?: boolean;
}

export interface AuthSessionResponse {
  access_token: string;
  token_type: string;
  token?: string;
  message?: string;
  user: AuthUser;
}

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

/**
 * Stores authentication token and session both in localStorage and in HTTP-accessible cookies
 * so Next.js Edge Middleware can verify the session on server-side requests.
 */
export function setBrowserSession(token: string, user?: AuthUser | null) {
  if (typeof window === "undefined") return;

  // Local storage for client-side API requests
  localStorage.setItem("bhudristi_token", token);
  localStorage.setItem("ip-sakti-token", token); // Guide compatibility alias
  if (user) {
    localStorage.setItem("bhudristi_user", JSON.stringify(user));
    localStorage.setItem("ip-sakti-user", JSON.stringify(user));
  }

  // Cookie for Next.js Edge Middleware route guards
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  const maxAge = 60 * 60 * 8; // 8 hours
  document.cookie = `bhudristi_session=${encodeURIComponent(token)}; path=/; max-age=${maxAge}; SameSite=Lax${secure}`;
  document.cookie = `ip_sakti_session=${encodeURIComponent(token)}; path=/; max-age=${maxAge}; SameSite=Lax${secure}`;
}

export function clearBrowserSession() {
  if (typeof window === "undefined") return;

  localStorage.removeItem("bhudristi_token");
  localStorage.removeItem("bhudristi_user");
  localStorage.removeItem("ip-sakti-token");
  localStorage.removeItem("ip-sakti-user");

  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `bhudristi_session=; path=/; max-age=0; SameSite=Lax${secure}`;
  document.cookie = `ip_sakti_session=; path=/; max-age=0; SameSite=Lax${secure}`;
  window.dispatchEvent(new Event("bhudristi-auth-expired"));
}

export function getBrowserSession(): { token: string | null; user: AuthUser | null } {
  if (typeof window === "undefined") return { token: null, user: null };

  const token = localStorage.getItem("bhudristi_token") || localStorage.getItem("ip-sakti-token");
  const userJson = localStorage.getItem("bhudristi_user") || localStorage.getItem("ip-sakti-user");
  let user: AuthUser | null = null;
  if (userJson) {
    try {
      user = JSON.parse(userJson);
    } catch {
      user = null;
    }
  }
  return { token, user };
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("bhudristi_token") || localStorage.getItem("ip-sakti-token");
}

async function authFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Construct target URL
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${API_BASE}${path}`;

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401) {
      clearBrowserSession();
    }
    const errBody = await res.json().catch(() => ({}));
    const message = errBody.detail || errBody.message || `Request failed with status ${res.status}`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return (await res.json()) as T;
}

export const authApi = {
  async register(data: { name?: string; email: string; password: string; organization?: string }) {
    return authFetch<{ message: string; requires_otp: boolean; email: string }>("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async login(email: string, password: string): Promise<AuthSessionResponse> {
    const res = await authFetch<AuthSessionResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (res.access_token || res.token) {
      setBrowserSession(res.access_token || res.token!, res.user);
    }
    return res;
  },

  async requestOtp(email: string) {
    return authFetch<{ message: string; email: string }>("/api/v1/auth/request-otp", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },

  async verifyOtp(email: string, otp: string): Promise<AuthSessionResponse> {
    const res = await authFetch<AuthSessionResponse>("/api/v1/auth/verify-otp", {
      method: "POST",
      body: JSON.stringify({ email, otp_code: otp.trim() }),
    });
    if (res.access_token || res.token) {
      setBrowserSession(res.access_token || res.token!, res.user);
    }
    return res;
  },

  async forgotPassword(email: string) {
    return authFetch<{ message: string }>("/api/v1/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(payload: { email: string; otp_code: string; new_password: string }): Promise<AuthSessionResponse> {
    const res = await authFetch<AuthSessionResponse>("/api/v1/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({
        email: payload.email,
        otp_code: payload.otp_code.trim(),
        new_password: payload.new_password,
      }),
    });
    if (res.access_token || res.token) {
      setBrowserSession(res.access_token || res.token!, res.user);
    }
    return res;
  },

  async googleLogin(payload: {
    email: string;
    first_name?: string;
    last_name?: string;
    name?: string;
    id_token?: string;
  }): Promise<AuthSessionResponse> {
    const res = await authFetch<AuthSessionResponse>("/api/v1/auth/google", {
      method: "POST",
      body: JSON.stringify({
        email: payload.email.trim().toLowerCase(),
        first_name: payload.first_name,
        last_name: payload.last_name,
        name: payload.name,
        id_token: payload.id_token,
      }),
    });
    if (res.access_token || res.token) {
      setBrowserSession(res.access_token || res.token!, res.user);
    }
    return res;
  },

  async me() {
    return authFetch<AuthUser & { is_authenticated: boolean }>("/api/v1/auth/me");
  },
};
