import React, { useState, useEffect } from 'react';
import { Check, Crown, Zap, X } from 'lucide-react';
import { supabaseDataService } from '../../services/supabaseDataService';

const SubscriptionManagement = ({ user, onClose }) => {
  const [subscription, setSubscription] = useState(null);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [accountBalance, setAccountBalance] = useState(0);

  useEffect(() => {
    loadSubscriptionData();
  }, [user]);

  const loadSubscriptionData = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);

      // Load subscription and plans in parallel
      const [subResult, plansResult, balance] = await Promise.all([
        supabaseDataService.getUserSubscription(user.id),
        supabaseDataService.getSubscriptionPlans(),
        supabaseDataService.getAccountBalance(user.id)
      ]);

      if (subResult.success) {
        setSubscription(subResult.subscription);
      }

      if (plansResult.success) {
        setPlans(plansResult.plans);
      }

      setAccountBalance(balance || 0);
    } catch (error) {
      console.error('Error loading subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (plan) => {
    if (plan.coming_soon) {
      alert('This plan is coming soon! Stay tuned for updates.');
      return;
    }

    if (plan.id === subscription?.plan_type) {
      alert('You are already on this plan.');
      return;
    }

    // Check if user has sufficient balance
    if (accountBalance < plan.price) {
      const shortfall = plan.price - accountBalance;
      const shouldTopUp = window.confirm(
        `💰 Insufficient Funds\n\n` +
        `Plan price: $${plan.price.toFixed(2)}\n` +
        `Your balance: $${accountBalance.toFixed(2)}\n` +
        `You need: $${shortfall.toFixed(2)} more\n\n` +
        `Would you like to go to the balance section to top up your account?`
      );
      
      if (shouldTopUp) {
        onClose(); // Close subscription modal
        // The parent component should handle scrolling to balance section
      }
      return;
    }

    // Confirm upgrade
    const confirmMessage = plan.id === 'free' 
      ? `Downgrade to ${plan.name}?\n\nYou will lose access to premium features immediately.`
      : `Upgrade to ${plan.name} for $${plan.price.toFixed(2)}?\n\nThis will be deducted from your account balance.\nYour new balance will be $${(accountBalance - plan.price).toFixed(2)}`;

    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      setUpgrading(true);

      const result = await supabaseDataService.upgradeSubscription(
        user.id,
        plan.id,
        plan.price
      );

      if (result.success) {
        // Update local state
        setSubscription(result.subscription);
        setAccountBalance(result.new_balance);

        alert(
          `✅ Subscription ${plan.id === 'free' ? 'Downgraded' : 'Upgraded'}!\n\n` +
          `You are now on the ${plan.name}.\n` +
          `${plan.price > 0 ? `Amount charged: $${result.amount_charged.toFixed(2)}\n` : ''}` +
          `Your new balance: $${result.new_balance.toFixed(2)}`
        );
      } else {
        if (result.error === 'insufficient_funds') {
          alert(
            '❌ Insufficient Funds\n\n' +
            `Required: $${result.required_amount.toFixed(2)}\n` +
            `Your balance: $${result.current_balance.toFixed(2)}\n\n` +
            'Please top up your account and try again.'
          );
        } else {
          alert('❌ Upgrade Failed\n\n' + (result.message || 'Unknown error occurred'));
        }
      }
    } catch (error) {
      console.error('Error upgrading subscription:', error);
      alert('❌ Failed to upgrade subscription. Please try again.');
    } finally {
      setUpgrading(false);
    }
  };

  const getPlanIcon = (planId) => {
    switch (planId) {
      case 'free': return <Check size={24} className="text-green-500" />;
      case 'plus': return <Zap size={24} className="text-yellow-500" />;
      case 'pro': return <Crown size={24} className="text-purple-500" />;
      default: return <Check size={24} className="text-gray-500" />;
    }
  };

  const getCurrentPlanBadge = (planId) => {
    if (planId === subscription?.plan_type) {
      return (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <div className="bg-[#0097B2] text-white text-xs px-3 py-1 rounded-full font-medium">
            Your current plan
          </div>
        </div>
      );
    }
    return null;
  };

  const getPopularBadge = (plan) => {
    if (plan.popular) {
      return (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white text-xs px-3 py-1 rounded-full font-medium">
            Popular
          </div>
        </div>
      );
    }
    return null;
  };

  const getButtonText = (plan) => {
    if (plan.coming_soon) return 'Coming Soon';
    if (plan.id === subscription?.plan_type) return 'Current Plan';
    if (plan.id === 'free') return 'Downgrade';
    return 'Upgrade';
  };

  const getButtonStyle = (plan) => {
    if (plan.coming_soon) {
      return 'bg-gray-400 text-white cursor-not-allowed';
    }
    if (plan.id === subscription?.plan_type) {
      return 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed';
    }
    if (plan.popular) {
      return 'bg-gradient-to-r from-[#0097B2] to-blue-600 text-white hover:from-[#0097B2]/90 hover:to-blue-600/90';
    }
    return 'bg-[#0097B2] text-white hover:bg-[#0097B2]/90';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-4xl">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0097B2]"></div>
            <span className="ml-3 text-lg">Loading subscription plans...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Choose your plan
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Upgrade or downgrade your subscription anytime
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
          >
            <X size={20} />
          </button>
        </div>

        {/* Balance Info */}
        <div className="px-6 py-4 bg-gradient-to-r from-[#0097B2]/5 to-blue-500/5 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your account balance
              </p>
              <p className="text-xl font-bold text-[#0097B2]">
                ${accountBalance.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Current plan
              </p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                {subscription?.plan_type || 'Free'} Plan
              </p>
            </div>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="p-6 pb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`relative border rounded-lg p-6 pb-8 ${
                  plan.popular
                    ? 'border-[#0097B2] ring-2 ring-[#0097B2]/20'
                    : 'border-gray-300 dark:border-gray-600'
                } ${
                  plan.id === subscription?.plan_type
                    ? 'bg-gradient-to-br from-[#0097B2]/5 to-blue-500/5'
                    : 'bg-white dark:bg-gray-800'
                }`}
              >
                {getCurrentPlanBadge(plan.id)}
                {getPopularBadge(plan)}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <div className="flex justify-center mb-3">{getPlanIcon(plan.id)}</div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {plan.name}
                  </h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">
                      ${plan.price}
                    </span>
                    <span className="text-gray-600 dark:text-gray-400 ml-1">
                      / {plan.billing_period}
                    </span>
                  </div>
                </div>

                {/* Features List */}
                <div className="space-y-2 mb-6">
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-start">
                      <Check
                        size={16}
                        className="text-green-500 mr-2 mt-0.5 flex-shrink-0"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {feature}
                      </span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleUpgrade(plan)}
                  disabled={
                    upgrading ||
                    plan.coming_soon ||
                    plan.id === subscription?.plan_type
                  }
                  className={`w-full py-3 px-4 rounded-lg font-medium text-sm transition-colors ${getButtonStyle(
                    plan
                  )} ${
                    upgrading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {upgrading ? 'Processing...' : getButtonText(plan)}
                </button>

                {/* Coming Soon Overlay */}
                {plan.coming_soon && (
                  <div className="absolute inset-0 bg-white/80 dark:bg-gray-800/80 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <Crown size={32} className="mx-auto text-gray-400 mb-2" />
                      <span className="text-lg font-semibold text-gray-600 dark:text-gray-400">
                        Coming Soon
                      </span>
                    </div>
                  </div>
                )}

                {/* Popular Badge - positioned in the middle */}
                {getPopularBadge(plan)}
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="text-center text-sm text-gray-600 dark:text-gray-400 space-y-2">
            <p>
              💡 All subscription payments are deducted from your account balance.
            </p>
            <p>
              Need more funds?{' '}
              <button
                onClick={onClose}
                className="text-[#0097B2] hover:underline font-medium"
              >
                Top up your balance
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionManagement;