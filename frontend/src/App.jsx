import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import JobsListPage from './pages/JobsListPage';
import JobDetailPage from './pages/JobDetailPage';
import RecruiterDashboardPage from './pages/RecruiterDashboardPage';
import JobFormPage from './pages/JobFormPage';
import MyApplicationsPage from './pages/MyApplicationsPage';
import ApplicationsReviewPage from './pages/ApplicationsReviewPage';
import { ProtectedRoute, RecruiterRoute, CandidateRoute } from './routes';
import './App.css';

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
            <Route path="/jobs" element={<JobsListPage />} />
            <Route path="/jobs/:id" element={<JobDetailPage />} />

            {/* Recruiter-only Routes */}
            <Route element={<RecruiterRoute />}>
              <Route path="/dashboard" element={<RecruiterDashboardPage />} />
              <Route path="/dashboard/jobs/new" element={<JobFormPage />} />
              <Route path="/dashboard/jobs/:id/edit" element={<JobFormPage />} />
              <Route path="/dashboard/jobs/:id/applications" element={<ApplicationsReviewPage />} />
            </Route>

            {/* Candidate-only Routes */}
            <Route element={<CandidateRoute />}>
              <Route path="/my-applications" element={<MyApplicationsPage />} />
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
