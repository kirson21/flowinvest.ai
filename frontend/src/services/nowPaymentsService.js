/**
 * NowPayments Service - Frontend API Client
 * Handles communication with NowPayments backend endpoints
 */

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class NowPaymentsService {
  /**
   * Make API request to backend
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}/api/nowpayments${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const requestOptions = {
      ...defaultOptions,
      ...options,
    };

    try {
      const response = await fetch(url, requestOptions);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error('NowPayments API Error:', error);
      throw error;
    }
  }

  /**
   * Check NowPayments service health
   */
  async healthCheck() {
    return this.makeRequest('/health');
  }

  /**
   * Get supported cryptocurrencies and networks
   */
  async getSupportedCurrencies() {
    return this.makeRequest('/currencies');
  }

  /**
   * Get minimum payment amount for currency pair
   */
  async getMinimumAmount(currencyFrom = 'usd', currencyTo = 'usdttrc20') {
    return this.makeRequest(`/min-amount?currency_from=${currencyFrom}&currency_to=${currencyTo}`);
  }

  /**
   * Get price estimate for crypto payment
   */
  async getEstimate(amount, currencyFrom = 'usd', currencyTo = 'usdttrc20') {
    return this.makeRequest(`/estimate?amount=${amount}&currency_from=${currencyFrom}&currency_to=${currencyTo}`);
  }

  /**
   * Create payment invoice
   */
  async createInvoice(invoiceData, userId) {
    // Validate userId is provided
    if (!userId) {
      throw new Error('User ID is required for invoice creation');
    }
    
    return this.makeRequest(`/invoice?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify(invoiceData),
    });
  }

  /**
   * Get payment status by ID
   */
  async getPaymentStatus(paymentId, userId = 'demo_user') {
    return this.makeRequest(`/payment/${paymentId}?user_id=${userId}`);
  }

  /**
   * Get user's payment history
   */
  async getUserPayments(userId = 'demo_user', limit = 50) {
    return this.makeRequest(`/user/${userId}/payments?limit=${limit}`);
  }

  /**
   * Create subscription plan
   */
  async createSubscriptionPlan(planData) {
    return this.makeRequest('/subscription/plan', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  }

  /**
   * Create subscription for user
   */
  async createSubscription(subscriptionData, userId) {
    // Validate userId is provided
    if (!userId) {
      throw new Error('User ID is required for subscription creation');
    }
    
    return this.makeRequest(`/subscription?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify(subscriptionData),
    });
  }

  /**
   * Process successful payment return
   */
  async handlePaymentReturn(orderId, status) {
    // This could be used to update local state or trigger notifications
    console.log(`Payment return: Order ${orderId} - Status: ${status}`);
    
    if (status === 'success') {
      // Optionally refresh user balance or show success message
      return { success: true, message: 'Payment completed successfully!' };
    } else {
      return { success: false, message: 'Payment was cancelled or failed.' };
    }
  }

  /**
   * Format currency display name
   */
  formatCurrencyDisplay(currency, network) {
    const currencyNames = {
      'USDT': 'Tether USD',
      'USDC': 'USD Coin'
    };
    
    const networkNames = {
      'TRX': 'Tron',
      'BSC': 'Binance Smart Chain',
      'SOL': 'Solana',
      'TON': 'TON',
      'ETH': 'Ethereum'
    };
    
    const currencyName = currencyNames[currency] || currency;
    const networkName = networkNames[network] || network;
    
    return `${currencyName} (${networkName})`;
  }

  /**
   * Get network display information
   */
  getNetworkInfo(network) {
    const networkInfo = {
      'TRX': {
        name: 'Tron',
        color: '#FF0013',
        icon: '⚡'
      },
      'BSC': {
        name: 'Binance Smart Chain',
        color: '#F3BA2F',
        icon: '🔶'
      },
      'SOL': {
        name: 'Solana',
        color: '#9945FF',
        icon: '☀️'
      },
      'TON': {
        name: 'TON',
        color: '#0088CC',
        icon: '💎'
      },
      'ETH': {
        name: 'Ethereum',
        color: '#627EEA',
        icon: '⟠'
      }
    };
    
    return networkInfo[network] || { name: network, color: '#666', icon: '🪙' };
  }

  /**
   * Validate payment amount (basic validation, real minimum checked separately)
   */
  validateAmount(amount) {
    const numAmount = parseFloat(amount);
    
    if (isNaN(numAmount) || numAmount <= 0) {
      return { valid: false, error: 'Amount must be a positive number' };
    }
    
    if (numAmount < 5) {
      return { valid: false, error: 'Minimum amount is $5.00' };
    }
    
    if (numAmount > 10000) {
      return { valid: false, error: 'Maximum amount is $10,000.00' };
    }
    
    return { valid: true };
  }

  /**
   * Validate email address
   */
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Get payment status badge info
   */
  getStatusBadge(status) {
    const statusInfo = {
      'waiting': { text: 'Waiting', color: 'orange', icon: '⏳' },
      'confirming': { text: 'Confirming', color: 'blue', icon: '🔄' },
      'confirmed': { text: 'Confirmed', color: 'green', icon: '✅' },
      'sending': { text: 'Sending', color: 'blue', icon: '📤' },
      'partially_paid': { text: 'Partial', color: 'yellow', icon: '⚠️' },
      'finished': { text: 'Completed', color: 'green', icon: '🎉' },
      'failed': { text: 'Failed', color: 'red', icon: '❌' },
      'expired': { text: 'Expired', color: 'gray', icon: '⏰' }
    };
    
    return statusInfo[status] || { text: status, color: 'gray', icon: '❓' };
  }

  /**
   * Format amount for display
   */
  formatAmount(amount, currency = 'USD') {
    if (typeof amount !== 'number') {
      amount = parseFloat(amount) || 0;
    }
    
    if (currency === 'USD' || currency === 'usd') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    }
    
    return `${amount.toFixed(8)} ${currency.toUpperCase()}`;
  }

  /**
   * Generate order description
   */
  generateOrderDescription(amount, purpose = 'Balance Top-up') {
    return `f01i.ai ${purpose} - ${this.formatAmount(amount)}`;
  }

  /**
   * Redirect to invoice URL
   */
  redirectToInvoice(invoiceUrl) {
    // Open in new tab for better UX
    window.open(invoiceUrl, '_blank', 'noopener,noreferrer');
  }
}

// Export singleton instance
const nowPaymentsService = new NowPaymentsService();
export default nowPaymentsService;