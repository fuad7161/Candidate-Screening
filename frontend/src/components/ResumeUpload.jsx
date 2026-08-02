import { useRef, useState } from 'react';
import applicationsService from '../services/applicationsService';
import './ResumeUpload.css';

const MAX_FILE_SIZE = Number(import.meta.env.VITE_MAX_RESUME_SIZE || 5 * 1024 * 1024);
const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx'];

function ResumeUpload({ onUploadSuccess, disabled = false }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setError('');
    setUploadedFile(null);
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setError('Choose a PDF, DOC, or DOCX file.');
      event.target.value = '';
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError('Resume size cannot exceed 5 MB.');
      event.target.value = '';
      return;
    }

    setUploading(true);
    setProgress(0);
    try {
      const upload = await applicationsService.uploadResume(file, setProgress);
      setUploadedFile(upload);
      setProgress(100);
      onUploadSuccess?.(upload);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Resume upload failed. Please try again.');
      event.target.value = '';
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="resume-upload">
      <input
        ref={inputRef}
        id="resume-file"
        type="file"
        accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        onChange={handleFileChange}
        disabled={disabled || uploading}
        className="resume-file-input"
      />
      <button
        type="button"
        className="btn btn-outline resume-picker"
        onClick={() => inputRef.current?.click()}
        disabled={disabled || uploading}
      >
        {uploading ? `Uploading ${progress}%` : uploadedFile ? 'Replace resume' : 'Choose resume'}
      </button>
      {uploading && (
        <div className="upload-progress" aria-label={`Upload progress: ${progress}%`}>
          <span style={{ width: `${progress}%` }} />
        </div>
      )}
      {uploadedFile && <p className="upload-success">✓ {uploadedFile.file_name} uploaded</p>}
      {error && <p className="field-error">{error}</p>}
      <span className="form-help">PDF, DOC, or DOCX; maximum 5 MB.</span>
    </div>
  );
}

export default ResumeUpload;
