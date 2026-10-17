import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const email = (body.email || "analyst@ntro.gov.in").toLowerCase();

  return NextResponse.json({
    access_token: `bhudristi_google_jwt_${Date.now()}`,
    token_type: "bearer",
    token: `bhudristi_google_jwt_${Date.now()}`,
    message: "Signed in with Google successfully",
    user: {
      id: "usr_google_fallback",
      email: email,
      name: body.name || email.split("@")[0],
      role: "Analyst",
      organization: "NTRO — Imagery Analysis",
      is_verified: true,
      is_active: true,
    },
  });
}
