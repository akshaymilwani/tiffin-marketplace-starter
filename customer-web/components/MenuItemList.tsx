"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCustomerSession } from "../lib/customerAuth";

type Kitchen = {
  id: string;
  business_name: string;
  slug: string;
};

type MenuItem = {
  id: string;
  name: string;
  description?: string;
  price: number;
  cuisine_tag?: string;
  dietary_tags?: string[];
};

type CartItem = {
  menu_item_id: string;
  name: string;
  description?: string;
  unit_price: number;
  quantity: number;
};

type Cart = {
  business_id: string;
  business_name: string;
  business_slug: string;
  items: CartItem[];
};

const CART_KEY = "tiffin_cart";

function readCart(): Cart | null {
  if (typeof window === "undefined") return null;

  const raw = window.localStorage.getItem(CART_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function writeCart(cart: Cart) {
  window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
  window.dispatchEvent(new Event("cart-updated"));
}

export default function MenuItemList({
  kitchen,
  menuItems,
}: {
  kitchen: Kitchen;
  menuItems: MenuItem[];
}) {
  const [cartCount, setCartCount] = useState(0);
  const [message, setMessage] = useState("");
  const [quantities, setQuantities] = useState<Record<string, number>>({});

  useEffect(() => {
    const cart = readCart();
    const count = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
    setCartCount(count);
  }, []);

  function selectedQuantity(itemId: string) {
    return quantities[itemId] || 1;
  }

  function updateSelectedQuantity(itemId: string, quantity: number) {
    if (!Number.isFinite(quantity)) return;

    const nextQuantity = Math.min(99, Math.max(1, Math.floor(quantity)));
    setQuantities((current) => ({ ...current, [itemId]: nextQuantity }));
  }

  function addToCart(item: MenuItem) {
    setMessage("");
    const quantity = selectedQuantity(item.id);

    if (!getCustomerSession()?.access_token) {
      setMessage("Please log in before adding items to your cart.");
      window.setTimeout(() => setMessage(""), 3000);
      return;
    }

    const existingCart = readCart();

    if (existingCart && existingCart.business_id !== kitchen.id) {
      const confirmClear = window.confirm(
        "Your cart has items from another kitchen. Clear cart and add this item?"
      );

      if (!confirmClear) return;
    }

    const cart: Cart =
      existingCart && existingCart.business_id === kitchen.id
        ? existingCart
        : {
            business_id: kitchen.id,
            business_name: kitchen.business_name,
            business_slug: kitchen.slug,
            items: [],
          };

    const existingItem = cart.items.find((x) => x.menu_item_id === item.id);

    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      cart.items.push({
        menu_item_id: item.id,
        name: item.name,
        description: item.description,
        unit_price: Number(item.price || 0),
        quantity,
      });
    }

    writeCart(cart);

    const count = cart.items.reduce((sum, x) => sum + x.quantity, 0);
    setCartCount(count);
    setMessage(`${quantity} ${item.name} added to cart.`);
    window.setTimeout(() => setMessage(""), 2500);
  }

  if (!menuItems || menuItems.length === 0) {
    return <p className="muted">No menu items available yet.</p>;
  }

  return (
    <div className="grid" style={{ gap: 16 }}>
      {message && <div className="toast" role="status">{message}</div>}

      {cartCount > 0 && (
        <div>
          <Link href="/cart" className="button">
            Go to cart ({cartCount})
          </Link>
        </div>
      )}

      {menuItems.map((item) => (
        <div
          key={item.id}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr auto",
            gap: 16,
            alignItems: "center",
            borderBottom: "1px solid #eee",
            paddingBottom: 12,
          }}
        >
          <div>
            <h3 style={{ marginBottom: 4 }}>{item.name}</h3>
            {item.description && <p className="muted">{item.description}</p>}
            <p>
              <strong>${Number(item.price || 0).toFixed(2)}</strong>
            </p>
          </div>

          <div className="menu-actions">
            <div className="quantity-stepper" aria-label={`${item.name} quantity`}>
              <button
                type="button"
                aria-label={`Decrease ${item.name} quantity`}
                onClick={() => updateSelectedQuantity(item.id, selectedQuantity(item.id) - 1)}
              >
                -
              </button>
              <input
                aria-label={`${item.name} quantity`}
                min={1}
                max={99}
                type="number"
                value={selectedQuantity(item.id)}
                onChange={(event) => updateSelectedQuantity(item.id, Number(event.target.value))}
              />
              <button
                type="button"
                aria-label={`Increase ${item.name} quantity`}
                onClick={() => updateSelectedQuantity(item.id, selectedQuantity(item.id) + 1)}
              >
                +
              </button>
            </div>
            <button className="button" type="button" onClick={() => addToCart(item)}>
              Add to cart
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
