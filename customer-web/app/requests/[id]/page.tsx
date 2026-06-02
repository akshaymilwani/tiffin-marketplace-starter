"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCustomerSession } from "../../../lib/customerAuth";

type Proposal = {
  id: string;
  quote_amount: number;
  eta_notes?: string;
  message?: string;
  status: string;
  created_at: string;
};

type RequestDetail = {
  request: {
    id: string;
    title: string;
    description?: string;
    cuisine_tag: string;
    quantity: number;
    target_date: string;
    budget_min: number;
    budget_max: number;
    location_text: string;
    dietary_notes?: string;
    status: string;
  };
  proposals: Proposal[];
};

export default function RequestDetailPage({ params }: { params: { id: string } }) {
  const [userId, setUserId] = useState("");
  const [detail, setDetail] = useState<RequestDetail | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadDetail(resolvedUserId: string) {
    try {
      const res = await fetch(`/api/requests/${params.id}?user_id=${encodeURIComponent(resolvedUserId)}`, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to load request");
      setDetail(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load request.");
    } finally {
      setLoaded(true);
    }
  }

  useEffect(() => {
    const session = getCustomerSession();
    setUserId(session?.user_id || "");
    if (!session?.user_id) {
      setLoaded(true);
      return;
    }
    loadDetail(session.user_id);
  }, [params.id]);

  async function updateProposal(proposalId: string, status: "accepted" | "rejected") {
    setError("");
    setMessage("");
    try {
      const res = await fetch(`/api/requests/${params.id}/proposals/${proposalId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, status }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Failed to update proposal");
      setMessage(status === "accepted" ? "Proposal accepted." : "Proposal rejected.");
      window.setTimeout(() => setMessage(""), 2500);
      await loadDetail(userId);
    } catch (err: any) {
      setError(err?.message || "Failed to update proposal.");
    }
  }

  if (!loaded) return <div className="card">Loading request...</div>;

  if (!userId) {
    return (
      <div className="card">
        <h1>Request detail</h1>
        <p>Please log in to view merchant quotes.</p>
        <Link href="/login" className="button">Login or create account</Link>
      </div>
    );
  }

  if (!detail) {
    return <div className="card">{error || "Request not found."}</div>;
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      {message && <div className="toast" role="status">{message}</div>}
      <Link href="/requests">Back to requests</Link>
      {error && <div className="card" style={{ color: "red" }}>{error}</div>}

      <div className="card">
        <h1>{detail.request.title}</h1>
        <p className="muted">{detail.request.cuisine_tag} / needed by {detail.request.target_date}</p>
        <p>Status: <strong>{detail.request.status}</strong></p>
        <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{detail.request.description}</pre>
        {detail.request.dietary_notes && <p>Dietary notes: {detail.request.dietary_notes}</p>}
        <p>Budget: ${Number(detail.request.budget_min).toFixed(2)} - ${Number(detail.request.budget_max).toFixed(2)}</p>
        <p>Location: {detail.request.location_text}</p>
      </div>

      <section>
        <h2>Merchant quotes</h2>
        {detail.proposals.length === 0 ? (
          <div className="card">No merchant quotes yet.</div>
        ) : (
          <div className="grid" style={{ gap: 12 }}>
            {detail.proposals.map((proposal) => (
              <div className="card" key={proposal.id}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
                  <div>
                    <h3>${Number(proposal.quote_amount).toFixed(2)}</h3>
                    <p className="muted">Status: {proposal.status}</p>
                  </div>
                  {proposal.status === "submitted" && detail.request.status !== "accepted" && (
                    <div style={{ display: "flex", gap: 8 }}>
                      <button className="button" type="button" onClick={() => updateProposal(proposal.id, "accepted")}>Accept</button>
                      <button type="button" onClick={() => updateProposal(proposal.id, "rejected")}>Reject</button>
                    </div>
                  )}
                </div>
                {proposal.eta_notes && <p>ETA: {proposal.eta_notes}</p>}
                {proposal.message && <p>{proposal.message}</p>}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
