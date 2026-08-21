import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import { Shell } from './components/layout/Shell';

// Auth & Shared Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { LiveMonitoringPage } from './pages/shared/LiveMonitoringPage';
import { ProfilePage } from './pages/shared/ProfilePage';
import { NotificationCenterPage } from './pages/shared/NotificationCenterPage';

// Student Pages
import { StudentDashboard } from './pages/student/StudentDashboard';
import { StudyGoalsPage } from './pages/student/StudyGoalsPage';
import { StudentAnalyticsPage } from './pages/student/StudentAnalyticsPage';
import { ActivityHistoryPage } from './pages/student/ActivityHistoryPage';
import { RecommendationsPage } from './pages/student/RecommendationsPage';
import { ReportsPage } from './pages/student/ReportsPage';
import { FocusTimerPage } from './pages/student/FocusTimerPage';
import { StudentSettingsPage } from './pages/student/StudentSettingsPage';
import { MessagesPage } from './pages/student/MessagesPage';

// Parent Pages
import { ParentDashboardPage } from './pages/parent/ParentDashboardPage';
import { ParentAcademicPage } from './pages/parent/ParentAcademicPage';
import { ParentDigitalBehaviorPage } from './pages/parent/ParentDigitalBehaviorPage';
import { ParentInsightsPage } from './pages/parent/ParentInsightsPage';
import { ParentTimelinePage } from './pages/parent/ParentTimelinePage';
import { ParentNotificationsPage } from './pages/parent/ParentNotificationsPage';
import { ParentControlsPage } from './pages/parent/ParentControlsPage';
import { ParentReportsPage } from './pages/parent/ParentReportsPage';
import { ParentMessagesPage } from './pages/parent/ParentMessagesPage';
import { ParentProfilePage } from './pages/parent/ParentProfilePage';
import { ParentSettingsPage } from './pages/parent/ParentSettingsPage';

// Mentor Pages
import { MentorDashboard } from './pages/mentor/MentorDashboard';
import { MentorPriorityQueuePage } from './pages/mentor/MentorPriorityQueuePage';
import { MentorStudentsPage } from './pages/mentor/MentorStudentsPage';
import { MentorCounselingPage } from './pages/mentor/MentorCounselingPage';
import { MentorMeetingsPage } from './pages/mentor/MentorMeetingsPage';
import { MentorMessagesPage } from './pages/mentor/MentorMessagesPage';
import { MentorReportsPage } from './pages/mentor/MentorReportsPage';
import { MentorNotificationsPage } from './pages/mentor/MentorNotificationsPage';
import { MentorProfilePage } from './pages/mentor/MentorProfilePage';
import { MentorSettingsPage } from './pages/mentor/MentorSettingsPage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { StudentsManagement } from './pages/admin/StudentsManagement';
import { TeachersManagement } from './pages/admin/TeachersManagement';
import { MentorsManagement } from './pages/admin/MentorsManagement';
import { ParentsManagement } from './pages/admin/ParentsManagement';
import { DepartmentsPage } from './pages/admin/DepartmentsPage';
import { AdminAnalyticsPage } from './pages/admin/AdminAnalyticsPage';
import { AdminReportsPage } from './pages/admin/AdminReportsPage';
import { ReportCenterPage } from './pages/admin/ReportCenterPage';
import { AdminSettingsPage } from './pages/admin/AdminSettingsPage';

// Error Pages
import { NotFoundPage } from './components/errors/NotFoundPage';
import { ForbiddenPage } from './components/errors/ForbiddenPage';
import { ServerErrorPage } from './components/errors/ServerErrorPage';

const ProtectedLayout: React.FC<{ children: React.ReactNode; allowedRole?: 'student' | 'parent' | 'mentor' | 'admin' }> = ({ children, allowedRole }) => {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (allowedRole && user && user.role !== 'admin' && user.role !== allowedRole) {
    const redirectPath = user.role === 'parent' ? '/parent/dashboard' : user.role === 'mentor' ? '/mentor/dashboard' : '/student/dashboard';
    return <Navigate to={redirectPath} replace />;
  }

  return <Shell>{children}</Shell>;
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Landing & Auth Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />

              {/* Shared Routes */}
              <Route path="/profile" element={<ProtectedLayout><ProfilePage /></ProtectedLayout>} />
              <Route path="/notifications" element={<ProtectedLayout><NotificationCenterPage /></ProtectedLayout>} />

              {/* Student Routes */}
              <Route path="/student" element={<Navigate to="/student/dashboard" replace />} />
              <Route path="/student/dashboard" element={<ProtectedLayout allowedRole="student"><StudentDashboard /></ProtectedLayout>} />
              <Route path="/student/monitoring" element={<ProtectedLayout allowedRole="student"><LiveMonitoringPage /></ProtectedLayout>} />
              <Route path="/student/analytics" element={<ProtectedLayout allowedRole="student"><StudentAnalyticsPage /></ProtectedLayout>} />
              <Route path="/student/goals" element={<ProtectedLayout allowedRole="student"><StudyGoalsPage /></ProtectedLayout>} />
              <Route path="/student/history" element={<ProtectedLayout allowedRole="student"><ActivityHistoryPage /></ProtectedLayout>} />
              <Route path="/student/recommendations" element={<ProtectedLayout allowedRole="student"><RecommendationsPage /></ProtectedLayout>} />
              <Route path="/student/reports" element={<ProtectedLayout allowedRole="student"><ReportsPage /></ProtectedLayout>} />
              <Route path="/student/timer" element={<ProtectedLayout allowedRole="student"><FocusTimerPage /></ProtectedLayout>} />
              <Route path="/student/settings" element={<ProtectedLayout allowedRole="student"><StudentSettingsPage /></ProtectedLayout>} />
              <Route path="/student/messages" element={<ProtectedLayout allowedRole="student"><MessagesPage /></ProtectedLayout>} />

              {/* Parent Routes */}
              <Route path="/parent" element={<Navigate to="/parent/dashboard" replace />} />
              <Route path="/parent/dashboard" element={<ProtectedLayout allowedRole="parent"><ParentDashboardPage /></ProtectedLayout>} />
              <Route path="/parent/monitoring" element={<Navigate to="/parent/dashboard" replace />} />
              <Route path="/parent/academic" element={<ProtectedLayout allowedRole="parent"><ParentAcademicPage /></ProtectedLayout>} />
              <Route path="/parent/digital-behavior" element={<ProtectedLayout allowedRole="parent"><ParentDigitalBehaviorPage /></ProtectedLayout>} />
              <Route path="/parent/insights" element={<ProtectedLayout allowedRole="parent"><ParentInsightsPage /></ProtectedLayout>} />
              <Route path="/parent/timeline" element={<ProtectedLayout allowedRole="parent"><ParentTimelinePage /></ProtectedLayout>} />
              <Route path="/parent/notifications" element={<ProtectedLayout allowedRole="parent"><ParentNotificationsPage /></ProtectedLayout>} />
              <Route path="/parent/controls" element={<ProtectedLayout allowedRole="parent"><ParentControlsPage /></ProtectedLayout>} />
              <Route path="/parent/reports" element={<ProtectedLayout allowedRole="parent"><ParentReportsPage /></ProtectedLayout>} />
              <Route path="/parent/messages" element={<ProtectedLayout allowedRole="parent"><ParentMessagesPage /></ProtectedLayout>} />
              <Route path="/parent/profile" element={<ProtectedLayout allowedRole="parent"><ParentProfilePage /></ProtectedLayout>} />
              <Route path="/parent/settings" element={<ProtectedLayout allowedRole="parent"><ParentSettingsPage /></ProtectedLayout>} />

              {/* Mentor Routes */}
              <Route path="/mentor" element={<Navigate to="/mentor/dashboard" replace />} />
              <Route path="/mentor/dashboard" element={<ProtectedLayout allowedRole="mentor"><MentorDashboard /></ProtectedLayout>} />
              <Route path="/mentor/priority-queue" element={<ProtectedLayout allowedRole="mentor"><MentorPriorityQueuePage /></ProtectedLayout>} />
              <Route path="/mentor/students" element={<ProtectedLayout allowedRole="mentor"><MentorStudentsPage /></ProtectedLayout>} />
              <Route path="/mentor/counseling" element={<ProtectedLayout allowedRole="mentor"><MentorCounselingPage /></ProtectedLayout>} />
              <Route path="/mentor/meetings" element={<ProtectedLayout allowedRole="mentor"><MentorMeetingsPage /></ProtectedLayout>} />
              <Route path="/mentor/messages" element={<ProtectedLayout allowedRole="mentor"><MentorMessagesPage /></ProtectedLayout>} />
              <Route path="/mentor/reports" element={<ProtectedLayout allowedRole="mentor"><MentorReportsPage /></ProtectedLayout>} />
              <Route path="/mentor/notifications" element={<ProtectedLayout allowedRole="mentor"><MentorNotificationsPage /></ProtectedLayout>} />
              <Route path="/mentor/profile" element={<ProtectedLayout allowedRole="mentor"><MentorProfilePage /></ProtectedLayout>} />
              <Route path="/mentor/settings" element={<ProtectedLayout allowedRole="mentor"><MentorSettingsPage /></ProtectedLayout>} />

              {/* Admin Routes */}
              <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="/admin/dashboard" element={<ProtectedLayout allowedRole="admin"><AdminDashboard /></ProtectedLayout>} />
              <Route path="/admin/live-monitoring" element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="/admin/students" element={<ProtectedLayout allowedRole="admin"><StudentsManagement /></ProtectedLayout>} />
              <Route path="/admin/teachers" element={<ProtectedLayout allowedRole="admin"><TeachersManagement /></ProtectedLayout>} />
              <Route path="/admin/mentors" element={<ProtectedLayout allowedRole="admin"><MentorsManagement /></ProtectedLayout>} />
              <Route path="/admin/parents" element={<ProtectedLayout allowedRole="admin"><ParentsManagement /></ProtectedLayout>} />
              <Route path="/admin/departments" element={<ProtectedLayout allowedRole="admin"><DepartmentsPage /></ProtectedLayout>} />
              <Route path="/admin/analytics" element={<ProtectedLayout allowedRole="admin"><AdminAnalyticsPage /></ProtectedLayout>} />
              <Route path="/admin/reports" element={<ProtectedLayout allowedRole="admin"><AdminReportsPage /></ProtectedLayout>} />
              <Route path="/admin/report-center" element={<ProtectedLayout allowedRole="admin"><ReportCenterPage /></ProtectedLayout>} />
              <Route path="/admin/settings" element={<ProtectedLayout allowedRole="admin"><AdminSettingsPage /></ProtectedLayout>} />

              {/* Error Routes */}
              <Route path="/403" element={<ProtectedLayout><ForbiddenPage /></ProtectedLayout>} />
              <Route path="/500" element={<ProtectedLayout><ServerErrorPage /></ProtectedLayout>} />
              <Route path="*" element={<ProtectedLayout><NotFoundPage /></ProtectedLayout>} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
};

export default App;
