import React, { useEffect, useState } from "react";
import DeviceTable, { Device } from "./components/DeviceTable";

export default function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDevices();
  }, []);

  async function loadDevices() {
    setError(null);
    try {
      const r = await fetch("/api/devices");
      if (r.ok) {
        const data = await r.json();
        setDevices((data as any).devices ?? (data as any) ?? []);
      }
    } catch (_) {
      // optional endpoint; ignore errors
    }
  }

  async function startScan() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch("/api/scan/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cidr: "192.168.1.0/24", aggressive: false, max_hosts: 256 }),
      });
      if (!r.ok) {
        const text = await r.text();
        throw new Error(`Scan failed: ${r.status} ${text}`);
      }
      const data = await r.json();
      setDevices((data as any).devices ?? []);
    } catch (e: any) {
      setError(e?.message || "Scan error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20, fontFamily: "system-ui, Avenir, Helvetica, Arial" }}>
      <h1>Edik Cyber Lab — Devices</h1>

      <div style={{ marginBottom: 12 }}>
        <button onClick={startScan} disabled={loading} style={{ padding: "8px 14px", cursor: "pointer" }}>
          {loading ? "Scanning…" : "Сканировать сеть"}
        </button>
        <button onClick={loadDevices} disabled={loading} style={{ padding: "8px 14px", marginLeft: 8, cursor: "pointer" }}>
          Обновить
        </button>
      </div>

      {error && <div style={{ color: "crimson", marginBottom: 8 }}>Ошибка: {error}</div>}

      <DeviceTable devices={devices} loading={loading} />
    </div>
  );
}

