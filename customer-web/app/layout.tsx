import "./globals.css";
import Link from "next/link";
import React from "react";

export const metadata = {
  title: "Tiffin Marketplace",
  description: "Preorder-first marketplace for local food businesses"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <div className="header">
            <Link href="/"><strong>Tiffin Marketplace</strong></Link>
            <div style={{ display: "flex", gap: 12 }}>
              <Link href="/kitchens">Kitchens</Link>
              <Link href="/requests">Requests</Link>
              <Link href="/orders">Orders</Link>
              <Link href="/login">Login</Link>
            </div>
          </div>
          {children}
        </div>
      </body>
    </html>
  );
}
