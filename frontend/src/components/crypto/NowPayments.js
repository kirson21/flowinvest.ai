import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import nowPaymentsService from '../../services/nowPaymentsService';
import {
  DollarSign,
  ArrowDownCircle,
  ArrowUpCircle,
  Wallet,
  ExternalLink,
  RefreshCw,
  Info,
  CreditCard,
  Clock,
  CheckCircle,
  AlertTriangle,
  X,
  Mail,
  Zap
} from 'lucide-react';

const NowPayments = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Supported currencies and networks state
  const [supportedCurrencies, setSupportedCurrencies] = useState({});
  const [serviceHealth, setServiceHealth] = useState(null);

  // Payment state
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [selectedCurrency, setSelectedCurrency] = useState('USDT');
  const [selectedNetwork, setSelectedNetwork] = useState('TRX');
  const [paymentDescription, setPaymentDescription] = useState('');

  // Subscription state
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [subscriptionEmail, setSubscriptionEmail] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('plan_plus');

  // Transaction history and withdrawals
  const [transactions, setTransactions] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [showTransactions, setShowTransactions] = useState(false);
  const [showAllTransactions, setShowAllTransactions] = useState(false);

  // Withdrawal state
  const [showWithdrawalModal, setShowWithdrawalModal] = useState(false);
  const [withdrawalAmount, setWithdrawalAmount] = useState('');
  const [withdrawalAddress, setWithdrawalAddress] = useState('');
  const [withdrawalCurrency, setWithdrawalCurrency] = useState('USDT');
  const [withdrawalNetwork, setWithdrawalNetwork] = useState('TRX');
  const [withdrawalDescription, setWithdrawalDescription] = useState('');
  const [withdrawalMinAmount, setWithdrawalMinAmount] = useState(null);
  const [withdrawalFee, setWithdrawalFee] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);

  // Price estimate and minimum amount
  const [priceEstimate, setPriceEstimate] = useState(null);
  const [minimumAmount, setMinimumAmount] = useState(null);

  // Available subscription plans (matching real NowPayments plan)
  const subscriptionPlans = [
    { 
      id: 'plan_plus', 
      name: 'Plus Plan', 
      price: 10.00,  // Updated to match your NowPayments plan
      interval: 31,  // Updated to match your NowPayments plan (31 days)
      features: [
        'Access to AI news feed + push notifications',
        'Telegram notifications + filters',
        'Create & manage 3 AI trading bots',
        'Create & manage 5 manual bots',
        'API access for copytrading integration',
        'Connect to ready-made bots from f01i.ai',
        'For marketplace sellers: up to 10 product slots'
      ] 
    }
  ];

  // Currency and network mappings
  const currencyNetworks = {
    'USDT': [
      { code: 'TRX', name: 'Tron (TRC20)', nowpayments_code: 'usdttrc20' },
      { code: 'BSC', name: 'Binance Smart Chain', nowpayments_code: 'usdtbsc' },
      { code: 'SOL', name: 'Solana', nowpayments_code: 'usdtsol' },
      { code: 'TON', name: 'TON', nowpayments_code: 'usdtton' },
      { code: 'ETH', name: 'Ethereum (ERC20)', nowpayments_code: 'usdterc20' }
    ],
    'USDC': [
      { code: 'ETH', name: 'Ethereum (ERC20)', nowpayments_code: 'usdcerc20' },
      { code: 'BSC', name: 'Binance Smart Chain', nowpayments_code: 'usdcbsc' },
      { code: 'SOL', name: 'Solana', nowpayments_code: 'usdcsol' }
    ]
  };

  useEffect(() => {
    checkServiceHealth();
    loadSupportedCurrencies();
    if (user) {
      loadUserTransactions();
    }
  }, [user]);

  // Update price estimate and minimum amount when currency changes
  useEffect(() => {
    const updateEstimates = async () => {
      const network = currencyNetworks[selectedCurrency]?.find(n => n.code === selectedNetwork);
      if (!network) return;

      try {
        // Get minimum amount for the selected currency
        const minResult = await nowPaymentsService.getMinimumAmount('usd', network.nowpayments_code);
        if (minResult.success) {
          setMinimumAmount(minResult.min_amount);
        }
      } catch (error) {
        console.error('Failed to get minimum amount:', error);
      }

      // Get price estimate if amount is set
      if (paymentAmount && parseFloat(paymentAmount) > 0) {
        try {
          const estimate = await nowPaymentsService.getEstimate(parseFloat(paymentAmount), 'usd', network.nowpayments_code);
          if (estimate.success) {
            setPriceEstimate(estimate.estimate);
          }
        } catch (error) {
          console.error('Failed to get price estimate:', error);
          setPriceEstimate(null);
        }
      }
    };

    const timer = setTimeout(updateEstimates, 300);
    return () => clearTimeout(timer);
  }, [paymentAmount, selectedCurrency, selectedNetwork]);

  const checkServiceHealth = async () => {
    try {
      const health = await nowPaymentsService.healthCheck();
      setServiceHealth(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setServiceHealth({ status: 'unhealthy', message: error.message });
    }
  };

  const loadSupportedCurrencies = async () => {
    try {
      const result = await nowPaymentsService.getSupportedCurrencies();
      if (result.success) {
        setSupportedCurrencies(result.currencies);
      }
    } catch (error) {
      console.error('Failed to load currencies:', error);
    }
  };

  const loadUserTransactions = async () => {
    try {
      if (!user?.id) return;

      const result = await nowPaymentsService.getUserPayments(user.id);
      if (result.success) {
        setTransactions(result.payments || []);
      }

      // Also load withdrawals
      const withdrawalsResult = await nowPaymentsService.getUserWithdrawals(user.id);
      if (withdrawalsResult.success) {
        setWithdrawals(withdrawalsResult.withdrawals || []);
      }
    } catch (error) {
      console.error('Failed to load transactions:', error);
    }
  };

  const loadWithdrawalMinAmount = async (currency) => {
    try {
      const result = await nowPaymentsService.getWithdrawalMinAmount(currency);
      if (result.success) {
        setWithdrawalMinAmount(result.min_amount);
      }
    } catch (error) {
      console.error('Failed to load min amount:', error);
    }
  };

  const loadWithdrawalFee = async (currency, amount) => {
    try {
      if (!amount || amount <= 0) {
        setWithdrawalFee(null);
        return;
      }

      const result = await nowPaymentsService.getWithdrawalFee(currency, amount);
      if (result.success) {
        setWithdrawalFee(result.fee);
      }
    } catch (error) {
      console.error('Failed to load withdrawal fee:', error);
    }
  };

  // Update withdrawal fee when amount or currency changes
  useEffect(() => {
    if (withdrawalAmount && withdrawalCurrency && withdrawalNetwork) {
      const network = currencyNetworks[withdrawalCurrency]?.find(n => n.code === withdrawalNetwork);
      if (network) {
        loadWithdrawalFee(network.nowpayments_code, parseFloat(withdrawalAmount));
      }
    }
  }, [withdrawalAmount, withdrawalCurrency, withdrawalNetwork]);

  // Update minimum amount when currency/network changes
  useEffect(() => {
    if (withdrawalCurrency && withdrawalNetwork) {
      const network = currencyNetworks[withdrawalCurrency]?.find(n => n.code === withdrawalNetwork);
      if (network) {
        loadWithdrawalMinAmount(network.nowpayments_code);
      }
    }
  }, [withdrawalCurrency, withdrawalNetwork]);

  const handleCreatePayment = async () => {
    try {
      setLoading(true);
      setError('');
      setMessage('');

      // Validate amount
      const validation = nowPaymentsService.validateAmount(paymentAmount);
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      const amount = parseFloat(paymentAmount);
      const network = currencyNetworks[selectedCurrency]?.find(n => n.code === selectedNetwork);
      
      if (!network) {
        setError('Invalid currency/network combination');
        return;
      }

      // Check minimum amount for the selected crypto
      try {
        const minAmountResult = await nowPaymentsService.getMinimumAmount('usd', network.nowpayments_code);
        if (minAmountResult.success && amount < minAmountResult.min_amount) {
          setError(`Minimum amount for ${selectedCurrency} (${selectedNetwork}) is $${minAmountResult.min_amount.toFixed(2)}`);
          return;
        }
      } catch (minError) {
        console.warn('Could not check minimum amount, proceeding:', minError);
      }

      const invoiceData = {
        amount: amount,
        currency: 'usd',
        pay_currency: network.nowpayments_code,
        description: paymentDescription || nowPaymentsService.generateOrderDescription(amount),
        user_email: user?.email
      };

      const result = await nowPaymentsService.createInvoice(invoiceData, user?.id);
      
      if (result.success) {
        setMessage('Payment invoice created successfully! Redirecting...');
        
        // Redirect directly in the same tab to avoid popup blocking
        setTimeout(() => {
          window.location.href = result.invoice_url;
        }, 1500);
      }
    } catch (error) {
      setError(`Failed to create payment: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSubscription = async () => {
    try {
      setLoading(true);
      setError('');
      setMessage('');

      if (!nowPaymentsService.validateEmail(subscriptionEmail)) {
        setError('Please enter a valid email address');
        return;
      }

      const subscriptionData = {
        plan_id: selectedPlan,
        user_email: subscriptionEmail
      };

      const result = await nowPaymentsService.createSubscription(subscriptionData, user?.id);
      
      if (result.success) {
        setMessage(`Subscription created! Payment instructions sent to ${subscriptionEmail}`);
        setTimeout(() => {
          setShowSubscriptionModal(false);
          resetSubscriptionForm();
        }, 3000);
      }
    } catch (error) {
      setError(`Failed to create subscription: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetPaymentForm = () => {
    setPaymentAmount('');
    setPaymentDescription('');
    setPriceEstimate(null);
    setMessage('');
    setError('');
  };

  const handleCreateWithdrawal = async () => {
    try {
      setLoading(true);
      setError('');
      setMessage('');

      // Validation
      const amount = parseFloat(withdrawalAmount);
      if (!amount || amount <= 0) {
        setError('Please enter a valid withdrawal amount');
        return;
      }

      if (!withdrawalAddress.trim()) {
        setError('Please enter a valid recipient address');
        return;
      }

      // Get the current network
      const network = currencyNetworks[withdrawalCurrency]?.find(n => n.code === withdrawalNetwork);
      if (!network) {
        setError('Invalid currency/network combination');
        return;
      }

      // Validate address format
      const addressValidation = nowPaymentsService.validateWithdrawalAddress(withdrawalAddress, network.nowpayments_code);
      if (!addressValidation.valid) {
        setError(addressValidation.error);
        return;
      }

      // Check minimum amount
      if (withdrawalMinAmount && amount < withdrawalMinAmount) {
        setError(`Amount must be at least ${withdrawalMinAmount} ${withdrawalCurrency}`);
        return;
      }

      const withdrawalData = {
        recipient_address: withdrawalAddress.trim(),
        amount: amount,
        currency: network.nowpayments_code,
        description: withdrawalDescription || `Withdrawal to ${withdrawalAddress.slice(0, 10)}...`
      };

      const result = await nowPaymentsService.createWithdrawal(withdrawalData, user?.id);
      
      if (result.success) {
        setMessage('Withdrawal request created successfully! Verifying...');
        
        // Auto-verify the withdrawal
        setTimeout(async () => {
          try {
            setIsVerifying(true);
            const verifyResult = await nowPaymentsService.verifyWithdrawal(result.withdrawal_id, user?.id);
            
            if (verifyResult.success) {
              setMessage('Withdrawal verified and processing! You will receive a notification when completed.');
              setTimeout(() => {
                setShowWithdrawalModal(false);
                resetWithdrawalForm();
                loadUserTransactions(); // Reload to show new withdrawal
              }, 3000);
            }
          } catch (verifyError) {
            setError(`Verification failed: ${verifyError.message}`);
          } finally {
            setIsVerifying(false);
          }
        }, 1500);
      }
    } catch (error) {
      setError(`Failed to create withdrawal: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetSubscriptionForm = () => {
    setSubscriptionEmail(user?.email || '');
    setSelectedPlan('plan_plus');
    setMessage('');
    setError('');
  };

  const resetWithdrawalForm = () => {
    setWithdrawalAmount('');
    setWithdrawalAddress('');
    setWithdrawalDescription('');
    setWithdrawalMinAmount(null);
    setWithdrawalFee(null);
    setMessage('');
    setError('');
  };

  const formatStatus = (status) => {
    const statusInfo = nowPaymentsService.getStatusBadge(status);
    return (
      <Badge variant={statusInfo.color === 'green' ? 'default' : 'secondary'} className="gap-1">
        <span>{statusInfo.icon}</span>
        {statusInfo.text}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 pb-8">
      {/* Service Health Status */}
      {serviceHealth && (
        <Alert className={`border-l-4 ${serviceHealth.status === 'healthy' ? 'border-l-green-500' : 'border-l-yellow-500'}`}>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            NowPayments Status: <strong>{serviceHealth.status}</strong>
            {serviceHealth.message && ` - ${serviceHealth.message}`}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <ArrowDownCircle className="h-5 w-5 text-green-600" />
              Top Up Balance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Add funds using cryptocurrency via secure payment gateway
            </p>
            <Button 
              onClick={() => setShowPaymentModal(true)}
              className="w-full bg-cyan-600 hover:bg-cyan-700"
            >
              <CreditCard className="h-4 w-4 mr-2" />
              Pay with Crypto
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Mail className="h-5 w-5 text-blue-600" />
              Subscriptions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Set up recurring payments for Pro features
            </p>
            <Button 
              onClick={() => setShowSubscriptionModal(true)}
              variant="outline"
              className="w-full"
            >
              <Zap className="h-4 w-4 mr-2" />
              Manage Plans
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Clock className="h-5 w-5 text-purple-600" />
              Transaction History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              View your payment and subscription history
            </p>
            <Button 
              onClick={() => setShowTransactions(!showTransactions)}
              variant="outline"
              className="w-full"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              View History
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Transaction History */}
      {showTransactions && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Payment History</span>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => setShowTransactions(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {transactions.length === 0 ? (
              <p className="text-center text-gray-500 py-4">No transactions found</p>
            ) : (
              <div className="space-y-3">
                {/* Display limited or all transactions based on state */}
                {(showAllTransactions ? transactions : transactions.slice(0, 5)).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-full">
                        <DollarSign className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">{tx.description || 'Payment'}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(tx.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        {nowPaymentsService.formatAmount(tx.amount)}
                      </p>
                      {formatStatus(tx.payment_status)}
                    </div>
                  </div>
                ))}
                
                {/* Show All / Show Less Button */}
                {transactions.length > 5 && (
                  <div className="flex justify-center pt-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowAllTransactions(!showAllTransactions)}
                      className="text-cyan-600 hover:text-cyan-700 border-cyan-600 hover:border-cyan-700"
                    >
                      {showAllTransactions ? (
                        <>
                          <ArrowUpCircle className="h-4 w-4 mr-2" />
                          Show Less
                        </>
                      ) : (
                        <>
                          <ArrowDownCircle className="h-4 w-4 mr-2" />
                          Show All ({transactions.length})
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Create Crypto Payment</span>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowPaymentModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert className="border-red-200 bg-red-50 dark:bg-red-900/20">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800 dark:text-red-200">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {message && (
                <Alert className="border-green-200 bg-green-50 dark:bg-green-900/20">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    {message}
                  </AlertDescription>
                </Alert>
              )}

              <div>
                <Label>Amount (USD)</Label>
                <Input
                  type="number"
                  placeholder="25.00"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  min="20"
                  max="10000"
                  step="0.01"
                />
                {minimumAmount && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                    Minimum for {selectedCurrency} ({selectedNetwork}): ${minimumAmount.toFixed(2)}
                  </p>
                )}
              </div>

              <div>
                <Label>Cryptocurrency</Label>
                <select
                  value={selectedCurrency}
                  onChange={(e) => {
                    setSelectedCurrency(e.target.value);
                    setSelectedNetwork(currencyNetworks[e.target.value]?.[0]?.code || '');
                  }}
                  className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                >
                  {Object.keys(currencyNetworks).map(currency => (
                    <option key={currency} value={currency}>{currency}</option>
                  ))}
                </select>
              </div>

              <div>
                <Label>Network</Label>
                <select
                  value={selectedNetwork}
                  onChange={(e) => setSelectedNetwork(e.target.value)}
                  className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                >
                  {(currencyNetworks[selectedCurrency] || []).map(network => (
                    <option key={network.code} value={network.code}>
                      {network.name}
                    </option>
                  ))}
                </select>
              </div>

              {priceEstimate && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    Estimated: {priceEstimate.estimated_amount} {selectedCurrency}
                  </p>
                </div>
              )}

              <div>
                <Label>Description (Optional)</Label>
                <Input
                  placeholder="Balance top-up"
                  value={paymentDescription}
                  onChange={(e) => setPaymentDescription(e.target.value)}
                />
              </div>

              <div className="pt-4 pb-6">
                <Button
                  onClick={handleCreatePayment}
                  disabled={loading || !paymentAmount}
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <ExternalLink className="h-4 w-4 mr-2" />
                  )}
                  {loading ? 'Creating...' : 'Create Payment Invoice'}
                </Button>
              </div>

              <div className="text-xs text-gray-500 space-y-1 pb-4">
                <p>• You'll be redirected to NowPayments secure gateway</p>
                <p>• Support for 300+ cryptocurrencies</p>
                <p>• Funds credited automatically after confirmation</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Subscription Modal */}
      {showSubscriptionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Crypto Subscriptions</span>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => setShowSubscriptionModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert className="border-red-200 bg-red-50 dark:bg-red-900/20">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800 dark:text-red-200">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {message && (
                <Alert className="border-green-200 bg-green-50 dark:bg-green-900/20">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    {message}
                  </AlertDescription>
                </Alert>
              )}

              <div>
                <Label>Email Address</Label>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={subscriptionEmail}
                  onChange={(e) => setSubscriptionEmail(e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Payment links will be sent to this email
                </p>
              </div>

              <div>
                <Label>Subscription Plan</Label>
                <div className="space-y-2 mt-2">
                  {subscriptionPlans.map(plan => (
                    <div 
                      key={plan.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedPlan === plan.id 
                          ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-900/20' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedPlan(plan.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{plan.name}</h4>
                          <p className="text-sm text-gray-500">
                            ${plan.price}/month • {plan.interval} days
                          </p>
                        </div>
                        <div className="text-right">
                          <div className={`w-4 h-4 rounded-full border-2 ${
                            selectedPlan === plan.id 
                              ? 'border-cyan-500 bg-cyan-500' 
                              : 'border-gray-300'
                          }`} />
                        </div>
                      </div>
                      <div className="mt-2">
                        {plan.features.map((feature, idx) => (
                          <p key={idx} className="text-xs text-gray-600">• {feature}</p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 pb-6">
                <Button
                  onClick={handleCreateSubscription}
                  disabled={loading || !subscriptionEmail}
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Mail className="h-4 w-4 mr-2" />
                  )}
                  {loading ? 'Creating...' : 'Create Subscription'}
                </Button>
              </div>

              <div className="text-xs text-gray-500 space-y-1 pb-4">
                <p>• Automated recurring crypto payments</p>
                <p>• Payment reminders sent via email</p>
                <p>• Cancel anytime from your dashboard</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default NowPayments;