"use client";
import { useState } from "react";
import { API_URL } from "@/lib/api";
import { Badge, Button, Card, CardBody } from "@/components/ui/card";

export default function ProfilePage() {
  const [email, setEmail] = useState("demo@astrosynth.space");
  const [msg, setMsg] = useState("");
  async function login() {
    const r = await fetch(`${API_URL}/auth/login?email=${encodeURIComponent(email)}&password=demo1234`, { method: "POST" });
    const j = await r.json();
    if (j.token) { localStorage.setItem("astrosynth_token", j.token); setMsg("Logged in. Token stored."); }
    else setMsg(JSON.stringify(j));
  }
  return (
    <div className="py-10">
      <Badge>PROFILE & SETTINGS</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">Profile</h1>
      <Card className="mt-6 max-w-lg"><CardBody>
        <label className="text-sm text-white/60">Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 w-full rounded-lg border border-white/10 bg-black/40 px-3 py-2" />
        <div className="mt-3"><Button onClick={login}>Login (demo)</Button></div>
        {msg && <p className="mt-3 text-sm text-cyan-200">{msg}</p>}
      </CardBody></Card>
    </div>
  );
}
