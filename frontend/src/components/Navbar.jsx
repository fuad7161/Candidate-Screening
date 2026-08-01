import { Link, useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import '../styles/Navbar.css';

function Navbar() {
  const { user, role, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          Candidate<span className="brand-accent">Screening</span>
        </Link>

        <div className="navbar-links">
          <Link to="/jobs" className="nav-link">
            Browse Jobs
          </Link>

          {isAuthenticated && role === 'candidate' && (
            <Link to="/my-applications" className="nav-link">
              My Applications
            </Link>
          )}

          {isAuthenticated && role === 'recruiter' && (
            <>
              <Link to="/dashboard" className="nav-link">
                Dashboard
              </Link>
              <Link to="/dashboard/jobs/new" className="nav-link nav-link-highlight">
                + Post Job
              </Link>
            </>
          )}
        </div>

        <div className="navbar-auth">
          {isAuthenticated ? (
            <div className="user-profile-badge">
              <span className="user-name">{user?.full_name || user?.email}</span>
              <span className={`role-badge role-${role}`}>
                {role}
              </span>
              <button onClick={handleLogout} className="btn-logout">
                Log Out
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <Link to="/login" className="nav-link nav-link-outline">
                Log In
              </Link>
              <Link to="/register" className="nav-link nav-link-primary">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
