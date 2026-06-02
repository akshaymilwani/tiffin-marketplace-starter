import "./globals.css";
import React from "react";
import AppHeader from "../components/AppHeader";

export const metadata = {
  title: "Tiffin Marketplace",
  description: "Preorder-first marketplace for local food businesses"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <AppHeader />
          {children}
        </div>
      </body>
    </html>
  );
}
