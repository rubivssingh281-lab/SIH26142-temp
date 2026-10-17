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

function getEffectiveApiBase(): string {
  const envBase = (process.env.NEXT_PUBLIC_API_BASE_URL || "").replace(/\/$/, "");
  if (envBase.includes("bhudristi-backend.onrender.com") || (!envBase && typeof window !== "undefined" && window.location.hostname.includes("vercel.app"))) {
    return "https://sih26142-temp.onrender.com";
  }
  if (!envBase && typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")) {
    return "http://127.0.0.1:8000";
  }
  return envBase || (typeof window !== "undefined" && window.location.hostname.includes("vercel.app") ? "https://sih26142-temp.onrender.com" : "http://127.0.0.1:8000");
}


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

  const storageKeys = [
    "bhudristi_token",
    "bhudristi_user",
    "ip-sakti-token",
    "ip-sakti-user",
    "access_token",
    "token",
    "user",
    "bhudristi_google_pending",
  ];
  storageKeys.forEach((key) => {
    try {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    } catch {}
  });

  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  const cookieNames = ["bhudristi_session", "ip_sakti_session"];
  cookieNames.forEach((name) => {
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=Lax${secure}`;
    document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; max-age=0; SameSite=None; Secure`;
  });

  window.dispatchEvent(new Event("bhudristi-auth-expired"));
}

export async function logoutUser(redirectTo = "/login?logout=true") {
  if (typeof window === "undefined") return;

  clearBrowserSession();

  // Try to sign out of Firebase if initialized
  try {
    const { getAuth, signOut } = await import("firebase/auth").catch(() => ({} as any));
    if (getAuth && signOut) {
      const auth = getAuth();
      if (auth && auth.currentUser) {
        await signOut(auth).catch(() => {});
      }
    }
  } catch {}

  // Request server route to expire HTTP cookies
  try {
    await fetch("/api/v1/auth/logout", { method: "POST" }).catch(() => {});
  } catch {}

  // Force clean navigation to login with logout parameter
  window.location.replace(redirectTo);
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
  const apiBase = getEffectiveApiBase();
  const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${apiBase}${path}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      if (res.status === 401) {
        clearBrowserSession();
      }
      if (apiBase && typeof window !== "undefined") {
        try {
          const localRes = await fetch(path, { ...options, headers });
          if (localRes.ok) {
            return (await localRes.json()) as T;
          }
        } catch {
          // fallback failed, continue to throw below
        }
      }
      const errBody = await res.json().catch(() => ({}));
      const message = errBody.detail || errBody.message || `Request failed with status ${res.status}`;
      throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }

    return (await res.json()) as T;
  } catch (err) {
    if (apiBase && typeof window !== "undefined") {
      try {
        const localRes = await fetch(path, { ...options, headers });
        if (localRes.ok) {
          return (await localRes.json()) as T;
        }
      } catch {
        // fallback failed, continue to throw original error below
      }
    }
    throw err;
  }
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
