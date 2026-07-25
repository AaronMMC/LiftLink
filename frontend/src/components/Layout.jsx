import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <span className="logo-icon">💪</span>
            <span className="logo-text">LiftLink</span>
          </Link>

          <div className="nav-links">
            {user ? (
              <>
                <Link to="/dashboard" className="nav-link">Dashboard</Link>
                {user.role === "instructor" && (
                  <>
                    <Link to="/instructor/profile/create" className="nav-link">Profile</Link>
                    <Link to="/instructor/progress" className="nav-link">Log Progress</Link>
                  </>
                )}
                {user.role === "client" && (
                  <>
                    <Link to="/client/search" className="nav-link">Find Instructors</Link>
                    <Link to="/client/history" className="nav-link">My Progress</Link>
                  </>
                )}
                <button onClick={handleLogout} className="btn btn-outline btn-sm">
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-link">Sign In</Link>
                <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="main-content">{children}</main>

      <footer className="footer">
        <p>© 2026 LiftLink — Built on AWS Free Tier</p>
      </footer>
    </div>
  );
}
