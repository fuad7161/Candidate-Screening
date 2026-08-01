import api from './api';

export const authService = {
  async register(userData) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  async login(credentials) {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },

  async refresh(refreshToken) {
    const response = await api.post('/auth/refresh/', { refresh: refreshToken });
    return response.data;
  },

  async me() {
    const response = await api.get('/auth/me/');
    return response.data;
  },
};

export default authService;
