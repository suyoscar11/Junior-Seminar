"use client";

import { useCallback, useEffect, useState } from "react";
import { AuthGate } from "@/components/AuthGate";
import { Dashboard } from "@/components/Dashboard";

export default function Home() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  useEffect(() => setAuthenticated(Boolean(localStorage.getItem("omnipost_token"))), []);
  const logout = useCallback(() => setAuthenticated(false), []);
  if (authenticated === null) return <main className="loading">Loading OmniPost...</main>;
  return authenticated ? <Dashboard onLogout={logout} /> : <AuthGate onAuthenticated={() => setAuthenticated(true)} />;
}

