"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setCustomerSession } from "../../lib/customerAuth";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");

  async function submit() {
    setError("");
    setStatus("");

    const path = mode === "login" ? "/api/auth/login" : "/api/auth/signup";
    const payload = mode === "login" ? { email, password } : { full_name: fullName, email, password };

    if (!email || !password || (mode === "signup" && !fullName)) {
      setError("Please fill in all required fields.");
      return;
    }

    try {
      const res = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || "Authentication failed");

      setCustomerSession({
        user_id: data.user_id,
        email,
        role: data.role || "customer",
        access_token: data.access_token,
      });
      setStatus(mode === "login" ? "Logged in." : "Account created.");
      router.push("/kitchens");
    } catch (err: any) {
      setError(err?.message || "Authentication failed.");
    }
  }

  return (
    <div className="card auth-card">
      <h1>{mode === "login" ? "Customer login" : "Create customer account"}</h1>
      <p className="muted">Use your email and password. Your customer ID is created and stored automatically.</p>

      <div className="segmented">
        <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
        <button type="button" className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>Sign up</button>
      </div>

      <div className="grid" style={{ gap: 12 }}>
        {mode === "signup" && (
          <label>
            Full name
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} style={{ width: "100%" }} />
          </label>
        )}
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: "100%" }} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%" }} />
        </label>
        <button className="button" type="button" onClick={submit}>{mode === "login" ? "Login" : "Create account"}</button>
        {status && <div style={{ color: "green" }}>{status}</div>}
        {error && <div style={{ color: "red" }}>Error: {error}</div>}
      </div>
    </div>
  );
}
