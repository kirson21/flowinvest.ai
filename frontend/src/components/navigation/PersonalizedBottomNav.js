import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { cn } from '../../lib/utils';
import { 
  Brain, 
  Bot, 
  Briefcase, 
  Settings 
} from 'lucide-react';

const PersonalizedBottomNav = ({ displayName, activeSection }) => {
  const { setActiveTab, t } = useApp();
  const navigate = useNavigate();

  const navItems = [
    {
      id: 'feed',
      label: t('aiFeed') || 'AI Feed',
      icon: Brain,
      color: 'text-[#0097B2]'
    },
    {
      id: 'bots',
      label: t('tradingBots') || 'Trading',
      icon: Bot,
      color: 'text-[#0097B2]'
    },
    {
      id: 'portfolios',
      label: 'Marketplace',
      icon: Briefcase,
      color: 'text-[#0097B2]'
    },
    {
      id: 'settings',
      label: t('settings') || 'Settings',
      icon: Settings,
      color: 'text-[#0097B2]'
    }
  ];

  const handleNavigation = (itemId) => {
    // Set active tab for component state
    setActiveTab(itemId);
    
    // Map internal tab IDs to URL segments
    const urlMapping = {
      'feed': 'feed',
      'bots': 'bots', 
      'portfolios': 'marketplace', // Map portfolios to marketplace URL
      'settings': 'settings'
    };
    
    // Navigate to personalized URL
    const urlSegment = urlMapping[itemId] || itemId;
    const newUrl = `/${encodeURIComponent(displayName)}/${urlSegment}`;
    navigate(newUrl);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 z-50">
      <div className="flex items-center justify-around px-4 py-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSection === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => handleNavigation(item.id)}
              className={cn(
                "flex flex-col items-center justify-center p-2 rounded-lg transition-all duration-200 min-w-0 flex-1 max-w-[80px]",
                isActive 
                  ? "bg-[#0097B2]/10 text-[#0097B2] scale-105" 
                  : "text-gray-500 dark:text-gray-400 hover:text-[#0097B2] hover:bg-[#0097B2]/5"
              )}
            >
              <Icon 
                size={20} 
                className={cn(
                  "mb-1 transition-transform duration-200",
                  isActive && "scale-110"
                )} 
              />
              <span className={cn(
                "text-xs font-medium truncate w-full text-center transition-colors duration-200",
                isActive && "text-[#0097B2]"
              )}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default PersonalizedBottomNav;