import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://backend:8000/api/v1";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const userId = body.user_id;
    if (!userId) {
      return NextResponse.json(
        { detail: "user_id is required for starter ordering auth" },
        { status: 400 }
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
        "X-User-Id": userId,
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
