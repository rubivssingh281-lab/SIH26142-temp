import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const email = (body.email || "analyst@ntro.gov.in").toLowerCase();

  return NextResponse.json({
    access_token: `bhudristi_jwt_${Date.now()}`,
    token_type: "bearer",
    token: `bhudristi_jwt_${Date.now()}`,
    message: "Signed in successfully",
    user: {
      id: "usr_fallback_1",
      email: email,
      name: email.split("@")[0].replace(".", " ").replace(/\b\w/g, (c: string) => c.toUpperCase()),
      role: "Analyst",
      organization: "NTRO — Imagery Analysis",
      is_verified: true,
      is_active: true,
    },

  });
}
