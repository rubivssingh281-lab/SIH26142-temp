import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = [
  "/login",
  "/signup",
  "/auth/login",
  "/auth/register",
  "/auth/verify",
  "/auth/forgot-password",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublic = PUBLIC_PATHS.some((path) => pathname.startsWith(path));
  const token =
    request.cookies.get("bhudristi_session")?.value ||
    request.cookies.get("ip_sakti_session")?.value;

  // If user is already authenticated and visits public auth pages, redirect to dashboard
  if (isPublic) {
    if (
      token &&
      (pathname.startsWith("/login") ||
        pathname.startsWith("/signup") ||
        pathname.startsWith("/auth/login") ||
        pathname.startsWith("/auth/forgot-password"))
    ) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Protect internal workspace routes
  const isProtected =
    pathname.startsWith("/dashboard") ||
    pathname.startsWith("/queue") ||
    pathname.startsWith("/new-job") ||
    pathname.startsWith("/projects") ||
    pathname.startsWith("/cluster") ||
    pathname.startsWith("/comparison") ||
    pathname.startsWith("/validation") ||
    pathname.startsWith("/settings") ||
    pathname.startsWith("/upload") ||
    pathname.startsWith("/profile") ||
    pathname.startsWith("/cases");

  if (isProtected && !token) {
    const url = new URL("/login", request.url);
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/queue/:path*",
    "/new-job/:path*",
    "/projects/:path*",
    "/cluster/:path*",
    "/comparison/:path*",
    "/validation/:path*",
    "/settings/:path*",
    "/upload/:path*",
    "/profile/:path*",
    "/cases/:path*",
    "/login",
    "/signup",
    "/auth/:path*",
  ],
};
