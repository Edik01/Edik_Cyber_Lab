import React from "react";

type Port = {
  port: number;
  proto?: string;
  service?: string | null;
  state?: string;
};

export type Device = {
  ip: string;
  hostname?: string | null;
  mac?: string | null;
  vendor?: string | null;
  ports?: Port[];
};

type Props = {
  devices: Device[];
  loading?: boolean;
};

export default function DeviceTable({ devices, loading }: Props) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <Th>IP</Th>
            <Th>Hostname</Th>
            <Th>MAC</Th>
            <Th>Vendor</Th>
            <Th>Open Ports</Th>
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr><Td colSpan={5}>Scanning…</Td></tr>
          ) : devices.length === 0 ? (
            <tr><Td colSpan={5}>Нет данных</Td></tr>
          ) : (
            devices.map((d) => (
              <tr key={d.ip}>
                <Td mono>{d.ip}</Td>
                <Td>{d.hostname || "—"}</Td>
                <Td mono>{d.mac || "—"}</Td>
                <Td>{d.vendor || "—"}</Td>
                <Td>
                  {d.ports && d.ports.length > 0
                    ? d.ports
                        .filter(p => (p.state || "open").toLowerCase() === "open")
                        .map(p => `${p.port}${p.service ? " (" + p.service + ")" : ""}`)
                        .join(", ")
                    : "—"}
                </Td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: "8px" }}>
      {children}
    </th>
  );
}

function Td({ children, mono, colSpan }: { children: React.ReactNode; mono?: boolean; colSpan?: number }) {
  return (
    <td
      colSpan={colSpan}
      style={{
        padding: "8px",
        borderBottom: "1px solid #f0f0f0",
        fontFamily: mono ? "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" : undefined,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </td>
  );
}

