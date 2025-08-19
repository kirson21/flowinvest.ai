import React, { useState, useEffect } from 'react';
import { Crown, Zap, Check, Shield } from 'lucide-react';
import { supabaseDataService } from '../../services/supabaseDataService';

const SubscriptionProfileBadge = ({ user }) => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserSubscription();
  }, [user]);

  const loadUserSubscription = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      const result = await supabaseDataService.getUserSubscription(user.id);
      
      if (result.success) {
        setSubscription(result.subscription);
      }
    } catch (error) {
      console.error('Error loading user subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBadgeConfig = (planType) => {
    switch (planType) {
      case 'super_admin':
        return {
          icon: <Shield size={16} className="text-red-400" />,
          text: 'Super Admin',
          bgColor: 'bg-gradient-to-r from-red-500 to-red-600',
          textColor: 'text-white',
          borderColor: 'border-red-500',
          glow: 'shadow-lg shadow-red-500/25',
        };
      case 'pro':
        return {
          icon: <Crown size={16} className="text-purple-400" />,
          text: 'Pro Plan',
          bgColor: 'bg-gradient-to-r from-purple-500 to-purple-600',
          textColor: 'text-white',
          borderColor: 'border-purple-500',
          glow: 'shadow-lg shadow-purple-500/25',
        };
      case 'plus':
        return {
          icon: <Zap size={16} className="text-yellow-400" />,
          text: 'Plus Plan',
          bgColor: 'bg-gradient-to-r from-yellow-500 to-orange-500',
          textColor: 'text-white',
          borderColor: 'border-yellow-500',
          glow: 'shadow-lg shadow-yellow-500/25',
        };
      case 'free':
      default:
        return {
          icon: <Check size={16} className="text-green-400" />,
          text: 'Free Plan',
          bgColor: 'bg-gradient-to-r from-green-500 to-green-600',
          textColor: 'text-white',
          borderColor: 'border-green-500',
          glow: 'shadow-lg shadow-green-500/25',
        };
    }
  };

  if (loading) {
    return (
      <div className="flex items-center">
        <div className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded-full px-3 py-1.5 w-20 h-7"></div>
      </div>
    );
  }

  const planType = subscription?.plan_type || 'free';
  const badgeConfig = getBadgeConfig(planType);
  
  // Check if user is Super Admin by UUID (fallback method)
  const isSuperAdmin = user?.id === 'cd0e9717-f85d-4726-81e9-f260394ead58';
  if (isSuperAdmin && planType !== 'super_admin') {
    // Use Super Admin styling even if subscription isn't set properly
    const superAdminConfig = getBadgeConfig('super_admin');
    return (
      <div className="flex items-center">
        <div className={`
          inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium
          border ${superAdminConfig.borderColor}
          ${superAdminConfig.bgColor} ${superAdminConfig.textColor}
          ${superAdminConfig.glow}
          transition-all duration-200 hover:scale-105
        `}>
          {superAdminConfig.icon}
          <span className="ml-1.5">{superAdminConfig.text}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center">
      <div className={`
        inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium
        border ${badgeConfig.borderColor}
        ${badgeConfig.bgColor} ${badgeConfig.textColor}
        ${badgeConfig.glow}
        transition-all duration-200 hover:scale-105
      `}>
        {badgeConfig.icon}
        <span className="ml-1.5">{badgeConfig.text}</span>
      </div>
    </div>
  );
};

export default SubscriptionProfileBadge;