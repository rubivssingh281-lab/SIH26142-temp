import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const email = (body.email || "analyst@bhudristi.gov.in").toLowerCase();
  const name = body.name || email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase());

  return NextResponse.json({
    access_token: `bhudristi_google_jwt_${Date.now()}`,
    token_type: "bearer",
    token: `bhudristi_google_jwt_${Date.now()}`,
    message: "Signed in with Google successfully",
    user: {
      id: "usr_google_" + Date.now(),
      email: email,
      name: name,
      photoURL: body.photoURL || body.avatar_url || "",
      avatar_url: body.photoURL || body.avatar_url || "",
      role: "Lead Analyst",
      organization: "National Geospatial Operations",
      department: "Space Technology & Remote Sensing",
      phone: body.phone && body.phone !== "+91 98765 43210" ? body.phone : "",
      employee_id: "GEO-2026",
      clearance_level: "Level 3 - Confidential",
      region: "New Delhi, India",
      is_verified: true,
      is_active: true,
    },
  });
}
