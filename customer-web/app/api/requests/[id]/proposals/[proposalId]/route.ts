import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string; proposalId: string } }
) {
  const body = await request.json();
  const userId = body.user_id;
  if (!userId) {
    return NextResponse.json({ detail: "user_id is required" }, { status: 400 });
  }

  const backendRes = await fetch(
    `${API_BASE_URL}/requests/${params.id}/proposals/${params.proposalId}/status`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": userId,
      },
      body: JSON.stringify({ status: body.status }),
      cache: "no-store",
    }
  );

  const data = await backendRes.json().catch(() => ({}));
  return NextResponse.json(data, { status: backendRes.status });
}
