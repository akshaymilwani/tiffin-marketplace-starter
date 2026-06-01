import Link from "next/link";

export default function HomePage() {
  return (
    <div className="grid" style={{ gap: 24 }}>
      <section className="card" style={{ padding: 24 }}>
        <h1>Preorder-first marketplace for local tiffin and cloud kitchens</h1>
        <p className="muted">
          Discover verified kitchens, place scheduled lunch or dinner preorders, and post custom food requests for merchants to bid on.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
          <Link href="/kitchens" className="button">Browse kitchens</Link>
          <Link href="/requests/new" className="button" style={{ background: "#444" }}>Post a request</Link>
        </div>
      </section>

      <section className="grid grid-3">
        <div className="card"><h3>Verified merchants</h3><p className="muted">Seller verification and moderated listings.</p></div>
        <div className="card"><h3>Preorder slots</h3><p className="muted">Lunch and dinner ordering with capacity-aware availability.</p></div>
        <div className="card"><h3>Request board</h3><p className="muted">Post demand before supply fully exists.</p></div>
      </section>
    </div>
  );
}
