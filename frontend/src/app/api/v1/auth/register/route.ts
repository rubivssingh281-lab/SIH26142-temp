import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  const email = (body.email || "analyst@ntro.gov.in").toLowerCase();

  return NextResponse.json({
    message: "Verification code sent to your email.",
    requires_otp: true,
    email: email,
  });
}
