import { useEffect, useState } from "react";
import DeviceTable, { type Device } from "./components/DeviceTable";

export default function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cidr, setCidr] = useState("auto");
  const [aggressive, setAggressive] = useState(false);
  const [maxHosts, setMaxHosts] = useState(256);

  useEffect(() => {
    loadDevices();
  }, []);

  async function loadDevices() {
    setError(null);
    try {
      const response = await fetch("/api/devices");
      if (!response.ok) return;
      const data = await response.json();
      setDevices((data as any).devices ?? (data as any) ?? []);
    } catch {
      // optional endpoint; ignore errors
    }
  }

  async function startScan() {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/scan/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cidr, aggressive, max_hosts: maxHosts }),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Scan failed: ${response.status} ${text}`);
      }
      const data = await response.json();
      setDevices((data as any).devices ?? []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Scan error";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20, fontFamily: "system-ui, Avenir, Helvetica, Arial" }}>
      <h1>Edik Cyber Lab - Devices</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 12, flexWrap: "wrap" }}>
        <label style={{ display: "flex", flexDirection: "column", minWidth: 180 }}>
          <span style={{ fontSize: 12, color: "#555" }}>CIDR to scan</span>
          <input
            type="text"
            value={cidr}
            onChange={(e) => setCidr(e.target.value)}
            style={{ padding: "6px 8px" }}
            placeholder="auto or 192.168.0.0/24"
            disabled={loading}
          />
        </label>
        <label style={{ display: "flex", flexDirection: "column", minWidth: 150 }}>
          <span style={{ fontSize: 12, color: "#555" }}>Max hosts</span>
          <input
            type="number"
            min={1}
            max={4096}
            value={maxHosts}
            onChange={(e) => {
              const next = Number(e.target.value);
              const clamped = Number.isFinite(next) ? Math.min(4096, Math.max(1, next)) : 1;
              setMaxHosts(clamped);
            }}
            style={{ padding: "6px 8px" }}
            disabled={loading}
          />
        </label>
        <label style={{ alignSelf: "flex-end", display: "flex", alignItems: "center", gap: 6 }}>
          <input
            type="checkbox"
            checked={aggressive}
            onChange={(e) => setAggressive(e.target.checked)}
            disabled={loading}
          />
          Aggressive scan
        </label>
      </div>

      <div style={{ marginBottom: 12 }}>
        <button onClick={startScan} disabled={loading} style={{ padding: "8px 14px", cursor: "pointer" }}>
          {loading ? "Scanning..." : "Start Scan"}
        </button>
        <button onClick={loadDevices} disabled={loading} style={{ padding: "8px 14px", marginLeft: 8, cursor: "pointer" }}>
          Refresh List
        </button>
      </div>

      {error && <div style={{ color: "crimson", marginBottom: 8 }}>Error: {error}</div>}

      <DeviceTable devices={devices} loading={loading} />
    </div>
  );
}
