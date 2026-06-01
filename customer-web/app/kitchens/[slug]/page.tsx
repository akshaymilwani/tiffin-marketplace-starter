import Link from "next/link";
import { apiGet } from "../../../lib/api";
import MenuItemList from "../../../components/MenuItemList";

export default async function KitchenDetailPage({
  params,
}: {
  params: { slug: string };
}) {
  let kitchen: any = null;
  let menuItems: any[] = [];
  let errorMessage = "";

  try {
  const result = await apiGet(`/businesses/${params.slug}`);

  kitchen = result.business;
  menuItems = Array.isArray(result.menu) ? result.menu : [];
} catch (error: any) {
  errorMessage = error?.message || "Failed to load kitchen.";
}



  if (!kitchen) {
    return (
      <div className="grid" style={{ gap: 16 }}>
        <Link href="/kitchens">← Back to kitchens</Link>
        <div className="card">Kitchen not found.</div>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <Link href="/kitchens">← Back to kitchens</Link>

      <div className="card">
        <h1>{kitchen.business_name}</h1>
        <p className="muted">{kitchen.cuisine_type}</p>
        <p>{kitchen.description}</p>
        <p className="muted">
          Verification: {kitchen.verification_status} | Listing:{" "}
          {kitchen.public_listing_status}
        </p>
      </div>

      <div className="card">
        <h2>Menu</h2>
        <MenuItemList kitchen={kitchen} menuItems={menuItems} />
      </div>
    </div>
  );
}
