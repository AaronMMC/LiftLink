import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
    setMenuOpen(false);
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            <span className="logo-icon">💪</span>
            <span className="logo-text">LiftLink</span>
          </Link>

          <button 
            className={`nav-toggle ${menuOpen ? 'active' : ''}`}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <div className={`nav-links ${menuOpen ? 'open' : ''}`}>
            {user ? (
              <>
                <Link to="/dashboard" className="nav-link" onClick={closeMenu}>Dashboard</Link>
                {user.role === "instructor" && (
                  <>
                    <Link to="/instructor/profile/create" className="nav-link" onClick={closeMenu}>Profile</Link>
                    <Link to="/instructor/progress" className="nav-link" onClick={closeMenu}>Log Progress</Link>
                  </>
                )}
                {user.role === "client" && (
                  <>
                    <Link to="/client/search" className="nav-link" onClick={closeMenu}>Find Instructors</Link>
                    <Link to="/client/history" className="nav-link" onClick={closeMenu}>My Progress</Link>
                  </>
                )}
                <button onClick={handleLogout} className="btn btn-outline btn-sm">
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-link" onClick={closeMenu}>Sign In</Link>
                <Link to="/register" className="btn btn-primary btn-sm" onClick={closeMenu}>Get Started</Link>
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
