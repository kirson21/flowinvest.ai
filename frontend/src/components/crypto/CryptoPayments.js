import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { 
  DollarSign,
  ArrowDownCircle,
  ArrowUpCircle,
  Wallet,
  Copy,
  CheckCircle,
  AlertTriangle,
  Clock,
  ExternalLink,
  QrCode,
  RefreshCw,
  Info,
  CreditCard,
  Send,
  Download
} from 'lucide-react';

const CryptoPayments = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // State for deposits
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [depositCurrency, setDepositCurrency] = useState('USDT');
  const [depositNetwork, setDepositNetwork] = useState('ERC20');
  const [depositAddress, setDepositAddress] = useState('');
  const [depositReference, setDepositReference] = useState('');
  const [transactionId, setTransactionId] = useState('');

  // State for withdrawals
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawCurrency, setWithdrawCurrency] = useState('USDT');
  const [withdrawNetwork, setWithdrawNetwork] = useState('ERC20');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawAddress, setWithdrawAddress] = useState('');
  const [withdrawMemo, setWithdrawMemo] = useState('');

  // State for transactions
  const [transactions, setTransactions] = useState([]);
  const [supportedCurrencies, setSupportedCurrencies] = useState([]);
  const [fees, setFees] = useState({});
  const [accountBalance, setAccountBalance] = useState(0);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    if (user) {
      loadSupportedCurrencies();
      loadWithdrawalFees();
      loadCryptoTransactions();
      loadAccountBalance();
    }
  }, [user]);

  const loadAccountBalance = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/auth/user/${user.id}/balance`);
      const result = await response.json();
      if (result.success) {
        setAccountBalance(result.balance);
      }
    } catch (error) {
      console.error('Error loading account balance:', error);
    }
  };

  const loadSupportedCurrencies = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/crypto/supported-currencies`);
      const result = await response.json();
      if (result.success) {
        setSupportedCurrencies(result.currencies);
      }
    } catch (error) {
      console.error('Error loading supported currencies:', error);
    }
  };

  const loadWithdrawalFees = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/crypto/fees`);
      const result = await response.json();
      if (result.success) {
        setFees(result.fees);
      }
    } catch (error) {
      console.error('Error loading withdrawal fees:', error);
    }
  };

  const loadCryptoTransactions = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/crypto/transactions?user_id=${user.id}&limit=20`);
      const result = await response.json();
      if (result.success) {
        setTransactions(result.transactions);
      }
    } catch (error) {
      console.error('Error loading crypto transactions:', error);
    }
  };

  const handleGenerateDepositAddress = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`${backendUrl}/api/crypto/deposit/address?user_id=${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currency: depositCurrency,
          network: depositNetwork
        })
      });

      const result = await response.json();

      if (result.success) {
        setDepositAddress(result.address);
        setDepositReference(result.deposit_reference || '');
        setTransactionId(result.transaction_id || '');
        setMessage('Deposit address retrieved successfully');
        setTimeout(() => setMessage(''), 5000);
      } else {
        setError(result.detail || 'Failed to get deposit address');
      }
    } catch (error) {
      console.error('Error getting deposit address:', error);
      setError('Failed to get deposit address. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReference = async () => {
    try {
      await navigator.clipboard.writeText(depositReference);
      setMessage('Payment reference copied to clipboard!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to copy reference:', error);
      setError('Failed to copy reference to clipboard');
    }
  };

  const handleCopyAddress = async () => {
    try {
      await navigator.clipboard.writeText(depositAddress);
      setMessage('Address copied to clipboard!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to copy address:', error);
      setError('Failed to copy address to clipboard');
    }
  };

  const handleWithdraw = async () => {
    try {
      setLoading(true);
      setError('');

      // Validate inputs
      if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
        setError('Please enter a valid amount');
        return;
      }

      if (!withdrawAddress) {
        setError('Please enter a recipient address');
        return;
      }

      const amount = parseFloat(withdrawAmount);
      const estimatedFee = Math.max(fees.withdrawal?.minimum_fee || 5, amount * (fees.withdrawal?.percentage_fee || 0.02));
      const totalNeeded = amount + estimatedFee;

      if (totalNeeded > accountBalance) {
        setError(`Insufficient balance. You need $${totalNeeded.toFixed(2)} (amount + fee) but have $${accountBalance.toFixed(2)}`);
        return;
      }

      const response = await fetch(`${backendUrl}/api/crypto/withdrawal?user_id=${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient_address: withdrawAddress,
          amount: amount,
          currency: withdrawCurrency,
          network: withdrawNetwork,
          memo: withdrawMemo || null
        })
      });

      const result = await response.json();

      if (result.success) {
        setMessage(`Withdrawal submitted successfully! Transaction ID: ${result.crypto_transaction_id}`);
        setWithdrawAmount('');
        setWithdrawAddress('');
        setWithdrawMemo('');
        setShowWithdrawModal(false);
        
        // Refresh data
        loadAccountBalance();
        loadCryptoTransactions();
        
        setTimeout(() => setMessage(''), 8000);
      } else {
        setError(result.detail || 'Failed to submit withdrawal');
      }
    } catch (error) {
      console.error('Error submitting withdrawal:', error);
      setError('Failed to submit withdrawal. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTransactionStatus = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      processing: { color: 'bg-blue-100 text-blue-800', icon: RefreshCw },
      confirmed: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      failed: { color: 'bg-red-100 text-red-800', icon: AlertTriangle },
      cancelled: { color: 'bg-gray-100 text-gray-800', icon: AlertTriangle }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-[#474545] dark:text-white flex items-center gap-3">
            <Wallet className="text-[#0097B2]" size={28} />
            Crypto Payments
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Deposit and withdraw funds using USDT and USDC cryptocurrencies
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600 dark:text-gray-400">Account Balance</p>
          <p className="text-2xl font-bold text-[#0097B2]">
            {formatCurrency(accountBalance)}
          </p>
        </div>
      </div>

      {/* Success/Error Messages */}
      {message && (
        <Alert className="border-green-200 bg-green-50 text-green-800">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert className="border-red-200 bg-red-50 text-red-800">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setShowDepositModal(true)}>
          <CardContent className="flex items-center justify-center p-6">
            <div className="text-center">
              <ArrowDownCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Deposit Crypto</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Add funds to your account</p>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setShowWithdrawModal(true)}>
          <CardContent className="flex items-center justify-center p-6">
            <div className="text-center">
              <ArrowUpCircle className="h-12 w-12 text-blue-600 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Withdraw Crypto</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">Send funds to your wallet</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-[#0097B2]" />
              Recent Crypto Transactions
            </CardTitle>
            <Button variant="outline" size="sm" onClick={loadCryptoTransactions}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {transactions.length > 0 ? (
            <div className="space-y-4">
              {transactions.map((tx) => (
                <div key={tx.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-full ${tx.transaction_type === 'deposit' ? 'bg-green-100' : 'bg-blue-100'}`}>
                      {tx.transaction_type === 'deposit' ? (
                        <ArrowDownCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <ArrowUpCircle className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">
                        {tx.transaction_type === 'deposit' ? 'Crypto Deposit' : 'Crypto Withdrawal'}
                      </p>
                      <p className="text-sm text-gray-600">
                        {tx.currency} ({tx.network}) • {new Date(tx.created_at).toLocaleDateString()}
                      </p>
                      {tx.transaction_hash && (
                        <p className="text-xs text-gray-500 font-mono">
                          {tx.transaction_hash.substring(0, 10)}...{tx.transaction_hash.substring(tx.transaction_hash.length - 8)}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold ${tx.transaction_type === 'deposit' ? 'text-green-600' : 'text-blue-600'}`}>
                      {tx.transaction_type === 'deposit' ? '+' : '-'}{formatCurrency(tx.amount)}
                    </p>
                    {formatTransactionStatus(tx.status)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Wallet className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No crypto transactions yet</p>
              <p className="text-sm">Start by making a deposit or withdrawal</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Deposit Modal */}
      {showDepositModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Deposit Cryptocurrency</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowDepositModal(false)}>
                ×
              </Button>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="depositCurrency" className="text-gray-700 dark:text-gray-300">Currency</Label>
                <select
                  id="depositCurrency"
                  value={depositCurrency}
                  onChange={(e) => {
                    setDepositCurrency(e.target.value);
                    // Reset network if not supported
                    if (e.target.value === 'USDC') {
                      setDepositNetwork('ERC20');
                    }
                  }}
                  className="w-full mt-1 p-2 border rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                >
                  <option value="USDT">USDT - Tether USD</option>
                  <option value="USDC">USDC - USD Coin</option>
                </select>
              </div>

              <div>
                <Label htmlFor="depositNetwork" className="text-gray-700 dark:text-gray-300">Network</Label>
                <select
                  id="depositNetwork"
                  value={depositNetwork}
                  onChange={(e) => setDepositNetwork(e.target.value)}
                  className="w-full mt-1 p-2 border rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                >
                  <option value="ERC20">ERC20 (Ethereum)</option>
                  {depositCurrency === 'USDT' && (
                    <option value="TRC20">TRC20 (Tron)</option>
                  )}
                </select>
              </div>

              <Button
                onClick={handleGenerateDepositAddress}
                disabled={loading}
                className="w-full"
              >
                {loading ? 'Loading...' : 'Show Deposit Address'}
              </Button>

              {depositAddress && (
                <div className="mt-6 space-y-4">
                  {/* CRITICAL: Payment Reference Section */}
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Label className="text-sm font-bold text-red-800 dark:text-red-200">🔥 PAYMENT REFERENCE (REQUIRED)</Label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCopyReference}
                        className="h-6 p-1"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <p className="font-mono text-lg font-bold bg-white dark:bg-gray-600 text-red-900 dark:text-red-100 p-3 rounded border-2 border-red-300 dark:border-red-700 text-center">
                      {depositReference}
                    </p>
                    <div className="mt-3 p-3 bg-red-100 dark:bg-red-900/30 rounded">
                      <p className="text-xs font-bold text-red-900 dark:text-red-100">
                        ⚠️ YOU MUST INCLUDE THIS REFERENCE IN YOUR DEPOSIT OR WE CANNOT CREDIT YOUR ACCOUNT!
                      </p>
                    </div>
                  </div>

                  {/* Deposit Address Section */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Label className="text-sm font-medium text-gray-700 dark:text-gray-300">Deposit Address</Label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleCopyAddress}
                        className="h-6 p-1"
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                    <p className="font-mono text-sm bg-white dark:bg-gray-600 text-gray-900 dark:text-white p-2 rounded border break-all">
                      {depositAddress}
                    </p>
                  </div>
                  
                  {/* Instructions Section */}
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                      <div className="text-xs text-blue-800 dark:text-blue-200">
                        <p className="font-medium mb-2">📋 Deposit Instructions:</p>
                        <ol className="space-y-1 list-decimal list-inside">
                          <li>Send {depositCurrency} to the address above using {depositNetwork} network</li>
                          <li><strong>Include reference "{depositReference}" in transaction description</strong></li>
                          <li>Alternative: Contact support with reference {depositReference}</li>
                          <li>Your account will be credited after confirmation (5-30 minutes)</li>
                          <li>Minimum deposit: $10 USD equivalent</li>
                        </ol>
                        <p className="mt-2 font-bold text-red-600 dark:text-red-400">
                          ⚠️ Without the reference, automatic crediting is not possible!
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Withdrawal Modal */}
      {showWithdrawModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Withdraw Cryptocurrency</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowWithdrawModal(false)}>
                ×
              </Button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="withdrawCurrency" className="text-gray-700 dark:text-gray-300">Currency</Label>
                  <select
                    id="withdrawCurrency"
                    value={withdrawCurrency}
                    onChange={(e) => {
                      setWithdrawCurrency(e.target.value);
                      if (e.target.value === 'USDC') {
                        setWithdrawNetwork('ERC20');
                      }
                    }}
                    className="w-full mt-1 p-2 border rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                  >
                    <option value="USDT">USDT</option>
                    <option value="USDC">USDC</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="withdrawNetwork" className="text-gray-700 dark:text-gray-300">Network</Label>
                  <select
                    id="withdrawNetwork"
                    value={withdrawNetwork}
                    onChange={(e) => setWithdrawNetwork(e.target.value)}
                    className="w-full mt-1 p-2 border rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                  >
                    <option value="ERC20">ERC20</option>
                    {withdrawCurrency === 'USDT' && (
                      <option value="TRC20">TRC20</option>
                    )}
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="withdrawAmount" className="text-gray-700 dark:text-gray-300">Amount (USD)</Label>
                <Input
                  id="withdrawAmount"
                  type="number"
                  step="0.01"
                  min="10"
                  max="100000"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  placeholder="Enter amount"
                  className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                />
                {withdrawAmount && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Fee: ~${Math.max(fees.withdrawal?.minimum_fee || 5, parseFloat(withdrawAmount || 0) * (fees.withdrawal?.percentage_fee || 0.02)).toFixed(2)}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="withdrawAddress" className="text-gray-700 dark:text-gray-300">Recipient Address</Label>
                <Input
                  id="withdrawAddress"
                  value={withdrawAddress}
                  onChange={(e) => setWithdrawAddress(e.target.value)}
                  placeholder={withdrawNetwork === 'ERC20' ? '0x...' : 'T...'}
                  className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                />
              </div>

              <div>
                <Label htmlFor="withdrawMemo" className="text-gray-700 dark:text-gray-300">Memo (Optional)</Label>
                <Input
                  id="withdrawMemo"
                  value={withdrawMemo}
                  onChange={(e) => setWithdrawMemo(e.target.value)}
                  placeholder="Enter memo if required"
                  className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600"
                />
              </div>

              <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-yellow-800 dark:text-yellow-200">
                    <p className="font-medium">Security Notice:</p>
                    <p>Double-check the recipient address and network. Transactions cannot be reversed.</p>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleWithdraw}
                disabled={loading || !withdrawAmount || !withdrawAddress}
                className="w-full"
              >
                {loading ? 'Processing...' : 'Submit Withdrawal'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CryptoPayments;