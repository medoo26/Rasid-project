import React, { useEffect, useState } from "react";

export default function VerificationBanner({ verification, onConfirm, onDismiss }) {
  const [secondsLeft, setSecondsLeft] = useState(null);

  useEffect(() => {
    if (!verification) return undefined;
    const update = () => {
      const expires = new Date(verification.expires_at).getTime();
      const now = Date.now();
      const diff = Math.max(0, Math.round((expires - now) / 1000));
      setSecondsLeft(diff);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, [verification]);

  if (!verification) return null;

  return (
    <div className="banner">
      <div>
        Medium risk detected for frame <strong>{verification.frame}</strong>. Please verify.
      </div>
      <div>Time left: {secondsLeft ?? "?"}s</div>
      <div className="actions">
        <button className="confirm" onClick={onConfirm}>
          Situation is real
        </button>
        <button className="dismiss" onClick={onDismiss}>
          False alarm
        </button>
      </div>
    </div>
  );
}

