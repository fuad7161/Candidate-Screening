import { useState } from 'react';
import applicationsService from '../services/applicationsService';
import ResumeUpload from './ResumeUpload';
import './ApplyForm.css';

function ApplyForm({ jobId, onSuccess }) {
  const [resumeUpload, setResumeUpload] = useState(null);
  const [coverLetter, setCoverLetter] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});

    if (!resumeUpload) {
      setFieldErrors({ resume_file: ['Upload your resume before submitting.'] });
      return;
    }

    setSubmitting(true);
    try {
      const data = await applicationsService.applyToJob(jobId, {
        resume_file: resumeUpload.id,
        cover_note: coverLetter.trim(),
      });
      if (onSuccess) onSuccess(data);
    } catch (err) {
      console.error('Failed to submit application:', err);
      if (err.response?.status === 409) {
        setError('You have already applied for this job.');
      } else if (err.response?.data?.error?.fields && Object.keys(err.response.data.error.fields).length) {
        setFieldErrors(err.response.data.error.fields);
      } else if (err.response?.data?.error?.message) {
        setError(err.response.data.error.message);
      } else if (err.response?.data) {
        setFieldErrors(err.response.data);
      } else {
        setError('Failed to submit application. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="apply-form-card">
      <h3 className="apply-form-title">Apply for this Position</h3>
      {error && <div className="error-alert">{error}</div>}
      <form onSubmit={handleSubmit} className="apply-form">
        <div className="form-group">
          <label htmlFor="resume-file">
            Resume <span className="required">*</span>
          </label>
          <ResumeUpload
            disabled={submitting}
            onUploadSuccess={(upload) => {
              setResumeUpload(upload);
              setFieldErrors((previous) => ({ ...previous, resume_file: undefined }));
            }}
          />
          {fieldErrors.resume_file && (
            <span className="field-error">{fieldErrors.resume_file.join(' ')}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="cover_letter">Cover Letter (Optional)</label>
          <textarea
            id="cover_letter"
            className={`form-control ${fieldErrors.cover_note ? 'is-invalid' : ''}`}
            placeholder="Tell the recruiter why you're a great fit for this role..."
            rows="4"
            value={coverLetter}
            onChange={(e) => setCoverLetter(e.target.value)}
            disabled={submitting}
          />
          {fieldErrors.cover_note && (
            <span className="field-error">{fieldErrors.cover_note.join(' ')}</span>
          )}
        </div>

        <button type="submit" className="btn btn-primary btn-lg" disabled={submitting}>
          {submitting ? 'Submitting Application...' : 'Submit Application'}
        </button>
      </form>
    </div>
  );
}

export default ApplyForm;
