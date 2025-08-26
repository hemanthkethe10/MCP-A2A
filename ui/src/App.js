import React, { useState } from "react";
import StreamingChat from "./StreamingChat";

const API_BASE = "http://localhost:8002";

const styles = {
  container: {
    maxWidth: 480,
    margin: "3rem auto",
    padding: "2rem 2.5rem",
    background: "#fff",
    borderRadius: 12,
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    fontFamily: "'Segoe UI', 'Roboto', 'Arial', sans-serif",
  },
  title: {
    fontSize: 28,
    fontWeight: 700,
    marginBottom: 8,
    color: "#2d3748",
  },
  subtitle: {
    fontSize: 16,
    color: "#4a5568",
    marginBottom: 24,
  },
  label: {
    display: "block",
    fontWeight: 500,
    marginBottom: 6,
    color: "#2d3748",
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #cbd5e1",
    borderRadius: 6,
    fontSize: 16,
    marginBottom: 18,
    outline: "none",
    transition: "border 0.2s",
  },
  button: {
    width: "100%",
    padding: "12px 0",
    background: "#2563eb",
    color: "#fff",
    fontWeight: 600,
    fontSize: 18,
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    marginTop: 8,
    transition: "background 0.2s",
  },
  buttonDisabled: {
    background: "#a5b4fc",
    cursor: "not-allowed",
  },
  result: {
    marginTop: 28,
    background: "#f1f5f9",
    borderRadius: 8,
    padding: 18,
    fontSize: 15,
    color: "#1e293b",
    wordBreak: "break-word",
  },
  error: {
    color: "#dc2626",
    background: "#fef2f2",
    borderRadius: 6,
    padding: 12,
    marginTop: 18,
    fontWeight: 500,
  },
  loader: {
    margin: "18px 0",
    textAlign: "center",
    color: "#2563eb",
    fontWeight: 500,
  },
  info: {
    background: "#f0fdf4",
    color: "#166534",
    borderRadius: 6,
    padding: 12,
    marginBottom: 18,
    fontSize: 14,
  },
  tabContainer: {
    marginBottom: 24,
    borderBottom: "2px solid #e2e8f0",
  },
  tabButton: {
    padding: "12px 24px",
    background: "transparent",
    border: "none",
    borderBottom: "3px solid transparent",
    fontSize: 16,
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.2s",
    marginRight: 8,
  },
  tabButtonActive: {
    borderBottomColor: "#2563eb",
    color: "#2563eb",
  },
  tabButtonInactive: {
    color: "#64748b",
  },
};

function App() {
  const [activeTab, setActiveTab] = useState("streaming");
  const [directory, setDirectory] = useState("");
  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [polling, setPolling] = useState(false);

  // Submit the workflow
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    setTaskId(null);

    if (!directory.trim() || !email.trim()) {
      setError("Please provide both directory and email.");
      setLoading(false);
      return;
    }

    const payload = {
      action: "summarize_and_email_pdfs",
      directory,
      email,
    };

    try {
      const res = await fetch(`${API_BASE}/tasks/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.task_id) {
        setTaskId(data.task_id);
        setPolling(true);
        pollTask(data.task_id);
      } else if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Network or server error. Please try again.");
    }
    setLoading(false);
  };

  // Poll for async result
  const pollTask = async (id) => {
    let done = false;
    while (!done) {
      await new Promise((r) => setTimeout(r, 2000));
      try {
        const res = await fetch(`${API_BASE}/tasks/${id}`);
        const data = await res.json();
        if (data.status === "completed" || data.status === "failed") {
          setResult(data.result || data.error);
          setPolling(false);
          done = true;
        }
      } catch (err) {
        setError("Error polling task status.");
        setPolling(false);
        done = true;
      }
    }
  };

  const renderTabContent = () => {
    if (activeTab === "streaming") {
      return <StreamingChat />;
    } else {
      return (
        <div>
          <div style={styles.title}>Summarize and Email PDFs</div>
          <div style={styles.subtitle}>
            <span role="img" aria-label="pdf">📄</span> Find all PDF files in a directory, summarize each, and email the summaries to a user.
          </div>
          <div style={styles.info}>
            <b>Instructions:</b> Enter the absolute directory path containing your PDF files and the recipient's email address. The workflow will find all PDFs, summarize them, and email the summaries.
          </div>
          <form onSubmit={handleSubmit} autoComplete="off">
            <label style={styles.label} htmlFor="directory">Directory Path</label>
            <input
              id="directory"
              type="text"
              placeholder="e.g. /home/user/docs"
              value={directory}
              onChange={(e) => setDirectory(e.target.value)}
              style={styles.input}
              required
            />
            <label style={styles.label} htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              placeholder="e.g. user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={styles.input}
              required
            />
            <button
              type="submit"
              style={loading || polling ? { ...styles.button, ...styles.buttonDisabled } : styles.button}
              disabled={loading || polling}
            >
              {loading || polling ? "Processing..." : "Run Workflow"}
            </button>
          </form>
          {loading && <div style={styles.loader}>Submitting task...</div>}
          {error && <div style={styles.error}>{error}</div>}
          {result && (
            <div style={styles.result}>
              <h4 style={{ margin: 0, marginBottom: 8, color: "#0f172a" }}>Result:</h4>
              <pre style={{ background: "none", padding: 0, margin: 0, fontSize: 14 }}>
                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      );
    }
  };

  return (
    <div>
      {activeTab === "streaming" ? (
        renderTabContent()
      ) : (
        <div style={styles.container}>
          <div style={styles.tabContainer}>
            <button
              style={{
                ...styles.tabButton,
                ...(activeTab === "streaming" ? styles.tabButtonActive : styles.tabButtonInactive),
              }}
              onClick={() => setActiveTab("streaming")}
            >
              🚀 Streaming Agent
            </button>
            <button
              style={{
                ...styles.tabButton,
                ...(activeTab === "pdf" ? styles.tabButtonActive : styles.tabButtonInactive),
              }}
              onClick={() => setActiveTab("pdf")}
            >
              📄 PDF Workflow
            </button>
          </div>
          {renderTabContent()}
        </div>
      )}
    </div>
  );
}

export default App; 