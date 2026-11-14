"use client";

import { FormEvent, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

export function AuthGate({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [mode, setMode] = useState<"register" | "login">("register");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    const form = new FormData(event.currentTarget);
    try {
      const payload = Object.fromEntries(form.entries());
      const result = await api<{ token: string }>(`/api/auth/${mode}`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      localStorage.setItem("omnipost_token", result.token);
      onAuthenticated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not continue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-story">
        <div className="brand"><span><Sparkles size={20} /></span> OmniPost</div>
        <div>
          <p className="eyebrow">ONE UPLOAD. EVERY CHANNEL.</p>
          <h1>Turn one idea into platform-ready posts.</h1>
          <p className="hero-copy">Adapt captions, review every version, and publish on your schedule from one focused workspace.</p>
        </div>
        <div className="workflow-line"><b>Upload</b><i /><b>Adapt</b><i /><b>Schedule</b><i /><b>Track</b></div>
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <p className="eyebrow">CREATOR WORKSPACE</p>
          <h2>{mode === "register" ? "Create your account" : "Welcome back"}</h2>
          <p className="muted">Use local demo credentials. No social account access is required.</p>
          <form onSubmit={submit}>
            {mode === "register" && <label>Name<input name="name" placeholder="Your name" minLength={2} required /></label>}
            <label>Email<input name="email" type="email" placeholder="you@example.com" required /></label>
            <label>Password<input name="password" type="password" placeholder="At least 8 characters" minLength={8} required /></label>
            {error && <p className="form-error">{error}</p>}
            <button className="primary wide" disabled={loading}>{loading ? "Working..." : mode === "register" ? "Create workspace" : "Sign in"}<ArrowRight size={18} /></button>
          </form>
          <button className="text-button" onClick={() => setMode(mode === "register" ? "login" : "register")}>{mode === "register" ? "Already registered? Sign in" : "Need an account? Register"}</button>
        </div>
      </section>
    </main>
  );
}

