import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const authorization = request.headers.get("authorization");

    if (!authorization) {
      return NextResponse.json(
        { detail: "Authentication required" },
        { status: 401 }
      );
    }

    const payload = {
      business_id: body.business_id,
      service_date: body.service_date,
      slot_type: body.slot_type,
      fulfillment_mode: body.fulfillment_mode,
      customer_notes: body.customer_notes || "",
      items: body.items,
    };

    const backendRes = await fetch(`${API_BASE_URL}/orders`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: authorization,
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });

    const text = await backendRes.text();

    let data: any;
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { detail: text };
    }

    if (!backendRes.ok) {
      return NextResponse.json(data, { status: backendRes.status });
    }

    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || "Failed to create order" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const authorization = request.headers.get("authorization");

  if (!authorization) {
    return NextResponse.json(
      { detail: "Authentication required" },
      { status: 401 }
    );
  }

  const backendRes = await fetch(`${API_BASE_URL}/orders`, {
    method: "GET",
    headers: {
      Authorization: authorization,
    },
    cache: "no-store",
  });

  const text = await backendRes.text();

  let data: any;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text };
  }

  return NextResponse.json(data, { status: backendRes.status });
}
