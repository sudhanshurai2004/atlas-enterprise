const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error("Login failed");
  const data = await response.json();
  localStorage.setItem("atlas_token", data.access_token);
  return data.access_token;
}

export async function streamQuery(question, sessionId, onText, onResult) {
  const token = localStorage.getItem("atlas_token");
  const response = await fetch(`${API_BASE}/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Query failed (${response.status})`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() || "";

    for (const frame of frames) {
      const event = frame.match(/^event: (.+)$/m)?.[1];
      const data = frame.match(/^data: (.+)$/m)?.[1];
      if (!data || data === "[DONE]") continue;
      const payload = JSON.parse(data);
      if (event === "token") onText(payload.text);
      if (event === "result") onResult(payload);
    }
  }
}

export async function getMetrics() {
  const token = localStorage.getItem("atlas_token");
  const response = await fetch(`${API_BASE}/metrics`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Metrics unavailable");
  return response.json();
}
