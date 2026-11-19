import { useEffect, useState } from "react";
import { getMetrics, streamQuery } from "./api";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const sessionId = "atlas-session";

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => setMetrics(null));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setAnswer("");
    await streamQuery(question, sessionId, (word) => {
      setAnswer((current) => `${current}${current ? " " : ""}${word}`);
    });
  }

  return (
    <main style={{ maxWidth: 780, margin: "40px auto", fontFamily: "sans-serif" }}>
      {metrics && (
        <section>
          <strong>Latency:</strong> {metrics.avg_latency_ms} ms ·{" "}
          <strong>Cost:</strong> ${metrics.avg_cost_per_request} ·{" "}
          <strong>Cache:</strong> {metrics.cache_hit_percentage}%
        </section>
      )}
      <h1>Atlas Chat</h1>
      <form onSubmit={submit}>
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask Atlas..."
          style={{ width: "70%", padding: 10 }}
        />
        <button type="submit" style={{ padding: 10, marginLeft: 8 }}>
          Send
        </button>
      </form>
      {answer && <article style={{ marginTop: 24 }}>{answer}</article>}
      {citations.map((citation, index) => (
        <a key={index} href={citation.source_uri}>
          {citation.title}
        </a>
      ))}
    </main>
  );
}
