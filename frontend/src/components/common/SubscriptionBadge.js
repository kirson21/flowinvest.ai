import React from 'react';
import { Crown, Zap, Check, Shield } from 'lucide-react';

const SubscriptionBadge = ({ planType, isSuperAdmin, className = '', showIcon = true }) => {
  const getBadgeConfig = () => {
    if (isSuperAdmin || planType === 'super_admin') {
      return {
        text: 'Super Admin',
        icon: Shield,
        bgColor: 'bg-gradient-to-r from-red-500 to-red-600',
        textColor: 'text-white',
        borderColor: 'border-red-500'
      };
    }

    switch (planType) {
      case 'pro':
        return {
          text: 'Pro Plan',
          icon: Crown,
          bgColor: 'bg-gradient-to-r from-purple-500 to-purple-600',
          textColor: 'text-white',
          borderColor: 'border-purple-500'
        };
      case 'plus':
        return {
          text: 'Plus Plan',
          icon: Zap,
          bgColor: 'bg-gradient-to-r from-yellow-400 to-yellow-500',
          textColor: 'text-gray-900',
          borderColor: 'border-yellow-400'
        };
      case 'free':
      default:
        return {
          text: 'Free Plan',
          icon: Check,
          bgColor: 'bg-gradient-to-r from-green-500 to-green-600',
          textColor: 'text-white',
          borderColor: 'border-green-500'
        };
    }
  };

  const config = getBadgeConfig();
  const IconComponent = config.icon;

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor} ${className}`}>
      {showIcon && <IconComponent size={12} className="mr-1" />}
      {config.text}
    </div>
  );
};

export default SubscriptionBadge;