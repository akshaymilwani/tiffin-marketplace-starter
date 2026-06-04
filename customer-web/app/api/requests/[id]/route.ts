import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const authorization = request.headers.get("authorization");
  if (!authorization) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const backendRes = await fetch(`${API_BASE_URL}/requests/${params.id}`, {
    headers: { Authorization: authorization },
    cache: "no-store",
  });

  const data = await backendRes.json().catch(() => ({}));
  return NextResponse.json(data, { status: backendRes.status });
}
