import React from 'react';
import { useApp } from '../contexts/AppContext';
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
    <div className="min-h-screen bg-gradient-to-br from-[#FAECEC] to-white dark:from-[#474545] dark:to-gray-900">
      <div className="relative">
        {renderActiveTab()}
        <BottomNav />
      </div>
    </div>
  );
};

export default MainApp;