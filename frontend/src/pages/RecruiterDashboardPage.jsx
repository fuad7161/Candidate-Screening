import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import jobsService from '../services/jobsService';
import JobCard from '../components/JobCard';
import Modal from '../components/Modal';
import useAuth from '../hooks/useAuth';
import '../styles/RecruiterDashboard.css';

function RecruiterDashboardPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchParams, setSearchParams] = useSearchParams();
  const [closeTarget, setCloseTarget] = useState(null);
  const [closing, setClosing] = useState(false);
  const navigate = useNavigate();

  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: currentPage };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const data = await jobsService.listMyJobs(params);
      setJobs(data.results || data);
      setTotalCount(data.count || (data.results ? data.results.length : data.length));
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
      setError('Failed to load your jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [currentPage, statusFilter]);

  const handleCloseJob = async () => {
    if (!closeTarget) return;
    setClosing(true);
    try {
      await jobsService.closeJob(closeTarget.id);
      setCloseTarget(null);
      // Refresh the list
      fetchJobs();
    } catch (err) {
      console.error('Failed to close job:', err);
      setError('Failed to close the job. Please try again.');
    } finally {
      setClosing(false);
    }
  };

  const handleEdit = (job) => {
    navigate(`/dashboard/jobs/${job.id}/edit`);
  };

  const goToPage = (page) => {
    setSearchParams({ page: String(page) });
  };

  const totalPages = Math.ceil(totalCount / 20) || 1;

  // Stats
  const openCount = jobs.filter((j) => j.status === 'open').length;
  const closedCount = jobs.filter((j) => j.status === 'closed').length;

  return (
    <div className="recruiter-dashboard">
      <div className="dashboard-header">
        <div className="dashboard-header-text">
          <h1 className="dashboard-title">Recruiter Dashboard</h1>
          <p className="dashboard-subtitle">Manage your job postings</p>
        </div>
        <Link to="/dashboard/jobs/new" className="btn btn-primary">
          + Post New Job
        </Link>
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-value">{totalCount}</div>
          <div className="stat-label">Total Jobs</div>
        </div>
        <div className="stat-card stat-card-open">
          <div className="stat-value">{openCount}</div>
          <div className="stat-label">Open</div>
        </div>
        <div className="stat-card stat-card-closed">
          <div className="stat-value">{closedCount}</div>
          <div className="stat-label">Closed</div>
        </div>
      </div>

      <div className="dashboard-filter-bar">
        <div className="filter-tabs">
          {['all', 'open', 'closed'].map((filter) => (
            <button
              key={filter}
              className={`filter-tab ${statusFilter === filter ? 'active' : ''}`}
              onClick={() => {
                setStatusFilter(filter);
                setSearchParams({ page: '1' });
              }}
            >
              {filter === 'all' ? 'All Jobs' : filter === 'open' ? '🟢 Open' : '🔴 Closed'}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-alert">{error}</div>}

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading your jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="jobs-empty-state">
          <div className="empty-icon">📝</div>
          <h3>
            {statusFilter === 'all'
              ? "You haven't posted any jobs yet"
              : `No ${statusFilter} jobs found`}
          </h3>
          <p>
            {statusFilter === 'all'
              ? 'Get started by creating your first job posting.'
              : 'Try a different filter.'}
          </p>
          {statusFilter === 'all' && (
            <Link to="/dashboard/jobs/new" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Post Your First Job
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="jobs-grid">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                showStatus={true}
                showActions={true}
                onClose={(j) => setCloseTarget(j)}
                onEdit={handleEdit}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="pagination-btn"
                disabled={currentPage <= 1}
                onClick={() => goToPage(currentPage - 1)}
              >
                ← Previous
              </button>
              <span className="pagination-info">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="pagination-btn"
                disabled={currentPage >= totalPages}
                onClick={() => goToPage(currentPage + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      <Modal
        isOpen={!!closeTarget}
        onClose={() => setCloseTarget(null)}
        onConfirm={handleCloseJob}
        title="Close Job Posting"
        message={`Are you sure you want to close "${closeTarget?.title}"? This will stop new applications. This action cannot be undone.`}
        confirmText="Close Job"
        cancelText="Keep Open"
        variant="danger"
        loading={closing}
      />
    </div>
  );
}

export default RecruiterDashboardPage;
