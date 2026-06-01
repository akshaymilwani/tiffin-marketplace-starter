import Link from "next/link";
import { apiGet } from "../../lib/api";

export default async function KitchensPage() {
  let kitchens = [] as any[];
  let errorMessage = "";

  try {
    const result = await apiGet("/businesses");
    kitchens = Array.isArray(result) ? result : [];
  } catch (error: any) {
    errorMessage = error?.message || "Failed to load kitchens";
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <h1>Discover kitchens</h1>

      {errorMessage && (
        <div className="card" style={{ color: "red" }}>
          API Error: {errorMessage}
        </div>
      )}

      <div className="grid grid-3">
        {kitchens.length === 0 ? (
          <div className="card">No public kitchens yet.</div>
        ) : (
          kitchens.map((kitchen) => (
            <div className="card" key={kitchen.id}>
              <h3>{kitchen.business_name}</h3>
              <p className="muted">{kitchen.cuisine_type}</p>
              <p className="muted">
                Verification: {kitchen.verification_status}
              </p>
              <Link href={`/kitchens/${kitchen.slug}`} className="button">
                View kitchen
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}