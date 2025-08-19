import React from 'react';
import { X, AlertTriangle, Trash2, Crown } from 'lucide-react';

const SubscriptionLimitModal = ({ 
  isOpen, 
  onClose, 
  limitData, 
  resourceType, 
  onUpgrade, 
  onManageExisting 
}) => {
  if (!isOpen || !limitData) return null;

  const getResourceDisplayName = (type) => {
    switch (type) {
      case 'ai_bots': return 'AI Trading Bots';
      case 'manual_bots': return 'Manual Bots';
      case 'marketplace_products': return 'Marketplace Products';
      default: return 'Resources';
    }
  };

  const getResourceSingularName = (type) => {
    switch (type) {
      case 'ai_bots': return 'AI bot';
      case 'manual_bots': return 'manual bot';
      case 'marketplace_products': return 'product';
      default: return 'resource';
    }
  };

  const planUpgradeMessage = limitData.plan_type === 'free' 
    ? 'Upgrade to Plus ($10/month) to get more resources!'
    : 'Upgrade to Pro ($49/month) for unlimited access!';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <AlertTriangle className="text-orange-500 mr-3" size={24} />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Subscription Limit Reached
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="text-center mb-6">
            <div className="bg-orange-50 dark:bg-orange-900/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="text-orange-500" size={32} />
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              You've reached your limit!
            </h3>
            
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              You have reached the limit for {getResourceDisplayName(resourceType)} on your{' '}
              <span className="font-semibold capitalize">{limitData.plan_type} Plan</span>.
            </p>

            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Current Usage:
                </span>
                <span className="font-bold text-lg">
                  {limitData.current_count} / {limitData.limit === -1 ? '∞' : limitData.limit}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* Option 1: Manage Existing */}
            <button
              onClick={onManageExisting}
              className="w-full flex items-center justify-center px-4 py-3 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              <Trash2 size={16} className="mr-2" />
              Delete existing {getResourceSingularName(resourceType)} to free up space
            </button>

            {/* Option 2: Upgrade Subscription */}
            <button
              onClick={onUpgrade}
              className="w-full flex items-center justify-center px-4 py-3 bg-gradient-to-r from-[#0097B2] to-blue-600 text-white rounded-lg hover:from-[#0097B2]/90 hover:to-blue-600/90 transition-colors"
            >
              <Crown size={16} className="mr-2" />
              Upgrade Subscription
            </button>
          </div>

          {/* Upgrade Info */}
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200 text-center">
              💡 {planUpgradeMessage}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionLimitModal;