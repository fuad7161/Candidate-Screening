import api from './api';

export const applicationsService = {
  /**
   * Submit application to a job (Candidate only).
   * @param {number|string} jobId
   * @param {Object} data - { resume_url, cover_letter }
   */
  async applyToJob(jobId, data) {
    const response = await api.post(`/jobs/${jobId}/apply/`, data);
    return response.data;
  },

  /**
   * List logged-in candidate's applications (Candidate only).
   */
  async getMyApplications() {
    const response = await api.get('/candidates/me/applications/');
    return Array.isArray(response.data) ? response.data : (response.data.results || []);
  },

  /**
   * List applications for a specific job (Recruiter owner only).
   * @param {number|string} jobId
   */
  async getJobApplications(jobId) {
    const response = await api.get(`/jobs/${jobId}/applications/`);
    return Array.isArray(response.data) ? response.data : (response.data.results || []);
  },

  /**
   * Get single application detail (Candidate owner or Recruiter job owner).
   * @param {number|string} id
   */
  async getApplication(id) {
    const response = await api.get(`/applications/${id}/`);
    return response.data;
  },

  /**
   * Update application status (Recruiter job owner only).
   * @param {number|string} id
   * @param {string} status - 'submitted' | 'under_review' | 'shortlisted' | 'rejected' | 'hired'
   */
  async updateStatus(id, status) {
    const response = await api.patch(`/applications/${id}/status/`, { status });
    return response.data;
  },
};

export default applicationsService;
