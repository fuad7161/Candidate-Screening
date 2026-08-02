import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import authService from '../services/authService';
import '../styles/AuthPages.css';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [unverifiedUser, setUnverifiedUser] = useState(null);
  const [resendMessage, setResendMessage] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setFieldErrors({});
    setSubmitting(true);

    try {
      const result = await login({ email, password });
      const userRole = result.user?.role;
      if (result.user?.is_email_verified === false) {
        setUnverifiedUser(result.user);
        return;
      }
      
      // Redirect based on role if default home was target
      if (from === '/') {
        if (userRole === 'recruiter') {
          navigate('/dashboard', { replace: true });
        } else {
          navigate('/jobs', { replace: true });
        }
      } else {
        navigate(from, { replace: true });
      }
    } catch (err) {
      console.error('Login error:', err);
      const apiError = err.response?.data?.error;
      if (apiError) {
        setErrorMsg(apiError.message || 'Invalid credentials.');
        if (apiError.fields) {
          setFieldErrors(apiError.fields);
        }
      } else {
        setErrorMsg('Failed to log in. Please check your credentials.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const continueToApp = () => {
    navigate(unverifiedUser?.role === 'recruiter' ? '/dashboard' : '/jobs', { replace: true });
  };

  const resendVerification = async () => {
    setResendMessage('');
    try {
      const data = await authService.resendVerification(unverifiedUser.email);
      setResendMessage(data.message);
    } catch (err) {
      setResendMessage(err.response?.data?.error?.message || 'Could not resend verification email.');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your candidate screening account</p>
        </div>

        {errorMsg && <div className="error-alert">{errorMsg}</div>}
        {unverifiedUser && (
          <div className="warning-alert">
            <strong>Your email is not verified.</strong>
            <span> Check your inbox, or request a new verification link.</span>
            {resendMessage && <p>{resendMessage}</p>}
            <div className="verification-actions">
              <button type="button" className="btn btn-outline btn-sm" onClick={resendVerification}>Resend email</button>
              <button type="button" className="btn btn-primary btn-sm" onClick={continueToApp}>Continue for now</button>
            </div>
          </div>
        )}

        {!unverifiedUser && <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className={`form-control ${fieldErrors.email ? 'is-invalid' : ''}`}
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {fieldErrors.email && (
              <span className="field-error">{fieldErrors.email[0]}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className={`form-control ${fieldErrors.password ? 'is-invalid' : ''}`}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {fieldErrors.password && (
              <span className="field-error">{fieldErrors.password[0]}</span>
            )}
          </div>

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={submitting}
          >
            {submitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>}

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Register here</Link>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
