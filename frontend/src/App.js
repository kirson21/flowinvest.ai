import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext'; // Keep the old AppProvider for compatibility
import RealAuthScreen from './components/auth/RealAuthScreen';
import AuthCallback from './components/auth/AuthCallback';
import MainApp from './components/MainApp';
import PersonalizedApp from './components/PersonalizedApp';
import PublicUserProfile from './components/public/PublicUserProfile';
import PublicBotDetails from './components/public/PublicBotDetails';
import PublicMarketplaceProduct from './components/public/PublicMarketplaceProduct';
import PublicFeedPost from './components/public/PublicFeedPost';
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
            {/* Public routes - available to everyone */}
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
            
            {/* Public URL routes - Direct section access for unauthenticated users */}
            <Route path="/marketplace" element={<Navigate to="/app?tab=portfolios" replace />} />
            <Route path="/bots" element={<Navigate to="/app?tab=bots" replace />} />
            <Route path="/feed" element={<Navigate to="/app?tab=feed" replace />} />
            <Route path="/settings" element={<Navigate to="/app?tab=settings" replace />} />
            
            {/* Public resource URLs */}
            <Route path="/marketplace/:slug" element={<PublicMarketplaceProduct />} />
            <Route path="/bots/:slug" element={<PublicBotDetails />} />
            <Route path="/feed/:slug" element={<PublicFeedPost />} />
            
            {/* Personalized authenticated user routes */}
            <Route path="/:displayName/feed" element={
              <ProtectedRoute>
                <PersonalizedApp section="feed" />
              </ProtectedRoute>
            } />
            <Route path="/:displayName/bots" element={
              <ProtectedRoute>
                <PersonalizedApp section="bots" />
              </ProtectedRoute>
            } />
            <Route path="/:displayName/marketplace" element={
              <ProtectedRoute>
                <PersonalizedApp section="portfolios" />
              </ProtectedRoute>
            } />
            <Route path="/:displayName/settings" element={
              <ProtectedRoute>
                <PersonalizedApp section="settings" />
              </ProtectedRoute>
            } />
            
            {/* Legacy protected routes - redirect to personalized URLs */}
            <Route path="/app" element={
              <ProtectedRoute>
                <PersonalizedRedirect />
              </ProtectedRoute>
            } />
            
            {/* Dashboard redirect */}
            <Route path="/dashboard" element={<Navigate to="/app" replace />} />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/app" replace />} />
            
            {/* User profile URLs - must be last to avoid conflicts */}
            <Route path="/:displayName" element={<PublicUserProfile />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

// Component to redirect /app to personalized URL
const PersonalizedRedirect = () => {
  const { user } = useAuth();
  const [profile, setProfile] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const loadProfile = async () => {
      if (user?.id) {
        try {
          // Get user profile to find display_name
          const { data: profileData } = await import('./lib/supabase').then(module => 
            module.supabase.from('user_profiles').select('display_name').eq('user_id', user.id).single()
          );
          setProfile(profileData);
        } catch (error) {
          console.error('Error loading profile for redirect:', error);
        }
      }
      setLoading(false);
    };

    loadProfile();
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Get the tab parameter if any
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get('tab') || 'feed';

  // Redirect to personalized URL
  const displayName = profile?.display_name || 'user';
  const personalizedUrl = `/${encodeURIComponent(displayName)}/${tab}`;
  
  return <Navigate to={personalizedUrl} replace />;
};

export default App;
