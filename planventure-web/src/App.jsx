import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AuthProvider from './context/AuthContext'
import Navigation from './components/Navigation'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import RoleBasedRedirect from './components/RoleBasedRedirect'
import { TalentLeadRoute } from './components/assessment'

// Auth & User Pages
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Users from './pages/Users'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import VerifyEmail from './pages/VerifyEmail'

// Assessment Pages
import Assessments from './pages/Assessments'
import CreateAssessmentTemplate from './pages/CreateAssessmentTemplate'
import AssessmentTemplateDetails from './pages/AssessmentTemplateDetails'
import AssessmentTemplateAnalytics from './pages/AssessmentTemplateAnalytics'
import AssessmentQuestions from './pages/AssessmentQuestions'
import CreateAssessmentQuestion from './pages/CreateAssessmentQuestion'
import ViewAssessmentQuestion from './pages/ViewAssessmentQuestion'
import EditAssessmentQuestion from './pages/EditAssessmentQuestion'
import AssessmentTake from './pages/AssessmentTake'
import AssessmentResult from './pages/AssessmentResult'

import './App.css'
import './styles/print.css'

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-vh-100 bg-light">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />
            <Route path="/verify-email/:token" element={<VerifyEmail />} />
            
            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <AdminRoute>
                  <Users />
                </AdminRoute>
              }
            />
            
            {/* Root route with role-based redirect */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <RoleBasedRedirect />
                </ProtectedRoute>
              }
            />
            
            {/* Catch all route - redirect to root */}
            {/* Assessment routes for talent leads and admins */}
            <Route
              path="/assessments"
              element={
                <TalentLeadRoute>
                  <Assessments />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/templates/create"
              element={
                <TalentLeadRoute>
                  <CreateAssessmentTemplate />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/templates/:templateId"
              element={
                <TalentLeadRoute>
                  <AssessmentTemplateDetails />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/templates/:templateId/analytics"
              element={
                <TalentLeadRoute>
                  <AssessmentTemplateAnalytics />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/questions"
              element={
                <TalentLeadRoute>
                  <AssessmentQuestions />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/questions/create"
              element={
                <TalentLeadRoute>
                  <CreateAssessmentQuestion />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/questions/:questionId"
              element={
                <TalentLeadRoute>
                  <ViewAssessmentQuestion />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/questions/:questionId/edit"
              element={
                <TalentLeadRoute>
                  <EditAssessmentQuestion />
                </TalentLeadRoute>
              }
            />
            <Route
              path="/assessments/results/:assessmentId"
              element={
                <TalentLeadRoute>
                  <AssessmentResult />
                </TalentLeadRoute>
              }
            />

            {/* Public assessment routes (accessible via token) */}
            <Route path="/assessment/:assessmentId" element={<AssessmentTake />} />
            <Route path="/assessment/results/:assessmentId" element={<AssessmentResult />} />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App
