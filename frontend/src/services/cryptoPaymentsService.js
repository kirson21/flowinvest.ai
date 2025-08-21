/**
 * Crypto Payments Service
 * Handles all cryptocurrency payment related API calls
 */

class CryptoPaymentsService {
  constructor() {
    this.backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  /**
   * Generate or retrieve deposit address for user
   */
  async generateDepositAddress(userId, currency, network) {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/deposit/address`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          currency: currency.toUpperCase(),
          network: network.toUpperCase()
        })
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error generating deposit address:', error);
      return {
        success: false,
        message: 'Failed to generate deposit address'
      };
    }
  }

  /**
   * Submit cryptocurrency withdrawal request
   */
  async submitWithdrawal(userId, withdrawalData) {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/withdrawal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...withdrawalData,
          user_id: userId
        })
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error submitting withdrawal:', error);
      return {
        success: false,
        message: 'Failed to submit withdrawal request'
      };
    }
  }

  /**
   * Get user's crypto transaction history
   */
  async getCryptoTransactions(userId, options = {}) {
    try {
      const {
        limit = 50,
        offset = 0,
        transactionType = null
      } = options;

      let url = `${this.backendUrl}/api/crypto/transactions?user_id=${userId}&limit=${limit}&offset=${offset}`;
      
      if (transactionType) {
        url += `&transaction_type=${transactionType}`;
      }

      const response = await fetch(url);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching crypto transactions:', error);
      return {
        success: false,
        transactions: [],
        message: 'Failed to fetch crypto transactions'
      };
    }
  }

  /**
   * Get transaction status by ID
   */
  async getTransactionStatus(userId, transactionId) {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/status/${transactionId}?user_id=${userId}`);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching transaction status:', error);
      return {
        success: false,
        message: 'Failed to fetch transaction status'
      };
    }
  }

  /**
   * Get supported cryptocurrencies and networks
   */
  async getSupportedCurrencies() {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/supported-currencies`);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching supported currencies:', error);
      return {
        success: false,
        currencies: [],
        networks: {},
        message: 'Failed to fetch supported currencies'
      };
    }
  }

  /**
   * Get withdrawal fees and limits
   */
  async getWithdrawalFees() {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/fees`);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching withdrawal fees:', error);
      return {
        success: false,
        fees: {},
        limits: {},
        message: 'Failed to fetch withdrawal fees'
      };
    }
  }

  /**
   * Get crypto payment system health status
   */
  async getHealthStatus() {
    try {
      const response = await fetch(`${this.backendUrl}/api/crypto/health`);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error fetching health status:', error);
      return {
        status: 'unhealthy',
        error: error.message
      };
    }
  }

  /**
   * Validate cryptocurrency address format
   */
  validateAddress(address, currency, network) {
    if (!address || address.length < 20) {
      return { valid: false, error: 'Address is too short' };
    }

    const patterns = {
      'USDT_ERC20': /^0x[a-fA-F0-9]{40}$/,
      'USDC_ERC20': /^0x[a-fA-F0-9]{40}$/,
      'USDT_TRC20': /^T[A-Za-z0-9]{33}$/
    };

    const key = `${currency}_${network}`;
    const pattern = patterns[key];

    if (!pattern) {
      return { valid: false, error: 'Unsupported currency/network combination' };
    }

    if (!pattern.test(address)) {
      return { 
        valid: false, 
        error: `Invalid ${currency} ${network} address format` 
      };
    }

    return { valid: true };
  }

  /**
   * Calculate withdrawal fee
   */
  calculateWithdrawalFee(amount, feeConfig = {}) {
    const minimumFee = feeConfig.minimum_fee || 5;
    const percentageFee = feeConfig.percentage_fee || 0.02;
    
    return Math.max(minimumFee, amount * percentageFee);
  }

  /**
   * Format crypto transaction for display
   */
  formatTransaction(transaction) {
    const formattedTransaction = {
      ...transaction,
      formattedAmount: this.formatCurrency(transaction.amount),
      formattedFee: transaction.total_fee ? this.formatCurrency(transaction.total_fee) : null,
      formattedDate: new Date(transaction.created_at).toLocaleString(),
      shortHash: transaction.transaction_hash ? 
        `${transaction.transaction_hash.substring(0, 10)}...${transaction.transaction_hash.substring(transaction.transaction_hash.length - 8)}` : 
        null,
      networkDisplayName: this.getNetworkDisplayName(transaction.network),
      statusColor: this.getStatusColor(transaction.status),
      typeIcon: transaction.transaction_type === 'deposit' ? 'ArrowDownCircle' : 'ArrowUpCircle'
    };

    return formattedTransaction;
  }

  /**
   * Get network display name
   */
  getNetworkDisplayName(network) {
    const networkNames = {
      'ERC20': 'Ethereum',
      'TRC20': 'Tron',
      'BTC': 'Bitcoin'
    };
    
    return networkNames[network] || network;
  }

  /**
   * Get status color for UI
   */
  getStatusColor(status) {
    const statusColors = {
      'pending': 'yellow',
      'processing': 'blue',
      'confirmed': 'green',
      'failed': 'red',
      'cancelled': 'gray'
    };
    
    return statusColors[status] || 'gray';
  }

  /**
   * Format currency amount
   */
  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 8
    }).format(amount);
  }

  /**
   * Generate QR code URL for address (if needed)
   */
  generateQRCodeUrl(address, amount = null, currency = null) {
    let qrData = address;
    
    if (amount && currency) {
      qrData += `?amount=${amount}&token=${currency}`;
    }
    
    // Using QR Server API (you can replace with your preferred QR service)
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrData)}`;
  }

  /**
   * Get explorer URL for transaction hash
   */
  getExplorerUrl(transactionHash, network) {
    const explorers = {
      'ERC20': `https://etherscan.io/tx/${transactionHash}`,
      'TRC20': `https://tronscan.org/#/transaction/${transactionHash}`,
      'BTC': `https://blockstream.info/tx/${transactionHash}`
    };
    
    return explorers[network] || null;
  }

  /**
   * Monitor transaction status (polling)
   */
  async monitorTransaction(userId, transactionId, onStatusUpdate, pollInterval = 30000) {
    const poll = async () => {
      try {
        const result = await this.getTransactionStatus(userId, transactionId);
        if (result.success) {
          onStatusUpdate(result.transaction);
          
          // Stop polling if transaction is in final state
          if (['confirmed', 'failed', 'cancelled'].includes(result.transaction.status)) {
            return;
          }
        }
      } catch (error) {
        console.error('Error monitoring transaction:', error);
      }
      
      // Schedule next poll
      setTimeout(poll, pollInterval);
    };
    
    // Start polling
    poll();
  }
}

// Create and export singleton instance
export const cryptoPaymentsService = new CryptoPaymentsService();
export default cryptoPaymentsService;