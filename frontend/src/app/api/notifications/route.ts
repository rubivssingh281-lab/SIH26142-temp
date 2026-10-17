import { NextResponse } from "next/server";

const MOCK_NOTIFICATIONS = [
  {
    id: "notif-1",
    type: "success",
    title: "Job SR_v2_20240521 Completed",
    message: "Super-resolution ×4 completed (2.5 m/pixel) for Ladakh Border Infrastructure.",
    time: "5m ago",
    read: false,
    href: "/comparison?job=SR_v2_20240520_1030",
    tag: "Processing",
  },
  {
    id: "notif-2",
    type: "info",
    title: "GPU Worker Cluster Allocation",
    message: "High-priority queue active. 4x A100 GPUs assigned to regional satellite batch.",
    time: "24m ago",
    read: false,
    href: "/queue",
    tag: "Compute",
  },
  {
    id: "notif-3",
    type: "warning",
    title: "Cloud Cover Threshold Alert",
    message: "Scene B02/B04 detected 18% cloud cover. Auto-masking applied successfully.",
    time: "1h ago",
    read: false,
    href: "/validation?job=SR_v2_20240520_1030",
    tag: "Preprocessing",
  },
  {
    id: "notif-4",
    type: "success",
    title: "Validation Report Ready",
    message: "Quality validation report exported (PSNR: 34.2 dB, SSIM: 0.892).",
    time: "3h ago",
    read: true,
    href: "/validation?job=SR_v2_20240520_1030",
    tag: "Reports",
  },
  {
    id: "notif-5",
    type: "alert",
    title: "Storage Usage Warning",
    message: "2.41 TB of 10.0 TB consumed. 48 satellite jobs currently archived.",
    time: "1d ago",
    read: true,
    href: "/settings",
    tag: "System",
  },
];

export async function GET() {
  return NextResponse.json(MOCK_NOTIFICATIONS);
}

export async function POST() {
  return NextResponse.json({ status: "ok", message: "Notifications updated" });
}

export async function DELETE() {
  return NextResponse.json({ status: "ok" });
}
