"use client";

import { useMemo, useState } from "react";

type MenuItem = {
  id: string;
  name: string;
  description?: string;
  price: number;
  available_slots?: string[];
};

type OrderFormProps = {
  businessId: string;
  menuItems: MenuItem[];
};

function tomorrowDateString() {
  const date = new Date();
  date.setDate(date.getDate() + 1);
  return date.toISOString().slice(0, 10);
}

export default function OrderForm({ businessId, menuItems }: OrderFormProps) {
  const [userId, setUserId] = useState("");
  const [serviceDate, setServiceDate] = useState(tomorrowDateString());
  const [slotType, setSlotType] = useState("lunch");
  const [fulfillmentMode, setFulfillmentMode] = useState("pickup");
  const [customerNotes, setCustomerNotes] = useState("");
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const selectedItems = useMemo(() => {
    return menuItems
      .map((item) => ({
        menu_item_id: item.id,
        quantity: quantities[item.id] || 0,
        item,
      }))
      .filter((entry) => entry.quantity > 0);
  }, [menuItems, quantities]);

  const subtotal = selectedItems.reduce(
    (sum, entry) => sum + Number(entry.item.price || 0) * entry.quantity,
    0
  );

  async function submitOrder() {
    setStatus("");
    setError("");

    if (!userId.trim()) {
      setError("Please enter a customer user_id. Create a customer in Swagger and paste its user_id here.");
      return;
    }

    if (selectedItems.length === 0) {
      setError("Please select at least one menu item.");
      return;
    }

    const payload = {
      user_id: userId.trim(),
      business_id: businessId,
      service_date: serviceDate,
      slot_type: slotType,
      fulfillment_mode: fulfillmentMode,
      customer_notes: customerNotes,
      items: selectedItems.map(({ menu_item_id, quantity }) => ({
        menu_item_id,
        quantity,
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

      setStatus(`Order created successfully. Order ID: ${data.id || data.order_id || "created"}`);
    } catch (err: any) {
      setError(err?.message || "Failed to create order.");
    }
  }

  return (
    <div className="card" style={{ marginTop: 24 }}>
      <h2>Place preorder</h2>

      <div className="grid" style={{ gap: 12 }}>
        <label>
          Customer User ID
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
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

        <h3>Menu</h3>

        {menuItems.length === 0 ? (
          <p>No menu items available yet.</p>
        ) : (
          menuItems.map((item) => (
            <div
              key={item.id}
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 100px",
                gap: 12,
                alignItems: "center",
                borderBottom: "1px solid #eee",
                paddingBottom: 8,
              }}
            >
              <div>
                <strong>{item.name}</strong>
                <div className="muted">{item.description}</div>
                <div>${Number(item.price).toFixed(2)}</div>
              </div>

              <input
                type="number"
                min={0}
                value={quantities[item.id] || 0}
                onChange={(e) =>
                  setQuantities({
                    ...quantities,
                    [item.id]: Number(e.target.value),
                  })
                }
              />
            </div>
          ))
        )}

        <label>
          Notes
          <textarea
            value={customerNotes}
            onChange={(e) => setCustomerNotes(e.target.value)}
            placeholder="Any pickup/delivery notes?"
            style={{ width: "100%" }}
          />
        </label>

        <div>
          <strong>Estimated subtotal:</strong> ${subtotal.toFixed(2)}
        </div>

        <button className="button" type="button" onClick={submitOrder}>
          Place preorder
        </button>

        {status && <div style={{ color: "green" }}>{status}</div>}
        {error && <div style={{ color: "red" }}>Error: {error}</div>}
      </div>
    </div>
  );
}
