import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import jobsService from '../services/jobsService';
import JobCard from '../components/JobCard';
import useAuth from '../hooks/useAuth';
import '../styles/JobsListPage.css';

function JobsListPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated, role } = useAuth();

  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await jobsService.listJobs({ page: currentPage });
        setJobs(data.results || data);
        setTotalCount(data.count || (data.results ? data.results.length : data.length));
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
        setError('Failed to load job listings. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [currentPage]);

  const totalPages = Math.ceil(totalCount / 20) || 1;

  const goToPage = (page) => {
    setSearchParams({ page: String(page) });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading job listings...</p>
      </div>
    );
  }

  return (
    <div className="jobs-list-page">
      <div className="jobs-list-header">
        <div className="jobs-list-header-text">
          <h1 className="jobs-list-title">Open Positions</h1>
          <p className="jobs-list-subtitle">
            {totalCount} {totalCount === 1 ? 'opportunity' : 'opportunities'} available
          </p>
        </div>
        {isAuthenticated && role === 'recruiter' && (
          <Link to="/dashboard/jobs/new" className="btn btn-primary">
            + Post a Job
          </Link>
        )}
      </div>

      {error && <div className="error-alert">{error}</div>}

      {jobs.length === 0 && !error ? (
        <div className="jobs-empty-state">
          <div className="empty-icon">📋</div>
          <h3>No open positions right now</h3>
          <p>New opportunities are added regularly. Check back soon!</p>
          {isAuthenticated && role === 'recruiter' && (
            <Link to="/dashboard/jobs/new" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Post the First Job
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="jobs-grid">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
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
    </div>
  );
}

export default JobsListPage;
