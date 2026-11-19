export async function login(username, password) {
  const response = await fetch("/api/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error("Login failed");
  const data = await response.json();
  localStorage.setItem("atlas_token", data.access_token);
  return data.access_token;
}

export function streamQuery(question, sessionId, onText) {
  const token = localStorage.getItem("atlas_token");
  return fetch("/api/query/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ question, session_id: sessionId }),
  }).then((response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    async function read() {
      const result = await reader.read();
      if (result.done) return;
      const text = decoder.decode(result.value);
      const words = text
        .split("\n")
        .filter((line) => line.startsWith("data: "))
        .map((line) => line.replace("data: ", ""));
      words.forEach(onText);
      return read();
    }

    return read();
  });
}

export async function getMetrics() {
  const token = localStorage.getItem("atlas_token");
  const response = await fetch("/api/metrics", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Metrics unavailable");
  return response.json();
}
