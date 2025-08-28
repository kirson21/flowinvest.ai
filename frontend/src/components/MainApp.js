import React, { useEffect } from 'react';
import { useApp } from '../contexts/AppContext';
import { useLocation, useSearchParams } from 'react-router-dom';
import LoginScreen from './auth/LoginScreen';
import BottomNav from './navigation/BottomNav';
import AIFeed from './feed/AIFeed';
import TradingBots from './bots/TradingBots';
import Portfolios from './portfolios/Portfolios';
import Settings from './settings/Settings';

const MainApp = () => {
  const { isAuthenticated, activeTab } = useApp();

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
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
          {renderActiveTab()}
        </div>
        <BottomNav />
      </div>
    </div>
  );
};

export default MainApp;