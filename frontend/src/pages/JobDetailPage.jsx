import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import jobsService from '../services/jobsService';
import applicationsService from '../services/applicationsService';
import useAuth from '../hooks/useAuth';
import Modal from '../components/Modal';
import ApplyForm from '../components/ApplyForm';
import StatusBadge from '../components/StatusBadge';
import '../styles/JobDetailPage.css';

const EMPLOYMENT_TYPE_LABELS = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  internship: 'Internship',
};

function JobDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated, role } = useAuth();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [closing, setClosing] = useState(false);

  const [hasApplied, setHasApplied] = useState(false);
  const [existingApplication, setExistingApplication] = useState(null);
  const [showApplyForm, setShowApplyForm] = useState(false);

  const isOwner =
    isAuthenticated &&
    role === 'recruiter' &&
    job?.recruiter?.id === user?.profile_id;

  useEffect(() => {
    const fetchJobAndApplication = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await jobsService.getJob(id);
        setJob(data);

        if (isAuthenticated && role === 'candidate') {
          try {
            const myApps = await applicationsService.getMyApplications();
            const matchingApp = myApps.find((app) => app.job === Number(id) || app.job?.id === Number(id));
            if (matchingApp) {
              setHasApplied(true);
              setExistingApplication(matchingApp);
            }
          } catch (appErr) {
            console.error('Failed to check application status:', appErr);
          }
        }
      } catch (err) {
        if (err.response?.status === 404) {
          setError('Job posting not found.');
        } else {
          setError('Failed to load job details. Please try again.');
        }
        console.error('Failed to fetch job:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobAndApplication();
  }, [id, isAuthenticated, role]);

  const handleCloseJob = async () => {
    setClosing(true);
    try {
      const updatedJob = await jobsService.closeJob(id);
      setJob(updatedJob);
      setShowCloseModal(false);
    } catch (err) {
      console.error('Failed to close job:', err);
      setError('Failed to close the job. Please try again.');
    } finally {
      setClosing(false);
    }
  };

  const handleApplySuccess = (newApplication) => {
    setHasApplied(true);
    setExistingApplication(newApplication);
    setShowApplyForm(false);
    setJob((prev) => ({
      ...prev,
      applications_count: (prev.applications_count || 0) + 1,
    }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading job details...</p>
      </div>
    );
  }

  if (error && !job) {
    return (
      <div className="job-detail-page">
        <div className="job-detail-error">
          <div className="error-icon">😕</div>
          <h2>Oops!</h2>
          <p>{error}</p>
          <Link to="/jobs" className="btn btn-outline">
            ← Back to Jobs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="job-detail-page">
      <div className="job-detail-breadcrumb">
        <Link to="/jobs" className="breadcrumb-link">Jobs</Link>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">{job.title}</span>
      </div>

      <div className="job-detail-card">
        <div className="job-detail-header">
          <div className="job-detail-header-left">
            <div className="job-detail-status-row">
              <span className={`status-badge status-badge-${job.status}`}>
                {job.status === 'open' ? '🟢 Open' : '🔴 Closed'}
              </span>
              {job.employment_type && (
                <span className="job-detail-type-badge">
                  {EMPLOYMENT_TYPE_LABELS[job.employment_type] || job.employment_type}
                </span>
              )}
            </div>
            <h1 className="job-detail-title">{job.title}</h1>
            <div className="job-detail-meta">
              {job.recruiter && (
                <span className="meta-item">
                  <span className="meta-icon">🏢</span>
                  {job.recruiter.company_name || job.recruiter.full_name}
                </span>
              )}
              {job.location && (
                <span className="meta-item">
                  <span className="meta-icon">📍</span>
                  {job.location}
                </span>
              )}
              <span className="meta-item">
                <span className="meta-icon">📅</span>
                Posted {formatDate(job.created_at)}
              </span>
              {job.applications_count !== undefined && (
                <span className="meta-item">
                  <span className="meta-icon">👥</span>
                  {job.applications_count} applicant{job.applications_count !== 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>

          {isOwner && (
            <div className="job-detail-owner-actions">
              <Link
                to={`/dashboard/jobs/${job.id}/edit`}
                className="btn btn-outline btn-sm"
              >
                ✏️ Edit Job
              </Link>
              {job.status === 'open' && (
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => setShowCloseModal(true)}
                >
                  🚫 Close Job
                </button>
              )}
            </div>
          )}
        </div>

        {error && <div className="error-alert" style={{ marginTop: '1rem' }}>{error}</div>}

        <div className="job-detail-body">
          <h2 className="job-detail-section-title">Description</h2>
          <div className="job-detail-description">
            {job.description.split('\n').map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>
        </div>

        <div className="job-detail-footer">
          {isAuthenticated && role === 'candidate' && job.status === 'open' && (
            <div className="job-detail-apply-cta">
              {hasApplied ? (
                <div className="applied-status-box">
                  <span className="applied-check">✓ Applied</span>
                  <div className="applied-details">
                    <span>Status: <StatusBadge status={existingApplication?.status || 'submitted'} /></span>
                    {existingApplication?.applied_at && (
                      <span className="applied-date">Submitted on {formatDate(existingApplication.applied_at)}</span>
                    )}
                  </div>
                </div>
              ) : showApplyForm ? (
                <ApplyForm jobId={job.id} onSuccess={handleApplySuccess} />
              ) : (
                <>
                  <p className="apply-prompt">Interested in this position?</p>
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={() => setShowApplyForm(true)}
                  >
                    Apply Now
                  </button>
                </>
              )}
            </div>
          )}

          {!isAuthenticated && job.status === 'open' && (
            <div className="job-detail-apply-cta">
              <p className="apply-prompt">Want to apply for this position?</p>
              <Link to="/register" className="btn btn-primary btn-lg">
                Create an Account to Apply
              </Link>
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={showCloseModal}
        onClose={() => setShowCloseModal(false)}
        onConfirm={handleCloseJob}
        title="Close Job Posting"
        message={`Are you sure you want to close "${job?.title}"? This will stop new applications from being submitted. This action cannot be undone.`}
        confirmText="Close Job"
        cancelText="Keep Open"
        variant="danger"
        loading={closing}
      />
    </div>
  );
}

export default JobDetailPage;

