import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json({ status: "ok", message: "All notifications marked as read" });
}
