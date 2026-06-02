"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCustomerSession } from "../../../lib/customerAuth";

type RequestItem = {
  name: string;
  quantity: number;
};

function nextWeekDateString() {
  const date = new Date();
  date.setDate(date.getDate() + 7);
  return date.toISOString().slice(0, 10);
}

export default function NewRequestPage() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [items, setItems] = useState<RequestItem[]>([{ name: "", quantity: 1 }]);
  const [cuisineTag, setCuisineTag] = useState("Indian");
  const [targetDate, setTargetDate] = useState(nextWeekDateString());
  const [budgetMin, setBudgetMin] = useState(0);
  const [budgetMax, setBudgetMax] = useState(50);
  const [locationText, setLocationText] = useState("");
  const [dietaryNotes, setDietaryNotes] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setUserId(getCustomerSession()?.user_id || "");
  }, []);

  function updateItem(index: number, patch: Partial<RequestItem>) {
    setItems((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, ...patch } : item));
  }

  function removeItem(index: number) {
    setItems((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function submitRequest() {
    setError("");
    setMessage("");
    const cleanItems = items
      .map((item) => ({ name: item.name.trim(), quantity: Number(item.quantity || 0) }))
      .filter((item) => item.name && item.quantity > 0);

    if (!userId) {
      setError("Please log in before creating a request.");
      return;
    }
    if (cleanItems.length === 0) {
      setError("Add at least one requested item.");
      return;
    }
    if (!locationText.trim()) {
      setError("Enter a pickup or delivery location.");
      return;
    }

    const itemSummary = cleanItems.map((item) => `${item.quantity} x ${item.name}`).join("\n");
    const title = cleanItems.length === 1 ? cleanItems[0].name : `${cleanItems[0].name} + ${cleanItems.length - 1} more`;

    const payload = {
      title,
      description: `Requested items:\n${itemSummary}${notes ? `\n\nNotes:\n${notes}` : ""}`,
      cuisine_tag: cuisineTag,
      quantity: cleanItems.reduce((sum, item) => sum + item.quantity, 0),
      target_date: targetDate,
      budget_min: budgetMin,
      budget_max: budgetMax,
      location_text: locationText,
      dietary_notes: dietaryNotes,
    };

    try {
      const res = await fetch("/api/requests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, payload }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to create request");
      setMessage("Request submitted. Kitchens can now send quotes.");
      window.setTimeout(() => router.push("/requests"), 1200);
    } catch (err: any) {
      setError(err?.message || "Failed to create request.");
    }
  }

  if (!userId) {
    return (
      <div className="card">
        <h1>Create request</h1>
        <p>Please log in to request custom dishes.</p>
        <Link href="/login" className="button">Login or create account</Link>
      </div>
    );
  }

  return (
    <div className="card">
      {message && <div className="toast" role="status">{message}</div>}
      <h1>Create custom dish request</h1>
      <div className="grid" style={{ gap: 12 }}>
        <h2>Requested items</h2>
        {items.map((item, index) => (
          <div className="request-item-row" key={index}>
            <input value={item.name} onChange={(e) => updateItem(index, { name: e.target.value })} placeholder="Item name, e.g. Paneer biryani" />
            <input type="number" min={1} value={item.quantity} onChange={(e) => updateItem(index, { quantity: Number(e.target.value) })} />
            <button type="button" onClick={() => removeItem(index)} disabled={items.length === 1}>Remove</button>
          </div>
        ))}
        <button type="button" onClick={() => setItems((current) => [...current, { name: "", quantity: 1 }])}>Add another item</button>

        <label>
          Cuisine
          <input value={cuisineTag} onChange={(e) => setCuisineTag(e.target.value)} style={{ width: "100%" }} />
        </label>
        <label>
          Needed by
          <input type="date" value={targetDate} onChange={(e) => setTargetDate(e.target.value)} style={{ width: "100%" }} />
        </label>
        <div className="grid grid-3">
          <label>
            Budget min
            <input type="number" min={0} value={budgetMin} onChange={(e) => setBudgetMin(Number(e.target.value))} style={{ width: "100%" }} />
          </label>
          <label>
            Budget max
            <input type="number" min={0} value={budgetMax} onChange={(e) => setBudgetMax(Number(e.target.value))} style={{ width: "100%" }} />
          </label>
        </div>
        <label>
          Location
          <input value={locationText} onChange={(e) => setLocationText(e.target.value)} placeholder="Pickup/delivery area" style={{ width: "100%" }} />
        </label>
        <label>
          Dietary notes
          <input value={dietaryNotes} onChange={(e) => setDietaryNotes(e.target.value)} placeholder="Vegetarian, no nuts, spice level..." style={{ width: "100%" }} />
        </label>
        <label>
          Extra notes
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} style={{ width: "100%" }} />
        </label>
        <button className="button" type="button" onClick={submitRequest}>Submit request</button>
        {error && <div style={{ color: "red" }}>Error: {error}</div>}
      </div>
    </div>
  );
}
