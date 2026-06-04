import { apiGet } from "../../lib/api";
import KitchenSearch from "../../components/KitchenSearch";

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

      {kitchens.length === 0 ? (
        <div className="grid grid-3">
          <div className="card">No public kitchens yet.</div>
        </div>
      ) : (
        <KitchenSearch kitchens={kitchens} />
      )}
    </div>
  );
}
