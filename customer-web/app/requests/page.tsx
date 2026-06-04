"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCustomerSession } from "../../lib/customerAuth";

type CustomRequest = {
  id: string;
  title: string;
  description?: string;
  cuisine_tag: string;
  quantity: number;
  target_date: string;
  budget_min: number;
  budget_max: number;
  location_text: string;
  status: string;
  created_at: string;
};

export default function RequestsPage() {
  const [requests, setRequests] = useState<CustomRequest[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    async function loadRequests() {
      const session = getCustomerSession();
      setEmail(session?.email || "");
      if (!session?.access_token) {
        setLoaded(true);
        return;
      }

      try {
        const res = await fetch("/api/requests", {
          headers: { Authorization: `Bearer ${session.access_token}` },
          cache: "no-store",
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data?.detail || "Failed to load requests");
        setRequests(Array.isArray(data) ? data : []);
      } catch (err: any) {
        setError(err?.message || "Failed to load requests.");
      } finally {
        setLoaded(true);
      }
    }

    loadRequests();
  }, []);

  if (!loaded) return <div className="card">Loading requests...</div>;

  if (!email) {
    return (
      <div className="card">
        <h1>Custom Requests</h1>
        <p>Please log in to create or view custom dish requests.</p>
        <Link href="/login" className="button">Login or create account</Link>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <h1>Custom Requests</h1>
          <p className="muted">Ask kitchens to quote dishes that are not listed on the menu.</p>
        </div>
        <Link href="/requests/new" className="button">Create request</Link>
      </div>

      {error && <div className="card" style={{ color: "red" }}>{error}</div>}

      {requests.length === 0 ? (
        <div className="card">No custom requests yet.</div>
      ) : (
        requests.map((request) => (
          <Link className="card" href={`/requests/${request.id}`} key={request.id}>
            <h3>{request.title}</h3>
            <p className="muted">{request.cuisine_tag} / {request.quantity} total items / needed by {request.target_date}</p>
            <p>Status: <strong>{request.status}</strong></p>
          </Link>
        ))
      )}
    </div>
  );
}
