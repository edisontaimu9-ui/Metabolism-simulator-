"use client";
import { useState } from "react";

type Result = {
  summary: {
    days_simulated: number; starting_weight_kg: number; ending_weight_kg: number;
    total_weight_change_kg: number; average_daily_energy_balance_kcal: number;
  };
  weight_kg: number[];
};

const field = { display: "flex", flexDirection: "column", gap: 4, fontSize: 13, minWidth: 0 } as const;
const input = { padding: 10, fontSize: 16, border: "1px solid #c9d1cb", borderRadius: 8, width: "100%", minWidth: 0, boxSizing: "border-box" } as const;

function Chart({ data }: { data: number[] }) {
  const W = 600, H = 260, P = 40;
  const min = Math.min(...data), max = Math.max(...data);
  const span = max - min || 1;
  const x = (i: number) => P + (i / Math.max(data.length - 1, 1)) * (W - P * 2);
  const y = (v: number) => H - P - ((v - min) / span) * (H - P * 2);
  const pts = data.map((v, i) => `${x(i)},${y(v)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", background: "#fff", borderRadius: 12 }}>
      <line x1={P} y1={H - P} x2={W - P} y2={H - P} stroke="#c9d1cb" />
      <line x1={P} y1={P} x2={P} y2={H - P} stroke="#c9d1cb" />
      <text x={P - 6} y={P + 4} fontSize="11" textAnchor="end">{max.toFixed(1)}</text>
      <text x={P - 6} y={H - P} fontSize="11" textAnchor="end">{min.toFixed(1)}</text>
      <text x={P} y={H - 14} fontSize="11">Day 0</text>
      <text x={W - P} y={H - 14} fontSize="11" textAnchor="end">Day {data.length - 1}</text>
      <polyline points={pts} fill="none" stroke="#2e7d4f" strokeWidth="3" strokeLinejoin="round" />
    </svg>
  );
}

export default function Home() {
  const [f, setF] = useState({
    sex: "male", age: "30", height: "175", weight: "80",
    protein: "120", carbs: "250", fat: "70", days: "30",
  });
  const [res, setRes] = useState<Result | null>(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setF({ ...f, [k]: e.target.value });

  async function run(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true); setErr(""); setRes(null);
    try {
      const r = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          person: { sex: f.sex, age_years: +f.age, height_cm: +f.height, weight_kg: +f.weight },
          macros: { protein_g: +f.protein, carbohydrate_g: +f.carbs, fat_g: +f.fat },
          days: +f.days,
        }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || `Error ${r.status}`);
      setRes(j);
    } catch (x) {
      setErr(x instanceof Error ? x.message : "Request failed");
    } finally { setBusy(false); }
  }

  const s = res?.summary;
  const card = (label: string, value: string) => (
    <div style={{ background: "#fff", borderRadius: 12, padding: 14 }}>
      <div style={{ fontSize: 12, color: "#5b6b61" }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
    </div>
  );

  return (
    <main style={{ maxWidth: 680, margin: "0 auto", padding: 16 }}>
      <h1 style={{ fontSize: 24 }}>Metabolism Simulator</h1>
      <form onSubmit={run} style={{ display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)", gap: 12 }}>
        <label style={field}>Sex
          <select style={input} value={f.sex} onChange={set("sex")}>
            <option value="male">Male</option><option value="female">Female</option>
          </select></label>
        {([["age", "Age (years)"], ["height", "Height (cm)"], ["weight", "Weight (kg)"],
          ["protein", "Protein (g/day)"], ["carbs", "Carbs (g/day)"], ["fat", "Fat (g/day)"],
          ["days", "Days (1–730)"]] as const).map(([k, label]) => (
          <label key={k} style={field}>{label}
            <input style={input} inputMode="decimal" value={f[k]} onChange={set(k)} required /></label>
        ))}
        <button disabled={busy} style={{ gridColumn: "1 / -1", padding: 14, boxSizing: "border-box", width: "100%", fontSize: 16, border: 0,
          borderRadius: 10, background: "#2e7d4f", color: "#fff" }}>
          {busy ? "Simulating…" : "Run simulation"}
        </button>
      </form>

      {err && <p style={{ color: "#b3261e" }}>{err}</p>}

      {s && res && (
        <section style={{ marginTop: 20, display: "grid", gap: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {card("Start", `${s.starting_weight_kg.toFixed(1)} kg`)}
            {card("End", `${s.ending_weight_kg.toFixed(1)} kg`)}
            {card("Change", `${s.total_weight_change_kg >= 0 ? "+" : ""}${s.total_weight_change_kg.toFixed(2)} kg`)}
            {card("Avg balance", `${s.average_daily_energy_balance_kcal >= 0 ? "+" : ""}${Math.round(s.average_daily_energy_balance_kcal)} kcal/day`)}
          </div>
          <Chart data={res.weight_kg} />
          <p style={{ fontSize: 12, color: "#5b6b61" }}>
            Estimates from a simulation model, not medical advice.
          </p>
        </section>
      )}
    </main>
  );
}
