import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import jobsService from '../services/jobsService';
import applicationsService from '../services/applicationsService';
import StatusBadge from '../components/StatusBadge';
import '../styles/ApplicationsReviewPage.css';

const STATUS_OPTIONS = [
  { value: 'applied', label: 'Applied' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'interview', label: 'Interview' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'hired', label: 'Hired' },
];

function ApplicationsReviewPage() {
  const { id: jobId } = useParams();
  const [job, setJob] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);
  const [statusError, setStatusError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [jobData, appsData] = await Promise.all([
          jobsService.getJob(jobId),
          applicationsService.getJobApplications(jobId),
        ]);
        setJob(jobData);
        setApplications(Array.isArray(appsData) ? appsData : (appsData?.results || []));
      } catch (err) {
        console.error('Failed to load review queue:', err);
        setError(err.response?.data?.detail || 'Failed to load applications for this job.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [jobId]);

  const handleStatusChange = async (appId, newStatus) => {
    setUpdatingId(appId);
    setStatusError(null);
    try {
      const updatedApp = await applicationsService.updateStatus(appId, newStatus);
      setApplications((prev) =>
        prev.map((app) => (app.id === appId ? { ...app, status: updatedApp.status } : app))
      );
    } catch (err) {
      console.error('Failed to update status:', err);
      if (err.response?.data?.error?.message) {
        setStatusError(`Failed to update application #${appId}: ${err.response.data.error.message}`);
      } else if (err.response?.data?.status) {
        setStatusError(`Failed to update status: ${err.response.data.status.join(' ')}`);
      } else {
        setStatusError('Failed to update application status.');
      }
    } finally {
      setUpdatingId(null);
    }
  };

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
        <p>Loading application review queue...</p>
      </div>
    );
  }

  return (
    <div className="review-queue-page">
      <div className="job-detail-breadcrumb">
        <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
        <span className="breadcrumb-sep">/</span>
        <Link to={`/jobs/${jobId}`} className="breadcrumb-link">{job?.title || `Job #${jobId}`}</Link>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">Applications</span>
      </div>

      <div className="page-header">
        <div>
          <h1 className="page-title">Applicant Review Queue</h1>
          <p className="page-subtitle">Reviewing candidates for <strong>{job?.title}</strong></p>
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}
      {statusError && <div className="error-alert">{statusError}</div>}

      {applications.length === 0 && !error ? (
        <div className="empty-state">
          <div className="empty-state-icon">👥</div>
          <h3>No applications received</h3>
          <p>No candidates have applied for this position yet.</p>
        </div>
      ) : (
        <div className="review-table-card">
          <table className="review-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Applied Date</th>
                <th>Resume</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app) => (
                <tr key={app.id}>
                  <td>
                    <div className="candidate-cell">
                      <span className="candidate-name">
                        {app.candidate?.full_name || app.candidate_name || `Candidate #${app.candidate?.id || ''}`}
                      </span>
                    </div>
                  </td>
                  <td>{formatDate(app.applied_at)}</td>
                  <td>
                    {app.resume_url ? (
                      <a
                        href={app.resume_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-outline btn-sm"
                      >
                        📄 View Resume
                      </a>
                    ) : (
                      <span className="text-muted">None</span>
                    )}
                  </td>
                  <td>
                    <StatusBadge status={app.status} />
                  </td>
                  <td>
                    <select
                      className="status-select"
                      value={app.status}
                      onChange={(e) => handleStatusChange(app.id, e.target.value)}
                      disabled={updatingId === app.id}
                    >
                      {STATUS_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ApplicationsReviewPage;
