import api from './api';

export const jobsService = {
  /**
   * List jobs (public). Candidates/unauthenticated see only open jobs.
   * @param {Object} params - Query params: { page, status }
   */
  async listJobs(params = {}) {
    const response = await api.get('/jobs/', { params });
    return response.data;
  },

  /**
   * Get a single job by ID (public).
   * @param {number|string} id
   */
  async getJob(id) {
    const response = await api.get(`/jobs/${id}/`);
    return response.data;
  },

  /**
   * Create a new job (recruiter only).
   * @param {Object} jobData - { title, description, location, employment_type }
   */
  async createJob(jobData) {
    const response = await api.post('/jobs/', jobData);
    return response.data;
  },

  /**
   * Update a job (recruiter, owner only).
   * @param {number|string} id
   * @param {Object} jobData - { title, description, location, employment_type }
   */
  async updateJob(id, jobData) {
    const response = await api.put(`/jobs/${id}/`, jobData);
    return response.data;
  },

  /**
   * Close a job (recruiter, owner only).
   * @param {number|string} id
   */
  async closeJob(id) {
    const response = await api.patch(`/jobs/${id}/close/`);
    return response.data;
  },

  /**
   * List recruiter's own jobs (recruiter only).
   * @param {Object} params - Query params: { page, status }
   */
  async listMyJobs(params = {}) {
    const response = await api.get('/jobs/', {
      params: { ...params, mine: 'true' },
    });
    return response.data;
  },
};

export default jobsService;
