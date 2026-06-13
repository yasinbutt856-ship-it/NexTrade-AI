import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Settings() {
  const { data: settings } = useQuery({ queryKey: ["settings"], queryFn: api.settings });

  return (
    <div>
      <h1>Settings</h1>
      <pre
        style={{
          background: "#fff",
          padding: "1rem",
          borderRadius: 8,
          overflow: "auto",
          maxHeight: "60vh",
        }}
      >
        {JSON.stringify(settings, null, 2)}
      </pre>
    </div>
  );
}
