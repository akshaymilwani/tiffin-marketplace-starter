"use client";

export type CustomerSession = {
  user_id: string;
  email: string;
  role: string;
  access_token?: string;
};

export const CUSTOMER_SESSION_KEY = "tiffin_customer_session";

export function getCustomerSession(): CustomerSession | null {
  if (typeof window === "undefined") return null;

  const raw = window.localStorage.getItem(CUSTOMER_SESSION_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    window.localStorage.removeItem(CUSTOMER_SESSION_KEY);
    return null;
  }
}

export function setCustomerSession(session: CustomerSession) {
  window.localStorage.setItem(CUSTOMER_SESSION_KEY, JSON.stringify(session));
  window.dispatchEvent(new Event("customer-session-updated"));
}

export function clearCustomerSession() {
  window.localStorage.removeItem(CUSTOMER_SESSION_KEY);
  window.dispatchEvent(new Event("customer-session-updated"));
}
