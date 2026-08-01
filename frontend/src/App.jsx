import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import { ProtectedRoute, RecruiterRoute, CandidateRoute } from './routes';
import './App.css';

// Placeholder views for phase 3-6 to verify auth routing
const RecruiterDashboardPlaceholder = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Recruiter Dashboard</h2>
    <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>
      Welcome! You are logged in as a <strong>Recruiter</strong>. Job management features (Phase 3 & 4) will be rendered here.
    </p>
  </div>
);

const CandidateApplicationsPlaceholder = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>My Applications</h2>
    <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>
      Welcome! You are logged in as a <strong>Candidate</strong>. Application tracking features (Phase 5 & 6) will be rendered here.
    </p>
  </div>
);

const JobsListPlaceholder = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h2>Open Job Postings</h2>
    <p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>
      Job postings list page. Job management UI (Phase 4) will be rendered here.
    </p>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<MainLayout />}>
            {/* Public Routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/jobs" element={<JobsListPlaceholder />} />

            {/* Recruiter-only Routes */}
            <Route element={<RecruiterRoute />}>
              <Route path="/dashboard" element={<RecruiterDashboardPlaceholder />} />
              <Route path="/dashboard/jobs/new" element={<RecruiterDashboardPlaceholder />} />
            </Route>

            {/* Candidate-only Routes */}
            <Route element={<CandidateRoute />}>
              <Route path="/my-applications" element={<CandidateApplicationsPlaceholder />} />
            </Route>

            {/* General Protected Routes */}
            <Route element={<ProtectedRoute />}>
              {/* Additional authenticated routes will be added in subsequent phases */}
            </Route>

            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
