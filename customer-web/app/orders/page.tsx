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

  useEffect(() => {
    async function loadOrders() {
      const session = getCustomerSession();
      setEmail(session?.email || "");

      if (!session?.user_id) {
        setLoaded(true);
        return;
      }

      try {
        const res = await fetch(`/api/orders?user_id=${encodeURIComponent(session.user_id)}`, { cache: "no-store" });
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
