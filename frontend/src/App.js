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

  console.log('ProtectedRoute check:', { user: user?.id, loading, isAuthenticated: !!user });

  if (loading) {
    console.log('ProtectedRoute: Still loading, showing spinner');
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading f01i.ai...</p>
        </div>
      </div>
    );
  }

  if (user) {
    console.log('ProtectedRoute: User authenticated, rendering app');
    return children;
  } else {
    console.log('ProtectedRoute: User not authenticated, redirecting to /login');
    return <Navigate to="/login" replace />;
  }
};

// Public Route Component (redirects to app if authenticated)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  console.log('PublicRoute check:', { user: user?.id, loading, isAuthenticated: !!user });

  if (loading) {
    console.log('PublicRoute: Still loading, showing spinner');
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading f01i.ai...</p>
        </div>
      </div>
    );
  }

  if (user) {
    console.log('PublicRoute: User authenticated, redirecting to /app');
    return <Navigate to="/app" replace />;
  } else {
    console.log('PublicRoute: User not authenticated, showing login screen');
    return children;
  }
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
            <Route path="/login" element={
              <PublicRoute>
                <RealAuthScreen />
              </PublicRoute>
            } />
            
            {/* Legacy auth route redirect */}
            <Route path="/auth" element={<Navigate to="/login" replace />} />
            
            {/* Auth callback routes */}
            <Route path="/login/callback" element={<AuthCallback />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            
            {/* Legacy callback route redirect */}
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
