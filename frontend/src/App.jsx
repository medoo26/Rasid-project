import React, { useEffect, useState, useCallback } from "react";
import { analyzeNext, fetchState, verify } from "./api";
import Feed from "./components/Feed";
import RiskCard from "./components/RiskCard";
import VerificationBanner from "./components/VerificationBanner";

const POLL_MS = 6000;

export default function App() {
  const [status, setStatus] = useState({
    frame: null,
    score: 0,
    level: "low",
    intent: "unknown_intent",
    verification: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [alertStatus, setAlertStatus] = useState(null);

  const refreshState = useCallback(async () => {
    try {
      const data = await fetchState();
      setStatus((prev) => ({ ...prev, ...data }));
      setAlertStatus(data?.last_alert_payload || null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeNext();
      setStatus((prev) => ({
        ...prev,
        frame: data.filename,
        score: data.score,
        level: data.level,
        intent: data.intent,
        verification: data.verification,
      }));
      if (data.alert_dispatched) {
        await refreshState();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [refreshState]);

  const handleVerify = async (decision) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await verify(decision);
      setStatus((prev) => ({ ...prev, verification: resp.verification }));
      await refreshState();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshState();
    const id = setInterval(() => {
      runAnalysis();
    }, POLL_MS);
    return () => clearInterval(id);
  }, [refreshState, runAnalysis]);

  return (
    <div className="page">
      <header>
        <h1>Risk Alert Demo</h1>
        <p>Intent-aware alerts with owner verification and secure dispatch.</p>
      </header>

      {error && <div className="error">Error: {error}</div>}

      <VerificationBanner
        verification={status.verification}
        onConfirm={() => handleVerify("confirm")}
        onDismiss={() => handleVerify("false_alarm")}
      />

      <div className="grid">
        <Feed filename={status.frame} />
        <div className="side">
          <RiskCard score={status.score} level={status.level} intent={status.intent} />
          <div className="controls">
            <button onClick={runAnalysis} disabled={loading}>
              {loading ? "Processing..." : "Next frame"}
            </button>
          </div>
          <div className="panel">
            <div className="label">Alert status</div>
            {alertStatus ? (
              <pre className="payload">{JSON.stringify(alertStatus, null, 2)}</pre>
            ) : (
              <div className="value">No alerts dispatched yet.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

