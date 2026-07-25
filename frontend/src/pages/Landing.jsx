import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Find Your Perfect
            <span className="gradient-text"> Fitness Match</span>
          </h1>
          <p className="hero-subtitle">
            LiftLink connects you with certified fitness instructors.
            Track your progress, achieve your goals.
          </p>
          <div className="hero-cta">
            <Link to="/register" className="btn btn-primary btn-lg">
              Get Started Free
            </Link>
            <Link to="/login" className="btn btn-outline btn-lg">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="features-grid">
          <div className="feature-card glass">
            <div className="feature-icon">🔍</div>
            <h3>Discover Instructors</h3>
            <p>Search by specialty and location to find the perfect trainer for your goals.</p>
          </div>
          <div className="feature-card glass">
            <div className="feature-icon">📊</div>
            <h3>Track Progress</h3>
            <p>Your instructor logs every workout. Watch your fitness journey unfold.</p>
          </div>
          <div className="feature-card glass">
            <div className="feature-icon">🔒</div>
            <h3>Private & Secure</h3>
            <p>Your data is yours alone. Strict authorization ensures complete privacy.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
