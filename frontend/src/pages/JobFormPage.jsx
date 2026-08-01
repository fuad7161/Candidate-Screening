import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import jobsService from '../services/jobsService';
import '../styles/JobFormPage.css';

const EMPLOYMENT_TYPES = [
  { value: '', label: 'Select type...' },
  { value: 'full_time', label: 'Full Time' },
  { value: 'part_time', label: 'Part Time' },
  { value: 'contract', label: 'Contract' },
  { value: 'internship', label: 'Internship' },
];

function JobFormPage() {
  const { id } = useParams(); // undefined for create, present for edit
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    employment_type: '',
  });
  const [errors, setErrors] = useState({});
  const [generalError, setGeneralError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(isEditing);

  useEffect(() => {
    if (!isEditing) return;

    const fetchJob = async () => {
      setLoading(true);
      try {
        const job = await jobsService.getJob(id);
        setFormData({
          title: job.title || '',
          description: job.description || '',
          location: job.location || '',
          employment_type: job.employment_type || '',
        });
      } catch (err) {
        console.error('Failed to fetch job for editing:', err);
        if (err.response?.status === 404) {
          setGeneralError('Job not found.');
        } else if (err.response?.status === 403) {
          setGeneralError('You do not have permission to edit this job.');
        } else {
          setGeneralError('Failed to load job data.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [id, isEditing]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear field error on change
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title.trim()) newErrors.title = 'Title is required.';
    if (!formData.description.trim()) newErrors.description = 'Description is required.';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError(null);

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setSubmitting(true);
    setErrors({});

    try {
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        location: formData.location.trim() || null,
        employment_type: formData.employment_type || null,
      };

      if (isEditing) {
        await jobsService.updateJob(id, payload);
        navigate(`/jobs/${id}`);
      } else {
        const newJob = await jobsService.createJob(payload);
        navigate(`/jobs/${newJob.id}`);
      }
    } catch (err) {
      console.error('Failed to save job:', err);
      if (err.response?.data) {
        const data = err.response.data;
        // Handle DRF field-level errors
        if (typeof data === 'object') {
          const fieldErrors = {};
          let hasFieldErrors = false;
          for (const [key, val] of Object.entries(data)) {
            if (Array.isArray(val)) {
              fieldErrors[key] = val.join(' ');
              hasFieldErrors = true;
            } else if (typeof val === 'string') {
              fieldErrors[key] = val;
              hasFieldErrors = true;
            }
          }
          if (hasFieldErrors) {
            setErrors(fieldErrors);
          } else {
            setGeneralError(data.detail || data.message || 'Failed to save job.');
          }
        } else {
          setGeneralError('Failed to save job.');
        }
      } else {
        setGeneralError('Network error. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading job data...</p>
      </div>
    );
  }

  if (generalError && isEditing && !formData.title) {
    return (
      <div className="job-form-page">
        <div className="job-detail-error">
          <div className="error-icon">😕</div>
          <h2>Cannot Edit</h2>
          <p>{generalError}</p>
          <Link to="/dashboard" className="btn btn-outline">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="job-form-page">
      <div className="job-form-breadcrumb">
        <Link to="/dashboard" className="breadcrumb-link">Dashboard</Link>
        <span className="breadcrumb-sep">/</span>
        <span className="breadcrumb-current">
          {isEditing ? 'Edit Job' : 'Post New Job'}
        </span>
      </div>

      <div className="job-form-card">
        <div className="job-form-header">
          <h1 className="job-form-title">
            {isEditing ? '✏️ Edit Job Posting' : '✨ Create New Job Posting'}
          </h1>
          <p className="job-form-subtitle">
            {isEditing
              ? 'Update the details of your job posting below.'
              : 'Fill in the details below to publish a new job listing.'}
          </p>
        </div>

        {generalError && (
          <div className="error-alert">{generalError}</div>
        )}

        <form onSubmit={handleSubmit} className="job-form" noValidate>
          <div className="form-group">
            <label htmlFor="job-title">Job Title *</label>
            <input
              type="text"
              id="job-title"
              name="title"
              className={`form-control ${errors.title ? 'is-invalid' : ''}`}
              placeholder="e.g. Senior Backend Engineer"
              value={formData.title}
              onChange={handleChange}
              autoFocus
            />
            {errors.title && <span className="field-error">{errors.title}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="job-location">Location</label>
              <input
                type="text"
                id="job-location"
                name="location"
                className={`form-control ${errors.location ? 'is-invalid' : ''}`}
                placeholder="e.g. Remote, New York, NY"
                value={formData.location}
                onChange={handleChange}
              />
              {errors.location && <span className="field-error">{errors.location}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="job-employment-type">Employment Type</label>
              <select
                id="job-employment-type"
                name="employment_type"
                className={`form-control ${errors.employment_type ? 'is-invalid' : ''}`}
                value={formData.employment_type}
                onChange={handleChange}
              >
                {EMPLOYMENT_TYPES.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              {errors.employment_type && (
                <span className="field-error">{errors.employment_type}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="job-description">Description *</label>
            <textarea
              id="job-description"
              name="description"
              className={`form-control form-textarea ${errors.description ? 'is-invalid' : ''}`}
              placeholder="Describe the role, responsibilities, qualifications, and benefits..."
              rows={10}
              value={formData.description}
              onChange={handleChange}
            />
            {errors.description && (
              <span className="field-error">{errors.description}</span>
            )}
          </div>

          <div className="job-form-actions">
            <Link to={isEditing ? `/jobs/${id}` : '/dashboard'} className="btn btn-outline">
              Cancel
            </Link>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? (
                <span className="btn-loading">
                  <span className="modal-spinner"></span>
                  {isEditing ? 'Saving...' : 'Publishing...'}
                </span>
              ) : isEditing ? (
                'Save Changes'
              ) : (
                'Publish Job'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default JobFormPage;
