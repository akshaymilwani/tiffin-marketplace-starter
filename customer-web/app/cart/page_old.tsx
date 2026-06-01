"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type CartItem = {
  menu_item_id: string;
  name: string;
  description?: string;
  unit_price: number;
  quantity: number;
};

type Cart = {
  business_id: string;
  business_name: string;
  business_slug: string;
  items: CartItem[];
};

const CART_KEY = "tiffin_cart";

function tomorrowDateString() {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().slice(0, 10);
}

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [customerUserId, setCustomerUserId] = useState("");
  const [serviceDate, setServiceDate] = useState(tomorrowDateString());
  const [slotType, setSlotType] = useState("lunch");
  const [fulfillmentMode, setFulfillmentMode] = useState("pickup");
  const [customerNotes, setCustomerNotes] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const raw = window.localStorage.getItem(CART_KEY);
    if (!raw) return;

    try {
      setCart(JSON.parse(raw));
    } catch {
      window.localStorage.removeItem(CART_KEY);
    }
  }, []);

  const subtotal = useMemo(() => {
    return (
      cart?.items.reduce(
        (sum, item) => sum + Number(item.unit_price || 0) * item.quantity,
        0
      ) || 0
    );
  }, [cart]);

  function updateQuantity(menuItemId: string, quantity: number) {
    if (!cart) return;

    const updatedItems = cart.items
      .map((item) =>
        item.menu_item_id === menuItemId ? { ...item, quantity } : item
      )
      .filter((item) => item.quantity > 0);

    const updatedCart = { ...cart, items: updatedItems };

    setCart(updatedCart);

    if (updatedItems.length === 0) {
      window.localStorage.removeItem(CART_KEY);
    } else {
      window.localStorage.setItem(CART_KEY, JSON.stringify(updatedCart));
    }
  }

  function clearCart() {
    window.localStorage.removeItem(CART_KEY);
    setCart(null);
    setStatus("");
    setError("");
  }

  async function placeOrder() {
    setStatus("");
    setError("");

    if (!cart || cart.items.length === 0) {
      setError("Your cart is empty.");
      return;
    }

    if (!customerUserId.trim()) {
      setError("Please enter customer user_id. For now, create a customer in Swagger and paste the returned user_id here.");
      return;
    }

    const payload = {
      user_id: customerUserId.trim(),
      business_id: cart.business_id,
      service_date: serviceDate,
      slot_type: slotType,
      fulfillment_mode: fulfillmentMode,
      customer_notes: customerNotes,
      items: cart.items.map((item) => ({
        menu_item_id: item.menu_item_id,
        quantity: item.quantity,
      })),
    };

    try {
      const res = await fetch("/api/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.detail || JSON.stringify(data));
      }

      window.localStorage.removeItem(CART_KEY);
      setCart(null);
      setStatus(`Order created successfully. Order ID: ${data.id || data.order_id || "created"}`);
    } catch (err: any) {
      setError(err?.message || "Failed to create order.");
    }
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="grid" style={{ gap: 16 }}>
        <h1>Your cart</h1>
        {status && <div className="card" style={{ color: "green" }}>{status}</div>}
        <div className="card">Your cart is empty.</div>
        <Link href="/kitchens" className="button">
          Browse kitchens
        </Link>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <h1>Your cart</h1>

      <div className="card">
        <h2>{cart.business_name}</h2>
        <p className="muted">Ordering from one kitchen at a time for MVP.</p>
        <Link href={`/kitchens/${cart.business_slug}`}>← Add more items from this kitchen</Link>
      </div>

      <div className="card">
        <h2>Items</h2>

        {cart.items.map((item) => (
          <div
            key={item.menu_item_id}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 120px 100px",
              gap: 12,
              alignItems: "center",
              borderBottom: "1px solid #eee",
              padding: "8px 0",
            }}
          >
            <div>
              <strong>{item.name}</strong>
              <div className="muted">${Number(item.unit_price).toFixed(2)} each</div>
            </div>

            <input
              type="number"
              min={0}
              value={item.quantity}
              onChange={(e) =>
                updateQuantity(item.menu_item_id, Number(e.target.value))
              }
            />

            <strong>
              ${(Number(item.unit_price) * item.quantity).toFixed(2)}
            </strong>
          </div>
        ))}

        <h3>Subtotal: ${subtotal.toFixed(2)}</h3>

        <button type="button" onClick={clearCart}>
          Clear cart
        </button>
      </div>

      <div className="card">
        <h2>Order details</h2>

        <div className="grid" style={{ gap: 12 }}>
          <label>
            Customer User ID
            <input
              value={customerUserId}
              onChange={(e) => setCustomerUserId(e.target.value)}
              placeholder="Paste customer user_id from /auth/signup"
              style={{ width: "100%" }}
            />
          </label>

          <label>
            Service Date
            <input
              type="date"
              value={serviceDate}
              onChange={(e) => setServiceDate(e.target.value)}
              style={{ width: "100%" }}
            />
          </label>

          <label>
            Slot
            <select
              value={slotType}
              onChange={(e) => setSlotType(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
            </select>
          </label>

          <label>
            Fulfillment
            <select
              value={fulfillmentMode}
              onChange={(e) => setFulfillmentMode(e.target.value)}
              style={{ width: "100%" }}
            >
              <option value="pickup">Pickup</option>
              <option value="self_delivery">Merchant Self Delivery</option>
            </select>
          </label>

          <label>
            Notes
            <textarea
              value={customerNotes}
              onChange={(e) => setCustomerNotes(e.target.value)}
              placeholder="Any pickup/delivery notes?"
              style={{ width: "100%" }}
            />
          </label>

          <button className="button" type="button" onClick={placeOrder}>
            Place order
          </button>

          {status && <div style={{ color: "green" }}>{status}</div>}
          {error && <div style={{ color: "red" }}>Error: {error}</div>}
        </div>
      </div>
    </div>
  );
}
