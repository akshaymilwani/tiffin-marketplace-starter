"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { clearCustomerSession, getCustomerSession } from "../lib/customerAuth";

const CART_KEY = "tiffin_cart";

function readCartCount() {
  const raw = window.localStorage.getItem(CART_KEY);
  if (!raw) return 0;

  try {
    const cart = JSON.parse(raw);
    return cart?.items?.reduce((sum: number, item: any) => sum + Number(item.quantity || 0), 0) || 0;
  } catch {
    return 0;
  }
}

export default function AppHeader() {
  const [cartCount, setCartCount] = useState(0);
  const [email, setEmail] = useState("");

  function refreshState() {
    setCartCount(readCartCount());
    setEmail(getCustomerSession()?.email || "");
  }

  useEffect(() => {
    refreshState();

    window.addEventListener("storage", refreshState);
    window.addEventListener("cart-updated", refreshState);
    window.addEventListener("customer-session-updated", refreshState);

    return () => {
      window.removeEventListener("storage", refreshState);
      window.removeEventListener("cart-updated", refreshState);
      window.removeEventListener("customer-session-updated", refreshState);
    };
  }, []);

  return (
    <div className="header">
      <Link href="/">
        <strong>Tiffin Marketplace</strong>
      </Link>
      <nav className="nav">
        {email ? (
          <button
            className="link-button"
            type="button"
            onClick={() => {
              clearCustomerSession();
              setEmail("");
            }}
          >
            Logout
          </button>
        ) : (
          <Link href="/login">Login</Link>
        )}
        <Link href="/kitchens">Kitchens</Link>
        <Link href="/orders">Orders</Link>
        <Link href="/requests">Requests</Link>
        {email && (
          <Link href="/cart" className="cart-button" aria-label={`Cart with ${cartCount} items`}>
            Cart{cartCount > 0 ? ` (${cartCount})` : ""}
          </Link>
        )}
      </nav>
    </div>
  );
}
