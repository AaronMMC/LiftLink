import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { getHistory } from "../../services/api";

export default function ClientDashboard() {
  const { user } = useAuth();
  const [entryCount, setEntryCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory(user.id)
      .then((res) => setEntryCount(res.data.count))
      .catch(() => setEntryCount(0))
      .finally(() => setLoading(false));
  }, [user.id]);

  return (
    <div className="dashboard-page">
      <h1>Client Dashboard</h1>
      <p className="subtitle">Your fitness journey at a glance.</p>

      <div className="stats-grid">
        <div className="stat-card glass">
          <div className="stat-value">{loading ? "—" : entryCount}</div>
          <div className="stat-label">Workout Sessions</div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/client/search" className="action-card glass">
            <span className="action-icon">🔍</span>
            <span>Find Instructors</span>
          </Link>
          <Link to="/client/history" className="action-card glass">
            <span className="action-icon">📊</span>
            <span>View Progress</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
