import { Link } from 'react-router-dom';
import '../styles/JobCard.css';

const EMPLOYMENT_TYPE_LABELS = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  internship: 'Internship',
};

function formatTimeAgo(dateString) {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: diffDays > 365 ? 'numeric' : undefined,
  });
}

function JobCard({ job, showStatus = false, showActions = false, onClose, onEdit }) {
  return (
    <div className={`job-card ${job.status === 'closed' ? 'job-card-closed' : ''}`}>
      <div className="job-card-header">
        <div className="job-card-meta-row">
          {job.recruiter && (
            <span className="job-card-company">
              {job.recruiter.company_name || job.recruiter.full_name}
            </span>
          )}
          <span className="job-card-time">{formatTimeAgo(job.created_at)}</span>
        </div>
        <h3 className="job-card-title">
          <Link to={`/jobs/${job.id}`}>{job.title}</Link>
        </h3>
      </div>

      <div className="job-card-tags">
        {job.location && (
          <span className="job-tag job-tag-location">
            <span className="tag-icon">📍</span>
            {job.location}
          </span>
        )}
        {job.employment_type && (
          <span className="job-tag job-tag-type">
            <span className="tag-icon">💼</span>
            {EMPLOYMENT_TYPE_LABELS[job.employment_type] || job.employment_type}
          </span>
        )}
        {showStatus && (
          <span className={`job-tag job-tag-status job-tag-status-${job.status}`}>
            {job.status === 'open' ? '🟢' : '🔴'} {job.status}
          </span>
        )}
      </div>

      <div className="job-card-footer">
        <div className="job-card-stats">
          {job.applications_count !== undefined && (
            <span className="job-stat">
              <span className="stat-icon">👥</span>
              {job.applications_count} applicant{job.applications_count !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        <div className="job-card-actions">
          {showActions && (
            <Link
              to={`/dashboard/jobs/${job.id}/applications`}
              className="job-action-btn job-action-apps"
              title="Review Applications"
            >
              👥 Review ({job.applications_count || 0})
            </Link>
          )}
          {showActions && job.status === 'open' && (
            <>
              <button
                className="job-action-btn job-action-edit"
                onClick={() => onEdit?.(job)}
                title="Edit job"
              >
                ✏️ Edit
              </button>
              <button
                className="job-action-btn job-action-close"
                onClick={() => onClose?.(job)}
                title="Close job"
              >
                🚫 Close
              </button>
            </>
          )}
          <Link to={`/jobs/${job.id}`} className="job-action-btn job-action-view">
            View →
          </Link>
        </div>
      </div>
    </div>
  );
}

export default JobCard;
