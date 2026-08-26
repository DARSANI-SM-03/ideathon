import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { UserRole, UserProfile } from '../types';
import { API_BASE_URL } from '../services/api';
import {
  BrainCircuit,
  Lock,
  User,
  Shield,
  GraduationCap,
  HeartHandshake,
  Award,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  Building,
  Mail,
  Phone,
  BookOpen,
  Sparkles,
  Zap,
  Sun,
  Moon
} from 'lucide-react';
import { Modal } from '../components/Modal';

export const LoginPage: React.FC = () => {
  const { continueAuth, setSessionTokens, isAuthenticated, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const queryRole = searchParams.get('role') as UserRole | null;
  const [role, setRole] = useState<UserRole>(
    queryRole && ['student', 'parent', 'mentor', 'admin', 'teacher'].includes(queryRole) ? queryRole : 'student'
  );

  const [stage, setStage] = useState<'initial' | 'registration'>('initial');
  const [showPassword, setShowPassword] = useState(false);

  // Single Entry Form states (Start completely empty - zero demo data)
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [forgotModalOpen, setForgotModalOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Registration form states (Empty defaults)
  const [fullName, setFullName] = useState('');
  const [studentId, setStudentId] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [collegeName, setCollegeName] = useState('Global Institute of Technology');
  const [department, setDepartment] = useState('Computer Science');
  const [semester, setSemester] = useState<number>(1);
  const [year, setYear] = useState<number>(1);
  const [institutionType, setInstitutionType] = useState('college');
  const [phone, setPhone] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  // Forgot / Reset Password state
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [newResetPassword, setNewResetPassword] = useState('');
  const [resetStage, setResetStage] = useState<'request' | 'reset'>('request');

  const getRedirectPath = (r: UserRole) => {
    switch (r) {
      case 'parent': return '/parent/dashboard';
      case 'mentor': return '/mentor/dashboard';
      case 'teacher': return '/teacher/dashboard';
      case 'admin': return '/admin/dashboard';
      default: return '/student/dashboard';
    }
  };

  // Redirect if session is already active
  useEffect(() => {
    if (isAuthenticated && user && user.role) {
      navigate(getRedirectPath(user.role), { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const handleRoleChange = (newRole: UserRole) => {
    setRole(newRole);
    setSearchParams({ role: newRole }, { replace: true });
    setErrorMsg('');
    setSuccessMsg('');
    setStage('initial');
  };

  useEffect(() => {
    if (queryRole && ['student', 'parent', 'mentor', 'admin', 'teacher'].includes(queryRole)) {
      setRole(queryRole);
    }
  }, [queryRole]);

  useEffect(() => {
    setErrorMsg('');
    setSuccessMsg('');
  }, [role, stage]);

  // Unified Continue Action
  const handleContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    if (!identifier.trim() || !password.trim()) {
      setErrorMsg('Please enter both your Email / ID and password.');
      setLoading(false);
      return;
    }

    try {
      const res = await continueAuth(identifier, password, role);
      if (res.status === 'authenticated' && res.redirect) {
        setSuccessMsg('Welcome back! Signing you in...');
        setTimeout(() => {
          navigate(res.redirect || getRedirectPath(role));
        }, 500);
      } else if (res.status === 'registration_required') {
        if (role === 'admin') {
          setErrorMsg('Admin account not found. Please contact the system administrator.');
        } else {
          setStage('registration');
          if (identifier.includes('@')) {
            setRegEmail(identifier);
          } else {
            setStudentId(identifier);
            setEmployeeId(identifier);
          }
          setSuccessMsg("No StudIQ account found. Let's create your account.");
        }
      } else {
        setErrorMsg(res.message || 'Invalid credentials. Please check your ID/email and password.');
      }
    } catch (err: any) {
      setErrorMsg('Unable to connect to the authentication server. Please check your network connection.');
    } finally {
      setLoading(false);
    }
  };

  // Role Registration Action
  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    if (!fullName.trim() || !regEmail.trim() || !password.trim()) {
      setErrorMsg('Please fill in all required fields.');
      setLoading(false);
      return;
    }

    if (role === 'student' && !studentId.trim()) {
      setErrorMsg('Please enter your Student ID.');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setErrorMsg('Password must be at least 6 characters long.');
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match. Please re-enter your password.');
      setLoading(false);
      return;
    }

    if (!agreedToTerms) {
      setErrorMsg('You must agree to the Terms of Service & Privacy Policy to register.');
      setLoading(false);
      return;
    }

    try {
      let endpoint = '';
      let bodyData: any = {};

      if (role === 'student') {
        endpoint = `${API_BASE_URL}/auth/register/student`;
        bodyData = {
          full_name: fullName,
          student_id: studentId,
          email: regEmail,
          college_name: collegeName,
          department,
          semester: Number(semester),
          year: Number(year),
          password,
          parent_email: regEmail,
          parent_phone: phone
        };
      } else if (role === 'parent') {
        endpoint = `${API_BASE_URL}/auth/register/parent`;
        bodyData = {
          full_name: fullName,
          email: regEmail,
          phone,
          password
        };
      } else if (role === 'mentor' || role === 'teacher') {
        endpoint = `${API_BASE_URL}/auth/register/mentor`;
        bodyData = {
          full_name: fullName,
          employee_id: employeeId || studentId,
          email: regEmail,
          department,
          password
        };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
      });

      const resData = await res.json().catch(() => ({}));
      if (res.ok) {
        if (resData.access_token) {
          const userProfile: UserProfile = {
            id: resData.user_id,
            user_identifier: resData.user_identifier,
            name: resData.name || fullName,
            email: resData.email || regEmail,
            role: role,
            department: department || 'General'
          };
          setSessionTokens(resData.access_token, userProfile);
          setSuccessMsg('Account created successfully. Signing you in...');
          setTimeout(() => {
            navigate(resData.redirect || getRedirectPath(role));
          }, 800);
        } else {
          setSuccessMsg('Account created successfully. Signing you in...');
          setTimeout(() => {
            navigate(getRedirectPath(role));
          }, 800);
        }
      } else {
        const detail = resData.detail || '';
        if (detail.includes('ACCOUNT_ALREADY_EXISTS') || detail.includes('already registered') || detail.includes('already exists')) {
          setErrorMsg('An account with these details already exists. Please sign in.');
          setStage('initial');
          if (regEmail) setIdentifier(regEmail);
          else if (studentId) setIdentifier(studentId);
          else if (employeeId) setIdentifier(employeeId);
        } else {
          setErrorMsg(detail || 'Registration failed. Please check your details and try again.');
        }
      }
    } catch (err: any) {
      setErrorMsg('Unable to complete registration. Please check your network connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotEmail.trim()) {
      setErrorMsg('Please enter your email address.');
      return;
    }
    setForgotLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: forgotEmail })
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.reset_token) {
        setResetToken(data.reset_token);
        setResetStage('reset');
        setSuccessMsg("Check your email. We've sent instructions to reset your password.");
      } else {
        setSuccessMsg("Check your email. We've sent instructions to reset your password.");
      }
    } catch (e) {
      setErrorMsg('Failed to process password reset request.');
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newResetPassword || newResetPassword.length < 6) {
      setErrorMsg('New password must be at least 6 characters long.');
      return;
    }
    setForgotLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reset_token: resetToken, new_password: newResetPassword })
      });
      if (res.ok) {
        setForgotModalOpen(false);
        setResetStage('request');
        setSuccessMsg('Password successfully reset! You can now log in with your new password.');
        setPassword(newResetPassword);
      } else {
        setErrorMsg('Invalid or expired password reset token.');
      }
    } catch (e) {
      setErrorMsg('Error resetting password.');
    } finally {
      setForgotLoading(false);
    }
  };

  const roleConfigs = {
    student: {
      title: 'Student Portal Access',
      subtitle: 'Monitor active focus, burnout telemetry & personalized recommendations.',
      accentColor: 'from-emerald-500 to-brand-600',
      buttonBg: 'bg-emerald-500 hover:bg-emerald-600 shadow-emerald-500/25',
      icon: GraduationCap,
      label: 'Student ID / College Email',
      placeholder: 'e.g. STU-2026-001 or alex.mercer@studiq.edu',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      activeTab: 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/30 font-bold',
      demoHelp: 'Demo ID: STU-2026-001'
    },
    parent: {
      title: 'Parent & Guardian Portal',
      subtitle: 'Visual wellness insights, digital balance & mentor communication.',
      accentColor: 'from-brand-500 to-indigo-600',
      buttonBg: 'bg-brand-600 hover:bg-brand-500 shadow-brand-500/25',
      icon: HeartHandshake,
      label: 'Registered Parent Email',
      placeholder: 'parent.mercer@gmail.com',
      badgeColor: 'bg-brand-500/10 text-brand-400 border-brand-500/30',
      activeTab: 'bg-brand-500 text-white shadow-lg shadow-brand-500/30 font-bold',
      demoHelp: 'Demo Email: parent.mercer@gmail.com'
    },
    mentor: {
      title: 'Faculty Mentor Portal',
      subtitle: 'High-risk student queue, fatigue alerts & intervention tracking.',
      accentColor: 'from-amber-500 to-orange-600',
      buttonBg: 'bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-amber-500/25',
      icon: Award,
      label: 'Employee ID / Faculty Email',
      placeholder: 'e.g. EMP-2026-001 or vance@studiq.edu',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      activeTab: 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/30 font-bold',
      demoHelp: 'Demo ID: EMP-2026-001'
    },
    admin: {
      title: 'Institutional Admin Console',
      subtitle: 'System health, mentor allocation & departmental analytics.',
      accentColor: 'from-purple-500 to-rose-600',
      buttonBg: 'bg-purple-600 hover:bg-purple-500 shadow-purple-500/25',
      icon: Shield,
      label: 'Username / Official Email',
      placeholder: 'admin or admin@studiq.edu',
      badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      activeTab: 'bg-purple-600 text-white shadow-lg shadow-purple-500/30 font-bold',
      demoHelp: 'Demo Username: admin'
    },
    teacher: {
      title: 'Faculty Mentor Portal',
      subtitle: 'High-risk student queue, fatigue alerts & intervention tracking.',
      accentColor: 'from-amber-500 to-orange-600',
      buttonBg: 'bg-amber-500 hover:bg-amber-600 text-slate-950 shadow-amber-500/25',
      icon: Award,
      label: 'Employee ID / Faculty Email',
      placeholder: 'e.g. EMP-2026-001 or vance@studiq.edu',
      badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      activeTab: 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/30 font-bold',
      demoHelp: 'Demo ID: EMP-2026-001'
    }
  };

  const currentConfig = roleConfigs[role] || roleConfigs.student;
  const RoleIcon = currentConfig.icon;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-4 md:p-8 relative overflow-hidden font-sans bg-grid-pattern">
      {/* Background Mesh Orbs */}
      <div className="absolute top-[-10%] left-[20%] w-[600px] h-[500px] bg-brand-600/15 rounded-full blur-[140px] pointer-events-none animate-pulse-slow" />
      <div className="absolute bottom-[-10%] right-[10%] w-[500px] h-[500px] bg-emerald-500/15 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Navigation */}
      <div className="max-w-6xl w-full mx-auto relative z-10 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-800 transition backdrop-blur-md shadow-md cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4 text-brand-500 dark:text-brand-400" /> Back to Home
        </button>

        <div className="flex items-center gap-4">
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-2 text-xs font-bold shadow-md cursor-pointer"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-brand-500 dark:text-brand-400" />}
            <span className="hidden sm:inline">{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
          </button>

          <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center shadow-md shadow-brand-500/20">
              <BrainCircuit className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-black text-slate-900 dark:text-white tracking-wider">Stud<span className="text-emerald-500 dark:text-emerald-400 font-black">IQ</span></span>
          </div>
        </div>
      </div>

      {/* Main Centered Auth Layout */}
      <div className="max-w-5xl w-full mx-auto relative z-10 my-auto py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Side Role Showcase Card (Visible on Large Screens) */}
        <div className="hidden lg:flex lg:col-span-5 flex-col justify-between space-y-6 glass-card p-8 rounded-3xl border border-slate-800 bg-slate-900/40 backdrop-blur-xl shadow-2xl">
          <div className="space-y-4">
            <div className={`inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr ${currentConfig.accentColor} shadow-xl ring-1 ring-white/20`}>
              <RoleIcon className="w-7 h-7 text-white" />
            </div>

            <div>
              <span className={`text-[10px] font-mono font-bold uppercase tracking-widest px-3 py-1 rounded-full border ${currentConfig.badgeColor}`}>
                {role.toUpperCase()} AUTHENTICATION
              </span>
              <h2 className="text-2xl font-black text-white mt-3 leading-tight">{currentConfig.title}</h2>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed font-medium">
                {currentConfig.subtitle}
              </p>
            </div>
          </div>

          <div className="space-y-3 pt-6 border-t border-slate-800/80">
            <div className="flex items-center gap-3 text-xs text-slate-300 font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Zero-Knowledge Encrypted Auth Session</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-300 font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Real-Time Desktop Agent Telemetry Sync</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-300 font-medium">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Predictive Fatigue & Burnout Protection</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 text-[11px] font-mono text-slate-400 flex items-center justify-between">
            <span>Authentication Security:</span>
            <span className="text-emerald-400 font-bold">256-Bit Encrypted JWT</span>
          </div>
        </div>

        {/* Right Side Glass Form Card */}
        <div className="lg:col-span-7 w-full max-w-md mx-auto space-y-5">
          
          {/* Role Selector Tabs (5 Roles) */}
          <div className="grid grid-cols-5 gap-1 p-1.5 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-xl shadow-xl text-center">
            {(['student', 'parent', 'mentor', 'teacher', 'admin'] as UserRole[]).map((r) => (
              <button
                key={r}
                type="button"
                onClick={() => handleRoleChange(r)}
                className={`py-2 px-1 rounded-xl text-[11px] transition capitalize font-bold ${
                  role === r
                    ? roleConfigs[r]?.activeTab || 'bg-brand-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {r}
              </button>
            ))}
          </div>

          {/* Form Header Title */}
          <div className="text-center">
            <h1 className="text-2xl font-black text-white tracking-tight">
              STUDIQ AUTHENTICATION
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Secure access to your personalized StudIQ portal.
            </p>
          </div>

          {/* Error & Success Messages */}
          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-medium flex items-center gap-2.5 animate-in fade-in">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium flex items-center gap-2.5 animate-in fade-in">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Auth Glass Card */}
          <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-800 bg-slate-900/70 backdrop-blur-xl shadow-2xl space-y-5">
            {stage === 'initial' ? (
              /* SINGLE CONTINUE ENTRY FORM */
              <form onSubmit={handleContinue} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    {role === 'student' ? 'Student ID / Email Address' : role === 'admin' ? 'Username / Official Email' : 'Email / Employee ID'}
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      placeholder={`Enter your registered ${role} Email or ID`}
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition font-medium"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-10 pr-10 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition font-medium"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs pt-1">
                  <label className="flex items-center gap-2 cursor-pointer text-slate-300">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded border-slate-700 bg-slate-950 text-brand-500 focus:ring-0"
                    />
                    Remember session
                  </label>
                  <button
                    type="button"
                    onClick={() => setForgotModalOpen(true)}
                    className="text-slate-400 hover:text-brand-400 transition font-medium"
                  >
                    Forgot Password?
                  </button>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-3.5 rounded-xl text-white text-xs font-black transition flex items-center justify-center gap-2 ${currentConfig.buttonBg}`}
                >
                  {loading ? (
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>Continue →</>
                  )}
                </button>
              </form>
            ) : (
              /* ROLE REGISTRATION FORM (When Account Not Found) */
              <form onSubmit={handleSignUp} className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2">
                  <span className="text-xs font-bold text-slate-300">Create {role.toUpperCase()} Profile</span>
                  <button
                    type="button"
                    onClick={() => setStage('initial')}
                    className="text-[11px] text-slate-400 hover:text-white underline"
                  >
                    ← Change ID/Email
                  </button>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter your full name"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>

                {role === 'student' && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Student ID</label>
                      <input
                        type="text"
                        value={studentId}
                        onChange={(e) => setStudentId(e.target.value)}
                        placeholder="e.g. STU-2026-001"
                        className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 mb-1">Department</label>
                      <input
                        type="text"
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                        required
                      />
                    </div>
                  </div>
                )}

                {(role === 'mentor' || role === 'teacher') && (
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Employee ID</label>
                    <input
                      type="text"
                      value={employeeId}
                      onChange={(e) => setEmployeeId(e.target.value)}
                      placeholder="e.g. EMP-2026-001"
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-white"
                      required
                    />
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
                  <input
                    type="email"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="user@studiq.edu"
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Min. 6 characters"
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Confirm Password</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Repeat password"
                      className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                      required
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-1 text-xs text-slate-300">
                  <input
                    type="checkbox"
                    id="termsCheck"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                    className="rounded border-slate-700 bg-slate-950 text-brand-500 focus:ring-0"
                    required
                  />
                  <label htmlFor="termsCheck" className="cursor-pointer">
                    I agree to the <span className="text-brand-400 underline">Terms of Service</span> & <span className="text-brand-400 underline">Privacy Policy</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full py-3.5 rounded-xl text-white text-xs font-black transition flex items-center justify-center gap-2 ${currentConfig.buttonBg}`}
                >
                  {loading ? (
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <>Create Account & Sign In →</>
                  )}
                </button>
              </form>
            )}
          </div>

        </div>

      </div>

      {/* Footer Info */}
      <footer className="max-w-6xl w-full mx-auto py-4 text-center text-xs text-slate-500 font-mono relative z-10">
        StudIQ Digital Behaviour Intelligence Platform • Predict • Prevent • Perform
      </footer>

      {/* FORGOT & RESET PASSWORD MODAL */}
      {forgotModalOpen && (
        <Modal title={resetStage === 'request' ? "Forgot Password" : "Reset Password"} isOpen={forgotModalOpen} onClose={() => { setForgotModalOpen(false); setResetStage('request'); }}>
          {resetStage === 'request' ? (
            <form onSubmit={handleForgotPassword} className="space-y-4">
              <p className="text-xs text-slate-300">
                Enter your registered email address below. We will send you password reset instructions.
              </p>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  placeholder="e.g. alex.mercer@studiq.edu"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setForgotModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold flex items-center gap-2"
                >
                  {forgotLoading ? <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : "Send Reset Link"}
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
                Check your email. We've sent instructions to reset your password.
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Reset Token</label>
                <input
                  type="text"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  placeholder="Paste reset token"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">New Password</label>
                <input
                  type="password"
                  value={newResetPassword}
                  onChange={(e) => setNewResetPassword(e.target.value)}
                  placeholder="Enter new password (min. 6 characters)"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => { setForgotModalOpen(false); setResetStage('request'); }}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2"
                >
                  {forgotLoading ? <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : "Reset Password"}
                </button>
              </div>
            </form>
          )}
        </Modal>
      )}
    </div>
  );
};
