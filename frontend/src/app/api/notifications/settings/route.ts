import { NextResponse } from "next/server";

const DEFAULT_SETTINGS = {
  channels: { email: true, inApp: true, sms: false },
  jobAlerts: [
    { id: "job_completed", event: "Job completed successfully", email: true, inApp: true, sms: false },
    { id: "job_failed", event: "Job failed or timed out", email: true, inApp: true, sms: true },
    { id: "cloud_cover", event: "Cloud cover exceeds threshold", email: false, inApp: true, sms: false },
    { id: "validation_ready", event: "Validation metrics ready", email: true, inApp: true, sms: false },
  ],
  teamAlerts: [
    { id: "member_joined", event: "New analyst joined team", email: true, inApp: true, sms: false },
    { id: "quota_warning", event: "Monthly compute quota at 80%", email: true, inApp: true, sms: true },
  ],
  frequency: "Real-time",
  quietHours: true,
  quietStart: "10:00 PM",
  quietEnd: "07:00 AM",
};

export async function GET() {
  return NextResponse.json(DEFAULT_SETTINGS);
}

export async function PUT(req: Request) {
  const body = await req.json().catch(() => ({}));
  return NextResponse.json({ status: "ok", preferences: { ...DEFAULT_SETTINGS, ...body } });
}
