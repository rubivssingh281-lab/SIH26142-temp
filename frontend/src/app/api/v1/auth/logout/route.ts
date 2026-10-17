import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const response = NextResponse.json({
    status: "ok",
    message: "Logged out successfully",
  });

  const cookieOptions = {
    path: "/",
    expires: new Date(0),
    maxAge: 0,
    httpOnly: false,
    sameSite: "lax" as const,
  };

  response.cookies.set("bhudristi_session", "", cookieOptions);
  response.cookies.set("ip_sakti_session", "", cookieOptions);

  return response;
}

export async function GET(request: NextRequest) {
  const loginUrl = new URL("/login?logout=true", request.url);
  const response = NextResponse.redirect(loginUrl);

  const cookieOptions = {
    path: "/",
    expires: new Date(0),
    maxAge: 0,
    httpOnly: false,
    sameSite: "lax" as const,
  };

  response.cookies.set("bhudristi_session", "", cookieOptions);
  response.cookies.set("ip_sakti_session", "", cookieOptions);

  return response;
}
