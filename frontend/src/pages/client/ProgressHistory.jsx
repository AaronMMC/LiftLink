import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { getHistory } from "../../services/api";
import LoadingSpinner from "../../components/LoadingSpinner";

export default function ProgressHistory() {
  const { user } = useAuth();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory(user.id)
      .then((res) => setEntries(res.data.entries))
      .catch(() => setError("Failed to load progress history"))
      .finally(() => setLoading(false));
  }, [user.id]);

  if (loading) return <LoadingSpinner message="Loading your progress..." />;

  return (
    <div className="history-page">
      <h1>My Progress</h1>
      <p className="subtitle">Your complete workout history</p>

      {error && <div className="alert alert-error">{error}</div>}

      {entries.length === 0 ? (
        <div className="empty-state glass">
          <div className="empty-icon">📭</div>
          <h3>No entries yet</h3>
          <p>Your instructor will log your workout progress here.</p>
        </div>
      ) : (
        <div className="timeline">
          {entries.map((entry) => (
            <div key={entry.entry_id} className="timeline-item glass">
              <div className="timeline-header">
                <span className="badge">{entry.workout_type}</span>
                <span className="timeline-date">
                  {new Date(entry.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              </div>
              <p className="timeline-notes">{entry.notes}</p>
              <div className="timeline-meta">
                <span>⏱️ {entry.duration_minutes} min</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
