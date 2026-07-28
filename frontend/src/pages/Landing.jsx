import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="landing">
      {/* Hero Section */}
      <section className="hero hero-bg">
        <div className="hero-content">
          <h1 className="hero-title fade-in-1">
            Elevate Your Fitness with <br />
            <span className="gradient-text">The Perfect Instructor</span>
          </h1>
          <p className="hero-subtitle fade-in-2">
            LiftLink is the premium marketplace connecting driven clients with elite fitness professionals. Real-time progress tracking, zero friction.
          </p>
          <div className="hero-cta fade-in-3">
            <Link to="/register" className="btn btn-primary btn-lg">
              Start Your Journey
            </Link>
            <Link to="/login" className="btn btn-outline btn-lg">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Social Proof / Stats Banner */}
      <section className="social-proof fade-in-3">
        <div className="proof-grid">
          <div className="proof-item pulse-stat">
            <div className="proof-value">1000+</div>
            <div className="proof-label">Workouts Logged</div>
          </div>
          <div className="proof-item pulse-stat">
            <div className="proof-value">200+</div>
            <div className="proof-label">Certified Instructors</div>
          </div>
          <div className="proof-item pulse-stat">
            <div className="proof-value">100%</div>
            <div className="proof-label">Free to Use</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="features-grid">
          <div className="feature-card glass fade-in-1">
            <div className="feature-icon">🔍</div>
            <h3>Discover Elite Instructors</h3>
            <p>Filter by specialty and location. Find the perfect professional to match your unique fitness goals.</p>
          </div>
          <div className="feature-card glass fade-in-2">
            <div className="feature-icon">📈</div>
            <h3>Seamless Progress Tracking</h3>
            <p>Your instructor logs every rep and set. Watch your performance metrics improve week over week.</p>
          </div>
          <div className="feature-card glass fade-in-3">
            <div className="feature-icon">🔒</div>
            <h3>Enterprise-Grade Security</h3>
            <p>Your fitness data is strictly isolated. Our robust authorization guarantees complete privacy.</p>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="how-it-works fade-in-3">
        <h2>How It Works</h2>
        <div className="steps-grid">
          <div className="step-card glass">
            <div className="step-number">1</div>
            <h3>Create an Account</h3>
            <p>Sign up in seconds as either a fitness enthusiast or a professional instructor.</p>
          </div>
          <div className="step-card glass">
            <div className="step-number">2</div>
            <h3>Find Your Match</h3>
            <p>Clients can browse and connect with local or specialized trainers.</p>
          </div>
          <div className="step-card glass">
            <div className="step-number">3</div>
            <h3>Track & Grow</h3>
            <p>Instructors log workouts; clients visualize their journey and smash their goals.</p>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="hero" style={{ paddingBottom: '6rem' }}>
        <h2 className="hero-title" style={{ fontSize: '2.5rem' }}>Ready to transform?</h2>
        <div className="hero-cta">
          <Link to="/register" className="btn btn-primary btn-lg">
            Join LiftLink Today
          </Link>
        </div>
      </section>
    </div>
  );
}
