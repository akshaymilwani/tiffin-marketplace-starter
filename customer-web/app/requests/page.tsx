import Link from "next/link";

export default function RequestsPage() {
  return <div className="card"><h1>My Requests</h1><p className="muted">Request board history.</p><Link href="/requests/new" className="button">Create request</Link></div>;
}
