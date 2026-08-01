import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import '../styles/LandingPage.css';

function LandingPage() {
  const { isAuthenticated, role } = useAuth();

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-badge">Candidate Screening Platform</div>
        <h1 className="hero-title">Hire Faster. Get Screened Smarter.</h1>
        <p className="hero-subtitle">
          Streamlining recruitment for forward-thinking teams and ambitious candidates.
          Post jobs, manage applications, and track progress effortlessly.
        </p>

        <div className="hero-actions">
          <Link to="/jobs" className="btn btn-primary">
            Browse Open Jobs
          </Link>
          {!isAuthenticated ? (
            <Link to="/register" className="btn btn-outline">
              Create Account
            </Link>
          ) : role === 'recruiter' ? (
            <Link to="/dashboard" className="btn btn-outline">
              Go to Dashboard
            </Link>
          ) : (
            <Link to="/my-applications" className="btn btn-outline">
              View My Applications
            </Link>
          )}
        </div>
      </section>

      <section className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">💼</div>
          <h3>For Recruiters</h3>
          <p>
            Post jobs in seconds, review candidate applications, manage statuses, and build your dream team.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🚀</div>
          <h3>For Candidates</h3>
          <p>
            Apply to top opportunities with a simple resume link and track your application status in real-time.
          </p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">🔒</div>
          <h3>Role-Based Access</h3>
          <p>
            Secure, token-based authentication with strict role permissions for recruiter and candidate workflows.
          </p>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;
