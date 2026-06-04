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

  try {
    const result = await apiGet(`/businesses/${params.slug}`);
    kitchen = result.business;
    menuItems = Array.isArray(result.menu) ? result.menu : [];
  } catch {
    kitchen = null;
  }

  if (!kitchen) {
    return (
      <div className="grid" style={{ gap: 16 }}>
        <Link href="/kitchens">Back to kitchens</Link>
        <div className="card">Kitchen not found.</div>
      </div>
    );
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      <Link href="/kitchens">Back to kitchens</Link>

      <div className="card">
        <h1>{kitchen.business_name}</h1>
        <p className="muted">{kitchen.cuisine_type}</p>
        <p className="muted">
          {kitchen.city || "City not set"}
          {kitchen.province ? `, ${kitchen.province}` : ""}
        </p>
        <p className="muted">
          Rating: {Number(kitchen.avg_rating || 0).toFixed(1)} / 5 ({kitchen.total_reviews || 0} reviews)
        </p>
        <p>{kitchen.description}</p>
        <p className="muted">
          Verification: {kitchen.verification_status} | Listing: {kitchen.public_listing_status}
        </p>
      </div>

      <div className="card">
        <h2>Menu</h2>
        <MenuItemList kitchen={kitchen} menuItems={menuItems} />
      </div>
    </div>
  );
}
