import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import authService from '../services/authService';
import '../styles/AuthPages.css';

function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState({ status: 'loading', message: 'Verifying your email…' });
  const requested = useRef(false);

  useEffect(() => {
    if (requested.current) return;
    requested.current = true;
    const token = searchParams.get('token');
    if (!token) {
      setState({ status: 'error', message: 'The verification link is missing its token.' });
      return;
    }
    authService.verifyEmail(token)
      .then((data) => setState({ status: 'success', message: data.message }))
      .catch((err) => setState({
        status: 'error',
        message: err.response?.data?.error?.message || 'This verification link is invalid or expired.',
      }));
  }, [searchParams]);

  return (
    <div className="auth-container">
      <div className="auth-card verification-card">
        <div className="auth-header">
          <h1 className="auth-title">Email verification</h1>
          <p className={`verification-message ${state.status}`}>{state.message}</p>
        </div>
        {state.status === 'loading' && <div className="spinner verification-spinner" />}
        {state.status !== 'loading' && (
          <Link className="auth-submit-btn auth-link-button" to="/login">
            {state.status === 'success' ? 'Continue to sign in' : 'Back to sign in'}
          </Link>
        )}
      </div>
    </div>
  );
}

export default VerifyEmailPage;
