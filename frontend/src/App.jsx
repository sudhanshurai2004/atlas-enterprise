import { useState } from "react";
import { login } from "./api";
import Chat from "./Chat";

export default function App() {
  const [authorized, setAuthorized] = useState(
    Boolean(localStorage.getItem("atlas_token"))
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  return authorized ? (
    <Chat />
  ) : (
    <main style={{ maxWidth: 400, margin: "80px auto", fontFamily: "sans-serif" }}>
      <h1>Atlas Login</h1>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setError("");
          try {
            await login(username, password);
            setAuthorized(true);
          } catch {
            setError("Login failed. Check your credentials and try again.");
          }
        }}
      >
        <input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Username" />
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" />
        <button type="submit">Login</button>
      </form>
      {error && <p role="alert">{error}</p>}
    </main>
  );
}
