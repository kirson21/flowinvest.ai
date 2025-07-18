import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext'; // Keep the old AppProvider for compatibility
import RealAuthScreen from './components/auth/RealAuthScreen';
import AuthCallback from './components/auth/AuthCallback';
import MainApp from './components/MainApp';
import { Loader2 } from 'lucide-react';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FAECEC] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading FlowinvestAI...</p>
        </div>
      </div>
    );
  }

  return user ? children : <Navigate to="/auth" replace />;
};

// Public Route Component (redirects to app if authenticated)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FAECEC] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading Flow Invest...</p>
        </div>
      </div>
    );
  }

  return user ? <Navigate to="/app" replace /> : children;
};

// Integration component that bridges old and new auth
const AppWithAuth = () => {
  const { user } = useAuth();
  
  return (
    <AppProvider initialUser={user}>
      <MainApp />
    </AppProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route path="/auth" element={
              <PublicRoute>
                <RealAuthScreen />
              </PublicRoute>
            } />
            
            {/* Auth callback route */}
            <Route path="/auth/callback" element={<AuthCallback />} />
            
            {/* Protected routes */}
            <Route path="/app" element={
              <ProtectedRoute>
                <AppWithAuth />
              </ProtectedRoute>
            } />
            
            {/* Dashboard redirect */}
            <Route path="/dashboard" element={<Navigate to="/app" replace />} />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/app" replace />} />
            
            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
