import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import applicationsService from '../services/applicationsService';
import StatusBadge from '../components/StatusBadge';
import '../styles/MyApplicationsPage.css';

function MyApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchApplications = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await applicationsService.getMyApplications();
        setApplications(Array.isArray(data) ? data : (data?.results || []));
      } catch (err) {
        console.error('Failed to fetch candidate applications:', err);
        setError('Failed to load your applications. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your applications...</p>
      </div>
    );
  }

  return (
    <div className="my-applications-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">My Applications</h1>
          <p className="page-subtitle">Track the status of your job applications</p>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}

      {applications.length === 0 && !error ? (
        <div className="empty-state">
          <div className="empty-state-icon">📄</div>
          <h3>No applications yet</h3>
          <p>You haven't submitted any job applications yet.</p>
          <Link to="/jobs" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Browse Jobs
          </Link>
        </div>
      ) : (
        <div className="applications-list">
          {applications.map((app) => (
            <div key={app.id} className="application-card">
              <div className="application-card-main">
                <div className="application-card-header">
                  <h3 className="application-job-title">
                    <Link to={`/jobs/${app.job?.id || app.job}`}>
                      {app.job_title || app.job?.title || `Job #${app.job}`}
                    </Link>
                  </h3>
                  <StatusBadge status={app.status} />
                </div>
                <div className="application-card-meta">
                  {app.company_name && (
                    <span className="meta-item">🏢 {app.company_name}</span>
                  )}
                  <span className="meta-item">📅 Applied on {formatDate(app.applied_at)}</span>
                  {app.resume_url && (
                    <a
                      href={app.resume_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="resume-link-inline"
                    >
                      🔗 Resume Link
                    </a>
                  )}
                </div>
                {app.cover_letter && (
                  <div className="application-cover-letter-preview">
                    <strong>Cover Letter:</strong> "{app.cover_letter.length > 120 ? `${app.cover_letter.slice(0, 120)}...` : app.cover_letter}"
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyApplicationsPage;
