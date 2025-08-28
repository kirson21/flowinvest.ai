import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import { supabase } from '../lib/supabase';
import BottomNav from './navigation/BottomNav';
import AIFeed from './feed/AIFeed';
import TradingBots from './bots/TradingBots';
import Portfolios from './portfolios/Portfolios';
import Settings from './settings/Settings';
import { Loader2 } from 'lucide-react';

const PersonalizedApp = ({ section = 'feed' }) => {
  const { displayName } = useParams();
  const { user } = useAuth();
  const { setActiveTab } = useApp();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isOwner, setIsOwner] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      if (!displayName) {
        setLoading(false);
        return;
      }

      try {
        // Get the profile for this display name
        const { data: profileData } = await supabase
          .from('user_profiles')
          .select('user_id, display_name')
          .eq('display_name', displayName)
          .single();

        if (profileData) {
          setProfile(profileData);
          // Check if this is the current user's profile
          setIsOwner(user?.id === profileData.user_id);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [displayName, user]);

  // Set the active tab based on section
  useEffect(() => {
    if (section) {
      setActiveTab(section);
    }
  }, [section, setActiveTab]);



  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading profile...</p>
        </div>
      </div>
    );
  }

  // If profile not found, redirect to user's own profile or 404
  if (!profile) {
    if (user?.id) {
      // Try to load user's own profile and redirect
      return <Navigate to="/app" replace />;
    } else {
      return <Navigate to="/login" replace />;
    }
  }

  // If not the owner, show unauthorized message (could be changed to allow viewing others)
  if (!isOwner) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center p-4">
        <div className="text-center bg-white rounded-lg shadow-lg p-8 max-w-md">
          <h2 className="text-xl font-semibold mb-4">Access Restricted</h2>
          <p className="text-gray-600 mb-6">
            You can only access your own personalized app pages.
          </p>
          <button
            onClick={() => navigate('/app')}
            className="bg-[#0097B2] text-white px-6 py-2 rounded-lg hover:bg-[#008299] transition-colors"
          >
            Go to Your App
          </button>
        </div>
      </div>
    );
  }

  const renderActiveSection = () => {
    switch (section) {
      case 'feed':
        return <AIFeed />;
      case 'bots':
        return <TradingBots />;
      case 'portfolios':
        return <Portfolios />;
      case 'settings':
        return <Settings />;
      default:
        return <AIFeed />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white dark:from-[#474545] dark:to-gray-900">
      <div className="relative">
        {/* Main content with proper bottom padding */}
        <div className="pb-20 sm:pb-16 md:pb-12 lg:pb-8 overflow-x-hidden">
          {renderActiveSection()}
        </div>
        
        {/* Use original BottomNav component */}
        <BottomNav />
      </div>
    </div>
  );
};

// Custom Bottom Navigation that uses personalized URLs
const PersonalizedBottomNav = ({ displayName, activeSection, onTabChange }) => {
  const tabs = [
    { id: 'feed', label: 'AI Feed', icon: '📊' },
    { id: 'bots', label: 'Trading', icon: '🤖' }, 
    { id: 'portfolios', label: 'Marketplace', icon: '💼' },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-2 z-50">
      <div className="flex justify-around items-center max-w-md mx-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex flex-col items-center p-2 rounded-lg transition-all duration-200 ${
              activeSection === tab.id
                ? 'text-[#0097B2] bg-[#0097B2]/10'
                : 'text-gray-600 dark:text-gray-400 hover:text-[#0097B2] hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span className="text-lg mb-1">{tab.icon}</span>
            <span className="text-xs font-medium">{tab.label}</span>
          </button>
        ))}
      </div>
      
      {/* URL indicator for debugging */}
      <div className="text-center mt-2">
        <span className="text-xs text-gray-400">
          f01i.app/{displayName}/{activeSection}
        </span>
      </div>
    </nav>
  );
};

export default PersonalizedApp;