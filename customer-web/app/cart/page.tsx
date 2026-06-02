"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { getCustomerSession } from "../../lib/customerAuth";

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

function updateStoredCart(cart: Cart | null) {
  if (cart) {
    window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
  } else {
    window.localStorage.removeItem(CART_KEY);
  }
  window.dispatchEvent(new Event("cart-updated"));
}

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [customerEmail, setCustomerEmail] = useState("");
  const [customerUserId, setCustomerUserId] = useState("");
  const [serviceDate, setServiceDate] = useState(tomorrowDateString());
  const [slotType, setSlotType] = useState("lunch");
  const [fulfillmentMode, setFulfillmentMode] = useState("pickup");
  const [customerNotes, setCustomerNotes] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getCustomerSession();
    setCustomerEmail(session?.email || "");
    setCustomerUserId(session?.user_id || "");

    const raw = window.localStorage.getItem(CART_KEY);
    if (!raw) {
      setLoaded(true);
      return;
    }

    try {
      setCart(JSON.parse(raw));
    } catch {
      updateStoredCart(null);
    }
    setLoaded(true);
  }, []);

  const subtotal = useMemo(() => {
    return cart?.items.reduce((sum, item) => sum + Number(item.unit_price || 0) * item.quantity, 0) || 0;
  }, [cart]);

  function updateQuantity(menuItemId: string, quantity: number) {
    if (!cart || !Number.isFinite(quantity) || quantity < 1) return;

    const updatedCart = {
      ...cart,
      items: cart.items.map((item) => (item.menu_item_id === menuItemId ? { ...item, quantity } : item)),
    };

    setCart(updatedCart);
    updateStoredCart(updatedCart);
  }

  function removeItem(menuItemId: string) {
    if (!cart) return;

    const updatedItems = cart.items.filter((item) => item.menu_item_id !== menuItemId);
    if (updatedItems.length === 0) {
      setCart(null);
      updateStoredCart(null);
      return;
    }

    const updatedCart = { ...cart, items: updatedItems };
    setCart(updatedCart);
    updateStoredCart(updatedCart);
  }

  function clearCart() {
    setCart(null);
    updateStoredCart(null);
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

    if (!customerUserId) {
      setError("Please log in or create a customer account before placing an order.");
      return;
    }

    const payload = {
      user_id: customerUserId,
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || JSON.stringify(data));

      setCart(null);
      updateStoredCart(null);
      setStatus(`Order created successfully. Order ID: ${data.id || data.order_id || "created"}`);
    } catch (err: any) {
      setError(err?.message || "Failed to create order.");
    }
  }

  if (!loaded) {
    return <div className="card">Loading cart...</div>;
  }

  if (!customerUserId) {
    return (
      <div className="card">
        <h1>Your cart</h1>
        <p>Please log in to view or use your cart.</p>
        <Link href="/login" className="button">Login or create account</Link>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="grid" style={{ gap: 16 }}>
        <h1>Your cart</h1>
        {status && <div className="card" style={{ color: "green" }}>{status}</div>}
        <div className="card">Your cart is empty.</div>
        <Link href="/kitchens" className="button">Browse kitchens</Link>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <h1>Your cart</h1>

      <div className="card">
        <h2>{cart.business_name}</h2>
        <p className="muted">Ordering from one kitchen at a time for MVP.</p>
        <Link href={`/kitchens/${cart.business_slug}`}>Back to this kitchen</Link>
      </div>

      <div className="card">
        <h2>Items</h2>
        {cart.items.map((item) => (
          <div key={item.menu_item_id} className="cart-row">
            <div>
              <strong>{item.name}</strong>
              <div className="muted">${Number(item.unit_price).toFixed(2)} each</div>
            </div>
            <input
              type="number"
              min={1}
              value={item.quantity}
              onChange={(e) => updateQuantity(item.menu_item_id, Number(e.target.value))}
            />
            <strong>${(Number(item.unit_price) * item.quantity).toFixed(2)}</strong>
            <button type="button" onClick={() => removeItem(item.menu_item_id)}>Remove</button>
          </div>
        ))}
        <h3>Subtotal: ${subtotal.toFixed(2)}</h3>
        <button type="button" onClick={clearCart}>Clear cart</button>
      </div>

      <div className="card">
        <h2>Order details</h2>
        <div className="grid" style={{ gap: 12 }}>
          {customerUserId ? (
            <div className="card" style={{ background: "#f7fff9" }}>
              Ordering as <strong>{customerEmail}</strong>
            </div>
          ) : (
            <div className="card">
              <p>Please log in before placing your order.</p>
              <Link href="/login" className="button">Login or create account</Link>
            </div>
          )}

          <label>
            Service Date
            <input type="date" value={serviceDate} onChange={(e) => setServiceDate(e.target.value)} style={{ width: "100%" }} />
          </label>

          <label>
            Slot
            <select value={slotType} onChange={(e) => setSlotType(e.target.value)} style={{ width: "100%" }}>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
            </select>
          </label>

          <label>
            Fulfillment
            <select value={fulfillmentMode} onChange={(e) => setFulfillmentMode(e.target.value)} style={{ width: "100%" }}>
              <option value="pickup">Pickup</option>
              <option value="self_delivery">Merchant Self Delivery</option>
            </select>
          </label>

          <label>
            Notes
            <textarea value={customerNotes} onChange={(e) => setCustomerNotes(e.target.value)} placeholder="Any pickup/delivery notes?" style={{ width: "100%" }} />
          </label>

          <button className="button" type="button" onClick={placeOrder}>Place order</button>
          {status && <div style={{ color: "green" }}>{status}</div>}
          {error && <div style={{ color: "red" }}>Error: {error}</div>}
        </div>
      </div>
    </div>
  );
}
