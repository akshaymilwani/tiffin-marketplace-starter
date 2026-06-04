"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { getCustomerSession } from "../../lib/customerAuth";

type OrderItem = {
  name: string;
  quantity: number;
  line_total: number;
};

type Order = {
  id: string;
  order_number: string;
  business_id: string;
  status: string;
  service_date: string;
  slot_type: string;
  fulfillment_mode: string;
  total_amount: number;
  created_at: string;
  merchant_notes?: string;
  items: OrderItem[];
};

const PAST_STATUSES = new Set(["fulfilled", "cancelled", "rejected"]);

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [reviewRating, setReviewRating] = useState<Record<string, number>>({});
  const [reviewText, setReviewText] = useState<Record<string, string>>({});
  const [reviewStatus, setReviewStatus] = useState<Record<string, string>>({});

  useEffect(() => {
    async function loadOrders() {
      const session = getCustomerSession();
      setEmail(session?.email || "");
      setAccessToken(session?.access_token || "");

      if (!session?.access_token) {
        setLoaded(true);
        return;
      }

      try {
        const res = await fetch("/api/orders", {
          headers: { Authorization: `Bearer ${session.access_token}` },
          cache: "no-store",
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data?.detail || "Failed to load orders");
        setOrders(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err?.message || "Failed to load orders.");
      } finally {
        setLoaded(true);
      }
    }

    loadOrders();
  }, []);

  const currentOrders = useMemo(() => orders.filter((order) => !PAST_STATUSES.has(order.status)), [orders]);
  const pastOrders = useMemo(() => orders.filter((order) => PAST_STATUSES.has(order.status)), [orders]);

  async function submitReview(order: Order) {
    const rating = Number(reviewRating[order.id] || 0);
    const text = reviewText[order.id] || "";

    if (!accessToken) {
      setReviewStatus((current) => ({ ...current, [order.id]: "Please log in before submitting a review." }));
      return;
    }
    if (rating < 1 || rating > 5) {
      setReviewStatus((current) => ({ ...current, [order.id]: "Choose a rating from 1 to 5." }));
      return;
    }

    try {
      const res = await fetch("/api/reviews", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify({
          preorder_id: order.id,
          rating,
          review_text: text,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to submit review");
      setReviewStatus((current) => ({ ...current, [order.id]: "Review saved." }));
    } catch (err: any) {
      setReviewStatus((current) => ({ ...current, [order.id]: err?.message || "Failed to submit review." }));
    }
  }

  function renderOrders(list: Order[]) {
    if (list.length === 0) return <div className="card">No orders found.</div>;

    return (
      <div className="grid" style={{ gap: 12 }}>
        {list.map((order) => (
          <div className="card" key={order.id}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
              <div>
                <h3>{order.order_number}</h3>
                <p className="muted">{order.service_date} / {order.slot_type} / {order.fulfillment_mode}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <strong>${Number(order.total_amount).toFixed(2)}</strong>
                <div className="status-pill">{order.status}</div>
              </div>
            </div>
            <ul>
              {order.items.map((item, index) => (
                <li key={`${order.id}_${index}`}>{item.quantity} x {item.name} - ${Number(item.line_total).toFixed(2)}</li>
              ))}
            </ul>
            {order.merchant_notes && <p className="muted">Merchant notes: {order.merchant_notes}</p>}
            {order.status === "fulfilled" && (
              <div className="review-form">
                <label>
                  Rating
                  <select
                    value={reviewRating[order.id] || ""}
                    onChange={(event) =>
                      setReviewRating((current) => ({ ...current, [order.id]: Number(event.target.value) }))
                    }
                    style={{ width: "100%" }}
                  >
                    <option value="">Select</option>
                    <option value="5">5 stars</option>
                    <option value="4">4 stars</option>
                    <option value="3">3 stars</option>
                    <option value="2">2 stars</option>
                    <option value="1">1 star</option>
                  </select>
                </label>
                <label>
                  Review
                  <textarea
                    value={reviewText[order.id] || ""}
                    onChange={(event) => setReviewText((current) => ({ ...current, [order.id]: event.target.value }))}
                    placeholder="Share your experience"
                    rows={2}
                    style={{ width: "100%" }}
                  />
                </label>
                <button className="button" type="button" onClick={() => submitReview(order)}>
                  Submit review
                </button>
                {reviewStatus[order.id] && <div className="muted">{reviewStatus[order.id]}</div>}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  if (!loaded) return <div className="card">Loading orders...</div>;

  if (!email) {
    return (
      <div className="card">
        <h1>My Orders</h1>
        <p>Please log in to view current and past orders.</p>
        <Link href="/login" className="button">Login or create account</Link>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <h1>My Orders</h1>
      <p className="muted">Showing orders for {email}</p>
      {error && <div className="card" style={{ color: "red" }}>{error}</div>}

      <section>
        <h2>Current orders</h2>
        {renderOrders(currentOrders)}
      </section>

      <section>
        <h2>Past orders</h2>
        {renderOrders(pastOrders)}
      </section>
    </div>
  );
}
