import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string; proposalId: string } }
) {
  const body = await request.json();
  const authorization = request.headers.get("authorization");
  if (!authorization) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const backendRes = await fetch(
    `${API_BASE_URL}/requests/${params.id}/proposals/${params.proposalId}/status`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: authorization,
      },
      body: JSON.stringify({ status: body.status }),
      cache: "no-store",
    }
  );

  const data = await backendRes.json().catch(() => ({}));
  return NextResponse.json(data, { status: backendRes.status });
}
