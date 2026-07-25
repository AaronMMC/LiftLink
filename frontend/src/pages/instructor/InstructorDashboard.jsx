import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { listEntries, getProfile } from "../../services/api";

export default function InstructorDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ entries: 0, hasProfile: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [entriesRes, profileRes] = await Promise.allSettled([
          listEntries(),
          getProfile(user.id),
        ]);
        setStats({
          entries: entriesRes.status === "fulfilled" ? entriesRes.value.data.count : 0,
          hasProfile: profileRes.status === "fulfilled",
        });
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user.id]);

  return (
    <div className="dashboard-page">
      <h1>Instructor Dashboard</h1>
      <p className="subtitle">Welcome back! Here's your overview.</p>

      <div className="stats-grid">
        <div className="stat-card glass">
          <div className="stat-value">{loading ? "—" : stats.entries}</div>
          <div className="stat-label">Progress Entries</div>
        </div>
        <div className="stat-card glass">
          <div className="stat-value">{loading ? "—" : stats.hasProfile ? "✅" : "❌"}</div>
          <div className="stat-label">Profile Created</div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          {!stats.hasProfile && (
            <Link to="/instructor/profile/create" className="action-card glass">
              <span className="action-icon">👤</span>
              <span>Create Profile</span>
            </Link>
          )}
          {stats.hasProfile && (
            <Link to="/instructor/profile/edit" className="action-card glass">
              <span className="action-icon">✏️</span>
              <span>Edit Profile</span>
            </Link>
          )}
          <Link to="/instructor/progress" className="action-card glass">
            <span className="action-icon">📝</span>
            <span>Log Progress</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
