import { useState } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import authService from '../services/authService';
import '../styles/AuthPages.css';

function RegisterPage() {
  const [role, setRole] = useState('candidate');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [phone, setPhone] = useState('');

  const [errorMsg, setErrorMsg] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [registration, setRegistration] = useState(null);
  const [resendState, setResendState] = useState({ loading: false, message: '' });

  const { register } = useAuth();
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setFieldErrors({});
    setSubmitting(true);

    const payload = {
      email,
      password,
      role,
      full_name: fullName,
      ...(role === 'recruiter' ? { company_name: companyName } : { phone }),
    };

    try {
      const result = await register(payload);
      setRegistration(result);
    } catch (err) {
      console.error('Registration error:', err);
      const apiError = err.response?.data?.error;
      if (apiError) {
        setErrorMsg(apiError.message || 'Registration failed.');
        if (apiError.fields) {
          setFieldErrors(apiError.fields);
        }
      } else {
        setErrorMsg('An unexpected error occurred. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const resendVerification = async () => {
    setResendState({ loading: true, message: '' });
    try {
      const result = await authService.resendVerification(email);
      setResendState({ loading: false, message: result.message });
    } catch (err) {
      setResendState({
        loading: false,
        message: err.response?.data?.error?.message || 'Could not resend the verification email.',
      });
    }
  };

  if (registration) {
    return (
      <div className="auth-container">
        <div className="auth-card verification-card">
          <div className="verification-icon">✉</div>
          <h1 className="auth-title">Check your inbox</h1>
          <p className="verification-message success">{registration.message}</p>
          <p className="auth-subtitle">We sent the link to <strong>{email}</strong>. It expires in {registration.verification_expiry_hours} hours.</p>
          {resendState.message && <div className="info-alert">{resendState.message}</div>}
          <button className="auth-submit-btn" onClick={resendVerification} disabled={resendState.loading}>
            {resendState.loading ? 'Sending…' : 'Resend verification email'}
          </button>
          <div className="auth-footer"><Link to="/login">Continue to sign in</Link></div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join as a Candidate or Recruiter</p>
        </div>

        <div className="role-toggle">
          <button
            type="button"
            className={`role-button ${role === 'candidate' ? 'active' : ''}`}
            onClick={() => {
              setRole('candidate');
              setFieldErrors({});
            }}
          >
            Candidate
          </button>
          <button
            type="button"
            className={`role-button ${role === 'recruiter' ? 'active' : ''}`}
            onClick={() => {
              setRole('recruiter');
              setFieldErrors({});
            }}
          >
            Recruiter
          </button>
        </div>

        {errorMsg && <div className="error-alert">{errorMsg}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              id="fullName"
              type="text"
              className={`form-control ${fieldErrors.full_name ? 'is-invalid' : ''}`}
              placeholder="Jane Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            {fieldErrors.full_name && (
              <span className="field-error">{fieldErrors.full_name[0]}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className={`form-control ${fieldErrors.email ? 'is-invalid' : ''}`}
              placeholder="jane@example.com"
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
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {fieldErrors.password && (
              <span className="field-error">{fieldErrors.password[0]}</span>
            )}
          </div>

          {role === 'recruiter' ? (
            <div className="form-group">
              <label htmlFor="companyName">Company Name</label>
              <input
                id="companyName"
                type="text"
                className={`form-control ${fieldErrors.company_name ? 'is-invalid' : ''}`}
                placeholder="Acme Corp"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
              />
              {fieldErrors.company_name && (
                <span className="field-error">{fieldErrors.company_name[0]}</span>
              )}
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="phone">Phone Number (Optional)</label>
              <input
                id="phone"
                type="tel"
                className={`form-control ${fieldErrors.phone ? 'is-invalid' : ''}`}
                placeholder="+1 (555) 000-0000"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              {fieldErrors.phone && (
                <span className="field-error">{fieldErrors.phone[0]}</span>
              )}
            </div>
          )}

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={submitting}
          >
            {submitting ? 'Creating account...' : `Register as ${role === 'recruiter' ? 'Recruiter' : 'Candidate'}`}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
