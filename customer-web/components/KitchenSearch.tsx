"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type Kitchen = {
  id: string;
  business_name: string;
  slug: string;
  cuisine_type: string;
  city?: string;
  province?: string;
  verification_status: string;
  avg_rating?: number | null;
  total_reviews?: number;
};

export default function KitchenSearch({ kitchens }: { kitchens: Kitchen[] }) {
  const [search, setSearch] = useState("");
  const [city, setCity] = useState("all");

  const cities = useMemo(
    () =>
      Array.from(new Set(kitchens.map((kitchen) => kitchen.city).filter(Boolean) as string[])).sort(),
    [kitchens]
  );

  const filteredKitchens = useMemo(() => {
    const query = search.trim().toLowerCase();
    return kitchens.filter((kitchen) => {
      const matchesSearch =
        !query ||
        kitchen.business_name.toLowerCase().includes(query) ||
        kitchen.cuisine_type.toLowerCase().includes(query);
      const matchesCity = city === "all" || kitchen.city === city;
      return matchesSearch && matchesCity;
    });
  }, [city, kitchens, search]);

  return (
    <div className="grid" style={{ gap: 16 }}>
      <div className="card kitchen-filters">
        <label>
          Search kitchens
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by kitchen or cuisine"
            style={{ width: "100%" }}
          />
        </label>
        <label>
          City
          <select value={city} onChange={(event) => setCity(event.target.value)} style={{ width: "100%" }}>
            <option value="all">All cities</option>
            {cities.map((cityName) => (
              <option value={cityName} key={cityName}>
                {cityName}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid grid-3">
        {filteredKitchens.length === 0 ? (
          <div className="card">No kitchens match your search.</div>
        ) : (
          filteredKitchens.map((kitchen) => (
            <div className="card" key={kitchen.id}>
              <h3>{kitchen.business_name}</h3>
              <p className="muted">{kitchen.cuisine_type}</p>
              <p className="muted">
                {kitchen.city || "City not set"}
                {kitchen.province ? `, ${kitchen.province}` : ""}
              </p>
              <p className="muted">
                Rating: {Number(kitchen.avg_rating || 0).toFixed(1)} / 5 ({kitchen.total_reviews || 0} reviews)
              </p>
              <p className="muted">Verification: {kitchen.verification_status}</p>
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
